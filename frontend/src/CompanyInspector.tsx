import { memo, useMemo } from 'react'
import { ArrowDownLeft, ArrowRight, Check, ChevronDown, CircleHelp, FileText, X } from 'lucide-react'
import type { Company, DetailTab, Snapshot } from './types'
import { GRADE_LABELS, branchLabel, companyPeriod, displayTicker, formatMetric, formatNumber, formatPeriod, humanizeMissingReason, humanizeScope, metricByName, nodeMap, primaryMetrics } from './format'
import { SourceRefs } from './SourceRefs'
import { GradeDefinitionPanel, GradeLadderCallout, GRADE_DEFINITIONS } from './conceptGradesGuide'

interface Props {
  snapshot: Snapshot
  company?: Company
  tab: DetailTab
  pairId: string
  eventStepId: string
  onTab: (tab: DetailTab) => void
  onPair: (pair: string) => void
  onEventStep: (step: string) => void
  onClose: () => void
  panelRef?: (element: HTMLElement | null) => void
}

const tabOptions: Array<{ id: DetailTab; label: string }> = [
  { id: 'overview', label: '概览' },
  { id: 'evidence', label: '证据' },
  { id: 'compare', label: '对比' },
  { id: 'event', label: '事件路径' },
]

const gradeHelp: Record<string, string> = Object.fromEntries(
  GRADE_DEFINITIONS.map((row) => [row.grade, row.meaning]),
)

function GradeBadge({ grade }: { grade: string }) {
  return <span className={`grade-badge grade-${grade.toLowerCase()}`} aria-label={`概念证据等级 ${grade}：${GRADE_LABELS[grade] ?? '待核验'}`}>{grade}</span>
}

function PeriodTag({ period }: { period: string }) {
  return <span className="period-tag">{formatPeriod(period)}</span>
}

function MetricCard({
  label, metric, note, company, change,
}: { label: string; metric?: Company['metrics'][number]; note: string; company: Company; change?: Company['gross_margin_change_pp'] }) {
  const value = formatMetric(metric, company)
  const title = metric ? `${metric.label} · ${humanizeScope(metric.scope)}` : note
  return (
    <article className={`metric-card${metric?.value == null ? ' is-missing' : ''}`} title={title}>
      <div className="metric-card-top"><span>{label}</span>{metric?.period && <PeriodTag period={metric.period} />}</div>
      <strong className="metric-value">{value}</strong>
      {change?.value != null && <span className="metric-change">{change.value > 0 ? '+' : ''}{formatNumber(change.value)} 个百分点</span>}
      <span className="metric-note">{metric?.value == null ? (metric?.missing_reason ? humanizeMissingReason(metric.missing_reason) : (company.research_status === 'candidate' ? '候选公司尚未展开财务指标' : '暂未取得可核验数据')) : humanizeScope(metric?.scope || note)}</span>
      {metric && <div className="metric-meta">{metric.unit === 'ratio' ? '无量纲比率' : metric.currency ? `${metric.currency} · ${metric.unit === 'currency_units' ? '原币金额' : metric.unit}` : humanizeScope(metric.unit)}</div>}
    </article>
  )
}

function BusinessComposition({ company, snapshot }: { company: Company; snapshot: Snapshot }) {
  const items = company.business_composition ?? []
  if (items.length === 0) return null
  return <section className="business-composition" aria-labelledby="composition-heading">
    <div className="section-heading-row compact"><div><span className="section-kicker">主营业务构成</span><h3 id="composition-heading">母类别收入占比</h3></div></div>
    <p className="composition-boundary">下列业务可能包含非 AI 应用，不代表 AI 专项收入占比。</p>
    <div className="composition-list">{items.map((item, index) => <article className="composition-item" key={`${item.label}-${index}`}>
      <div className="composition-item-top"><strong>{item.label}</strong><span>{item.share == null ? '暂无可核验数据' : `${formatNumber(item.share, 1)}%`}</span></div>
      <div className="composition-period">{formatPeriod(item.period)} · {item.missing_reason ? humanizeMissingReason(item.missing_reason) : '母类别口径'}</div>
      <details><summary>口径与来源 <ChevronDown size={12} aria-hidden="true" /></summary><p>{item.scope}</p><SourceRefs ids={item.source_ids} snapshot={snapshot} maxVisible={2} /></details>
    </article>)}</div>
  </section>
}

function SecondaryFinancials({ company, snapshot }: { company: Company; snapshot: Snapshot }) {
  const metrics = [metricByName(company, 'revenue'), metricByName(company, 'operating_cash_flow') ?? metricByName(company, 'ocf')].filter((metric): metric is Company['metrics'][number] => Boolean(metric))
  if (metrics.length === 0) return null
  return <details className="secondary-financials">
    <summary>更多财务指标：营收与经营现金流 <ChevronDown size={13} aria-hidden="true" /></summary>
    <div className="secondary-financial-list">{metrics.map((metric) => <div className="secondary-financial-row" key={metric.id}>
      <span>{metric.label}</span><strong>{formatMetric(metric, company)}</strong><small>{formatPeriod(metric.period)} · {humanizeScope(metric.scope)}</small>
    </div>)}</div>
    <SourceRefs ids={metrics.flatMap((metric) => metric.source_ids)} snapshot={snapshot} maxVisible={2} />
  </details>
}

function AssessmentDetails({ company, snapshot }: { company: Company; snapshot: Snapshot }) {
  return (
    <section className="assessment-block">
      <div className="section-heading-row">
        <div><span className="section-kicker">概念真实性</span><h3>{company.assessment.concept}</h3></div>
        <GradeBadge grade={company.assessment.grade} />
      </div>
      <p>{company.assessment.rationale}</p>
      <p className="grade-help"><CircleHelp size={13} aria-hidden="true" />{gradeHelp[company.assessment.grade] ?? '按已取得证据评估。'}</p>
      <GradeLadderCallout />
      <SourceRefs ids={company.assessment.source_ids} snapshot={snapshot} />
      <GradeDefinitionPanel compact />
    </section>
  )
}

function CompanyOverview({ company, snapshot }: { company: Company; snapshot: Snapshot }) {
  const nodes = useMemo(() => nodeMap(snapshot), [snapshot])
  const segment = nodes.get(company.segment_id)
  return (
    <div className="inspector-content overview-content">
      <section className="metrics-section" aria-labelledby="metric-heading">
        <div className="section-heading-row compact"><div><span className="section-kicker">财务摘要 · {formatPeriod(company.report_period ?? companyPeriod(company))}</span><h3 id="metric-heading">增长与盈利</h3></div></div>
        <div className="metric-grid">
          {primaryMetrics(company).map((item) => <MetricCard key={item.key} label={item.label} metric={item.metric} note={item.note} company={company} change={item.key === 'gross_margin' ? company.gross_margin_change_pp ?? undefined : undefined} />)}
        </div>
        <p className="metric-disclaimer"><FileText size={12} aria-hidden="true" />AI 专项收入与母类别主营收入分别展示；空值会标明原因。</p>
        <SourceRefs ids={primaryMetrics(company).flatMap((item) => item.metric?.source_ids ?? [])} snapshot={snapshot} maxVisible={2} />
        <SecondaryFinancials company={company} snapshot={snapshot} />
      </section>

      <BusinessComposition company={company} snapshot={snapshot} />

      <section className="company-intro">
        <div className="company-intro-line">
          <span className="market-badge">{company.market === 'CN' ? '中国大陆' : '美国'}</span>
          <span className="ticker-label">{displayTicker(company)}</span>
          {company.research_status === 'candidate' && <span className="candidate-label">广度候选</span>}
        </div>
        <p>{company.business_summary || '暂未取得主营业务说明。'}</p>
        <div className="company-path"><span>{branchLabel(snapshot, company.branch_id)}</span><ArrowRight size={12} aria-hidden="true" /><span>{segment?.label ?? '研究环节待核验'}</span></div>
      </section>

      <AssessmentDetails company={company} snapshot={snapshot} />

      {company.uncertainties.length > 0 && (
        <details className="uncertainty-details">
          <summary><span>待核验事项</span><span className="uncertainty-count">{company.uncertainties.length}</span><ChevronDown size={13} aria-hidden="true" /></summary>
          <ul>{company.uncertainties.map((item) => <li key={item}>{item}</li>)}</ul>
        </details>
      )}

      <section className="source-summary">
        <span className="section-kicker">研究依据</span>
        <SourceRefs ids={company.source_ids} snapshot={snapshot} />
      </section>
    </div>
  )
}

function EvidenceContent({ company, snapshot }: { company: Company; snapshot: Snapshot }) {
  const claims = company.claims ?? []
  const kindLabels: Record<string, string> = { fact: '披露事实', inference: '研究判断', scenario: '情景假设' }
  return (
    <div className="inspector-content evidence-content">
      <div className="tab-intro"><span className="section-kicker">证据与判断</span><h3>结论可以回到来源</h3><p>区分原始披露、研究归纳与条件情景。</p></div>
      {claims.length ? claims.map((claim, index) => (
        <article className="claim-card" key={`${claim.kind}-${index}`}>
          <div className="claim-heading"><span className={`claim-kind kind-${claim.kind}`}>{kindLabels[claim.kind] ?? claim.kind}</span><span className="claim-index">{String(index + 1).padStart(2, '0')}</span></div>
          <p>{claim.text}</p>
          <SourceRefs ids={claim.source_ids} snapshot={snapshot} />
        </article>
      )) : <div className="inline-empty"><FileText size={17} aria-hidden="true" /><p>暂无公司级证据，当前为广度候选。</p></div>}
      <AssessmentDetails company={company} snapshot={snapshot} />
      {company.uncertainties.length > 0 && <section className="uncertainty-list"><span className="section-kicker">仍待核验</span><ul>{company.uncertainties.map((item) => <li key={item}>{item}</li>)}</ul></section>}
    </div>
  )
}

function compareMetricRows(company: Company) {
  const names = ['revenue', 'consolidated_net_profit', 'operating_cash_flow', 'cash_conversion']
  return names.map((name) => metricByName(company, name)).filter((metric): metric is NonNullable<typeof metric> => Boolean(metric))
}

function isAmountMetric(metric: NonNullable<ReturnType<typeof metricByName>>): boolean {
  if (metric.unit === 'ratio' || metric.unit === '%') return false
  const name = (metric.name || '').toLowerCase()
  return ['revenue', 'consolidated_net_profit', 'operating_cash_flow', 'cash'].some((k) => name.includes(k))
}

function PairCard({ company, snapshot, amountAllowed, ratioAllowed }: {
  company: Company
  snapshot: Snapshot
  amountAllowed: boolean
  ratioAllowed: boolean
}) {
  const metrics = compareMetricRows(company).filter((metric) => {
    if (isAmountMetric(metric)) return amountAllowed
    // ratio / percent style
    return ratioAllowed
  })
  return (
    <article className="pair-company-card">
      <div className="pair-company-heading">
        <div><span className="market-badge">{company.market === 'CN' ? '中国大陆' : '美国'}</span><h4>{company.name}</h4><span className="ticker-label">{company.ticker}</span></div>
        <PeriodTag period={company.report_period ?? companyPeriod(company)} />
      </div>
      <div className="pair-metric-list">
        {metrics.length ? metrics.map((metric) => (
          <div className="pair-metric-row" key={metric.id}>
            <span>{metric.label}</span>
            <strong>{formatMetric(metric, company)}</strong>
            <small>{metric.unit === 'ratio' ? humanizeScope(metric.scope) : `${metric.currency ? `${metric.currency} · ` : ''}${humanizeScope(metric.scope)}`}</small>
          </div>
        )) : (
          <p className="pair-empty">
            {!amountAllowed && !ratioAllowed
              ? '本对比组未开放金额或比率并排对比。'
              : !amountAllowed
                ? '金额不可直接对比；比率类指标亦未开放或暂无数据。'
                : '候选公司没有可比较的财务数据。'}
          </p>
        )}
      </div>
      <SourceRefs ids={metrics.flatMap((metric) => metric.source_ids)} snapshot={snapshot} maxVisible={2} />
    </article>
  )
}

function CompareContent({ snapshot, pairId, onPair }: { snapshot: Snapshot; pairId: string; onPair: (pair: string) => void }) {
  const selectedPair = snapshot.pairs.find((pair) => pair.id === pairId) ?? snapshot.pairs[0]
  const companyById = useMemo(() => new Map(snapshot.companies.map((company) => [company.id, company])), [snapshot])
  if (!selectedPair) return <div className="inline-empty">当前没有可用的对比组。</div>
  const pairCompanies = selectedPair.company_ids.map((id) => companyById.get(id)).filter((company): company is Company => Boolean(company))
  const samePeriod = pairCompanies.length === 2 && (pairCompanies[0].report_period ?? companyPeriod(pairCompanies[0])) === (pairCompanies[1].report_period ?? companyPeriod(pairCompanies[1]))
  const amountAllowed = selectedPair.amount_compare_allowed === true
  const ratioAllowed = selectedPair.ratio_compare_allowed === true
  return (
    <div className="inspector-content compare-content">
      <div className="tab-intro"><span className="section-kicker">跨市场对比</span><h3>并排阅读，保留口径边界</h3><p>不做跨币种换算或金额排名；比率保留各自原始分母。</p></div>
      <label className="select-label" htmlFor="pair-select">选择研究对</label>
      <select id="pair-select" className="pair-select" value={selectedPair.id} onChange={(event) => onPair(event.target.value)}>
        {snapshot.pairs.map((pair) => <option value={pair.id} key={pair.id}>{pair.title}</option>)}
      </select>
      <div className="compare-notes">
        <span className={samePeriod ? 'note-positive' : 'note-caution'}>{samePeriod ? '报告期一致' : '报告期不同'}</span>
        {selectedPair.aligned_period
          ? <span>对齐报告期：{selectedPair.aligned_period}</span>
          : <span>金额均按公司报告币种列示；不作换汇排序。</span>}
        {!amountAllowed && <span className="note-caution">金额不可直接对比</span>}
        {ratioAllowed ? <span className="note-positive">比率类可比</span> : <span className="note-caution">比率类未开放并排对比</span>}
      </div>
      <div className="pair-summary-block">
        <p className="pair-summary-preview">{selectedPair.summary.length > 120 ? `${selectedPair.summary.slice(0, 120)}…` : selectedPair.summary}</p>
        {selectedPair.summary.length > 120 && <details className="pair-summary-details"><summary>展开完整比较摘要 <ChevronDown size={12} aria-hidden="true" /></summary><p>{selectedPair.summary}</p></details>}
      </div>
      <div className="pair-company-grid">
        {pairCompanies.map((company) => (
          <PairCard
            key={company.id}
            company={company}
            snapshot={snapshot}
            amountAllowed={amountAllowed}
            ratioAllowed={ratioAllowed}
          />
        ))}
      </div>
      <div className="comparison-boundaries">
        <section><h4><Check size={14} aria-hidden="true" />可比部分</h4><ul>{selectedPair.comparable.map((item) => <li key={item}>{item}</li>)}</ul></section>
        <section><h4><CircleHelp size={14} aria-hidden="true" />不可直接比较</h4><ul>{selectedPair.non_comparable.map((item) => <li key={item}>{item}</li>)}</ul></section>
      </div>
      <SourceRefs ids={selectedPair.source_ids} snapshot={snapshot} maxVisible={2} />
    </div>
  )
}

function EventContent({ snapshot, stepId, onSelectStep }: { snapshot: Snapshot; stepId: string; onSelectStep: (step: string) => void }) {
  const events = snapshot.events?.length ? snapshot.events : (snapshot.event ? [snapshot.event] : [])
  const kindLabels: Record<string, string> = { fact: '事实', inference: '推断', scenario: '情景' }
  const allSteps = events.flatMap((ev) => ev.steps.map((step) => ({ event: ev, step })))
  const activeEntry = allSteps.find((entry) => entry.step.id === stepId) ?? allSteps[0]
  const active = activeEntry?.step
  return (
    <div className="inspector-content event-content">
      {events.map((event, eventIndex) => (
        <div key={event.id} className="event-block" data-event-id={event.id}>
          <div className="tab-intro">
            <span className="section-kicker">{events.length > 1 ? `事件传导 ${eventIndex + 1}/${events.length}` : '事件传导'}</span>
            <h3>{event.title}</h3>
            <p>{event.summary}</p>
            <time className="event-date" dateTime={event.date}>{event.date}</time>
          </div>
          <div className="event-path" aria-label={`${event.title} 传导路径`}>
            {event.steps.map((step, index) => (
              <div className="event-path-item" key={step.id}>
                <button type="button" className={`event-step${active?.id === step.id ? ' is-active' : ''}`} onClick={() => onSelectStep(step.id)} aria-pressed={active?.id === step.id}>
                  <span className="event-step-index">{String(index + 1).padStart(2, '0')}</span><span className="event-step-label">{step.label}</span>
                </button>
                {index < event.steps.length - 1 && <span className="event-connector" aria-hidden="true"><ArrowDownLeft size={13} /></span>}
              </div>
            ))}
          </div>
          {active && activeEntry?.event.id === event.id && (
            <article className="event-detail">
              <div className="claim-heading"><span className={`claim-kind kind-${active.kind}`}>{kindLabels[active.kind] ?? active.kind}</span><span className="event-selected-label">{active.label}</span></div>
              <p>{active.text}</p>
              <SourceRefs ids={active.source_ids} snapshot={snapshot} />
            </article>
          )}
          <section className="event-limitations"><h4><CircleHelp size={14} aria-hidden="true" />传导边界</h4><ul>{event.limitations.map((item) => <li key={item}>{item}</li>)}</ul></section>
        </div>
      ))}
      <div className="event-direction-key"><span className="kind-fact">事实</span><span className="kind-inference">推断</span><span className="kind-scenario">情景</span><span>不表示股价方向</span></div>
    </div>
  )
}

function NoSelection() {
  return (
    <div className="no-selection">
      <div className="no-selection-icon"><ArrowRight size={18} aria-hidden="true" /></div>
      <span className="section-kicker">公司研究</span>
      <h2>从图谱选择一家企业</h2>
      <p>查看概念依据、财务口径、跨市场对比和事件传导。</p>
      <span className="keyboard-hint"><kbd>Esc</kbd> 关闭详情面板</span>
    </div>
  )
}

const CompanyInspector = memo(function CompanyInspector({ snapshot, company, tab, pairId, eventStepId, onTab, onPair, onEventStep, onClose, panelRef }: Props) {
  return (
    <aside ref={panelRef} className="inspector-panel" aria-label="研究详情" aria-live="polite">
      {company ? <>
        <div className="inspector-topline">
          <span className="inspector-label">研究卡片</span>
          <button type="button" className="icon-button close-inspector" onClick={onClose} aria-label="关闭公司详情" title="关闭详情"><X size={15} aria-hidden="true" /></button>
        </div>
        <div className="inspector-title-row">
          <div className="inspector-title-main"><GradeBadge grade={company.assessment.grade} /><div><h1 id="drawer-company-title">{company.name}</h1><span className="ticker-label">{displayTicker(company)} · {company.report_period ? formatPeriod(company.report_period) : formatPeriod(companyPeriod(company))}</span></div></div>
        </div>
        <p className="drawer-headline" title={company.headline}>{company.headline || '暂未形成公司级研究结论。'}</p>
        <div className="inspector-tabs" role="tablist" aria-label="研究详情视图">
          {tabOptions.map((item, index) => <button key={item.id} id={`research-tab-${item.id}`} type="button" role="tab" aria-controls={`research-panel-${item.id}`} aria-selected={tab === item.id} tabIndex={tab === item.id ? 0 : -1} className={tab === item.id ? 'is-active' : ''} onClick={() => onTab(item.id)} onKeyDown={(event) => {
            if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
            event.preventDefault()
            const nextIndex = event.key === 'Home' ? 0 : event.key === 'End' ? tabOptions.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : tabOptions.length - 1)) % tabOptions.length
            onTab(tabOptions[nextIndex].id)
            document.getElementById(`research-tab-${tabOptions[nextIndex].id}`)?.focus()
          }}>{item.label}</button>)}
        </div>
        <div id={`research-panel-${tab}`} className="research-tabpanel" role="tabpanel" aria-labelledby={`research-tab-${tab}`} tabIndex={0}>
          {tab === 'overview' && <CompanyOverview company={company} snapshot={snapshot} />}
          {tab === 'evidence' && <EvidenceContent company={company} snapshot={snapshot} />}
          {tab === 'compare' && <CompareContent snapshot={snapshot} pairId={pairId} onPair={onPair} />}
          {tab === 'event' && <EventContent snapshot={snapshot} stepId={eventStepId} onSelectStep={onEventStep} />}
        </div>
      </> : <NoSelection />}
    </aside>
  )
})

export default CompanyInspector
