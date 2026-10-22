"""Primary document corpus and deterministic financial operators for round two."""
import hashlib
import json
import os
from pathlib import Path
import re
from bs4 import BeautifulSoup
from probe import ROOT,save,now

OUT=ROOT/'data/round2'
DOCS={
 'inspur':['inspur_annual_2025'], 'innolight':['innolight_annual_2025'],
 'kehua':['kehua_annual_2025'], 'envicool':['envicool_annual_2025','envicool_h1_2026'],
 'smci':['smci_fy2025'], 'cohr':['coherent_fy2025_tables','coherent_optics_product'],
 'etn':['eaton_fy2025'], 'vrt':['vertiv_annual_2025','vertiv_fy2025','vertiv_q2_2026','vertiv_cooling_product'],
 'global':['nvidia_blackwell_ultra_2025']}

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))

def ratio(a,b):
    if a is None or b in (None,0):return None
    if (a['currency'],a['period_start'],a['period_end'])!=(b['currency'],b['period_start'],b['period_end']):
        raise ValueError('ratio currency or period mismatch')
    return None if b['value'] in (None,0) or a['value'] is None else a['value']/b['value']

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    sources={};metrics={};companies={c['id']:c for c in load('data/company_research.json')['companies'] if c['research_depth']=='deep'}
    for company,docs in DOCS.items():
        for doc in docs:
            text=(ROOT/f'artifacts/public/{doc}.txt').read_text(encoding='utf-8')
            meta=load(f'artifacts/public/{doc}.meta.json')
            original=f'artifacts/public/{doc}'+('.txt' if meta.get('retrieval_method')=='web_tool_transcription' else ('.pdf' if meta['pages'] else '.html'))
            chunks=re.split(r'\[PDF PAGE (\d+)\]',text)
            if len(chunks)>1:parts=[(f'p{chunks[i]}',chunks[i+1]) for i in range(1,len(chunks),2)]
            else:parts=[(f'c{i//1500}',text[i:i+1800]) for i in range(0,len(text),1500)]
            for locator,chunk in parts:
                if not chunk.strip():continue
                sid=f'r2.{doc}.{locator}'
                sources[sid]={'id':sid,'company_id':company,'document_id':doc,'title':meta['title'],'url':meta['url'],'published_at':meta['published_at'],'retrieved_at':meta['retrieved_at'],'local_path':original,'sha256':digest(ROOT/original),'locator':locator,'access':'analyst_transcription' if meta.get('retrieval_method') else 'public_primary','text':chunk.strip()}

    def source_for(doc,anchor):
        options=[s for s in sources.values() if s['document_id']==doc and anchor.lower() in s['text'].lower()]
        if not options:raise ValueError(f'Cannot locate {doc}: {anchor}')
        return options[0]['id']

    def add(cid,period,name,value,sid,currency,start,end,scope,formula=None,inputs=None,note=None):
        mid=f'm.{cid}.{period}.{name}'
        metrics[mid]={'id':mid,'company_id':cid,'period':period,'name':name,'value':value,'currency':currency,'period_start':start,'period_end':end,'unit':'ratio' if formula and 'divide' in formula else ('percent' if name.endswith('_yoy_pct') else 'currency_units'),'scope':scope,'source_ids':[sid] if isinstance(sid,str) else sid,'formula':formula,'input_metric_ids':inputs or [],'note':note,'missing_reason':'本轮未核实该项，保持null' if value is None else None}
        return metrics[mid]

    for cid,c in companies.items():
        currency='CNY' if c['market']=='CN' else 'USD'
        for old in c['metrics']:
            if old['name'] not in ['revenue','parent_net_profit','net_profit','related_revenue']:continue
            doc=DOCS[cid][0]
            sid=source_for(doc,{'inspur':'16,478,199.77','innolight':'38,239,935,640.67','kehua':'8,160,262,477.61','envicool':'6,067,759,091.55','smci':'21,972,042','cohr':'5,810','etn':'27.4 billion','vrt':'10,229.9'}[cid])
            add(cid,'FY2025',old['name'],old['value'],sid,currency,old['period_start'],old['period_end'],old['scope'],note=old.get('disclosure_status'))
        if c['market']=='CN':
            income=load(f'artifacts/raw/fuyao_{cid}_financial.json')['response']['data']['item']
            cash=load(f'artifacts/raw/r2_{cid}_cashflow.json')['response']['data']['item']
            for period_year in [2025,2024]:
                row=next(r for r in cash if r['fiscal_year']==period_year)
                ir=next(r for r in income if r['fiscal_year']==period_year)
                if row['currency']!='CNY' or row['thscode']!=c['ticker']:raise ValueError('source identity mismatch')
                sid=f'r2.api.{cid}.cashflow.{period_year}';path=f'artifacts/raw/r2_{cid}_cashflow.json'
                sources[sid]={'id':sid,'company_id':cid,'document_id':path,'title':'扶摇合并现金流原始响应','url':'https://fuyao.aicubes.cn'+load(path)['request']['path'],'published_at':None,'retrieved_at':load(path)['retrieved_at'],'local_path':path,'sha256':digest(ROOT/path),'locator':f'fiscal_year={period_year}','access':'authenticated_api','text':json.dumps(row,ensure_ascii=False)}
                start=f'{period_year}-01-01';end=f'{period_year}-12-31';period=f'FY{period_year}'
                ocf=add(cid,period,'ocf',row.get('act_cash_flow_net'),sid,'CNY',start,end,'consolidated_operating_cash_flow')
                capex=add(cid,period,'cash_capex',row.get('pay_fixed_assets_etc_cash'),sid,'CNY',start,end,'cash_paid_to_acquire_fixed_intangible_other_long_term_assets')
                profit=add(cid,period,'consolidated_net_profit',ir.get('net_profit'),sid,'CNY',start,end,'consolidated_net_profit',note='数值来自对应扶摇合并利润表；输入来源另列于raw/fuyao公司financial.json')
                income_path=f'artifacts/raw/fuyao_{cid}_financial.json';psid=f'r2.api.{cid}.income.{period_year}'
                sources[psid]={**sources[sid],'id':psid,'title':'扶摇合并利润表原始响应','url':'https://fuyao.aicubes.cn'+load(income_path)['request']['path'],'local_path':income_path,'sha256':digest(ROOT/income_path),'text':json.dumps(ir,ensure_ascii=False)}
                profit['source_ids']=[psid]
                add(cid,period,'cash_conversion',ratio(ocf,profit),[sid,psid],'CNY',start,end,'consolidated_ocf / consolidated_net_profit','divide(ocf,consolidated_net_profit)',[ocf['id'],profit['id']])
                add(cid,period,'ocf_less_cash_capex',None if ocf['value'] is None or capex['value'] is None else ocf['value']-capex['value'],sid,'CNY',start,end,'经营现金流减购建长期资产现金支出；分析代理，非公司披露自由现金流','subtract(ocf,cash_capex)',[ocf['id'],capex['id']])

    def cn_line(label):
        text=(ROOT/'artifacts/public/envicool_h1_2026.txt').read_text(encoding='utf-8')
        compact=re.sub(r'\s+','',text);label=re.sub(r'\s+','',label)
        pos=compact.find(label)
        if pos<0:raise ValueError('missing CN row '+label)
        values=re.findall(r'-?\d[\d,]*\.\d{2}',compact[pos+len(label):pos+len(label)+120])
        if len(values)<2:raise ValueError('cannot parse CN row '+label)
        return [float(x.replace(',','')) for x in values[:2]],source_for('envicool_h1_2026',label[:5])
    cn_values={}
    for name,label,scope in [('revenue','营业收入（元）','consolidated_total'),('parent_net_profit','归属于上市公司股东的净利润（元）','attributable_to_parent'),('ocf','经营活动产生的现金流量净额（元）','consolidated_operating_cash_flow'),('consolidated_net_profit','五、净利润（净亏损以“—”号填列）','consolidated_net_profit'),('cash_capex','购建固定资产、无形资产和其他长期资产支付的现金','cash_paid_to_acquire_fixed_intangible_other_long_term_assets')]:
        vals,sid=cn_line(label);cn_values[name]=vals
        for index,year in enumerate([2026,2025]):add('envicool',f'H1{year}',name,vals[index],sid,'CNY',f'{year}-01-01',f'{year}-06-30',scope)
    for year in [2026,2025]:
        ocf=metrics[f'm.envicool.H1{year}.ocf'];profit=metrics[f'm.envicool.H1{year}.consolidated_net_profit'];capex=metrics[f'm.envicool.H1{year}.cash_capex']
        add('envicool',f'H1{year}','cash_conversion',ratio(ocf,profit),ocf['source_ids']+profit['source_ids'],'CNY',ocf['period_start'],ocf['period_end'],'consolidated_ocf / consolidated_net_profit','divide(ocf,consolidated_net_profit)',[ocf['id'],profit['id']])
        add('envicool',f'H1{year}','ocf_less_cash_capex',ocf['value']-capex['value'],ocf['source_ids']+capex['source_ids'],'CNY',ocf['period_start'],ocf['period_end'],'经营现金流减长期资产购建支出，非公司披露FCF','subtract(ocf,cash_capex)',[ocf['id'],capex['id']])

    def us_rows(doc):
        soup=BeautifulSoup((ROOT/f'artifacts/public/{doc}.html').read_text(encoding='utf-8'),'html.parser')
        return [' '.join(tr.stripped_strings) for tr in soup.select('tr')]
    def numbers(row,label):
        tail=row[len(label):];raw=re.findall(r'\(?-?\d[\d,]*(?:\.\d+)?\)?',tail)
        return [-float(x[1:-1].replace(',','')) if x.startswith('(') and x.endswith(')') else float(x.replace(',','')) for x in raw]
    for doc,period,years,indices in [('vertiv_q2_2026','H1',[2026,2025],[2,3]),('vertiv_fy2025','FY',[2025,2024],[2,3])]:
        rows=us_rows(doc)
        for name,label,scope in [('revenue','Net sales','consolidated_total'),('consolidated_net_profit','Net income (loss)','consolidated_net_profit'),('ocf','Net cash provided by (used for) operating activities','consolidated_operating_cash_flow'),('cash_capex','Capital expenditures','cash_capital_expenditures_excludes_capitalized_software')]:
            matches=[r for r in rows if r.startswith(label) and re.match(r'^[\$\d(]',r[len(label):].lstrip()) and len(numbers(r,label))==4]
            if not matches:continue
            row=matches[0];vals=numbers(row,label)
            for year,index in zip(years,indices):
                sid=source_for(doc,f'{abs(vals[index]):,.1f}')
                add('vrt',f'{period}{year}',name,abs(vals[index])*1e6 if name=='cash_capex' else vals[index]*1e6,sid,'USD',f'{year}-01-01',f'{year}-06-30' if period=='H1' else f'{year}-12-31',scope,note='单位美元百万换算；原表列顺序为当季本期、当季同期、累计本期、累计同期')
        for year in years:
            p=f'{period}{year}';ocf=metrics.get(f'm.vrt.{p}.ocf');profit=metrics.get(f'm.vrt.{p}.consolidated_net_profit');capex=metrics.get(f'm.vrt.{p}.cash_capex')
            if ocf and profit:add('vrt',p,'cash_conversion',ratio(ocf,profit),ocf['source_ids']+profit['source_ids'],'USD',ocf['period_start'],ocf['period_end'],'consolidated_ocf / consolidated_net_profit','divide(ocf,consolidated_net_profit)',[ocf['id'],profit['id']])
            if ocf and capex:add('vrt',p,'ocf_less_cash_capex',ocf['value']-capex['value'],ocf['source_ids']+capex['source_ids'],'USD',ocf['period_start'],ocf['period_end'],'经营现金流减资本开支，不等于公司adjusted FCF；未扣资本化软件','subtract(ocf,cash_capex)',[ocf['id'],capex['id']])
    # Compare like periods only. A negative/zero base is not turned into an ordinary growth rate.
    for cid in ['envicool','vrt']:
        for name in ['revenue','parent_net_profit','consolidated_net_profit','ocf']:
            current=metrics.get(f'm.{cid}.H12026.{name}');prior=metrics.get(f'm.{cid}.H12025.{name}')
            if current and prior:
                value=None if prior['value'] is None or prior['value']<=0 else (current['value']/prior['value']-1)*100
                add(cid,'H12026',name+'_yoy_pct',value,current['source_ids']+prior['source_ids'],current['currency'],current['period_start'],current['period_end'],name+'同比，负基期不输出常规增长率','growth_positive_base',[current['id'],prior['id']],note='若上年基数不为正，增长率置空并看绝对额变化')
    # Parse an issuer-hosted filing with the installed open-source library, offline.
    os.environ['EDGAR_LOCAL_DATA_DIR']=str(ROOT/'artifacts/edgar-cache');os.environ['EDGAR_CACHE_DIR']=str(ROOT/'artifacts/edgar-cache')
    try:
        from edgar.documents import parse_html
        document=parse_html((ROOT/'artifacts/public/vertiv_10k_2025_html.html').read_text(encoding='utf-8'))
        parsed=document.text();(ROOT/'artifacts/public/vertiv_10k_2025.edgartools.txt').write_text(parsed,encoding='utf-8')
        save('artifacts/round2/edgartools_parse.json',{'status':'success','mode':'offline issuer-hosted Form10K HTML parsing','text_chars':len(parsed),'table_count':len(document.tables),'sec_identity_required':False,'note':'本次使用本地已下载10-K解析，没有声称绕过SEC的身份或访问要求'})
    except Exception as e:save('artifacts/round2/edgartools_parse.json',{'status':'failed','error':type(e).__name__})
    save('data/round2/sources.json',{'sources':sources});save('data/round2/financial_metrics.json',{'metrics':metrics});save('data/round2/company_registry.json',{'companies':companies})
    print(json.dumps({'sources':len(sources),'metrics':len(metrics),'companies':len(companies)}))

if __name__=='__main__':prepare()
