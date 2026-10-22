"""Produce evaluation, review memo and hash manifest; no network calls."""
import hashlib
import json
from pathlib import Path
from probe import ROOT,save,now
from models import Evaluation,Manifest,Research
from model_adapter import model_name as registry_model_name
from validate import load,check_bundle

def finalize():
    research=load('company_research');sources=load('sources');graph=load('industry_graph')
    review_edits=[]
    for company in research['companies']:
        ai=company['ai_analysis']
        if ai:
            for i,obs in enumerate(ai['observations']):
                if obs['kind']=='fact' and any(w in obs['text'] for w in ['不能','不可','不等于']):
                    review_edits.append({'company_id':company['id'],'observation_index':i,'old_kind':'fact','new_kind':'inference','reason':'同一句包含研究解释边界，保守标为推断；原始模型输出保留在Trace'})
                    obs['kind']='inference'
        if company['id']=='etn':company['metrics'][0]['disclosure_status']='rounded_reported'
    save('data/company_research.json',Research.model_validate(research).model_dump())
    save('artifacts/semantic_review.json',{'reviewed_at':now(),'reviewer':'Codex，基于本地原始披露和对话中的源文核对','scope':'八家公司AI摘要与主要业务、相关收入和比较边界抽核；未进行全量审计','edits':review_edits,'preserved_limitations':['14家广度候选AI关联待核验','Eaton官网仅保存事实转录，直连下载失败','Supermicro引用未审计业绩稿','不把Schema通过当作事实正确率100%']})
    validation=check_bundle(research,sources,graph)
    records=[]
    probe=json.loads((ROOT/'artifacts/connectivity/deepseek.json').read_text(encoding='utf-8'))
    records.append({'id':'connectivity_probe','model':'deepseek-flash','http_status':probe['chat_request']['http_status'],'elapsed_seconds':probe['chat_request']['elapsed_seconds'],'usage':probe['usage'],'accepted':False,'note':'首个JSON测试返回畸形JSON，未当作合格结构化输出'})
    for p in sorted((ROOT/'artifacts/agent').glob('*attempt*.json')):
        r=json.loads(p.read_text(encoding='utf-8'))
        records.append({'id':p.name,'company_id':r['company_id'],'http_status':r['transport']['http_status'],'elapsed_seconds':r['transport']['elapsed_seconds'],'usage':r.get('response',{}).get('usage'),'accepted':r['accepted'],'validation_error':r['validation_error'],'trace_path':str(p.relative_to(ROOT)).replace('\\','/')})
    paid=[r for r in records if r['http_status']==200 and r['usage']]
    usage={k:sum(r['usage'].get(k,0) for r in paid) for k in ['prompt_tokens','completion_tokens','total_tokens','prompt_cache_hit_tokens','prompt_cache_miss_tokens']}
    cost_low=(usage['prompt_cache_hit_tokens']*.02+usage['prompt_cache_miss_tokens']*1+usage['completion_tokens']*4)/1e6
    costs={'currency':'CNY','off_peak_estimate':round(cost_low,6),'peak_estimate':round(cost_low*2,6),'billing_status':'估算，不是账户实际扣费账单','pricing_source':'https://api-docs.deepseek.com/zh-cn/quick_start/pricing/','pricing_retrieved_at':json.loads((ROOT/'artifacts/public/deepseek_pricing.meta.json').read_text(encoding='utf-8'))['retrieved_at'],'includes_rejected_model_responses':True,'excludes_codex_session_and_financial_data_license_cost':True}
    failure_cases=[{'type':'malformed_json','observed':True,'handling':'保留首个probe响应；不发布为研究结果'}, {'type':'schema_length_mismatch','observed':True,'handling':'首轮提示未明确条目上限，输出被Schema拒绝；修正提示后重新执行；不将这次迭代声称为受控性能对比'}, {'type':'technical_identifier_false_positive','observed':True,'handling':'数字守卫错误拦截已被原文支持的1.6T技术型号；修正为原文字面核验，并从原Trace离线复验，不增加调用'}, {'type':'fiscal_period_mismatch','observed':True,'handling':'海外MCP没有按要求对齐财年，隔离整份财务结果，改用官网披露'}, {'type':'obsolete_ticker_collision','observed':True,'handling':'VRT-1.N与VRT.N并存，仅保留已核实的VRT'}, {'type':'public_source_access','observed':True,'handling':'Eaton官网直连超时、SEC拒绝；以网页工具读取官网并标记本地为人工事实转录'}, {'type':'sandbox_network_denied','observed':True,'handling':'局部离线执行遇网络拒绝，未获HTTP响应，不记入Token收费调用；重放使用缓存'}]
    evaluation=Evaluation(generated_at=now(),model=registry_model_name(),calls=records,usage={**usage,'billable_successful_http_calls':len(paid),'local_transport_failed_attempts':sum(r['http_status'] is None for r in records),'accepted_deep_company_results':sum(c['ai_analysis'] is not None for c in research['companies']),'sum_successful_call_seconds':round(sum(r['elapsed_seconds'] for r in paid),3),'timing_note':'逐次调用耗时之和，不是并发流水线墙钟时间'},estimated_cost_cny=costs,failure_cases=failure_cases,validation=validation).model_dump()
    save('data/agent_evaluation.json',evaluation)
    hashes={f'data/{name}.json':hashlib.sha256((ROOT/f'data/{name}.json').read_bytes()).hexdigest() for name in ['industry_graph','company_research','sources','agent_evaluation']}
    manifest=Manifest(research_version='2026-10-21.pilot-v1',topic='AI数据中心基础设施',research_as_of='2026-10-21',generated_at=now(),financial_baseline='FY2025；A股/Eaton/Vertiv为2025自然年；Supermicro/Coherent为截至2025-06-30财年',freshness_note='本轮是FY2025基线研究；未全面采集研究截至日最新季报，也不声称信息已穷尽。',validation_status='passed_with_limitations',company_count=len(research['companies']),deep_company_count=8,files=hashes,limitations=['22家公司含8家首轮深度研究及14家仅广度候选；不得标成22家AI业务已验证','概念等级针对具体概念和口径，不是给公司整体背书','无实时行情、自动定时刷新或股票收益预测','Eaton使用官网人工事实转录；原始HTML未归档','Supermicro为未审计业绩稿；正式10-K对照待补','未运行Baseline对优化流程的受控实验','AI窄口径缺失保留null；集团总收入不能替代']).model_dump()
    save('data/research_manifest.json',manifest)
    lines=['# ChainScope 第一阶段结果','',f'生成时间：{manifest["generated_at"]}。模型统一为 `deepseek-flash`。','', '**已完成：三个数据源实际连通、五类数据契约、22家公司数据集（8家首轮深度研究 + 14家待核验广度候选）、四组中外比较、证据与真实运行记录。**','', '本轮采用FY2025比较基线。研究截至2026-10-21，但不把旧财报说成最新季度。','', '## 接口结果','', '- 扶摇：四家公司合并利润表实际取数成功，原始响应保留。','- iFinD：综合、A股、海外股票、资讯四个服务完成初始化与工具发现，实际执行公司资料与公告检索。工具数量包含跨服务重复，见连接记录。','- DeepSeek：真实调用成功；输出经Schema、引用、数字边界校验及研究者抽核。','', '## 八家公司首轮结果','', '| 公司 | FY2025集团营收 | 相关业务收入/口径 | 窄口径概念等级 | 状态 |','|---|---:|---|---|---|']
    for c in research['companies']:
        if c['research_depth']!='deep':continue
        revenue=c['metrics'][0];value=f'{revenue["value"]/1e8:,.2f} 亿{revenue["currency"]}'
        relevant=next((m for m in c['metrics'] if m['name']=='related_revenue'),None)
        related=f'{relevant["value"]/1e8:,.2f} 亿CNY；{relevant["scope"]}' if relevant else '本次未单列可比相关收入，保持null'
        a=c['assessments'][-1]
        lines.append(f'| {c["name"]} | {value} | {related} | {a["concept"]}：{a["grade"]} | 首轮研究，含边界说明 |')
    lines+=['','A股四家在宽口径业务上为A级，表中等级针对更窄的AI概念；不得混用。B代表有商业业务证据但窄口径收入未知，C代表当前核验到产品或订单进展，尚未单独核实销售交付。保守标C并不代表公司事实上没有收入。','', '## 为什么可比、哪里不可比','']
    for cid in ['inspur','innolight','kehua','envicool']:
        c=next(c for c in research['companies'] if c['id']==cid);p=c['comparisons'][0];peer=next(x for x in research['companies'] if x['id']==p['peer_id'])
        lines.append(f'- **{c["name"]} / {peer["name"]}**：'+ '；'.join(p['comparable'])+'。边界：'+'；'.join(p['non_comparable'])+'。')
    lines+=['','## 证据与校验','',f'- {len(sources["sources"])} 条来源记录，原始响应或原文件带SHA-256。包含补充公告片段，并非全部已核验全文。',f'- 图谱包含 {len(graph["nodes"])} 个节点、{len(graph["edges"])} 条边；公司节点统一大小，避免混用币种和业务口径。','- 产业层级为人工规则；光器件到光模块的环节关系有年报依据，不推定公司之间的供货关系。',f'- 确定性规则检查：{validation["deterministic_checks"]} 项通过。Schema/引用存在性通过不等于所有结论真实。','- 已抽核八家公司核心业务、相关收入口径及AI摘要；广度候选AI关联没有完成定向核验。','', '## Flash运行实测','',f'- 获得用量的真实API调用：{len(paid)} 次（包括被拒绝的模型输出与连通测试）。',f'- 输入：{usage["prompt_tokens"]:,} Token；输出：{usage["completion_tokens"]:,} Token；合计：{usage["total_tokens"]:,} Token。',f'- 按已读取官网价目估算：空闲时段约 ¥{cost_low:.4f}，高峰约 ¥{cost_low*2:.4f}。这不是账户扣费账单，不含本Codex会话与金融数据许可成本。','- 本次调用发生于香港时间晚间；费用仍同时给出两档，避免把估算当账单。','- 本轮没有受控Baseline/优化实验，不宣称节省比例。','', '## 真实异常与处理','']
    lines += [f'- **{f["type"]}**：{f["handling"]}。' for f in failure_cases]
    lines+=['','## 文件入口','', '- [公司研究](../data/company_research.json)','- [图谱](../data/industry_graph.json)','- [来源](../data/sources.json)','- [运行评估](../data/agent_evaluation.json)','- [研究版本与边界](../data/research_manifest.json)','- [Schema](../schemas/)','- [验证报告](../artifacts/validation_report.json)','', '## 本轮尚未完成','', '- 14家广度候选的AI关联定向核验。','- 最新季度财务补齐、Eaton原始财务文件归档、Supermicro正式年报复核。','- 热点事件传导、交互Web、部署、视频与成本对照实验属于后续步骤。','- 金融接口数据许可未进行公开再分发审查，当前成果只在本地。']
    path=ROOT/'reports/第一阶段结果.md';path.parent.mkdir(exist_ok=True);path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'companies':len(research['companies']),'sources':len(sources['sources']),'usage':usage,'cost_estimate_cny':costs,'validation':validation},ensure_ascii=True))

if __name__=='__main__':finalize()
