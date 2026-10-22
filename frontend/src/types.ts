export type Market = 'CN' | 'US'
export type NodeType = 'theme' | 'branch' | 'segment' | 'company'
export type ClaimKind = 'fact' | 'inference' | 'scenario' | string
export type DemoPriority = 'focus' | 'deep' | 'candidate'
/** Node impact vs theme: positive = related (verified); negative = substitute/crowded-out; unclear = not verified. */
export type ImpactValue = 'positive' | 'negative' | 'unclear' | string

export interface Metric {
  id: string
  name: string
  label: string
  value: number | null
  unit: string
  currency: string | null
  period: string | null
  period_start: string | null
  period_end: string | null
  scope: string
  source_ids: string[]
  missing_reason: string | null
}

export interface BusinessCompositionItem {
  label: string
  share: number | null
  scope: string
  source_ids: string[]
  period: string | null
  missing_reason: string | null
}

export interface SnapshotOverview {
  title: string
  subtitle: string
  changes: Array<{ title: string; text: string; kind: ClaimKind; date?: string | null; source_ids: string[] }>
  coverage: {
    total: number
    researched: number
    candidates: number
    scoped_revenue_evidence_count: number
    revenue_evidence_denominator?: number
    commercial_evidence_count?: number
    scope_label: string
    comparable_pairs: number
    validated_impact_paths: number
    conditional_impact_cases: number
  }
  focus_company_ids: string[]
}

export interface Claim {
  text: string
  kind: ClaimKind
  source_ids: string[]
}

export interface Company {
  id: string
  name: string
  ticker: string
  exchange: string
  market: Market
  research_status: 'reviewed' | 'candidate' | string
  branch_id: string
  segment_id: string
  business_summary: string
  headline: string
  assessment: {
    concept: string
    grade: 'A' | 'B' | 'C' | 'D' | 'E'
    rationale: string
    source_ids: string[]
  }
  metrics: Metric[]
  report_period?: string | null
  relevant_revenue_share?: Metric | null
  revenue_yoy?: Metric | null
  gross_margin?: Metric | null
  gross_margin_change_pp?: Metric | null
  net_profit_yoy?: Metric | null
  evidence_id?: string[]
  comparable_company_ids?: string[]
  impact_paths?: string[]
  business_composition?: BusinessCompositionItem[]
  claims: Claim[]
  uncertainties: string[]
  peer_id: string | null
  source_ids: string[]
  /** Demo fold priority: focus (narrative leads) / deep / candidate (hidden by default). */
  demo_priority?: DemoPriority
  /** True when company is on the narrative focus line. */
  narrative_focus?: boolean
  /** Optional concept/board rank; smaller = higher. */
  rank?: number | null
  /** What rank measures, e.g. concept_weight / market_cap. */
  rank_metric?: string | null
  /** As-of date for rank. */
  rank_as_of?: string | null
}

export interface GraphNode {
  id: string
  label: string
  type: NodeType
  parent_id: string | null
  company_id: string | null
  market: Market | null
  layer: number
  size: number
  size_basis: string
  distance_basis: string
  /** positive = theme-related (verified); negative = substitute/crowded-out; unclear = not verified. */
  impact: ImpactValue
  impact_source_ids?: string[]
  impact_rationale?: string
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  type: string
  kind: ClaimKind
  direction: string
  confidence: string
  source_ids: string[]
  mechanism: string
  conditions: string[]
}

export interface Source {
  id: string
  title: string
  url: string | null
  published_at: string | null
  locator: string | null
  excerpt: string
  access: string
}

export interface Pair {
  id: string
  title: string
  company_ids: string[]
  summary: string
  comparable: string[]
  non_comparable: string[]
  /** Optional free-text incomparability notes (P2 C-zone). */
  incomparability_notes?: string | null
  source_ids: string[]
  /** Shared report window when amounts/ratios were aligned for comparison. */
  aligned_period?: string | null
  /** When false, do not bare-compare absolute amounts across the pair. */
  amount_compare_allowed?: boolean
  /** When true, ratio-style metrics (YoY, margins) may be compared. */
  ratio_compare_allowed?: boolean
}

export interface EventStep {
  id: string
  label: string
  text: string
  kind: 'fact' | 'inference' | 'scenario' | string
  source_ids: string[]
}

export interface SnapshotEvent {
  id: string
  title: string
  date: string
  summary: string
  steps: EventStep[]
  limitations: string[]
}

export interface Evaluation {
  completed_stages: number
  validation_checks: number
  tests_passed: number
  requests: number
  input_tokens: number
  output_tokens: number
  cache_read_tokens: number
  tool_calls: number
  estimated_cost_cny: number
  estimate_basis: string
  limitations: string[]
  workflow: Array<{ label: string; count: number }>
}

/** One ranked row on a RankBoard (P2 dual boards). */
export interface RankItem {
  rank: number
  /** Deep-core slug matching companies[].id; null when not deep-linked. */
  company_id: string | null
  name?: string
  thscode?: string | null
  ticker?: string | null
  value?: number | null
  value_display?: string | null
  /** false ⇒ list-only market row, never open C. Omitted on legacy boards. */
  deep_linked?: boolean
}

/** Dual rank board shared shape (mkt_cap / concept_weight). */
export interface RankBoard {
  metric: 'mkt_cap' | 'concept_weight' | string
  metric_label: string
  as_of: string | null
  unit: string | null
  items: RankItem[]
  /** Machine-readable empty code; never show raw to retail UI. */
  missing_reason: string | null
  /** Retail empty-state copy; prefer over humanizing missing_reason. */
  empty_reason_zh?: string | null
}

/** @deprecated 0.3.1 array-shaped board entry; runtime may still arrive — treat as RankItem. */
export interface ConceptRankEntry {
  company_id: string
  rank: number
  metric?: number | null
  as_of?: string | null
  name?: string
  thscode?: string | null
  value?: number | null
  value_display?: string | null
}

/** Runtime board field: RankBoard object, or legacy RankItem[] / ConceptRankEntry[]. */
export type RankBoardField = RankBoard | RankItem[] | ConceptRankEntry[] | null

/** P2 concept-board taxonomy node (optional until algo exports). Missing analysis_enabled ⇒ false. */
export interface ConceptNode {
  id: string
  name: string
  parent_id: string | null
  level: number
  company_count?: number
  company_ids?: string[]
  /** When true, A2 CTA may enter B. Default false if omitted. */
  analysis_enabled?: boolean
  description?: string
  source_ids?: string[]
  shallow?: boolean
  ths_code?: string
  /** Market-cap rank board (object shape; legacy arrays accepted at runtime). */
  rank_by_mkt_cap?: RankBoardField
  /** Concept-weight rank board (object shape; empty items + missing_reason when unavailable). */
  rank_by_concept_weight?: RankBoardField
}

/** P2 per-concept news / filing / announcement feed item. */
export interface ConceptFeedItem {
  id: string
  title: string
  date: string | null
  url: string | null
  kind: string
  source_id?: string
  excerpt?: string
  publisher?: string
}

/** Per-concept feeds empty-state meta (Record, not array). */
export interface ConceptFeedsMetaEntry {
  empty_reason_zh: string | null
  source_policy?: string
  filtered?: boolean
  raw_count?: number
  kept_count?: number
}

export interface Snapshot {
  schema_version: string
  meta: {
    ui_version: string
    research_version: string
    as_of: string
    generated_at: string
    mode: string
    model: string
    deep_companies: number
    candidate_companies: number
    data_hash: string
    /** Narrative focus branch keys when present. */
    narrative_focus?: string[]
  }
  overview?: SnapshotOverview
  graph: { nodes: GraphNode[]; edges: GraphEdge[] }
  companies: Company[]
  pairs: Pair[]
  /** Primary drive event (compat with older UI). */
  event: SnapshotEvent
  /** Dual/multi drive events when present; prefer over single `event`. */
  events?: SnapshotEvent[]
  sources: Record<string, Source>
  evaluation: Evaluation
  /** P2 concept board; omit until algo exports. */
  concepts?: ConceptNode[]
  /** P2 feeds keyed by concept id; omit until algo exports. */
  concept_feeds?: Record<string, ConceptFeedItem[]>
  /** P1 retail empty-state for feeds; keyed by concept id (object, not array). */
  concept_feeds_meta?: Record<string, ConceptFeedsMetaEntry>
}

export type DetailTab = 'overview' | 'evidence' | 'compare' | 'event'
export type MarketFilter = 'all' | 'CN'

export interface LocationState {
  conceptId: string
  analysisStarted: boolean
  summaryExpanded: boolean
  market: MarketFilter
  branch: string
  segment: string
  company: string
  tab: DetailTab
  pair: string
  event: string
  query: string
  showCandidates: boolean
}
