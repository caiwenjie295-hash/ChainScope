import { useEffect, useMemo, useRef, useState, type Dispatch, type ReactNode, type SetStateAction } from 'react'
import type { Company, GraphEdge, Metric, Snapshot, SnapshotEvent } from './types'
import {
  GRADE_LABELS,
  branchLabel,
  formatMetric,
  formatNumber,
  formatPeriod,
  customerCopy,
  humanizeConceptHierarchy,
  humanizeFieldLabel,
  humanizeMissingReason,
  nodeMap,
} from './format'
import { SourceRefs } from './SourceRefs'
import { GradeHelpButton, GradeLadderCallout } from './conceptGradesGuide'

interface CompanyZoneProps {
  snapshot: Snapshot
  company: Company | null
  summaryExpanded: boolean
  onExpandSummary: () => void
  onClearBody?: () => void
}

const KIND_LABELS: Record<string, string> = {
  fact: '事实',
  inference: '推断',
  scenario: '情景',
}

function metricValue(metric: Metric | null | undefined): number | null {
  if (!metric || metric.value === null || metric.value === undefined) return null
  return metric.value
}

function metricDisplay(company: Company, metric: Metric | null | undefined): string {
  if (!metric || metric.value === null || metric.value === undefined) {
    return metric?.missing_reason
      ? `未核验（${humanizeMissingReason(metric.missing_reason)}）`
      : '未披露/未核验'
  }
  return formatMetric(metric, company)
}

function BarRow({ label, leftLabel, leftValue, rightLabel, rightValue, unit }: {
  label: string
  leftLabel: string
  leftValue: number | null
  rightLabel: string
  rightValue: number | null
  unit: string
}) {
  const max = Math.max(Math.abs(leftValue ?? 0), Math.abs(rightValue ?? 0), 1)
  const leftPct = leftValue == null ? 0 : Math.min(100, (Math.abs(leftValue) / max) * 100)
  const rightPct = rightValue == null ? 0 : Math.min(100, (Math.abs(rightValue) / max) * 100)
  const fmt = (v: number | null) => (v == null ? '未披露/未核验' : `${formatNumber(v)}${unit}`)
  return (
    <div className="bar-compare-row">
      <div className="bar-compare-label">{label}</div>
      <div className="bar-compare-side">
        <span>{leftLabel}</span>
        <div className="bar-track" aria-hidden="true"><div className="bar-fill is-left" style={{ width: `${leftPct}%` }} /></div>
        <strong>{fmt(leftValue)}</strong>
      </div>
      <div className="bar-compare-side">
        <span>{rightLabel}</span>
        <div className="bar-track" aria-hidden="true"><div className="bar-fill is-right" style={{ width: `${rightPct}%` }} /></div>
        <strong>{fmt(rightValue)}</strong>
      </div>
    </div>
  )
}

function HardBlock({ index, title, children, id, titleExtra }: { index: number; title: string; children: ReactNode; id: string; titleExtra?: ReactNode }) {
  return (
    <section className="c-block c-hard-block" aria-labelledby={id}>
      <div className="c-hard-head">
        <span className="c-hard-index" aria-hidden="true">{index}</span>
        <h3 id={id}>{title}</h3>
        {titleExtra}
      </div>
      {children}
    </section>
  )
}

/** ① 归属：产业链分类/层级 + 公司归属证据 */
function MembershipBlock({ snapshot, company }: { snapshot: Snapshot; company: Company }) {
  const nodes = useMemo(() => nodeMap(snapshot), [snapshot])
  const branch = nodes.get(company.branch_id)
  const segment = nodes.get(company.segment_id)
  const companyNodeId = useMemo(() => {
    const byCompanyId = snapshot.graph.nodes.find((n) => n.company_id === company.id)?.id
    return byCompanyId ?? `company.${company.id}`
  }, [snapshot, company.id])

  const membershipEdges = useMemo(() => {
    return snapshot.graph.edges.filter((edge) => {
      if (edge.type !== 'industry_membership') return false
      // Only this company's membership edge — do not pull sibling firms on the same segment.
      return edge.source === companyNodeId || edge.target === companyNodeId
    })
  }, [snapshot.graph.edges, companyNodeId])

  const conceptHits = useMemo(() => {
    const list = snapshot.concepts ?? []
    return list.filter((c) => (c.company_ids ?? []).includes(company.id))
  }, [snapshot.concepts, company.id])

  const factClaims = useMemo(
    () => (company.claims ?? []).filter((c) => c.kind === 'fact'),
    [company.claims],
  )

  const edgeSourceIds = membershipEdges.flatMap((e) => e.source_ids ?? [])
  const hasMembershipSources = edgeSourceIds.length > 0
    || (company.assessment.source_ids?.length ?? 0) > 0
    || factClaims.some((c) => (c.source_ids?.length ?? 0) > 0)

  return (
    <HardBlock index={1} id="c-hard-membership" title="归属：产业链分类与公司归属证据">
      <div className="c-taxonomy-path" aria-label="产业链层级">
        <span className="c-path-chip">{branch?.label ?? branchLabel(snapshot, company.branch_id)}</span>
        <span className="c-path-sep" aria-hidden="true">→</span>
        <span className="c-path-chip">{segment?.label ?? '环节待核验'}</span>
      </div>

      {conceptHits.length > 0 ? (
        <ul className="c-concept-tags" aria-label="概念板归属">
          {conceptHits.map((c) => {
            const parentName = c.parent_id
              ? (snapshot.concepts ?? []).find((p) => p.id === c.parent_id)?.name
              : null
            return (
              <li key={c.id}>
                <strong>{c.name}</strong>
                <span>{humanizeConceptHierarchy(c, parentName)}</span>
                {c.source_ids && c.source_ids.length > 0 && (
                  <SourceRefs ids={c.source_ids} snapshot={snapshot} maxVisible={2} />
                )}
              </li>
            )
          })}
        </ul>
      ) : (
        <p className="c-block-lead">暂无概念板命中；层级标签来自产业结构图。</p>
      )}

      {membershipEdges.length === 0 ? (
        <div className="status-block">
          暂未找到产业链归属关系；目前仅有图谱节点标签，证据尚不充分。
        </div>
      ) : (
        <ul className="c-membership-list">
          {membershipEdges.map((edge: GraphEdge) => {
            const peerId = edge.source === companyNodeId ? edge.target : edge.source
            const peer = nodes.get(peerId)
            const kind = edge.kind || 'inference'
            return (
              <li key={edge.id}>
                <span className={`claim-kind claim-kind-${kind}`}>{KIND_LABELS[kind] ?? kind}</span>
                <div>
                  <p>
                    <strong>{peer?.label ?? '关联节点待核验'}</strong>
                    {edge.mechanism ? ` — ${customerCopy(edge.mechanism)}` : ' — 归属边未附机制说明'}
                  </p>
                  {edge.conditions?.length > 0 && (
                    <ul className="c-condition-list">
                      {edge.conditions.map((cond) => <li key={cond}>{customerCopy(cond)}</li>)}
                    </ul>
                  )}
                  {(edge.source_ids?.length ?? 0) > 0 ? (
                    <SourceRefs ids={edge.source_ids} snapshot={snapshot} maxVisible={2} />
                  ) : (
                    <div className="status-block">此归属关系未附来源，证据尚不充分。</div>
                  )}
                </div>
              </li>
            )
          })}
        </ul>
      )}

      {factClaims.length > 0 && (
        <div className="c-inline-facts">
          <h4>归属相关事实主张</h4>
          <ul className="claim-list">
            {factClaims.slice(0, 4).map((claim, index) => (
              <li key={`memb-fact-${index}`}>
                <span className="claim-kind claim-kind-fact">事实</span>
                <div>
                  <p>{customerCopy(claim.text)}</p>
                  <SourceRefs ids={claim.source_ids} snapshot={snapshot} maxVisible={2} />
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {!hasMembershipSources && (
        <div className="status-block">
          归属证据来源不足，暂不能视为已确认归属。
        </div>
      )}
    </HardBlock>
  )
}

/** ② A–E 概念可信度 */
function GradeBlock({ snapshot, company }: { snapshot: Snapshot; company: Company }) {
  const grade = company.assessment?.grade
  const concept = company.assessment?.concept
  const rationale = company.assessment?.rationale
  const sourceIds = company.assessment?.source_ids ?? []
  const revenueShare = company.relevant_revenue_share
  const hasEvidence = sourceIds.length > 0 || (company.claims ?? []).some((c) => (c.source_ids?.length ?? 0) > 0)
  const relatedClaims = (company.claims ?? []).slice(0, 6)

  return (
    <HardBlock index={2} id="c-hard-grade" title="概念可信度" titleExtra={<GradeHelpButton />}>
      <GradeLadderCallout />
      <div className="c-grade-row">
        <span className={`c-grade-badge grade-${(grade || 'E').toLowerCase()}`} aria-label={`等级 ${grade || 'E'}`}>
          {grade || 'E'}
        </span>
        <div>
          <p className="c-block-lead" style={{ marginBottom: 4 }}>
            <strong>{concept || '概念待核验'}</strong>
            {' · '}
            {GRADE_LABELS[grade || 'E'] ?? '待核验'}
          </p>
          <p className="c-block-lead">{customerCopy(rationale) || '暂未附概念判断理由。'}</p>
        </div>
      </div>

      <div className="c-narrow-revenue status-block">
        <strong>主题相关专项收入：</strong>
        {revenueShare && revenueShare.value != null
          ? metricDisplay(company, revenueShare)
          : (
            <span>
              暂未取得可核验的专项收入
              {revenueShare?.missing_reason ? `（${humanizeMissingReason(revenueShare.missing_reason)}）` : ''}
              。达到 A 级需有可核验专项收入。
            </span>
          )}
        {revenueShare?.source_ids?.length ? (
          <SourceRefs ids={revenueShare.source_ids} snapshot={snapshot} maxVisible={2} />
        ) : null}
      </div>

      {sourceIds.length > 0 ? (
        <SourceRefs ids={sourceIds} snapshot={snapshot} />
      ) : (
        <div className="status-block">概念判断未附来源；等级仅供参考，不视为已核验结论。</div>
      )}

      {relatedClaims.length > 0 && (
        <ul className="claim-list" aria-label="概念相关主张">
          {relatedClaims.map((claim, index) => (
            <li key={`grade-claim-${index}`}>
              <span className={`claim-kind claim-kind-${claim.kind}`}>{KIND_LABELS[claim.kind] ?? claim.kind}</span>
              <div>
                <p>{customerCopy(claim.text)}</p>
                <SourceRefs ids={claim.source_ids} snapshot={snapshot} maxVisible={2} />
              </div>
            </li>
          ))}
        </ul>
      )}

      {!hasEvidence && (
        <div className="status-block">证据不足：暂无概念判断来源与事实主张来源。</div>
      )}

      {company.uncertainties.length > 0 && (
        <div className="c-honest-status">
          <h4>不确定与待补证</h4>
          <ul className="uncertainty-list">
            {company.uncertainties.map((item, index) => (
              <li key={index} className="status-block">{customerCopy(item)}</li>
            ))}
          </ul>
        </div>
      )}
    </HardBlock>
  )
}

/** ③ 中外可比 */
function CompareBlock({ snapshot, company }: { snapshot: Snapshot; company: Company }) {
  // Only algorithm-exported pairs — never invent a peer set from same-segment companies.
  const pair = snapshot.pairs.find((p) => p.company_ids.includes(company.id))
  const peers = useMemo(() => {
    if (!pair) return [] as Company[]
    return pair.company_ids
      .map((id) => snapshot.companies.find((c) => c.id === id))
      .filter((c): c is Company => Boolean(c))
  }, [snapshot, pair])

  if (!pair) {
    return (
      <HardBlock index={3} id="c-hard-compare" title="中外可比：为何可比 / 哪些不可比">
        <div className="status-block">暂无适合直接比较的海外公司；本页不展示跨市场对照数据。</div>
      </HardBlock>
    )
  }

  const left = peers.find((c) => c.id === company.id) ?? peers[0]
  const right = peers.find((c) => c.id !== left.id)
  if (!left || !right) {
    return (
      <HardBlock index={3} id="c-hard-compare" title="中外可比：为何可比 / 哪些不可比">
        <div className="status-block">已有对照设定，但可研究公司样本不足。</div>
      </HardBlock>
    )
  }

  const title = pair?.title ?? `${left.name} / ${right.name}`
  const summary = pair?.summary ?? '同环节已研究公司对照；期间与币种按各自披露保留。'
  const amountAllowed = pair ? pair.amount_compare_allowed === true : false
  const ratioAllowed = pair ? pair.ratio_compare_allowed === true : true
  const alignedPeriod = pair?.aligned_period

  return (
    <HardBlock index={3} id="c-hard-compare" title="中外可比：为何可比 / 哪些不可比">
      <p className="c-block-lead"><strong>{customerCopy(title)}</strong> — {customerCopy(summary)}</p>

      <div className="c-gate-row" aria-label="可比条件">
        <span className={`c-gate ${alignedPeriod ? 'is-on' : 'is-off'}`}>
          {humanizeFieldLabel('aligned_period')}：{alignedPeriod ? formatPeriod(alignedPeriod) : '未对齐'}
        </span>
        <span className={`c-gate ${amountAllowed ? 'is-on' : 'is-off'}`}>
          {humanizeFieldLabel('amount_compare_allowed')}：{amountAllowed ? '是' : '否'}
        </span>
        <span className={`c-gate ${ratioAllowed ? 'is-on' : 'is-off'}`}>
          {humanizeFieldLabel('ratio_compare_allowed')}：{ratioAllowed ? '是' : '否'}
        </span>
      </div>

      {!amountAllowed && (
        <p className="compare-boundary-note">
          金额不可直接对比；不同币种请勿并排比较金额。
        </p>
      )}
      {!ratioAllowed && (
        <p className="compare-boundary-note">
          当前比率口径不满足并列比较条件，本页不绘制比率条形图，避免造成可比印象。
        </p>
      )}

      {pair && (pair.comparable?.length > 0 || pair.non_comparable?.length > 0) && (
        <div className="c-compare-boundaries">
          {pair.comparable?.length > 0 && (
            <section>
              <h4>为何可比</h4>
              <ul>{pair.comparable.map((item) => <li key={item}>{customerCopy(item)}</li>)}</ul>
            </section>
          )}
          {pair.non_comparable?.length > 0 && (
            <section>
              <h4>哪些不可比</h4>
              <ul>{pair.non_comparable.map((item) => <li key={item}>{customerCopy(item)}</li>)}</ul>
            </section>
          )}
        </div>
      )}

      {pair?.incomparability_notes && (
        <div className="status-block">{customerCopy(pair.incomparability_notes)}</div>
      )}

      {ratioAllowed ? (
        <div className="bar-compare" role="img" aria-label="财务比率条形对比">
          <BarRow
            label="营收同比"
            leftLabel={left.name}
            leftValue={metricValue(left.revenue_yoy)}
            rightLabel={right.name}
            rightValue={metricValue(right.revenue_yoy)}
            unit="%"
          />
          <BarRow
            label="毛利率"
            leftLabel={left.name}
            leftValue={metricValue(left.gross_margin)}
            rightLabel={right.name}
            rightValue={metricValue(right.gross_margin)}
            unit="%"
          />
          <BarRow
            label="净利润同比"
            leftLabel={left.name}
            leftValue={metricValue(left.net_profit_yoy)}
            rightLabel={right.name}
            rightValue={metricValue(right.net_profit_yoy)}
            unit="%"
          />
        </div>
      ) : (
        <div className="status-block">
          暂不展示比率条形对比，避免误读为可并排比较。
        </div>
      )}

      {pair && <SourceRefs ids={pair.source_ids} snapshot={snapshot} maxVisible={2} />}
    </HardBlock>
  )
}

/** True when an event mentions this company (id / name / ticker) in id, title, summary, steps, or source_ids. */
function eventRelatedToCompany(event: SnapshotEvent, company: Company): boolean {
  const needles = [company.id, company.name, company.ticker]
    .filter(Boolean)
    .map((s) => s.trim().toLowerCase())
    .filter((s) => s.length >= 2)
  if (needles.length === 0) return false

  const hayParts: string[] = [
    event.id || '',
    event.title || '',
    event.summary || '',
    ...(event.steps ?? []).flatMap((s) => [s.id || '', s.label || '', s.text || '', ...(s.source_ids ?? [])]),
  ]
  const hay = hayParts.join('\n').toLowerCase()
  return needles.some((n) => {
    if (hay.includes(n)) return true
    // id slug as token boundary: fii in fii_ai_server_cloud
    const slug = company.id.toLowerCase()
    if (slug && (hay.includes(`${slug}_`) || hay.includes(`_${slug}`) || hay.includes(`.${slug}`))) return true
    // ticker root without exchange suffix
    const code = company.ticker.split('.')[0]?.toLowerCase()
    if (code && code.length >= 3 && hay.includes(code.toLowerCase())) return true
    return false
  })
}

function EventCard({
  event,
  eventIndex,
  total,
  snapshot,
  activeByEvent,
  setActiveByEvent,
}: {
  event: SnapshotEvent
  eventIndex: number
  total: number
  snapshot: Snapshot
  activeByEvent: Record<string, string>
  setActiveByEvent: Dispatch<SetStateAction<Record<string, string>>>
}) {
  const activeId = activeByEvent[event.id] ?? event.steps[0]?.id
  const active = event.steps.find((s) => s.id === activeId) ?? event.steps[0]
  const hasFact = event.steps.some((s) => s.kind === 'fact')
  return (
    <div className="c-event-block">
      <div className="c-event-head">
        <span className="c-event-kicker">
          {total > 1 ? `事件 ${eventIndex + 1}/${total}` : '事件'}
        </span>
        <h4>{customerCopy(event.title)}</h4>
        <p>{customerCopy(event.summary)}</p>
        {event.date && <time dateTime={event.date}>{event.date}</time>}
      </div>

      <ol className="c-tx-path" aria-label={`${customerCopy(event.title)} 传导路径`}>
        {event.steps.map((step, index) => (
          <li key={step.id}>
            <button
              type="button"
              className={`c-tx-step${active?.id === step.id ? ' is-active' : ''}`}
              onClick={() => setActiveByEvent((prev) => ({ ...prev, [event.id]: step.id }))}
              aria-pressed={active?.id === step.id}
            >
              <span className="c-tx-index">{String(index + 1).padStart(2, '0')}</span>
              <span className={`claim-kind claim-kind-${step.kind}`}>{KIND_LABELS[step.kind] ?? step.kind}</span>
              <span className="c-tx-label">{customerCopy(step.label)}</span>
            </button>
            {index < event.steps.length - 1 && <span className="c-tx-arrow" aria-hidden="true">↓</span>}
          </li>
        ))}
      </ol>

      {active && (
        <article className="c-tx-detail">
          <div className="c-tx-detail-head">
            <span className={`claim-kind claim-kind-${active.kind}`}>{KIND_LABELS[active.kind] ?? active.kind}</span>
            <strong>{customerCopy(active.label)}</strong>
          </div>
          <p>{customerCopy(active.text)}</p>
          <SourceRefs ids={active.source_ids} snapshot={snapshot} />
          {active.kind !== 'fact' && !hasFact && (
            <div className="status-block">路径中尚无事实步骤；本步不视为已证实财务影响。</div>
          )}
          {active.kind === 'scenario' && (
            <div className="status-block">情景假设，不等于已实现订单或已审计财务结果。</div>
          )}
        </article>
      )}

      {event.limitations?.length > 0 && (
        <div className="c-honest-status">
          <h4>传导边界</h4>
          <ul className="uncertainty-list">
            {event.limitations.map((item) => (
              <li key={item} className="status-block">{customerCopy(item)}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

/** ④ 传导：默认仅当前公司相关；其余收进「同主题其他」 */
function TransmissionBlock({ snapshot, company }: { snapshot: Snapshot; company: Company }) {
  const events: SnapshotEvent[] = snapshot.events?.length
    ? snapshot.events
    : (snapshot.event ? [snapshot.event] : [])
  const [activeByEvent, setActiveByEvent] = useState<Record<string, string>>({})
  const [othersOpen, setOthersOpen] = useState(false)
  useEffect(() => {
    setOthersOpen(false)
  }, [company.id])
  const { related, others } = useMemo(() => {
    const relatedList: SnapshotEvent[] = []
    const otherList: SnapshotEvent[] = []
    for (const ev of events) {
      if (eventRelatedToCompany(ev, company)) relatedList.push(ev)
      else otherList.push(ev)
    }
    return { related: relatedList, others: otherList }
  }, [events, company])

  if (events.length === 0) {
    return (
      <HardBlock index={4} id="c-hard-tx" title="传导：外部变化→环节→业务→财务">
        <div className="status-block">暂无事件传导数据；不会编造财务影响。</div>
      </HardBlock>
    )
  }

  return (
    <HardBlock index={4} id="c-hard-tx" title="传导：外部变化→环节→业务→财务">
      <p className="c-block-lead">
        默认仅展示与「{company.name}」相关的传导；事实、推断、情景分标签。无事实依据时，不表述为已证实财务影响。
      </p>
      {related.length === 0 ? (
        <div className="status-block">暂无与该公司直接相关的传导事件。</div>
      ) : (
        related.map((event, eventIndex) => (
          <EventCard
            key={event.id}
            event={event}
            eventIndex={eventIndex}
            total={related.length}
            snapshot={snapshot}
            activeByEvent={activeByEvent}
            setActiveByEvent={setActiveByEvent}
          />
        ))
      )}
      {others.length > 0 && (
        <details
          className="c-tx-others"
          open={othersOpen}
          onToggle={(e) => setOthersOpen((e.currentTarget as HTMLDetailsElement).open)}
        >
          <summary>同主题其他（{others.length}）</summary>
          <div className="c-tx-others-body">
            {others.map((event, eventIndex) => (
              <EventCard
                key={event.id}
                event={event}
                eventIndex={eventIndex}
                total={others.length}
                snapshot={snapshot}
                activeByEvent={activeByEvent}
                setActiveByEvent={setActiveByEvent}
              />
            ))}
          </div>
        </details>
      )}
    </HardBlock>
  )
}

function SupplementalInfo({ company, snapshot }: { company: Company; snapshot: Snapshot }) {
  const items = company.business_composition ?? []
  return (
    <section className="c-supplemental-block" aria-labelledby="c-supplemental-title">
      <h3 id="c-supplemental-title">补充信息</h3>
      <section className="c-block" aria-labelledby="composition-heading">
        <h4 id="composition-heading">业务构成（母类别）</h4>
        {items.length === 0 ? (
          <div className="status-block">业务构成未披露/未核验</div>
        ) : (
          <>
            <p className="c-block-lead">可能包含非 AI 应用，不代表 AI 专项收入占比。</p>
            <ul className="composition-list">
              {items.map((item, index) => (
                <li key={item.label + "-" + index}>
                  <div className="composition-bar-top">
                    <strong>{customerCopy(item.label)}</strong>
                    <span>{item.share == null ? "未披露/未核验" : formatNumber(item.share, 1) + "%"}</span>
                  </div>
                  <small>{formatPeriod(item.period)} · {item.missing_reason ? humanizeMissingReason(item.missing_reason) : "母类别口径"}</small>
                  <SourceRefs ids={item.source_ids} snapshot={snapshot} maxVisible={1} />
                </li>
              ))}
            </ul>
          </>
        )}
      </section>
      <section className="c-block">
        <h4>公司资料来源</h4>
        <SourceRefs ids={company.source_ids} snapshot={snapshot} maxVisible={4} />
      </section>
    </section>
  )
}

export function CompanyZone({
  snapshot,
  company,
  summaryExpanded,
  onExpandSummary,
  onClearBody,
}: CompanyZoneProps) {
  const [summaryThinking, setSummaryThinking] = useState(false)
  const [summaryStep, setSummaryStep] = useState(0)
  const summaryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const summaryStepRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const companyIdRef = useRef(company?.id)
  const titleRef = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    companyIdRef.current = company?.id
    setSummaryThinking(false)
    setSummaryStep(0)
    if (summaryTimerRef.current) clearTimeout(summaryTimerRef.current)
    if (summaryStepRef.current) clearInterval(summaryStepRef.current)
    summaryTimerRef.current = null
    summaryStepRef.current = null

    if (company) {
      const frame = window.requestAnimationFrame(() => {
        if (window.matchMedia("(max-width: 860px)").matches) {
          titleRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
          titleRef.current?.focus({ preventScroll: true })
        }
      })
      return () => window.cancelAnimationFrame(frame)
    }
  }, [company?.id])

  useEffect(() => {
    return () => {
      if (summaryTimerRef.current) clearTimeout(summaryTimerRef.current)
      if (summaryStepRef.current) clearInterval(summaryStepRef.current)
    }
  }, [])

  const runSummary = () => {
    if (!company || summaryThinking || summaryExpanded) return
    const requestedCompany = company.id
    setSummaryThinking(true)
    setSummaryStep(0)
    if (summaryStepRef.current) clearInterval(summaryStepRef.current)
    summaryStepRef.current = setInterval(() => {
      setSummaryStep((step) => Math.min(step + 1, 2))
    }, 900)
    if (summaryTimerRef.current) clearTimeout(summaryTimerRef.current)
    summaryTimerRef.current = setTimeout(() => {
      if (summaryStepRef.current) clearInterval(summaryStepRef.current)
      summaryStepRef.current = null
      summaryTimerRef.current = null
      if (companyIdRef.current === requestedCompany) {
        setSummaryThinking(false)
        onExpandSummary()
      }
    }, 3000)
  }

  if (!company) {
    return (
      <section className="zone zone-c is-placeholder" aria-labelledby="zone-c-title">
        <div className="zone-head">
          <span className="zone-index zone-index-wide">公司</span>
          <div>
            <h2 id="zone-c-title">公司信息</h2>
            <p>选择产业环节中的公司后显示</p>
          </div>
        </div>
        <div className="zone-placeholder-body">
          <p>先查看公司基础信息，再点击「AI智能总结」阅读已有研究内容。</p>
        </div>
      </section>
    )
  }

  const keyMetrics = [
    { key: "revenue_yoy", label: "营收同比", metric: company.revenue_yoy },
    { key: "gross_margin", label: "毛利率", metric: company.gross_margin },
    { key: "net_profit_yoy", label: "净利润同比", metric: company.net_profit_yoy },
    { key: "gross_margin_change_pp", label: "毛利率同比变化", metric: company.gross_margin_change_pp },
    { key: "relevant_revenue_share", label: "AI主题相关收入占比", metric: company.relevant_revenue_share },
  ]

  return (
    <section className="zone zone-c is-filled" aria-labelledby="zone-c-title">
      <div className="zone-head">
        <span className="zone-index zone-index-wide">公司</span>
        <div>
          <h2 id="zone-c-title" ref={titleRef} tabIndex={-1}>{company.name}</h2>
          <p>{company.ticker} · {company.market === "CN" ? "中国上市市场" : "美国上市市场"} · {company.exchange}</p>
        </div>
        {onClearBody && (
          <button type="button" className="secondary-link" onClick={onClearBody}>
            清除选中
          </button>
        )}
      </div>

      <div className="c-body">
        <section className="company-business-block" aria-labelledby="company-business-title">
          <h3 id="company-business-title">主营业务</h3>
          <p>{customerCopy(company.business_summary) || "主营业务暂未披露/核验。"}</p>
        </section>

        <section className="company-key-metrics" aria-labelledby="company-metrics-title">
          <div className="company-key-metrics-heading">
            <h3 id="company-metrics-title">关键财务指标</h3>
          </div>
          <div className="company-metrics-grid">
            {keyMetrics.map(({ key, label, metric }) => (
              <article className="company-metric-card" key={label}>
                <span>{label}</span>
                <strong>{key === "relevant_revenue_share" && (metric?.value == null) ? "暂未披露/核实" : metricDisplay(company, metric)}</strong>
                <small>报告期 · {formatPeriod(metric?.period || company.report_period)}</small>
                {key === "relevant_revenue_share" && metric?.value == null && metric?.missing_reason && (
                  <small className="company-metric-note">{customerCopy(metric.missing_reason)}</small>
                )}
              </article>
            ))}
          </div>
        </section>

        <div className="company-summary-action">
          <button
            type="button"
            className="primary-cta"
            disabled={summaryThinking || summaryExpanded}
            aria-busy={summaryThinking}
            aria-expanded={summaryExpanded}
            aria-controls="company-research-summary"
            onClick={runSummary}
          >
            <span className="summary-sparkle" aria-hidden="true">✦</span>
            AI智能总结
          </button>
          {!summaryExpanded && !summaryThinking && <span className="cta-hint">查看公司业务关联与研究依据</span>}
        </div>

        {summaryThinking && (
          <div className="summary-thinking" role="status" aria-live="polite" aria-busy="true">
            <div className="think-pulse" aria-hidden="true" />
            <p>正在整理已有研究内容…</p>
            <ul className="think-steps">
              <li className={summaryStep >= 0 ? "is-on" : ""}>读取已发布公司总结</li>
              <li className={summaryStep >= 1 ? "is-on" : ""}>整理归属、可信度与对照边界</li>
              <li className={summaryStep >= 2 ? "is-on" : ""}>汇总传导和补充来源</li>
            </ul>
          </div>
        )}

        {summaryExpanded && (
          <div id="company-research-summary" className="company-research-summary">
            <article className="c-ai-summary" aria-labelledby="c-ai-summary-title">
              <h3 id="c-ai-summary-title">AI智能总结</h3>
              <p>{customerCopy(company.headline) || "当前没有已发布的公司总结。"}</p>
            </article>
            <MembershipBlock snapshot={snapshot} company={company} />
            <GradeBlock snapshot={snapshot} company={company} />
            <CompareBlock snapshot={snapshot} company={company} />
            <TransmissionBlock snapshot={snapshot} company={company} />
            <SupplementalInfo company={company} snapshot={snapshot} />
          </div>
        )}
      </div>
    </section>
  )
}
