"""Build a reproducible analyst-reviewed snapshot from cached real sources."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from probe import ROOT, now, save
from models import Research, Sources, Graph

SOURCES=[]
PACKETS={}
AS_OF='2026-10-21'

def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))

def document(doc, tag, anchor):
    text=(ROOT/f'artifacts/public/{doc}.txt').read_text(encoding='utf-8')
    meta=read(f'artifacts/public/{doc}.meta.json')
    pos=text.lower().find(anchor.lower())
    if pos<0:raise ValueError(f'Anchor missing: {doc}: {anchor}')
    page_matches=list(re.finditer(r'\[PDF PAGE (\d+)\]',text[:pos]))
    locator=f"PDF page {page_matches[-1].group(1)}" if page_matches else f'text offset {pos}, anchor: {anchor}'
    eid='src.'+doc+'.'+tag
    excerpt=text[pos:pos+min(65,len(anchor)+20)].strip()
    item={'id':eid,'title':meta['title'],'provider':'company_disclosure','source_type':'annual_report' if 'annual' in doc else ('product_release' if 'product' in doc or 'delivery' in doc else 'earnings_release'),'url':meta['url'],'published_at':meta['published_at'],'retrieved_at':meta['retrieved_at'],'local_path':f'artifacts/public/{doc}'+('.txt' if meta.get('retrieval_method')=='web_tool_transcription' else ('.pdf' if meta['pages'] else '.html')),'sha256':meta['sha256'],'locator':locator,'excerpt':excerpt,'excerpt_kind':'analyst_transcription' if meta.get('retrieval_method')=='web_tool_transcription' else 'original','access':'public_verified','limitations':(['公司原始披露的第三方镜像，未验证与巨潮文件字节一致'] if doc.startswith('inspur') else (['官网已通过网页工具读取；本地仅保存人工转录事实，不含原始HTML'] if meta.get('retrieval_method')=='web_tool_transcription' else []))}
    if not any(s['id']==eid for s in SOURCES):SOURCES.append(item)
    PACKETS[eid]=text[max(0,pos-250):pos+1800]
    return eid

def api_source(raw_id, tag, text, source_type='api_profile'):
    rec=read('artifacts/raw/'+raw_id+'.json')
    eid='src.'+raw_id+'.'+tag
    source={'id':eid,'title':raw_id+' / '+tag,'provider':rec['request']['provider'],'source_type':source_type,'url':('https://fuyao.aicubes.cn'+rec['request']['path']) if rec['request']['provider']=='fuyao' else None,'published_at':None,'retrieved_at':rec['retrieved_at'],'local_path':'artifacts/raw/'+raw_id+'.json','sha256':hashlib.sha256((ROOT/'artifacts/raw'/f'{raw_id}.json').read_bytes()).hexdigest(),'locator':tag,'excerpt':text[:200],'access':'authenticated_api','limitations':['需有效账户权限复取；MCP结果没有提供原公告直链，不能当成已核验全文'] if rec['request']['provider']!='fuyao' else ['供应商标准化字段；需核对业务口径及原报告']}
    SOURCES.append(source);PACKETS[eid]=text[:3500]
    return eid

def metric(cid,name,value,currency,period,start,end,scope,sids,unit='currency_units',missing=None,basis=None,status='reported'):
    return {'id':f'{cid}.{name}','name':name,'value':value,'unit':unit,'currency':currency,'period':period,'period_start':start,'period_end':end,'scope':scope,'accounting_basis':basis or ('CAS' if currency=='CNY' else 'US_GAAP'),'disclosure_status':status,'source_ids':sids,'missing_reason':missing}

def claim(cid,text,sids,kind='fact',verification='primary_checked'):
    return {'id':cid,'text':text,'kind':kind,'source_ids':sids,'verification':verification,'limitations':[]}

def assessment(concept,grade,rationale,sids,revenue_id=None,limitations=None):
    return {'concept':concept,'grade':grade,'rationale':rationale,'revenue_metric_id':revenue_id,'source_ids':sids,'limitations':limitations or []}

def unwrap(raw_id):
    rec=read('artifacts/raw/'+raw_id+'.json')
    obj=json.loads(rec['response']['result']['content'][0]['text'])
    if obj.get('code')!=1:raise ValueError('iFinD business error')
    return obj['data']

def build():
    global SOURCES,PACKETS
    SOURCES=[];PACKETS={}
    companies=[]
    deep_specs=[
      ('inspur','浪潮信息','000977.SZ','SZSE','server','inspur_annual_2025','服务器产品','服务器等云计算基础设施；收入包含通用服务器与AI服务器。','Supermicro','smci',154605252900.0,'服务器产品（年报万元换算为元，原表四舍五入）'),
      ('innolight','中际旭创','300308.SZ','SZSE','transceiver','innolight_annual_2025','光通信收发模块','高速光通信收发模块；产品用于数据中心及通信网络。','Coherent','cohr',37456518745.90,'光通信收发模块（包含非AI应用）'),
      ('kehua','科华数据','002335.SZ','SZSE','power_equipment','kehua_annual_2025','数据中心产品','数据中心基础设施、电源、新能源及IDC服务。','Eaton','etn',2239034564.24,'数据中心产品（不含IDC服务，包含非AI应用，非UPS单品）'),
      ('envicool','英维克','002837.SZ','SZSE','thermal','envicool_annual_2025','机房温控节能产品','精密温控设备，覆盖机房、储能等应用；提供液冷产品。','Vertiv','vrt',3448477492.62,'机房温控节能产品（含风冷，包含非AI应用）')
    ]
    broad_concepts=['服务器','光通信收发模块','数据中心基础设施产品','机房温控']
    narrow_concepts=['AI服务器','AI专用高速光模块','AI数据中心UPS','AI数据中心液冷']
    for i,(cid,name,ticker,exchange,segment,doc,anchor,summary,peername,peer,relevant,scope) in enumerate(deep_specs):
        related_revenue_anchor={'inspur':'15,460,525.29','innolight':'37,456,518,745.90','kehua':'2,239,034,564.24','envicool':'3,448,477,492.62'}[cid]
        business=document(doc,'business',related_revenue_anchor)
        raw_id=f'fuyao_{cid}_financial';row=read('artifacts/raw/'+raw_id+'.json')['response']['data']['item'][0]
        if row['fiscal_year']!=2025 or row['thscode']!=ticker:raise ValueError('financial identity/period mismatch')
        fin=api_source(raw_id,'FY2025',json.dumps(row,ensure_ascii=False),'api_financial')
        # Financial table anchors are checked against the source text, not inferred from a model.
        fin_anchor={'inspur':'16,478,199.77','innolight':'38,239,935,640.67','kehua':'8,160,262,477.61','envicool':'6,067,759,091.55'}[cid]
        docfin=document(doc,'financial',fin_anchor)
        metrics=[metric(cid,'revenue',row['operating_income'],'CNY','FY2025','2025-01-01','2025-12-31','consolidated_total',[fin,docfin]),metric(cid,'parent_net_profit',row['parent_holder_net_profit'],'CNY','FY2025','2025-01-01','2025-12-31','attributable_to_parent',[fin]),metric(cid,'related_revenue',relevant,'CNY','FY2025','2025-01-01','2025-12-31',scope,[business]),metric(cid,'ai_specific_revenue',None,'CNY','FY2025','2025-01-01','2025-12-31',narrow_concepts[i],[business],missing='当前核验材料未单列该窄口径收入；不得用母类别或公司总收入替代')]
        narrow_anchor={'inspur':'超节点 AI 服务器','innolight':'800G','kehua':'100kW','envicool':'规模采购应用'}[cid]
        narrow=document(doc,'narrow_business',narrow_anchor)
        company={'id':cid,'name':name,'ticker':ticker,'exchange':exchange,'market':'CN','domicile':'中国','research_depth':'deep','business_summary':summary,'claims':[claim(cid+'.business',summary,[business,narrow]),claim(cid+'.scope_boundary','相关业务收入不等于AI专用业务收入。',[business],'inference','analyst_inference')],'assessments':[assessment(broad_concepts[i],'A','年报披露可核验的相关业务收入；等级仅适用于本条概念及收入口径。',[business],cid+'.related_revenue'),assessment(narrow_concepts[i],'C' if cid=='inspur' else 'B','本次核验到明确产品发布；未单独核实AI产品销售交付，保守C。' if cid=='inspur' else '年报存在商业业务或规模应用证据，未单列对应窄口径收入。',[narrow],limitations=['不能解释成已知AI收入占比'])],'metrics':metrics,'comparisons':[],'uncertainties':['不将母类别收入当作AI业务收入','当前采用FY2025作为财务比较基线，未声称为研究日最新季度'],'ai_analysis':None}
        if cid=='inspur':company['uncertainties'].append('年报对2024年比较数据作同一控制合并追溯调整，增长率需使用调整后口径；服务器收入由万元换算且带原表舍入误差')
        companies.append(company)

    us_specs=[
      ('smci','Supermicro','SMCI','NASDAQ','美国','server','smci_fy2025','Net sales','liquid cooling',21972042000.0,1048854000.0,'2024-07-01','2025-06-30','服务器及存储等IT系统，包含多种冷却方案。','B','服务器与IT系统','未审计业绩新闻稿，后续应与10-K复核'),
      ('cohr','Coherent','COHR','NYSE','美国','transceiver','coherent_fy2025_tables','Revenues','First Revenue from 1.6T',5810000000.0,None,'2024-07-01','2025-06-30','光子与光学器件，覆盖数据通信、电信及工业等市场；1.6T数通模块已有收入发货。','B','数据中心光通信','收入采用业绩披露四舍五入值；正净利润与负普通股EPS可能并存，不能混为同一指标'),
      ('etn','Eaton','ETN','NYSE','爱尔兰','power_equipment','eaton_fy2025','27.4 billion','data center',27400000000.0,None,'2025-01-01','2025-12-31','电气和电力管理等多元业务；数据中心相关需求属于部分业务。','C','AI数据中心供配电','本次核验到数据中心推动订单进展，但未单独核实对应销售交付，保守C；公司收入含航空等业务；收入采用官网舍入值'),
      ('vrt','Vertiv','VRT','NYSE','美国','thermal','vertiv_fy2025','10,229.9','critical digital infrastructure',10229900000.0,1332800000.0,'2025-01-01','2025-12-31','关键数字基础设施产品与服务；液冷单品不能用公司总收入计量。','C','AI液冷产品','已核验液冷产品发布；本次材料尚未核实对应交付和收入，保守标C')
    ]
    for cid,name,ticker,exchange,domicile,segment,doc,fin_anchor,biz_anchor,revenue,profit,start,end,summary,grade,concept,limitation in us_specs:
        fin=document(doc,'financial',fin_anchor)
        biz=document(doc,'business',biz_anchor)
        extra=[]
        if cid=='cohr':extra=[document('coherent_optics_product','product','transceivers')]
        if cid=='etn':extra=[]
        if cid=='vrt':extra=[document('vertiv_cooling_product','product','CoolLoop')]
        metrics=[metric(cid,'revenue',revenue,'USD','FY2025',start,end,'consolidated_total',[fin],status='unaudited_release' if cid=='smci' else ('rounded_reported' if cid=='cohr' else 'reported')),metric(cid,'net_profit',profit,'USD','FY2025',start,end,'GAAP_net_income_not_EPS',[fin],missing='本次不提取该净利润值，避免与普通股EPS、优先股调整或合并口径混淆' if profit is None else None),metric(cid,'ai_specific_revenue',None,'USD','FY2025',start,end,concept,[biz]+extra,missing='本次核验材料未给出对应AI专用业务收入')]
        companies.append({'id':cid,'name':name,'ticker':ticker,'exchange':exchange,'market':'US','domicile':domicile,'research_depth':'deep','business_summary':summary,'claims':[claim(cid+'.business',summary,[biz]+extra),claim(cid+'.scope_boundary',limitation,[fin],'inference','analyst_inference')],'assessments':[assessment(concept,grade,limitation,[biz]+extra,limitations=['未使用集团总收入证明窄口径收入'])],'metrics':metrics,'comparisons':[],'uncertainties':[limitation,'FY2025基线，不等于2026年10月最新季度数据'],'ai_analysis':None})

    index={c['id']:c for c in companies}
    pairs=[('inspur','smci',['均设计生产销售服务器等IT基础设施','可比较产品组合、利润率与营运资本'],['AI服务器与全部服务器口径不同','中国企业会计准则与US GAAP；CNY与USD','自然年与6月末财年不同，未做汇率归一']),('innolight','cohr',['高速光互联产品与数据中心需求存在交集'],['Coherent含上游器件、材料、工业业务，业务边界更宽','中际旭创披露模块收入；Coherent总收入不能代替光模块收入','财年、币种和会计准则不同']),('kehua','etn',['数据中心供配电、UPS等基础设施需求有交集'],['科华包含IDC与新能源；Eaton包含航空等多元业务','总收入、数据中心产品收入和UPS收入不是同一口径','同为12月末财年，币种与会计准则仍不同']),('envicool','vrt',['面向高密度计算的温控与冷却需求有交集'],['英维克有储能温控；Vertiv含供配电与服务','机房温控包含风冷，不能与液冷单品直接比较','本次Vertiv液冷为产品证据C级，未核实交付，不能拔高等级'])]
    for left,right,same,different in pairs:
        sids=list(dict.fromkeys(index[left]['claims'][0]['source_ids']+index[right]['claims'][0]['source_ids']))
        index[left]['comparisons']=[{'peer_id':right,'comparable':same,'non_comparable':different,'source_ids':sids}]
        index[right]['comparisons']=[{'peer_id':left,'comparable':same,'non_comparable':different,'source_ids':sids}]

    profiles=[('cn_profiles_compute',{'000977.SZ':('inspur','server'),'601138.SH':('fii','server'),'603019.SH':('sugon','server'),'000938.SZ':('unis','network_switch')}),('cn_profiles_optics',{'300308.SZ':('innolight','transceiver'),'300502.SZ':('eoptolink','transceiver'),'300394.SZ':('tfc','optical_component'),'002281.SZ':('accelink','optical_component')}),('cn_profiles_power_cooling',{'002335.SZ':('kehua','power_equipment'),'002518.SZ':('kstar','power_equipment'),'002837.SZ':('envicool','thermal'),'301018.SZ':('shenling','thermal')}),('us_profiles_more',{'NVDA.O':('nvda','accelerator'),'AMD.O':('amd','accelerator'),'DELL.N':('dell','server'),'ANET.N':('anet','network_switch'),'LITE.O':('lite','optical_component'),'AVGO.O':('avgo','network_chip')})]
    segments={spec[0]:spec[4] for spec in deep_specs};segments.update({s[0]:s[5] for s in us_specs})
    for raw_id,mapping in profiles:
        data=unwrap(raw_id);table=data['answer']
        rows=[r.split('|')[1:-1] for r in table.splitlines() if r.startswith('|')]
        header=[c.strip() for c in rows[0]]
        for cells in rows[2:]:
            row=dict(zip(header,[c.strip() for c in cells]));ticker=row.get('证券代码')
            if ticker not in mapping:continue
            cid,segment=mapping[ticker];segments[cid]=segment
            if cid in index:continue
            business=row.get('主营业务','')
            if not business.strip():continue
            sid=api_source(raw_id,cid,' | '.join(cells))
            market='CN' if raw_id.startswith('cn') else 'US'
            companies.append({'id':cid,'name':row.get('证券简称',cid),'ticker':ticker,'exchange':'SZSE' if ticker.endswith('.SZ') else ('SSE' if ticker.endswith('.SH') else ('NASDAQ' if ticker.endswith('.O') else 'NYSE')),'market':market,'domicile':'中国' if market=='CN' else '美国','research_depth':'breadth','business_summary':business,'claims':[claim(cid+'.business',business,[sid],verification='provider_only'),claim(cid+'.membership','基于主营业务的宽口径产业环节候选，尚未完成AI产品证据核验。',[sid],'inference','pending')],'assessments':[assessment('AI数据中心相关窄口径业务','E','本条仅有宽泛主营业务，尚未完成针对性核验；E不等于证明没有业务。',[sid])],'metrics':[],'comparisons':[],'uncertainties':['仅广度层候选：主营业务已取数，AI关联与业务收入待核验','不据此编造供应商关系'],'ai_analysis':None})

    # Preserve notice fragments as supplemental evidence, never silently promote them to originals.
    for raw_id in ['cn_notice_inspur','cn_notice_innolight','cn_notice_kehua','cn_notice_envicool','cn_notice_breadth_compute','cn_notice_breadth_optics','cn_notice_breadth_power_cooling']:
        fragments=unwrap(raw_id)
        if isinstance(fragments,str):fragments=json.loads(fragments)
        for j,fragment in enumerate(fragments):
            if '公告片段内容' not in fragment:continue
            sid=api_source(raw_id,str(j),fragment['公告片段内容'],'notice_excerpt')
            source=next(s for s in SOURCES if s['id']==sid)
            source.update(title=fragment.get('公告标题',raw_id),published_at=fragment.get('日期'),access='excerpt_only')
    # Disclosed taxonomy, not actual customer/supplier relationships.
    taxonomy={'compute':('算力与AI服务器',{'accelerator':'计算芯片','server':'服务器与整机'}),'optics':('高速光通信',{'optical_component':'光器件','transceiver':'光收发模块','network_switch':'网络交换设备（光互联配套）','network_chip':'网络芯片（光互联配套）'}),'power':('供配电',{'power_equipment':'供配电设备与UPS'}),'cooling':('液冷散热',{'thermal':'温控与液冷相关设备'})}
    nodes=[{'id':'theme.ai_dc','label':'AI数据中心基础设施','type':'theme','parent_id':None,'company_id':None,'market':None,'layer':0,'distance_basis':'人工定义产业分类层级，不是统计相关系数','size':1,'size_basis':'固定大小','impact':'unclear'}];edges=[]
    segment_parent={}
    for branch,(label,children) in taxonomy.items():
        bid='branch.'+branch
        nodes.append({'id':bid,'label':label,'type':'branch','parent_id':'theme.ai_dc','company_id':None,'market':None,'layer':1,'distance_basis':'人工定义分类第1层','size':1,'size_basis':'固定大小','impact':'unclear'})
        edges.append({'id':'edge.'+bid,'source':'theme.ai_dc','target':bid,'type':'taxonomy','kind':'inference','direction':'unclear','confidence':'medium','source_ids':[],'mechanism':'按技术功能分类；不是供应关系','conditions':[]})
        for segment,slabel in children.items():
            sid='segment.'+segment;segment_parent[segment]=sid
            nodes.append({'id':sid,'label':slabel,'type':'segment','parent_id':bid,'company_id':None,'market':None,'layer':2,'distance_basis':'人工定义分类第2层','size':1,'size_basis':'固定大小','impact':'unclear'})
            edges.append({'id':'edge.'+sid,'source':bid,'target':sid,'type':'taxonomy','kind':'inference','direction':'unclear','confidence':'medium','source_ids':[],'mechanism':'业务功能子类；不表示所有子类均为AI专用','conditions':[]})
    for c in companies:
        node='company.'+c['id'];parent=segment_parent[segments[c['id']]]
        nodes.append({'id':node,'label':c['name'],'type':'company','parent_id':parent,'company_id':c['id'],'market':c['market'],'layer':3,'distance_basis':'按已披露主营业务或候选归属分层，非相关系数','size':1,'size_basis':'统一默认尺寸；相关收入口径不可比，不按集团总收入放大','impact':'unclear'})
        edges.append({'id':'edge.'+node,'source':parent,'target':node,'type':'industry_membership','kind':'inference','direction':'unclear','confidence':'medium' if c['research_depth']=='deep' else 'low','source_ids':c['claims'][0]['source_ids'],'mechanism':c['business_summary'],'conditions':['宽口径产业归属，不构成具体客户/供应商关系','广度候选AI关联待核验'] if c['research_depth']=='breadth' else ['不把集团或母类别收入等同AI收入']})
    chain_source=document('innolight_annual_2025','industry_chain','光模块行业的上游')
    edges.append({'id':'edge.optical_components_to_modules','source':'segment.optical_component','target':'segment.transceiver','type':'technology','kind':'fact','direction':'unclear','confidence':'high','source_ids':[chain_source],'mechanism':'年报描述光模块上游包含光芯片、有源及无源光器件；下游包含数通、电信等应用。此为环节关系，不推定任意两家公司存在供应合同。','conditions':['不把产业层级关系当作具体客户关系']})
    research=Research(companies=companies).model_dump(); sources=Sources(sources=SOURCES).model_dump()
    graph=Graph(taxonomy_basis='研究者按设备功能分为四分支；分支为平行技术功能，不强行串成单一上下游链；公司归属依据事实材料并明确推断属性',nodes=nodes,edges=edges).model_dump()
    save('data/company_research.json',research);save('data/sources.json',sources);save('data/industry_graph.json',graph)
    # Minimal sample is a real, validated company, not fictional data.
    save('examples/company_research.real.json',Research(companies=[companies[0]]).model_dump())
    save('artifacts/evidence_packets.json',PACKETS)
    save('artifacts/analyst_review.json',{'reviewed_at':now(),'reviewer':'Codex source inspection','scope':'八家公司主要业务、相关收入口径、四组对标边界；非全面审计','notes':['广度层E候选未计为AI业务已验证公司','Vertiv液冷仅产品证据，保守C','海外MCP财年错配结果隔离，不进入指标','Coherent净利润与普通股EPS分开处理']})
    print(json.dumps({'companies':len(companies),'deep':sum(c['research_depth']=='deep' for c in companies),'sources':len(SOURCES),'graph_nodes':len(nodes)},ensure_ascii=True))

if __name__=='__main__':build()
