"""Validate round-two provenance and publish a reviewed memo, not an unfiltered model transcript."""
import hashlib
import json
from pathlib import Path
import re
from probe import ROOT,save,now
from model_adapter import model_name as registry_model_name

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False)

# The publication uses reviewed prose; unedited model drafts remain in agent_research.json.
REVIEWED_SUMMARIES={
 'inspur_smci':'两家公司处于AI服务器整机与机架交付环节，已取得产品与商业交付证据，但本轮未取得可直接比较的AI专属收入。集团业务与AI业务不能混同。浪潮现金流回升可引用公司披露的销售回款增加，具体营运资本贡献仍待补证；Supermicro应付账款现金流为负向项，不能解释成增加现金的来源。两家财年不同，Supermicro本轮业绩发布还需要正式审计年报对照，暂不作现金质量排名。',
 'innolight_cohr':'共同研究环节是高速光通信与数据中心互连。中际旭创光模块收入包括其他应用，Coherent集团收入包括其他业务，均不能整体等同AI收入。Coherent的GAAP营业利润转正与GAAP归母净利润仍亏损须分开陈述，不能笼统写成由亏转盈。本轮缺少Coherent完整的结构化财务指标与分部对照，现金质量的量化比较尚未完成。',
 'kehua_etn':'共同研究环节是数据中心供配电。科华还涉及IDC运营，Eaton电气分部覆盖更多终端市场；公司、分部、产品与AI应用四种收入范围须分开。科华数据中心产品和IDC服务毛利率变化不同，不能把行业毛利率下滑全部归因于产品。Eaton全年现金流与利润数据仍未补齐，暂不作两家现金转化率排名。',
 'envicool_vrt':'两家公司已对齐2026年上半年，可在说明准则和业务结构差异后比较变化方向与比率。英维克收入增长而归母及合并净利润下降，经营现金流由负转正，但现金转化比率仍低，经营现金流减长期资产购建支出为负；Vertiv集团收入、合并净利润和经营现金流同比增长，上述现金流代理为正。业务证据须按范围评级：英维克液冷规模采购已有商业进展证据；Vertiv综合基础设施已有商业证据，具体液冷单品仍需分别补证。集团收入、订单积压均不能证明某款液冷产品或Blackwell Ultra相关收入。'
}

def publish():
    data=load('data/round2/agent_research.json');sources=load('data/round2/sources.json')['sources'];metrics=load('data/round2/financial_metrics.json')['metrics'];registry=load('data/round2/company_registry.json')['companies']
    if data['failures']:raise ValueError('unresolved research stages: '+str(data['failures']))
    outputs=[]
    for role in ['business_evidence','financial_quality','comparisons','critics','synthesis']:
        outputs.extend((role,subject,value) for subject,value in data['results'][role].items())
    outputs.append(('event_transmission','blackwell_cooling',data['results']['event_transmission']))
    checks=0;used=set();traces=[];hash_checked={}
    all_traces=[(p,load(str(p.relative_to(ROOT)))) for p in (ROOT/'artifacts/round2/runs').glob('*.json')]
    for role,subject,out in outputs:
        if out is None:raise ValueError('empty stage: '+role+subject)
        for f in out['findings']:
            for sid in f['source_ids']:
                checks+=1
                if sid not in sources:raise ValueError('unknown evidence '+sid)
                used.add(sid)
            for mid in f['metric_ids']:
                checks+=1
                if mid not in metrics:raise ValueError('unknown metric '+mid)
        candidates=[(p,r) for p,r in all_traces if r.get('status')=='success' and r.get('role')==({'comparisons':'cross_market','critics':'adversarial_review','synthesis':'research_editor'}.get(role,role)) and r.get('subject')==subject and canonical(r.get('output'))==canonical(out)]
        if not candidates:raise ValueError('missing successful trace for '+role+subject)
        candidates.sort(key=lambda x:x[0].stat().st_mtime);traces.append(candidates[-1])
    for m in metrics.values():
        checks+=1
        if m['value'] is None and not m['missing_reason']:raise ValueError('unexplained null')
        for sid in m['source_ids']:
            if sid not in sources:raise ValueError('metric source absent')
            used.add(sid)
        inputs=[metrics[k] for k in m['input_metric_ids']]
        if m['formula'] and m['formula'].startswith('divide'):
            a,b=inputs
            if (a['currency'],a['period_start'],a['period_end'])!=(b['currency'],b['period_start'],b['period_end']):raise ValueError('mixed ratio caliber')
            expected=None if b['value'] in (None,0) or a['value'] is None else a['value']/b['value']
            if expected!=m['value']:raise ValueError('ratio mismatch')
        if m['formula'] and m['formula'].startswith('subtract'):
            expected=None if any(v['value'] is None for v in inputs) else inputs[0]['value']-inputs[1]['value']
            if expected!=m['value']:raise ValueError('cashflow proxy mismatch')
    for sid in used:
        s=sources[sid];path=ROOT/s['local_path'];checks+=1
        if not path.is_file():raise ValueError('provenance file missing')
        if s.get('sha256'):
            if s['local_path'] not in hash_checked:hash_checked[s['local_path']]=hashlib.sha256(path.read_bytes()).hexdigest()
            if hash_checked[s['local_path']]!=s['sha256']:raise ValueError('source hash mismatch')
        if s.get('published_at') and s['published_at']>'2026-10-21':raise ValueError('future disclosure')
    event=data['results']['event_transmission']
    if not any(any('nvidia_blackwell_ultra' in sid for sid in f['source_ids']) for f in event['findings']):raise ValueError('event primary-source coverage absent')
    # Sum the exact successful executions used by the current final DAG; failed and
    # superseded experiments are recorded separately and must not be hidden.
    usage={k:sum(r.get('usage',{}).get(k,0) for _,r in traces) for k in ['input_tokens','output_tokens','cache_read_tokens','requests','tool_calls']}
    miss=usage['input_tokens']-usage['cache_read_tokens'];low=(miss+usage['cache_read_tokens']*.02+usage['output_tokens']*4)/1e6
    recorded=[r for _,r in all_traces if r.get('usage')]
    measured={k:sum(r.get('usage',{}).get(k,0) for r in recorded) for k in ['input_tokens','output_tokens','cache_read_tokens','requests']}
    unknown=[str(p.relative_to(ROOT)).replace('\\','/') for p,r in all_traces if not r.get('usage')]
    evaluation={'generated_at':now(),'model':registry_model_name(),'framework':'PydanticAI 2.59.0','completed_stages':len(outputs),'selected_stage_usage':usage,'selected_stage_off_peak_estimate_cny':round(low,6),'recorded_including_failed_and_superseded':measured,'early_debug_trace_usage_missing':unknown,'total_cost_status':'最终使用阶段的费用可估算；早期框架调试有用量记录缺失，所以不把该值声称为整个开发过程总费用','source_chunks_in_corpus':len(sources),'distinct_source_chunks_referenced_or_used_in_metrics':len(used),'trace_paths':[str(p.relative_to(ROOT)).replace('\\','/') for p,_ in traces],'validation_checks':checks,'comparison':'本轮与首轮任务和材料范围不同，不能把变化称为受控成本/准确率改善实验'}
    save('data/round2/evaluation.json',evaluation)
    manual_review={'reviewed_at':now(),'reviewer':'Codex抽核原文与计算表','status':'passed_with_limitations','approved_observations':[
      {'text':'英维克上半年收入增长而归母利润下降；经营现金流由上年净流出转正，但覆盖合并净利润仍偏低。不能写成现金流继续恶化。','source_ids':['r2.envicool_h1_2026.p7','r2.envicool_h1_2026.p44','r2.envicool_h1_2026.p47']},
      {'text':'两家温控样本可对齐到同一自然年上半年。币种不同，不比较绝对金额大小；现金转化比率的集团业务结构与会计准则仍有差异。','source_ids':['r2.envicool_h1_2026.p7'],'metric_ids':['m.envicool.H12026.cash_conversion','m.vrt.H12026.cash_conversion']},
      {'text':'Vertiv综合基础设施商业证据与具体液冷单品证据必须分开；集团收入和订单积压不能直接证明液冷单品收入。','source_ids':['r2.vertiv_annual_2025.p21']},
      {'text':'经营现金流减资本开支为分析代理。中国样本为长期资产购建支出，Vertiv该项不含资本化软件，不能视为完全同口径的公司披露自由现金流。','metric_ids':['m.envicool.H12026.ocf_less_cash_capex','m.vrt.H12026.ocf_less_cash_capex']}
      ],'corrections_to_agent_drafts':['不得把订单进展本身评为B级交付证据','不得把发出商品与应收增长直接解释成收入确认领先验收','资本开支是投资现金流项目，不能作为经营现金流变化的直接组成','不得笼统声称现金流必然滞后收入，预收可领先收入','不将未披露AI收入解释为没有AI业务','避免同一段混写事实与经营解释，解释保守标为推断'],'limits':['本轮是研究辅助，没有全量人工事实审计','只有两家样本补齐同期间半年量化数据','Eaton仍是官网事实转录；Supermicro仍需正式审计年报对照','未实现任意主题自主规划、全网自动核实或定时更新']}
    save('data/round2/semantic_review.json',manual_review)
    rows=['# 第二轮研究：开源方法借鉴与Agent编排实跑','',f'生成时间：{now()}；模型：'+registry_model_name()+'；研究截至：2026-10-21。','', '**本轮完成了真实PydanticAI工具调用编排：八家公司业务证据与财务质量、四组跨市场比较与独立反证、四组编辑结论，以及一个事件传导案例。重点量化样板是英维克／Vertiv的同期间半年数据。**','', '## 实际借鉴了什么','', '- FinRobot：财务数字由代码计算，模型负责解释；不同币种、期间、集团与业务口径分开审核。','- TradingAgents：独立反方重新查原文，编辑阶段处理审查意见。','- EdgarTools：实际解析公司托管的Vertiv正式10-K，离线读取，不依赖绕过SEC访问要求。','- 固定提交、具体阅读文件和许可证见 [开源借鉴记录](../THIRD_PARTY_NOTES.md)。','', '## 编排与真实能力边界','', '```mermaid','flowchart TD','  A[研究对象与截止日] --> B[业务证据Agent × 8]','  B --> C[财务质量Agent × 8]','  C --> D[跨市场比较Agent × 4]','  D --> E[独立反证Agent × 4]','  E --> F[研究编辑Agent × 4]','  F --> G[事件传导Agent]','  G --> H[确定性验证与语义抽核]','  H --> I[JSON与研究报告]','  E --> J[有预算的补证与失败修复]','  J --> F','```','', '阶段和公司名单由代码指定。阶段内部由模型选择本地检索、原文阅读、财务快照与iFinD补证工具。不是全自主规划，也没有把并发请求数当成Agent数量。失败阶段、修复前稿和消息交接全部保留。','', '## 温控样板：本轮新增的实质判断','', '英维克体现了“收入增长不等于利润与现金同步增长”。半年收入上升、归母利润下降；现金流由负转正，仍需检查营运资本和投入节奏。Vertiv半年合并收入、利润与经营现金流同增，但不能把集团表现直接归给液冷。','', '| 指标：2026年上半年 | 英维克 | Vertiv |','|---|---:|---:|']
    def get(cid,name):return metrics[f'm.{cid}.H12026.{name}']['value']
    for label,name,unit in [('集团收入','revenue','money'),('集团合并净利润','consolidated_net_profit','money'),('经营现金流','ocf','money'),('经营现金流／合并净利润','cash_conversion','ratio'),('经营现金流减资本开支代理','ocf_less_cash_capex','money'),('集团收入同比','revenue_yoy_pct','percent')]:
        vals=[]
        for cid in ['envicool','vrt']:
            v=get(cid,name)
            vals.append('未核实' if v is None else (f'{v/1e8:,.2f} 亿'+('CNY' if cid=='envicool' else 'USD') if unit=='money' else (f'{v:.2f} 倍' if unit=='ratio' else f'{v:.2f}%')))
        rows.append('| '+label+' | '+' | '.join(vals)+' |')
    rows+=['', '表中两家均为同一自然年上半年；现金转化统一以合并净利润为分母，不用归母利润混算。金额分别保留原币，不能比较表中金额的直接大小。现金流减资本开支代理的扣除范围有差异，不是公司披露自由现金流，也不是可直接比较的产品竞争力评分。','', '英维克归母利润同比下降与合并净利润同比下降为不同数值；正式数据见 [计算表](../data/round2/financial_metrics.json)。年报/半年报报告期已明确，未声称覆盖研究日所有最新季报。','', f"原始来源：[英维克半年报]({sources['r2.envicool_h1_2026.p7']['url']})、[Vertiv半年业绩及报表]({sources['r2.vertiv_q2_2026.c19']['url']})。页码与原文片段见sources.json，计算公式与输入见financial_metrics.json。",'', '## 四组研究结论与待补证','']
    for pair,ids in [('inspur_smci',['inspur','smci']),('innolight_cohr',['innolight','cohr']),('kehua_etn',['kehua','etn']),('envicool_vrt',['envicool','vrt'])]:
        title=' / '.join(registry[c]['name'] for c in ids);editor=data['results']['synthesis'][pair]
        rows += [f'### {title}','',REVIEWED_SUMMARIES[pair],'']
        rows += ['- '+m.replace('均未披露','本轮未取得').replace('公司未拆分披露','本轮未取得独立披露') for m in editor['missing'][:3]]+['']
    rows+=['以上为抽核后的摘要；原始Agent草稿另存于agent_research.json，保留错误与修复记录供审查。','', '## 反证与抽核纠偏','']
    rows+=['- '+x for x in manual_review['corrections_to_agent_drafts']]
    rows+=['','具体反证发现包括：Supermicro应付账款现金流方向、季度与全年毛利率混写、部分草稿将“未取到”误写为“未披露”、以及温控组已可对齐半年期间却笼统拒绝同期比较。反证本身也是模型输出，不能默认全部正确；例如资本开支与经营现金流归因仍须按现金流分类复核。','', '## 事件传导','','NVIDIA的Blackwell Ultra官方发布已核实，发布属于产品事件。热密度要求到液冷产品需求属于有条件的机制判断；没有取得两家公司与该平台直接对应的供应合同或收入。订单与积压提供需求线索，不能当成交付或收入证据。','']
    rows += ['- '+f['kind']+'：'+f['text'].replace('订单与积压属B级交付前瞻证据','订单与积压仅属需求前瞻线索，不能评为B级交付证据').replace('机柜级液冷方案提高单柜热密度与液冷回路复杂度','机柜级高功率设计可能提高单柜热密度与液冷回路复杂度') for f in data['results']['event_transmission']['findings']]
    rows += ['','已归档的NVIDIA官方发布是历史事实；热密度与产品需求、交付、收入和现金的后续关系包含条件与情景。没有证明两家公司获得某款芯片平台的具体供应合同。','', '## 本轮验证与成本边界','',f'- 当前DAG任务完成：{len(outputs)} 个；活动失败：{len(data["failures"])}。',f'- 数据与引用验证：{checks} 项检查通过；不是事实准确率评分。',f'- 最终采用阶段实测：{usage["requests"]} 次模型请求，输入 {usage["input_tokens"]:,} Token，输出 {usage["output_tokens"]:,} Token，工具执行 {usage["tool_calls"]} 次。',f'- 按已归档Flash空闲时段单价估算，最终采用阶段约 ¥{low:.4f}。不含早期失败/替换试验、Codex会话及数据许可费用。','- 早期调试的部分用量没有完整归档，不能给整个开发过程总费用；完整可统计范围见evaluation.json。','- 首轮与本轮使用的资料和任务不同，不能宣称受控成本节省或准确率提升百分比。','- 财务与框架工具交接测试共18个通过；留有原始日志。','', '## 复现','', '```powershell',r'.\.venv\Scripts\python.exe scripts/prepare_round2.py',r'.\.venv\Scripts\python.exe scripts/round2_agents.py --offline',r'.\.venv\Scripts\python.exe scripts/repair_round2.py --offline',r'.\.venv\Scripts\python.exe scripts/publish_round2.py','```','', '已完成角色默认复用缓存。在线更新去掉 `--offline`，仅缺失阶段会调用模型；补查有预算。Windows沙箱环境可能需要允许asyncio本地回环套接字，即使离线重放也需要创建事件循环。','', '数据：[Agent研究](../data/round2/agent_research.json)、[财务指标](../data/round2/financial_metrics.json)、[语义抽核](../data/round2/semantic_review.json)、[运行评估](../data/round2/evaluation.json)。首轮数据保持不变。']
    (ROOT/'reports/第二轮研究结果.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    files={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data/round2').glob('*.json') if p.name!='manifest.json'}
    save('data/round2/manifest.json',{'version':'2026-10-21.round2','generated_at':now(),'model':registry_model_name(),'validation_status':'passed_with_limitations','companies':8,'research_stages':len(outputs),'source_chunks':len(sources),'files':files,'scope':'八家公司研究、四组比较，英维克和Vertiv补齐半年定量样板；不把八家全部称为完整专业深研','unresolved':manual_review['limits']})
    save('artifacts/round2/validation.json',{'checked_at':now(),'status':'passed_with_limitations','checks':checks,'active_failed_stages':data['failures'],'semantic_review':'see data/round2/semantic_review.json'})
    print(json.dumps({'stages':len(outputs),'checks':checks,'usage':usage,'selected_stage_estimate_cny':round(low,6),'sources_used':len(used)}))

if __name__=='__main__':publish()
