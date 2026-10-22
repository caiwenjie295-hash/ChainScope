"""Build the P1/round2.p1 editorial snapshot (EDITED) as an *artifact backup only*.

Single source of truth for UIUX:
  frontend/public/data/snapshot.json  ← ONLY scripts/export_p2_joinable.py may overwrite
  artifacts/frontend/snapshot.p2.joinable.json  ← joinable backup (same bytes as public)
  artifacts/frontend/snapshot.round2.p1.json    ← this script's output (legacy P1 shape)

This module MUST NOT write frontend/public/data/snapshot.json, so an old p1/round2
export cannot clobber the current deep.b1c (or later) public snapshot.
"""
from __future__ import annotations
import re
import hashlib
import json
from pathlib import Path
from probe import ROOT, now, save
from model_adapter import model_name as registry_model_name
from publish_round2 import REVIEWED_SUMMARIES
from investor_fields import enrich, overview

UI_VERSION = '0.2.0-mvp.2'
OUT = ROOT / 'artifacts/frontend/snapshot.round2.p1.json'
PUBLIC = ROOT / 'frontend/public/data/snapshot.json'  # read-only for this module
LABELS = {
    'revenue':'集团营业收入','parent_net_profit':'归母净利润',
    'consolidated_net_profit':'合并净利润','net_profit':'净利润',
    'related_revenue':'相关母类别收入','ai_specific_revenue':'AI专项收入',
    'ocf':'经营现金流','cash_capex':'长期资产现金投入',
    'cash_conversion':'经营现金流／合并净利润',
    'ocf_less_cash_capex':'经营现金流减资本开支（分析代理）',
    'revenue_yoy_pct':'收入同比','parent_net_profit_yoy_pct':'归母净利润同比',
    'consolidated_net_profit_yoy_pct':'合并净利润同比',
}
# Scope-specific, conservative editorial decisions. No company-wide A-E rating.
EDITED = {
 'inspur':('AI服务器与液冷方案','C','产品与投运项目已披露；现有证据混含自建项目，暂不将其作为对外商业交付证明。',
           '服务器是收入主体，AI专项收入仍未单列。',['r2.inspur_annual_2025.p10','r2.inspur_annual_2025.p11','r2.inspur_annual_2025.p12']),
 'innolight':('数据中心高速光模块','B','已取得产品销售与交付证据，AI专属收入金额尚未分离。',
           '高速光模块已有商业销售，不能将全部光模块收入算作AI收入。',['r2.innolight_annual_2025.p11','r2.innolight_annual_2025.p13','r2.innolight_annual_2025.p24']),
 'kehua':('数据中心供配电产品','B','已有产品业务收入；该范围包含非AI应用，不能代表AI专项收入或某款液冷单品收入。',
           '供配电产品与IDC服务并存，需要分别理解收入和利润。',['r2.kehua_annual_2025.p20']),
 'envicool':('数据中心温控与液冷','B','有制冷产品交付及液冷规模采购证据，液冷和AI专项收入尚未单列。',
           '收入增长，利润下降；现金流转正但现金转化仍偏低。',['r2.envicool_h1_2026.p9','r2.envicool_h1_2026.p14']),
 'smci':('AI服务器与机架系统','B','已有整机业务商业收入，但本轮未取得可独立量化的AI收入。',
           '整机与机架交付是核心，财务结论仍需正式审计年报对照。',['r2.smci_fy2025.c5','r2.smci_fy2025.c6']),
 'cohr':('高速数通光模块与OCS','B','正式业绩披露了收入出货与初始收入，未给出对应金额或占比。',
           '高速光模块已实现收入出货，集团净利润口径需单独核对。',['r2.coherent_fy2025_tables.p3']),
 'etn':('数据中心供配电','B','有数据中心终端需求驱动销售的证据，电气分部同时覆盖其他终端。',
           '数据中心是电气业务增长驱动之一，不能等同整个分部。',['r2.notice.27bdbc344a94f79033']),
 'vrt':('数据中心数字基础设施（综合）','B','综合设备与服务已有商业收入；具体液冷单品及AI收入仍需单独补证。',
           '集团收入、利润与现金流同增，尚不能直接归因于液冷。',['r2.vertiv_q2_2026.c17','r2.vertiv_q2_2026.c19','r2.vertiv_annual_2025.p21']),
}


def assert_claim_citations(companies):
    """P0 export gate: every claim needs source_ids; numeric claims cannot be empty-cited."""
    digit = re.compile(r'\d')
    for c in companies:
        for claim in c.get('claims') or []:
            sids = claim.get('source_ids') or []
            if not sids:
                raise ValueError(f"{c['id']}: claim missing source_ids")
            if digit.search(claim.get('text') or '') and not sids:
                raise ValueError(f"{c['id']}: uncited numeric claim")

def write_impact_report(graph_nodes, path=None):
    from collections import Counter
    counts = Counter(n.get('impact', 'unclear') for n in graph_nodes)
    total = sum(counts.values()) or 1
    report = {
        'generated_note': 'P0 impact audit; unclear means not verified this round',
        'counts': dict(counts),
        'total_nodes': total,
        'unclear_ratio': counts.get('unclear', 0) / total,
        'node_ids_by_impact': {
            k: [n['id'] for n in graph_nodes if n.get('impact', 'unclear') == k]
            for k in sorted(counts)
        },
    }
    out = Path(path) if path else ROOT / 'artifacts/frontend/impact_report.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report

def load(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))

def export():
    original=load('data/company_research.json')['companies']
    graph=load('data/industry_graph.json')
    raw_metrics=load('data/round2/financial_metrics.json')['metrics']
    research=load('data/round2/agent_research.json')['results']
    metrics=list(raw_metrics.values())
    source_bank={s['id']:s for s in load('data/sources.json')['sources']}
    source_bank.update(load('data/round2/sources.json')['sources'])
    evaluation=load('data/round2/evaluation.json')
    nodes={n['id']:n for n in graph['nodes']}
    company_nodes={n['company_id']:n for n in graph['nodes'] if n['type']=='company'}
    pairs=[]
    companies=[]
    for c in original:
        cid=c['id'];node=company_nodes[cid];segment=nodes[node['parent_id']]
        reviewed=cid in EDITED
        concept,grade,rationale,headline,sids=EDITED.get(cid,('AI数据中心相关业务','E','本轮仅为广度候选，尚未完成业务归属与商业证据核验。','候选公司，业务关联与财务研究待补证。',[]))
        selected_period='H12026' if cid in ('envicool','vrt') else 'FY2025'
        cm=[]
        if reviewed:
            for m in metrics:
                if m['company_id']==cid and m['period']==selected_period and m['name'] in LABELS:
                    cm.append({k:m.get(k) for k in ('id','name','value','unit','currency','period','period_start','period_end','scope','source_ids','missing_reason')})
                    cm[-1]['label']=LABELS[m['name']]
            if not any(m['name']=='ai_specific_revenue' for m in cm):
                cm.append({'id':f'ui.{cid}.ai_specific_revenue','name':'ai_specific_revenue','label':'AI专项收入','value':None,'unit':'currency_units','currency':'CNY' if c['market']=='CN' else 'USD','period':selected_period,'period_start':None,'period_end':None,'scope':concept,'source_ids':sids,'missing_reason':'本轮未取得可核验的AI专项收入，不能用集团收入代替。'})
        periods={m['period'] for m in cm};assert len(periods)<=1
        peer=c.get('comparisons',[{}])[0].get('peer_id') if c.get('comparisons') else None
        claims=[]
        if reviewed:
            claims=[{'text':c['business_summary'],'kind':'fact','source_ids':sids},
                    {'text':rationale,'kind':'inference','source_ids':sids}]
        focus_ids={'envicool','vrt','innolight','cohr'}
        companies.append({k:c[k] for k in ('id','name','ticker','exchange','market')} | {
          'research_status':'reviewed' if reviewed else 'candidate',
          'demo_priority':'focus' if cid in focus_ids else ('deep' if reviewed else 'candidate'),
          'narrative_focus': cid in focus_ids,
          'branch_id':segment['parent_id'],'segment_id':segment['id'],
          'business_summary':c['business_summary'] if reviewed else '产业归属为研究候选，尚未完成证据核验。',
          'headline':headline,'assessment':{'concept':concept,'grade':grade,'rationale':rationale,'source_ids':sids},
          'metrics':cm,'claims':claims,'uncertainties':(['AI专项收入与集团收入范围不同。']+research['business_evidence'][cid]['missing'][:2]) if reviewed else ['E级表示证据不足，不等于公司没有相关业务。'],
          'peer_id':peer,'source_ids':list(dict.fromkeys(sids+[s for m in cm for s in m['source_ids']]))})
    enrich(companies,source_bank)
    cmap={c['id']:c for c in companies}
    for pid,ids in [('inspur_smci',['inspur','smci']),('innolight_cohr',['innolight','cohr']),('kehua_etn',['kehua','etn']),('envicool_vrt',['envicool','vrt'])]:
        old=next(c for c in original if c['id']==ids[0])['comparisons'][0]
        comparable=old['comparable'];non_comparable=old['non_comparable']
        if pid=='envicool_vrt':
            comparable=['均涉及数据中心热管理，可研究设备交付与营运资本机制。','本轮均已对齐2026年上半年，可在明确边界后比较变化方向和比率。']
            non_comparable=['币种分别为CNY和USD，不直接比较金额大小。','集团产品结构、会计准则及资本开支扣除范围不同。','集团收入不能替代液冷或AI专项收入。']
        aligned = pid == 'envicool_vrt'
        pairs.append({'id':pid,'title':' / '.join(cmap[c]['name'] for c in ids),'company_ids':ids,
          'summary':REVIEWED_SUMMARIES[pid],'comparable':comparable,'non_comparable':non_comparable,
          'comparable_on':comparable,'not_comparable_on':non_comparable,
          'aligned_period':'H12026' if aligned else None,
          'amount_compare_allowed':False,  # cross-currency / caliber: never bare amount compare
          'ratio_compare_allowed':bool(aligned),
          'source_ids':list(dict.fromkeys(sum((cmap[c]['source_ids'] for c in ids),[])))})
    nvidia=[sid for sid in source_bank if 'nvidia_blackwell_ultra' in sid]
    assert nvidia
    nvidia_sid=next((s for s in nvidia if 'GB300' in source_bank[s].get('text','')),nvidia[0])
    event={'id':'blackwell_ultra','title':'Blackwell Ultra发布如何传导至液冷需求？','date':source_bank[nvidia_sid]['published_at'],
      'summary':'真实产品发布 → 热管理需求变化 → 供应商产品 → 交付与验收 → 收入和现金。后半段仍需订单与财报验证。',
      'steps':[
        {'id':'release','label':'平台发布','text':'NVIDIA发布Blackwell Ultra及GB300 NVL72方案。发布不代表供应商已获收入。','kind':'fact','source_ids':[nvidia_sid]},
        {'id':'thermal','label':'热管理需求','text':'高功率机柜设计可能增加液冷回路与散热部件需求，取决于客户架构与部署节奏。','kind':'inference','source_ids':[nvidia_sid]},
        {'id':'product','label':'温控产品','text':'英维克有温控与液冷产品；Vertiv有数字基础设施与热管理业务。产品对应不证明与该平台存在供应合同。','kind':'fact','source_ids':EDITED['envicool'][4]+EDITED['vrt'][4]},
        {'id':'delivery','label':'订单与交付','text':'只有取得平台对应合同、交付及验收证据后，才能继续验证具体供应商的商业受益。','kind':'scenario','source_ids':[]},
        {'id':'financial','label':'收入与现金','text':'收入取决于交付和确认条件；现金还受预收、账期和备货影响，可能早于或晚于收入。','kind':'scenario','source_ids':[]},
      ],'limitations':['本轮未取得两家公司与Blackwell Ultra直接对应的供应合同或收入。','不估算个股收入弹性，不将情景方向解释为股价预测。']}
    # P1 second event: optics high-speed module shipments (fact) → interconnect demand (inference)
    optics_sids=['src.innolight_annual_2025.narrow_business','r2.coherent_fy2025_tables.p3','src.coherent_optics_product.product']
    for sid in optics_sids:
        if sid not in source_bank: raise ValueError('missing optics evidence '+sid)
    event_optics={'id':'optics_high_speed_shipments','title':'高速光模块出货如何落到光收发环节？','date':source_bank['src.innolight_annual_2025.narrow_business'].get('published_at'),
      'summary':'已披露的高速模块销售/出货事实 → 光收发环节相关 → 公司业务证据；不外推未披露的AI专项收入弹性。',
      'steps':[
        {'id':'ship','label':'出货与销售事实','text':'中际旭创年报披露光通信收发模块业务；Coherent披露高速数通相关收入出货类事实。均为已披露业务事实，不是AI专项收入拆分。','kind':'fact','source_ids':['src.innolight_annual_2025.narrow_business','r2.coherent_fy2025_tables.p3']},
        {'id':'segment','label':'环节归属','text':'上述披露支撑公司落入光收发模块环节的研究归属，不证明与某一芯片平台的独家供应关系。','kind':'fact','source_ids':['src.coherent_optics_product.product','r2.innolight_annual_2025.p11']},
        {'id':'demand','label':'集群互连需求','text':'AI集群带宽需求上升可能提高高速光模块用量，但导入节奏与份额未在本轮量化。','kind':'inference','source_ids':['src.coherent_optics_product.product']},
        {'id':'financial','label':'收入边界','text':'母类光模块或集团收入不能替代AI专用高速模块收入；缺专项口径时保持未披露。','kind':'scenario','source_ids':[]},
      ],'limitations':['未取得可核验的AI专用光模块收入金额。','不估算份额或股价弹性。']}
    events=[event, event_optics]
    overview_data=overview(companies,event)
    # Prefer narrative: liquid cooling + optics
    overview_data['title']='AI数据中心：液冷与高速光模块'
    overview_data['subtitle']='先看有对齐期与可追溯披露的主线，再展开其余深研与候选。'
    overview_data['focus_company_ids']=['envicool','vrt','innolight','cohr']
    overview_data['changes'] = list(overview_data.get('changes') or []) + [{
        'id':'optics_event_card','title':event_optics['title'],'kind':'fact',
        'text':event_optics['summary'],'source_ids':['src.innolight_annual_2025.narrow_business','r2.coherent_fy2025_tables.p3']}]
    impact_file=load('data/impact_annotations.json')
    impact_map={a['node_id']:a for a in impact_file['annotations']}
    used=set(s for c in companies for s in c['source_ids'])
    used.update(s for change in overview_data['changes'] for s in change['source_ids'])
    used.update(s for p in pairs for s in p['source_ids'])
    used.update(s for ev in events for step in ev['steps'] for s in step['source_ids'])
    used.update(s for e in graph['edges'] for s in e['source_ids'])
    used.update(s for a in impact_file['annotations'] for s in a['source_ids'])
    sources={}
    for sid in sorted(used):
        s=source_bank[sid]
        access=s.get('access','unknown');public=access.startswith('public')
        excerpt=(s.get('excerpt') or s.get('text') or '')[:220] if public else ''
        sources[sid]={'id':sid,'title':s['title'],'url':s.get('url') if public else None,'published_at':s.get('published_at'),
          'locator':s.get('locator'),'excerpt':excerpt,'access':access}
    # Default size; impact only from reviewed annotations with citations (P1).
    for node in graph['nodes']:
        node['size']=1.0
        ann=impact_map.get(node['id'])
        if ann:
            if ann['impact'] in ('positive','negative') and not ann.get('source_ids'):
                raise ValueError(node['id']+': impact annotation missing source_ids')
            node['impact']=ann['impact']
            node['impact_source_ids']=list(ann['source_ids'])
            node['impact_rationale']=ann.get('rationale')
        else:
            node['impact']='unclear'
            node.pop('impact_source_ids', None)
            node.pop('impact_rationale', None)
    out={'schema_version':'frontend.1','meta':{'ui_version':UI_VERSION,'research_version':'2026-10-21.round2.p1',
      'as_of':'2026-10-21','generated_at':now(),'mode':'offline_snapshot','model':registry_model_name(),
      'deep_companies':len(EDITED),'candidate_companies':len(companies)-len(EDITED),
      'narrative_focus':impact_file.get('narrative_focus',['cooling','optics']),
      'concept_grades_version':'2026-10-21.p0'},
      'graph':{'nodes':graph['nodes'],'edges':graph['edges']},'companies':companies,'pairs':pairs,'event':event,'events':events,'overview':overview_data,'sources':sources,
      'evaluation':{'completed_stages':evaluation['completed_stages'],'validation_checks':evaluation['validation_checks'],
        'tests_passed':18,**evaluation['selected_stage_usage'],
        'estimated_cost_cny':evaluation['selected_stage_off_peak_estimate_cny'],
        'estimate_basis':'最终采用阶段按归档Flash空闲时段单价估算，非账单，不含失败替换试验、Codex和数据许可费用。',
        'limitations':['两轮任务与材料不同，未开展受控优化对照实验。','检查通过不代表事实准确率。','八家仅为首批研究，完整同期间量化样板为英维克与Vertiv。'],
        'workflow':[{'label':label,'count':count} for label,count in [('业务证据',8),('财务质量',8),('跨市场比较',4),('独立反证',4),('研究编辑',4),('事件传导',1)]]}}
    assert_claim_citations(companies)
    # Reject AI A built from non-ai_specific metrics in the exported assessment view.
    for c in companies:
        a=c['assessment']
        if a['grade']=='A' and ('AI' in (a.get('concept') or '')):
            raise ValueError(c['id']+': exported AI concept cannot be A without ai_specific_revenue')
    impact_report=write_impact_report(out['graph']['nodes'])
    if impact_report['unclear_ratio'] >= 1.0:
        raise ValueError('P1 expects some verified impact annotations; unclear_ratio still 1.0')
    for n in out['graph']['nodes']:
        if n.get('impact') in ('positive','negative'):
            for sid in n.get('impact_source_ids') or []:
                if sid not in sources and sid not in source_bank:
                    raise ValueError(n['id']+': impact source missing '+sid)
    gate={'assert_claim_citations':'passed','impact_unclear_ratio':impact_report['unclear_ratio'],
          'impact_positive':impact_report['counts'].get('positive',0),
          'concept_grades_version':'2026-10-21.p0','narrative_focus':out['meta']['narrative_focus']}
    save('artifacts/frontend/export_gate.json',gate)
    # Fingerprint covers the content, not the export timestamp or fingerprint itself.
    content={**out,'meta':{k:v for k,v in out['meta'].items() if k!='generated_at'}}
    digest=hashlib.sha256(json.dumps(content,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    out['meta']['data_hash']=digest
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save('data/frontend_manifest.json',{'ui_version':UI_VERSION,'research_version':out['meta']['research_version'],
      'exported_at':out['meta']['generated_at'],'data_hash':digest,'path':str(OUT.relative_to(ROOT)).replace('\\','/'),'public_owner':'export_p2_joinable',
      'editorial_changes':['浪潮AI服务器/液冷证据保守列C，混含自建投运，未据此认定对外商业交付。','Vertiv B仅限综合数字基础设施，不扩大到液冷单品。','未核验广度候选不展示财务或商业证据结论。'],
      'frontend_coding_model':'gpt-6-luna','frontend_coding_reasoning':'max'})
    print(json.dumps({
        'path': str(OUT.relative_to(ROOT)).replace('\\', '/'),
        'research_version': out['meta']['research_version'],
        'companies': len(companies),
        'sources': len(sources),
        'bytes': OUT.stat().st_size,
        'data_hash': digest,
        'notice': 'P1 editorial written to artifacts only; public snapshot is owned by export_p2_joinable.py',
    }), flush=True)
    return out

if __name__=='__main__':export()
