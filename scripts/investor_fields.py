"""Adapt already-cached disclosures to investor questions; no model or network calls."""
import json
import re
from bs4 import BeautifulSoup
from probe import ROOT

def enrich(companies,source_bank):
    def find(doc,anchor):
        candidates=[sid for sid,s in source_bank.items() if s.get('document_id')==doc and anchor in re.sub(r'\s+',' ',s.get('text',''))]
        if not candidates:raise ValueError(f'Financial anchor absent: {doc}/{anchor}')
        return candidates[0]
    def metric(c,name,value,scope,sids,reason=None,**extra):
        period=next((m['period'] for m in c['metrics']),'H12026' if c['id'] in ('envicool','vrt') else 'FY2025')
        year=int(period[-4:]);end=f'{year}-06-30' if period.startswith('H1') else f'{year}-12-31'
        label={'relevant_revenue_share':'AI主题相关收入占比','revenue_yoy':'营业收入同比','gross_margin':'集团毛利率','net_profit_yoy':'净利润同比','gross_margin_change_pp':'毛利率同比变化'}[name]
        result={'id':f'ui.{c["id"]}.{period}.{name}','name':name,'label':label,'value':value,'unit':'percentage_points' if name.endswith('_pp') else 'percent','currency':None,'period':period,'period_start':f'{year}-01-01','period_end':end,'scope':scope,'source_ids':sids,'missing_reason':reason,**extra}
        c['metrics'].append(result)
        return result
    def yoy(current,prior):
        return (current/prior-1)*100 if current is not None and prior is not None and prior>0 else None
    def table_rows(doc):
        soup=BeautifulSoup((ROOT/f'artifacts/public/{doc}.html').read_text(encoding='utf-8'),'html.parser')
        return [' '.join(tr.stripped_strings) for tr in soup.select('tr')]
    def us_row(rows,label):
        matches=[s for s in rows if s.startswith(label) and re.match(r'^[\$\d(]',s[len(label):].lstrip())]
        for s in matches:
            numbers=re.findall(r'\(?-?\d[\d,]*(?:\.\d+)?\)?',s[len(label):])
            if len(numbers)==4:
                return [(-1 if n.startswith('(') else 1)*float(n.strip('()').replace(',','')) for n in numbers]
        raise ValueError('Cannot match consolidated table row '+label)
    for c in companies:
        reviewed=c['research_status']=='reviewed';cm={m['name']:m for m in c['metrics']}
        c.update({'report_period':next((m['period'] for m in c['metrics']),None),'evidence_id':c['assessment']['source_ids'][:],
          'comparable_company_ids':[c['peer_id']] if c['peer_id'] else [],'impact_paths':['blackwell_ultra'] if c['id'] in ('envicool','vrt') else [],'business_composition':[]})
        for name in ('relevant_revenue_share','revenue_yoy','gross_margin','net_profit_yoy','gross_margin_change_pp'):
            c[name]=metric(c,name,None,'AI专项口径' if name=='relevant_revenue_share' else '集团合并口径',c['assessment']['source_ids'],
              '本轮未取得可核验的AI专项收入占比，不能用母类别占比替代。' if name=='relevant_revenue_share' else '本轮未取得本报告期可核验数据。') if reviewed else None
        if not reviewed:continue
        def assign(name,value,scope,sids,reason=None,**extra):
            m=c[name];m.update({'value':value,'scope':scope,'source_ids':sids,'missing_reason':reason,**extra})
        cid=c['id'];period=c['report_period']
        if cid in ('inspur','innolight','kehua'):
            rows=json.loads((ROOT/f'artifacts/raw/fuyao_{cid}_financial.json').read_text(encoding='utf-8'))['response']['data']['item']
            a=next(r for r in rows if r['fiscal_year']==2025);b=next(r for r in rows if r['fiscal_year']==2024)
            if any(r['currency']!='CNY' or r['thscode']!=c['ticker'] for r in (a,b)):raise ValueError('income identity mismatch')
            sids=[f'r2.api.{cid}.income.2025',f'r2.api.{cid}.income.2024']
            doc={'inspur':'inspur_annual_2025','innolight':'innolight_annual_2025','kehua':'kehua_annual_2025'}[cid]
            cost_anchor={'inspur':'15,673,500.42','innolight':'22,165,537,126.77','kehua':'6,156,493,643.38'}[cid]
            sids.append(find(doc,cost_anchor))
            assign('revenue_yoy',yoy(a['operating_income'],b['operating_income']),'集团营业收入，同比；上年数采用本年报告比较口径',sids)
            gm=(1-a['operating_costs']/a['operating_income'])*100;prior=(1-b['operating_costs']/b['operating_income'])*100
            assign('gross_margin',gm,'集团合并毛利率；(营业收入－营业成本)／营业收入',sids)
            assign('gross_margin_change_pp',gm-prior,'集团毛利率同比变化，单位为百分点',sids)
            assign('net_profit_yoy',yoy(a['net_profit'],b['net_profit']),'集团合并净利润同比，非归母口径',sids)
        elif cid=='envicool':
            current=cm['revenue']['value'];prior=2573139460.90
            sid=find('envicool_h1_2026','2,264,528,834.12')
            sids=[sid]+cm['revenue']['source_ids']
            gm=(1-2264528834.12/current)*100
            assign('gross_margin',gm,'集团合并毛利率；(营业收入－营业成本)／营业收入',sids)
            # Preserve the issuer's disclosed rounded change, rather than silently
            # showing a different last decimal from unrounded re-computation.
            change_sid=find('envicool_h1_2026','-1.22%')
            assign('gross_margin_change_pp',-1.22,'公司披露集团毛利率同比变化，单位为百分点；保留披露的四舍五入值',[change_sid])
            for new,old in [('revenue_yoy','revenue_yoy_pct'),('net_profit_yoy','consolidated_net_profit_yoy_pct')]:
                assign(new,cm[old]['value'],'集团营业收入同比' if new=='revenue_yoy' else '集团合并净利润同比，非归母口径',cm[old]['source_ids'])
            part_sid=find('envicool_h1_2026','1,700,144,828.46')
            c['business_composition']=[{'label':'机房温控节能产品','share':1700144828.46/current*100,'scope':'母类别，包含风冷及非AI应用；不代表液冷或AI收入占比','source_ids':[part_sid]+cm['revenue']['source_ids'],'period':period,'missing_reason':None}]
        elif cid=='vrt':
            doc='vertiv_q2_2026';rows=table_rows(doc)
            costs=us_row(rows,'Cost of sales');revenue=us_row(rows,'Net sales')
            gm=(1-costs[2]/revenue[2])*100;last_gm=(1-costs[3]/revenue[3])*100
            sid=find(doc,'3,689.2')
            assign('gross_margin',gm,'集团US GAAP毛利率；合并收入与合并销售成本计算',[sid]+cm['revenue']['source_ids'])
            assign('gross_margin_change_pp',gm-last_gm,'集团毛利率同比变化，单位为百分点',[sid]+cm['revenue']['source_ids'])
            for new,old in [('revenue_yoy','revenue_yoy_pct'),('net_profit_yoy','consolidated_net_profit_yoy_pct')]:
                assign(new,cm[old]['value'],'集团营业收入同比' if new=='revenue_yoy' else '集团合并净利润同比',cm[old]['source_ids'])
        elif cid=='smci':
            doc='smci_fy2025';rows=table_rows(doc)
            rev=us_row(rows,'Net sales');cost=us_row(rows,'Cost of sales');profit=us_row(rows,'Net income')
            sid=find(doc,'21,972,042');sids=[sid,find(doc,'19,542,120'),find(doc,'1,048,854')]
            gm=(1-cost[2]/rev[2])*100;prior=(1-cost[3]/rev[3])*100
            assign('revenue_yoy',yoy(rev[2],rev[3]),'US GAAP集团收入同比；未经审计业绩发布',sids)
            assign('gross_margin',gm,'US GAAP全年集团毛利率；非第四季度毛利率，非Non-GAAP',sids)
            assign('gross_margin_change_pp',gm-prior,'US GAAP全年毛利率同比变化，百分点；未经审计',sids)
            assign('net_profit_yoy',yoy(profit[2],profit[3]),'US GAAP集团净利润同比；未经审计业绩发布',sids)
        elif cid=='cohr':
            sid=find('coherent_fy2025_tables','35.2%')
            assign('gross_margin',35.2,'集团US GAAP全年毛利率；公司披露百分数已四舍五入',[sid])
            sid2=find('coherent_fy2025_tables','revenue growth of 23%')
            assign('revenue_yoy',23.0,'集团全年收入同比；公司披露百分数已四舍五入',[sid2])
            c['net_profit_yoy']['missing_reason']='未计算负基数或GAAP净亏损的普通同比百分比；不得以Non-GAAP盈利替代。'
        if not c['business_composition'] and 'related_revenue' in cm and cm['related_revenue']['value'] is not None:
            related=cm['related_revenue'];total=cm['revenue']
            if related['period']==total['period'] and related['currency']==total['currency']:
                c['business_composition']=[{'label':{'inspur':'服务器产品','innolight':'光通信收发模块','kehua':'数据中心产品（不含IDC服务）'}.get(cid,'相关母类别'),
                  'share':related['value']/total['value']*100,'scope':related['scope']+'；包含非AI应用，不代表AI专项收入占比',
                  'source_ids':related['source_ids']+total['source_ids'],'period':period,'missing_reason':None}]
        c['source_ids']=list(dict.fromkeys(c['source_ids']+[sid for m in c['metrics'] for sid in m['source_ids']]+[sid for item in c['business_composition'] for sid in item['source_ids']]))
        c['evidence_id']=c['source_ids'][:]

def overview(companies,event):
    reviewed=[c for c in companies if c['research_status']=='reviewed']
    return {'title':'AI 算力扩张如何影响产业链企业？',
      'subtitle':'从算力、光通信、供配电到液冷，先看真实业务，再看增长是否转化为利润。',
      'coverage':{'total':len(companies),'researched':len(reviewed),'candidates':len(companies)-len(reviewed),
        'scoped_revenue_evidence_count':sum(c['assessment']['grade']=='A' for c in reviewed),'revenue_evidence_denominator':len(reviewed),
        'commercial_evidence_count':sum(c['assessment']['grade'] in ('A','B') for c in reviewed),
        'scope_label':'本轮已核验的AI主题相关口径；母类别收入不算AI专项收入',
        'comparable_pairs':4,'validated_impact_paths':0,'conditional_impact_cases':1},
      'changes':[
        {'title':'驱动：机柜级算力部署','text':'Blackwell Ultra发布提供了机柜级部署案例；后续供应商收入仍须交付证据验证。','kind':'fact','date':event['date'],'source_ids':event['steps'][0]['source_ids']},
        {'title':'光通信：新产品进入收入出货','text':'Coherent披露1.6T数通模块收入出货；这不等于已拆出AI收入金额。','kind':'fact','date':None,'source_ids':['r2.coherent_fy2025_tables.p3']},
        {'title':'液冷：增长与盈利兑现有差异','text':'2026上半年英维克收入增长、利润下降；Vertiv集团收入与利润同增。不能据此把集团表现归为液冷表现。','kind':'inference','date':None,'source_ids':['r2.envicool_h1_2026.p7','r2.vertiv_q2_2026.c17']},
      ],'focus_company_ids':['envicool','vrt','innolight','cohr','inspur','smci','kehua','etn']}
