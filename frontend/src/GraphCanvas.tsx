import { memo, useEffect, useMemo, useRef, useState } from 'react'
import type { GraphNode, Snapshot } from './types'

interface Point { x: number; y: number }

interface GraphCanvasProps {
  snapshot: Snapshot
  activeSegment: string
  onSelectSegment: (id: string) => void
  onHover?: (node: GraphNode | null) => void
}

const POSITIVE = new Set(['related', 'positive', 'support'])
const NEGATIVE = new Set(['substitute', 'crowd', 'negative', 'displace'])

function polarity(node: GraphNode, snapshot: Snapshot): 'positive' | 'negative' | 'unclear' {
  const impact = (node.impact || '').toLowerCase()
  if (POSITIVE.has(impact)) return 'positive'
  if (NEGATIVE.has(impact)) return 'negative'
  if (impact && impact !== 'unclear') return 'unclear'
  const edge = snapshot.graph.edges.find((e) => e.source === node.id || e.target === node.id)
  const direction = (edge?.direction || '').toLowerCase()
  if (POSITIVE.has(direction)) return 'positive'
  if (NEGATIVE.has(direction)) return 'negative'
  return 'unclear'
}

function hasVerifiedPositive(snapshot: Snapshot) {
  const structural = snapshot.graph.nodes.filter((n) => n.type === 'theme' || n.type === 'branch' || n.type === 'segment')
  return structural.some((n) => POSITIVE.has((n.impact || '').toLowerCase()))
}

function hasVerifiedNegative(snapshot: Snapshot) {
  const structural = snapshot.graph.nodes.filter((n) => n.type === 'theme' || n.type === 'branch' || n.type === 'segment')
  return structural.some((n) => NEGATIVE.has((n.impact || '').toLowerCase()))
}

function allImpactUnclear(snapshot: Snapshot) {
  const structural = snapshot.graph.nodes.filter((n) => n.type === 'theme' || n.type === 'branch' || n.type === 'segment')
  const impactUnclear = structural.every((n) => (n.impact || 'unclear').toLowerCase() === 'unclear')
  const edgeUnclear = snapshot.graph.edges.every((e) => (e.direction || 'unclear').toLowerCase() === 'unclear')
  return impactUnclear && edgeUnclear
}

function allSizeDefault(snapshot: Snapshot) {
  const structural = snapshot.graph.nodes.filter((n) => n.type === 'theme' || n.type === 'branch' || n.type === 'segment')
  return structural.every((n) => n.size === 1 || n.size === 1.0)
}

function fillFor(pol: 'positive' | 'negative' | 'unclear', neutralMode: boolean): string {
  if (neutralMode || pol === 'unclear') return '#4A6080'
  if (pol === 'positive') return '#8B1E2D'
  return '#1F6B4A'
}

function nodeTitle(node: GraphNode, pol: 'positive' | 'negative' | 'unclear'): string {
  const full = node.label
  const parts = [full]
  if (pol === 'positive') parts.push('相关（已核验）')
  else if (pol === 'negative') parts.push('替代/受挤占（已核验）')
  else parts.push('相关方向未核验')
  if (node.impact_rationale) parts.push(node.impact_rationale)
  if (node.impact_source_ids?.length) parts.push(`来源: ${node.impact_source_ids.join(', ')}`)
  return parts.join(' · ')
}

/** Deterministic 0..1 from string (FNV-1a style). */
function hash01(seed: string): number {
  let h = 2166136261
  for (let i = 0; i < seed.length; i += 1) {
    h ^= seed.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return ((h >>> 0) % 10000) / 10000
}

const BRANCH_BASE_R = 130
const SEGMENT_BASE_R = 230
const SEGMENT_OUTER_R = 258
const SEGMENT_INNER_R = 208

function makeLayout(snapshot: Snapshot) {
  const points = new Map<string, Point>()
  const theme = snapshot.graph.nodes.find((n) => n.type === 'theme')
  if (theme) points.set(theme.id, { x: 0, y: 0 })

  // Preserve snapshot order; no hardcoded branch id list.
  const ordered = snapshot.graph.nodes.filter((n) => n.type === 'branch')
  const weights = ordered.map((b) => 0.72 + hash01(`${b.id}:w`) * 0.56)
  const totalW = weights.reduce((a, b) => a + b, 0) || 1
  let cursor = -Math.PI / 2

  ordered.forEach((branch, index) => {
    const span = (Math.PI * 2 * weights[index]) / totalW
    const angle = cursor + span / 2
    const aJitter = (hash01(`${branch.id}:a`) - 0.5) * 0.1
    const rJitter = (hash01(`${branch.id}:r`) - 0.5) * 20
    const a = angle + aJitter
    const r = BRANCH_BASE_R + rJitter
    points.set(branch.id, { x: Math.cos(a) * r, y: Math.sin(a) * r })
    cursor += span

    const segments = snapshot.graph.nodes.filter((n) => n.type === 'segment' && n.parent_id === branch.id)
    const segWeights = segments.map((s) => 0.75 + hash01(`${s.id}:sw`) * 0.5)
    const segTotal = segWeights.reduce((x, y) => x + y, 0) || 1
    const fan = Math.min(1.05, Math.max(0.28, 0.22 + segments.length * 0.22))
    let segCursor = a - fan / 2
    segments.forEach((segment, si) => {
      const segSpan = (fan * segWeights[si]) / segTotal
      const sa = segCursor + segSpan / 2 + (hash01(`${segment.id}:sa`) - 0.5) * 0.06
      let radius = SEGMENT_BASE_R + (hash01(`${segment.id}:sr`) - 0.5) * 16
      if (segments.length > 1) {
        radius = (si % 2 === 0 ? SEGMENT_OUTER_R : SEGMENT_INNER_R) + (hash01(`${segment.id}:sr2`) - 0.5) * 12
      }
      points.set(segment.id, { x: Math.cos(sa) * radius, y: Math.sin(sa) * radius })
      segCursor += segSpan
    })
  })
  return { points, orderedBranches: ordered }
}

function quadraticPath(x1: number, y1: number, x2: number, y2: number, seed: string): string {
  const mx = (x1 + x2) / 2
  const my = (y1 + y2) / 2
  const dx = x2 - x1
  const dy = y2 - y1
  const len = Math.hypot(dx, dy) || 1
  const nx = -dy / len
  const ny = dx / len
  const bulge = (hash01(seed) - 0.5) * Math.min(40, len * 0.28)
  const cx = mx + nx * bulge
  const cy = my + ny * bulge
  return `M ${x1.toFixed(2)} ${y1.toFixed(2)} Q ${cx.toFixed(2)} ${cy.toFixed(2)} ${x2.toFixed(2)} ${y2.toFixed(2)}`
}

function nodeRadius(node: GraphNode, sizeDefault: boolean): number {
  if (sizeDefault) {
    if (node.type === 'theme') return 42
    if (node.type === 'branch') return 26
    return 16
  }
  const base = node.type === 'theme' ? 36 : node.type === 'branch' ? 22 : 14
  return base * Math.max(0.7, Math.min(1.6, node.size || 1))
}

/** Short display from node.label only — no product-id hardcoding. */
function displayLabel(node: GraphNode): string {
  if (node.type === 'segment' && node.label.length > 6) {
    return `${node.label.slice(0, 5)}…`
  }
  return node.label
}

const GraphCanvas = memo(function GraphCanvas({ snapshot, activeSegment, onSelectSegment, onHover }: GraphCanvasProps) {
  const surfaceRef = useRef<HTMLDivElement>(null)
  const [viewport, setViewport] = useState({ width: 720, height: 560 })
  const neutralMode = useMemo(() => allImpactUnclear(snapshot), [snapshot])
  const showPositive = useMemo(() => hasVerifiedPositive(snapshot), [snapshot])
  const showNegative = useMemo(() => hasVerifiedNegative(snapshot), [snapshot])
  const sizeDefault = useMemo(() => allSizeDefault(snapshot), [snapshot])
  const { points, orderedBranches } = useMemo(() => makeLayout(snapshot), [snapshot])

  useEffect(() => {
    const surface = surfaceRef.current
    if (!surface) return
    const observer = new ResizeObserver((entries) => {
      const rect = entries[0]?.contentRect
      if (rect && rect.width > 0 && rect.height > 0) setViewport({ width: rect.width, height: rect.height })
    })
    observer.observe(surface)
    return () => observer.disconnect()
  }, [])

  const scale = Math.min(1, Math.max(0.45, (Math.min(viewport.width, viewport.height) / 2 - 28) / 280))
  const structural = snapshot.graph.nodes.filter((n) => n.type === 'theme' || n.type === 'branch' || n.type === 'segment')
  const theme = structural.find((n) => n.type === 'theme')

  return (
    <div className="graph-stage concentric-stage">
      <div ref={surfaceRef} className="graph-surface concentric-surface" aria-label="三层产业结构图">
        <svg
          className="radial-graph concentric-graph"
          viewBox={`${-viewport.width / 2} ${-viewport.height / 2} ${viewport.width} ${viewport.height}`}
          role="img"
          aria-label="主题、产业分支与环节三层图。点击最外层环节可查看企业列表。"
        >
          <g transform={`scale(${scale})`}>
            <circle className="orbit-ring" r={130} />
            <circle className="orbit-ring" r={230} />
            <circle className="orbit-ring orbit-ring-outer" r={258} />
            {orderedBranches.map((branch) => {
              const bp = points.get(branch.id)
              const tp = theme ? points.get(theme.id) : { x: 0, y: 0 }
              if (!bp || !tp) return null
              return (
                <path
                  key={`e-${branch.id}`}
                  className="graph-edge is-membership"
                  fill="none"
                  d={quadraticPath(tp.x, tp.y, bp.x, bp.y, `edge:${branch.id}`)}
                />
              )
            })}
            {structural.filter((n) => n.type === 'segment').map((segment) => {
              const sp = points.get(segment.id)
              const bp = segment.parent_id ? points.get(segment.parent_id) : null
              if (!sp || !bp) return null
              return (
                <path
                  key={`e-${segment.id}`}
                  className="graph-edge is-membership"
                  fill="none"
                  d={quadraticPath(bp.x, bp.y, sp.x, sp.y, `edge:${segment.id}`)}
                />
              )
            })}
            {structural.map((node) => {
              const point = points.get(node.id)
              if (!point) return null
              const r = nodeRadius(node, sizeDefault)
              const pol = polarity(node, snapshot)
              const fill = fillFor(pol, neutralMode)
              const selected = node.type === 'segment' && node.id === activeSegment
              const interactive = node.type === 'segment'
              const label = displayLabel(node)
              const full = node.label
              const dy = node.type === 'theme' ? r + 18 : point.y >= 0 ? r + 14 : -(r + 8)
              return (
                <g
                  key={node.id}
                  className={`graph-node graph-node-${node.type}${selected ? ' is-selected' : ''}${interactive ? ' is-interactive' : ''}`}
                  transform={`translate(${point.x} ${point.y})`}
                  role={interactive ? 'button' : 'img'}
                  tabIndex={interactive ? 0 : undefined}
                  aria-label={interactive ? `环节：${full}，点击查看企业` : `${node.type === 'theme' ? '主题' : '分支'}：${full}`}
                  aria-pressed={interactive ? selected : undefined}
                  onClick={interactive ? (e) => { e.stopPropagation(); onSelectSegment(node.id) } : undefined}
                  onKeyDown={interactive ? (e) => {
                    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelectSegment(node.id) }
                  } : undefined}
                  onPointerEnter={() => onHover?.(node)}
                  onPointerLeave={() => onHover?.(null)}
                >
                  <title>{nodeTitle(node, pol)}</title>
                  <circle className="node-hit-area" r={Math.max(r + 10, 20)} />
                  <circle className="node-core" r={r} fill={fill} />
                  <text className={`node-label node-label-${node.type}`} textAnchor="middle" x={0} y={dy}>{label}</text>
                </g>
              )
            })}
          </g>
        </svg>
      </div>
      <div className="map-legend concentric-legend" aria-label="星图图例">
        {neutralMode ? (
          <span><i style={{ background: '#4A6080' }} />本轮相关方向未核验，暂用中性色</span>
        ) : (
          <>
            {showPositive && (
              <span><i style={{ background: '#8B1E2D' }} />红=与主题相关（已核验）</span>
            )}
            {showNegative ? (
              <span><i style={{ background: '#1F6B4A' }} />绿=替代/受挤占（已核验）</span>
            ) : (
              <span className="map-hint">本轮无替代/受挤占核验</span>
            )}
            <span><i style={{ background: '#4A6080' }} />中性=未核验</span>
            <span className="map-hint">红绿表示产业相关方向，不是股价涨跌</span>
          </>
        )}
        {sizeDefault && <span className="size-note">体量未披露 · 节点使用默认尺寸</span>}
      </div>
    </div>
  )
})

export default GraphCanvas
