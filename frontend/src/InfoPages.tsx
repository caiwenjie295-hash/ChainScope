import { Activity, Check, CircleHelp, Clock3, Database, FileCheck2, FlaskConical, GitBranch, Globe2, LockKeyhole, Orbit, ShieldCheck, Waypoints } from 'lucide-react'
import type { Snapshot } from './types'
import { PageFooter, PageFrame } from './Chrome'
import { formatDate, formatNumber } from './format'
import researchValidation from './researchValidation.json'

function StatCard({ label, value, detail, icon: Icon }: { label: string; value: string; detail: string; icon: typeof Orbit }) {
  return (
    <article className="info-stat-card">
      <span className="info-stat-icon"><Icon size={16} strokeWidth={1.6} aria-hidden="true" /></span>
      <span className="info-stat-label">{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  )
}

function SectionHeading({ kicker, title, description }: { kicker: string; title: string; description: string }) {
  return <div className="info-section-heading"><span className="section-kicker">{kicker}</span><h2>{title}</h2><p>{description}</p></div>
}

function isRestrictedAccess(access: string | null | undefined) {
  const value = (access || '').toLocaleLowerCase()
  return ['authenticated_api', 'mcp', 'internal', 'local', 'restricted', 'authorized'].some((key) => value.includes(key))
}

function hasCitedBusinessFact(company: Snapshot['companies'][number]) {
  return (company.claims ?? []).some((claim) => claim.kind === 'fact' && (claim.source_ids?.length ?? 0) > 0)
}

function hasNumericFinancialMetric(company: Snapshot['companies'][number]) {
  return (company.metrics ?? []).some((metric) => typeof metric.value === 'number' && Number.isFinite(metric.value))
}

export function ArchitecturePage({ snapshot }: { snapshot: Snapshot }) {
  const companies = snapshot.companies
  const reviewedCompanies = companies.filter((company) => company.research_status === 'reviewed').length
  const candidateCompanies = companies.filter((company) => company.research_status === 'candidate').length
  const sources = Object.values(snapshot.sources)
  const publicSources = sources.filter((source) => Boolean(source.url) && !isRestrictedAccess(source.access)).length
  const restrictedSources = Object.keys(snapshot.sources).length - publicSources
  const structureNodes = snapshot.graph.nodes.filter((node) => node.type !== 'company').length
  const companyNodes = snapshot.graph.nodes.filter((node) => node.type === 'company').length
  const factsCompanies = companies.filter(hasCitedBusinessFact).length
  const financialCompanies = companies.filter(hasNumericFinancialMetric).length
  const events = snapshot.events?.length ?? (snapshot.event ? 1 : 0)
  const validationMatches = researchValidation.snapshot_data_hash.toLocaleLowerCase() === snapshot.meta.data_hash.toLocaleLowerCase()
    && researchValidation.status === 'passed'
  const validationLabel = validationMatches
    ? `当前数据校验 ${formatNumber(researchValidation.checks, 0)} 项`
    : '待重新校验'
  const archived = researchValidation.archived_workflow
  return (
    <PageFrame page="architecture" snapshot={snapshot}>
      <main id="main-content" className="info-page architecture-page">
        <section className="info-hero architecture-hero">
          <div className="info-hero-copy"><span className="hero-overline"><span className="hero-pulse" />研究流程 · 已执行</span><h1>流程与证据</h1><p>研究以来源、口径和缺失边界为基础；前端读取已发布研究结果，不在浏览器里生成结论。</p><div className="hero-pills"><span><Check size={12} aria-hidden="true" />可追溯引用</span><span><Check size={12} aria-hidden="true" />明确缺失状态</span><span><Check size={12} aria-hidden="true" />离线可读</span></div></div>
          <div className="architecture-orbit" aria-hidden="true"><div className="orbit-r1" /><div className="orbit-r2" /><div className="orbit-r3" /><span className="orbit-center">CS</span><span className="orbit-node orbit-node-a" /><span className="orbit-node orbit-node-b" /><span className="orbit-node orbit-node-c" /><span className="orbit-node orbit-node-d" /></div>
        </section>

        <section className="info-stats-grid" aria-label="研究范围">
          <StatCard label="已研究公司" value={`${formatNumber(reviewedCompanies, 0)} 家`} detail={`已形成部分研究结论；另有 ${formatNumber(candidateCompanies, 0)} 家广度候选`} icon={FlaskConical} />
          <StatCard label="来源记录" value={`${formatNumber(sources.length, 0)} 条`} detail={`${formatNumber(publicSources, 0)} 条公开链接 · ${formatNumber(restrictedSources, 0)} 条受限引用`} icon={Globe2} />
          <StatCard label="图谱节点" value={`${formatNumber(snapshot.graph.nodes.length, 0)} 个`} detail={`${formatNumber(structureNodes, 0)} 个产业结构 · ${formatNumber(companyNodes, 0)} 家公司`} icon={GitBranch} />
          <StatCard label="数据校验" value={validationLabel} detail={validationMatches ? `截至 ${formatDate(researchValidation.checked_date)} · 与当前数据匹配` : '校验记录与当前数据不匹配'} icon={ShieldCheck} />
        </section>

        <section className="info-section pipeline-section">
          <SectionHeading kicker="研究数据流" title="当前研究覆盖" description="以下数量按已发布研究快照统计；概念归属不等于供应商关系。" />
          <div className="current-coverage-grid">
            <StatCard label="有业务事实引用" value={`${formatNumber(factsCompanies, 0)} 家`} detail="至少一条事实主张附有来源" icon={Database} />
            <StatCard label="含财务数值" value={`${formatNumber(financialCompanies, 0)} 家`} detail="至少一项公司财务指标有数值" icon={FileCheck2} />
            <StatCard label="跨市场对照" value={`${formatNumber(snapshot.pairs.length, 0)} 组`} detail="按已发布对照关系计数" icon={GitBranch} />
            <StatCard label="事件传导" value={`${formatNumber(events, 0)} 条`} detail="按已发布事件记录计数" icon={Waypoints} />
          </div>
          <p className="coverage-caveat">有财务数值不代表该公司已完成全面财务核验；报告期、指标缺失和对比边界仍以公司研究详情为准。</p>
        </section>

        <section className="info-section boundary-section">
          <SectionHeading kicker="产品边界" title="已实现与规划中，分开展示" description="本版证明离线研究闭环；动态更新和商业服务仍需后续建设。" />
          <div className="boundary-grid">
            <article className="boundary-card is-live"><div className="boundary-label"><span className="status-led" />当前已实现</div><h3>可核验的离线研究体验</h3><ul><li>公开来源可直接打开；授权数据明确显示访问边界。</li><li>集团财务与概念专项指标分别呈现，未取得时保留原因。</li><li>跨市场比较说明可比项与口径差异，金额按原币展示。</li><li>事件路径分别标记事实、推断与情景。</li></ul></article>
            <article className="boundary-card is-planned"><div className="boundary-label"><span className="planned-led" />产品规划</div><h3>动态研究服务</h3><ul><li>登录、会员、个性化跟踪与实时行情。</li><li>在线刷新研究、通知和按需生成报告。</li><li>面向机构的权限、审阅和协作流程。</li><li>以上为产品设想，当前没有接入或对外提供。</li></ul></article>
          </div>
          <div className="architecture-footer-note"><LockKeyhole size={14} aria-hidden="true" /><span>浏览器只读取已发布研究数据；研究凭证不会进入前台。</span></div>
        </section>

        <section className="workflow-archive" aria-label="早期已归档流程记录">
          <details>
            <summary>早期已归档流程记录</summary>
            <div className="workflow-archive-body">
              <p>{archived.scope}。累计 {formatNumber(archived.completed_stages, 0)} 个研究阶段、{formatNumber(archived.validation_checks, 0)} 项归档校验；这些数字不代表当前研究覆盖或上方当前数据校验结果。</p>
              <div className="workflow-counts">
                {archived.workflow.map((item) => <div className="workflow-count" key={item.label}><span>{item.label}</span><strong>{formatNumber(item.count, 0)}</strong><small>次归档运行</small></div>)}
              </div>
            </div>
          </details>
        </section>
      </main>
      <PageFooter snapshot={snapshot} />
    </PageFrame>
  )
}

function TokenBar({ label, value, max, detail }: { label: string; value: number; max: number; detail: string }) {
  const width = max > 0 ? Math.max(3, (value / max) * 100) : 0
  return (
    <div className="token-bar-row">
      <div className="token-bar-label"><span>{label}</span><strong>{formatNumber(value, 0)}</strong></div>
      <div className="token-bar-track"><span style={{ width: `${width}%` }} /></div>
      <small>{detail}</small>
    </div>
  )
}

export function CostPage({ snapshot }: { snapshot: Snapshot }) {
  const evaluation = snapshot.evaluation
  const archived = researchValidation.archived_workflow
  const maxTokens = Math.max(evaluation.input_tokens, evaluation.output_tokens)
  const totalWorkflow = evaluation.workflow.reduce((sum, stage) => sum + stage.count, 0)
  return (
    <PageFrame page="cost" snapshot={snapshot}>
      <main id="main-content" className="info-page cost-page">
        <section className="info-hero cost-hero">
          <div className="info-hero-copy"><span className="hero-overline"><span className="hero-pulse" />运行记录 · 费用估算</span><h1>Deepseek Flash API调用成本核算</h1><p>这页只展示归档运行数据。没有受控基线时，不推断优化幅度或质量提升。</p><div className="hero-pills"><span><Check size={12} aria-hidden="true" />计量口径可见</span><span><Check size={12} aria-hidden="true" />限制同时呈现</span></div></div>
          <div className="cost-hero-stat"><span>费用估算</span><strong>¥{evaluation.estimated_cost_cny.toFixed(3)}</strong><small>人民币 · 非账单</small><span className="cost-decoration" aria-hidden="true"><i /><i /><i /><i /><i /></span></div>
        </section>

        <section className="info-stats-grid cost-stats" aria-label="运行指标">
          <StatCard label="输入 Token" value={formatNumber(evaluation.input_tokens, 0)} detail="含缓存读取部分" icon={Database} />
          <StatCard label="输出 Token" value={formatNumber(evaluation.output_tokens, 0)} detail="归档阶段记录" icon={Activity} />
          <StatCard label="模型请求" value={formatNumber(evaluation.requests, 0)} detail={`${formatNumber(evaluation.tool_calls, 0)} 次工具调用`} icon={Waypoints} />
          <StatCard label="校验结果" value={`${formatNumber(evaluation.tests_passed, 0)} 项通过`} detail={`${formatNumber(evaluation.validation_checks, 0)} 项确定性检查`} icon={FileCheck2} />
        </section>

        <p className="cost-archive-scope" role="note">
          本页的 {formatNumber(evaluation.requests, 0)} 次模型请求、{formatNumber(archived.validation_checks, 0)} 项校验和 {formatNumber(archived.completed_stages, 0)} 个研究阶段，来自早期 8 家公司归档研究；不含后续补充研究及本次前端开发。它们不代表当前研究覆盖或当前数据校验结果。
        </p>

        <section className="info-section token-section">
          <SectionHeading kicker="Token 使用" title="输入与输出分开查看" description="缓存读取属于输入 Token 的子集，不能重复相加。" />
          <div className="token-card">
            <TokenBar label="输入 Token" value={evaluation.input_tokens} max={maxTokens} detail="按归档阶段计数" />
            <TokenBar label="输出 Token" value={evaluation.output_tokens} max={maxTokens} detail="按归档阶段计数" />
            <div className="cache-read-note"><div><span className="cache-icon"><Database size={14} aria-hidden="true" /></span><span>缓存读取 Token</span></div><strong>{formatNumber(evaluation.cache_read_tokens, 0)}</strong><small>已包含在输入 Token 中</small></div>
          </div>
        </section>

        <section className="cost-details-grid">
          <article className="cost-breakdown-card">
            <div className="cost-card-heading"><span className="section-kicker">工作流计数</span><span>{totalWorkflow} 次阶段记录</span></div>
            <div className="cost-stage-list">{evaluation.workflow.map((stage) => {
              const width = totalWorkflow ? Math.max(3, (stage.count / totalWorkflow) * 100) : 0
              return <div className="cost-stage" key={stage.label}><div><span>{stage.label}</span><strong>{stage.count}</strong></div><span className="stage-track"><i style={{ width: `${width}%` }} /></span></div>
            })}</div>
            <div className="cost-estimate"><div><span>费用估算</span><strong>¥{evaluation.estimated_cost_cny.toFixed(6)}</strong></div><p>{evaluation.estimate_basis}</p></div>
          </article>
          <article className="measurement-card">
            <div className="measurement-head"><span className="measurement-icon"><Clock3 size={17} aria-hidden="true" /></span><div><span className="section-kicker">实验边界</span><h3>尚无受控对照</h3></div></div>
            <p>尚未用相同任务、材料和质量标准做对照比较，因此不报告节省比例或质量提升。</p>
            <div className="measurement-unavailable"><span>运行耗时</span><strong>未记录</strong><span>对照质量</span><strong>未测</strong></div>
            <ul>{evaluation.limitations.map((item) => (
              <li key={item}>
                {item.startsWith('八家仅为首批研究')
                  ? '成本与阶段归档只覆盖首批 8 家公司，不代表当前研究总数；当前公司覆盖见“流程与证据”。英维克与 Vertiv 是完整同期间量化样本。'
                  : item}
              </li>
            ))}</ul>
          </article>
        </section>

        <section className="info-section cost-disclaimer-section">
          <div className="cost-disclaimer"><span className="disclaimer-icon"><CircleHelp size={17} aria-hidden="true" /></span><div><h3>估算不等于账单</h3><p>{evaluation.estimate_basis}</p><p>检查通过表示规则校验完成，不代表研究事实准确率。成本不包含未列入估算的失败替换试验、前端实现模型和数据许可费用。</p></div></div>
        </section>
      </main>
      <PageFooter snapshot={snapshot} />
    </PageFrame>
  )
}


export function ProdLoopPage({ snapshot }: { snapshot: Snapshot }) {
  const steps = [
    { no: '1', title: '汇入数据', detail: '定期汇入披露、行情与产业资讯' },
    { no: '2', title: '研究更新', detail: '按可分析主题增量更新，保留证据边界' },
    { no: '3', title: '发布结果', detail: '发布已验证研究结果，前台只读秒开' },
    { no: '4', title: '查看研究摘要', detail: '公司基础信息即时显示；点击 AI智能总结后查看已发布研究依据' },
    { no: '5', title: '事件补研', detail: '重大题材出现时补充研究' },
  ]
  const map = [
    { prod: '已发布研究信息', proto: '选择公司后即时展示基础信息；总结整理过程约数秒' },
    { prod: '研究依据', proto: '总结展开后显示现有归属、可信度、对照、传导与补充资料' },
    { prod: '日更 / 定时', proto: '当前原型尚未接入自动定时更新' },
  ]
  return (
    <PageFrame page="prodLoop" snapshot={snapshot}>
      <main id="main-content" className="info-page prod-loop-page">
        <section className="info-hero">
          <div className="info-hero-copy">
            <span className="hero-overline"><span className="hero-pulse" />产品说明</span>
            <h1>研究流程说明</h1>
            <p>ChainScope 以可核验研究为基础：前台只读已发布结果，不编造财务数据。</p>
            <div className="hero-pills">
              <span><Check size={12} aria-hidden="true" />只读已发布结果</span>
              <span><Check size={12} aria-hidden="true" />不编造财务数据</span>
              <span><Check size={12} aria-hidden="true" />研究结论供核验</span>
            </div>
          </div>
        </section>

        <section className="info-section" aria-labelledby="prod-steps-title">
          <div className="info-section-heading">
            <span className="section-kicker">目标流程</span>
            <h2 id="prod-steps-title">五步闭环</h2>
            <p>基础信息即时显示；点击 AI智能总结后查看已发布的公司结论和依据。</p>
          </div>
          <ol className="prod-loop-steps">
            {steps.map((s) => (
              <li key={s.no}>
                <span className="prod-step-no">{s.no}</span>
                <div>
                  <strong>{s.title}</strong>
                  <p>{s.detail}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section className="info-section" aria-labelledby="proto-map-title">
          <div className="info-section-heading">
            <span className="section-kicker">当前原型</span>
            <h2 id="proto-map-title">与正式服务对照</h2>
            <p>当前界面展示真实研究结果的产品形态；完整调度与计费仍在规划中。</p>
          </div>
          <ul className="prod-loop-map">
            {map.map((row) => (
              <li key={row.prod}>
                <strong>{row.prod}</strong>
                <span>{row.proto}</span>
              </li>
            ))}
          </ul>
        </section>
      </main>
      <PageFooter snapshot={snapshot} />
    </PageFrame>
  )
}
