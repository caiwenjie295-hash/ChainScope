"""Bounded repair stage, preserving rejected drafts and upstream handoffs."""
import asyncio
import json
from probe import ROOT,save,now
from round2_agents import Bank,run_role

async def repair():
    path=ROOT/'data/round2/agent_research.json';data=json.loads(path.read_text(encoding='utf-8'));bank=Bank();r=data['results']
    original=json.dumps(data,sort_keys=True,ensure_ascii=False)
    import hashlib
    save('artifacts/round2/before_repair.'+hashlib.sha256(original.encode()).hexdigest()[:12]+'.json',data)
    repairs=[]
    if r['financial_quality'].get('vrt') is None:
        task='只研究Vertiv财务质量。必须financial_snapshot(vrt,FY2025)和financial_snapshot(vrt,H12026)，再search_evidence(vrt,[cash flow,working capital,customer advances])核验现金流归因。现金转化与现金流减资本开支直接引用metric_ids，文字不要写任何数字或FY/H1标签，最多三条结论。集团现金流不能等于液冷现金流；预收、应收与应付贡献分别解释。'
        r['financial_quality']['vrt']=await run_role(bank,'financial_quality','vrt',['vrt'],task)
        repairs.append('financial_quality.vrt')
    # The narrow cooling pair is the deep sample; repair and re-review it whenever a
    # financial stage failed, or a prior critic was blocked on unseen citations.
    if not data.get('repair_completed'):
        ids=['envicool','vrt'];drafts={role:{cid:r[role][cid] for cid in ids} for role in ['business_evidence','financial_quality']}
        task='独立反证温控对比稿。先用financial_snapshot取两家公司H12026，再直接read_evidence核实r2.envicool_h1_2026.p7、r2.envicool_h1_2026.p47、r2.vertiv_q2_2026.c19；必要时再查一个原文，合计最多六个工具。重点：两家本次可对齐自然年上半年，不能笼统称不可同期；发出商品不等于收入已确认，更不能说收入领先验收；公司积压不是收入；投资资本开支不能作为经营现金流增减的直接组成。只引用本轮自己读到的来源。最多三条结论，不写数字。'
        task+=' quote字段一律设为null；可以用自己的语言归纳并引用source_ids，但不要把改写放进quote。'
        r['critics']['envicool_vrt']=await run_role(bank,'adversarial_review','envicool_vrt',ids,task,{**drafts,'comparison':r['comparisons']['envicool_vrt']})
        repairs.append('adversarial_review.envicool_vrt')
        task='完成温控组研究结论，先用工具核对两家公司本报告期财务与相关原文。逐项处理反证，财务结论来自代码指标。两家公司这里均为同一自然年上半年，可以在明确准则和集团业务边界下比较方向、比率；不得跨币种比绝对额。英维克有液冷规模采购证据，但Vertiv综合基础设施B与液冷具体产品C不能混成同一概念升级。应收、验收、发出商品不可混同收入确认。三到四条关键判断，不给目标价。'
        r['synthesis']['envicool_vrt']=await run_role(bank,'research_editor','envicool_vrt',ids,task,{**drafts,'comparison':r['comparisons']['envicool_vrt'],'critic':r['critics']['envicool_vrt']})
        repairs.append('research_editor.envicool_vrt')
    event=r.get('event_transmission')
    if not event or not any(any('nvidia_blackwell_ultra' in sid for sid in f['source_ids']) for f in event['findings']):
        task='首先必须search_evidence(company_id=global,keywords=[Blackwell Ultra,rack,liquid])核实已归档的NVIDIA官方发布。随后核对两家公司热管理资料。把真实发布事件与后续情景区分，建立事件→算力设计/热密度要求→产品→订单交付/验收→收入和现金的机制。发布不是销售，订单不是B级收入证据；现金流可以受预收而领先收入，不作必然滞后结论。不证明具体供应商关系，不给量化弹性。'
        r['event_transmission']=await run_role(bank,'event_transmission','blackwell_cooling',['envicool','vrt'],task)
        repairs.append('event_transmission.blackwell_cooling')
    data['repair_completed']=True;data['repaired_at']=now();data['failure_history']=data.get('failure_history',[])+data.get('failures',[]);data['failures']=[]
    for role in ['business_evidence','financial_quality']:
        data['failures'] += [{'role':role,'subject':cid} for cid,value in r[role].items() if value is None]
    for role in ['comparisons','critics','synthesis']:
        data['failures'] += [{'role':role,'subject':pair} for pair,value in r[role].items() if value is None]
    save('data/round2/agent_research.json',data);save('data/round2/sources.json',{'sources':bank.sources})
    save('artifacts/round2/repair_log.json',{'completed_at':now(),'repaired_stages':repairs,'active_failures':data['failures'],'note':'保留历史失败，不将修复成功当作首轮成功；角色输出仍需语义抽核'})
    print(json.dumps({'repaired':repairs,'active_failures':data['failures']}),flush=True)

if __name__=='__main__':asyncio.run(repair())
