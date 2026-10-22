import type { Company, Metric, Snapshot } from './types'

/** @deprecated P2: do not map branch ids; always use GraphNode.label from snapshot. */
export const BRANCH_LABELS: Record<string, string> = {}

export const GRADE_LABELS: Record<string, string> = {
  A: '可核验专项收入',
  B: '有业务交付、收入未单列',
  C: '产品/订单进展未核实交付',
  D: '仅战略或合作意向',
  E: '证据不足或未核验',
}

export function companyMap(snapshot: Snapshot) {
  return new Map(snapshot.companies.map((company) => [company.id, company]))
}

export function nodeMap(snapshot: Snapshot) {
  return new Map(snapshot.graph.nodes.map((node) => [node.id, node]))
}

export function sourceTitle(snapshot: Snapshot, id: string) {
  return snapshot.sources[id]?.title ?? id
}

export function shortSourceId(id: string) {
  const parts = id.split('.')
  return parts.length > 2 ? parts.slice(-2).join(' · ') : id
}

export function formatDate(value: string | null | undefined) {
  if (!value) return '未注明日期'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeZone: 'UTC' }).format(parsed)
}

export function formatPeriod(value: string | null | undefined) {
  if (!value) return '期间待核验'
  const half = value.match(/^H([12])(\d{4})$/)
  if (half) return `${half[2]}年${half[1] === '1' ? '上' : '下'}半年`
  const fiscal = value.match(/^FY(\d{4})$/)
  if (fiscal) return `${fiscal[1]}财年`
  const quarter = value.match(/^Q([1-4])\s?(\d{4})$/)
  if (quarter) return `${quarter[2]}年第${quarter[1]}季度`
  return value
}

/** Translate machine-shaped or internal research notes for customers without changing their meaning. */
export function customerCopy(value: string | null | undefined): string {
  if (!value) return ''
  let text = value.trim()
  if (!text) return ''
  text = text
    .replace(/Coherent的GAAP营业利润转正与GAAP归母净利润仍亏损须分开陈述，不能笼统写成由亏转盈/g, 'Coherent 的 GAAP 营业利润已转正，但 GAAP 归母净利润仍为亏损；两项指标口径不同，需分别表述')
    .replace(/H12026（FY2026上半年）财务数据未在本地语料命中，无法核对最新半年收入与结构/g, '2026年上半年财务数据尚未收录，暂无法核对最新半年收入与结构')
    .replace(/H12026财务指标在快照中为空，最新半年度收入与交付节奏未核实/g, '2026年上半年财务指标暂无可用数据，最新半年度收入与交付节奏尚未核实')
    .replace(/本轮未取得可核验的AI专项收入占比，不能用母类别占比替代/g, 'AI 专项收入占比尚未核实，未以母类别收入替代')
    .replace(/本轮无\s*(?:中外可比\s*)?pair\s*[（(]missing_reason[）)]/gi, '本轮暂无适合直接比较的海外公司（缺少满足可比口径的样本）')
    .replace(/本轮无\s*pair\s*[、,，]\s*无\s*event\s*财务传导/gi, '本轮暂无适合直接比较的海外公司，也暂无相关财务传导事件')
    .replace(/本轮无\s*(?:中外可比\s*)?pair/gi, '本轮暂无适合直接比较的海外公司')
    .replace(/禁假A/g, '现有材料不足以支持 A 级判断')
    .replace(/勿用条形图暗示可比/g, '不绘制比率条形图，以免图形造成可比印象')
    .replace(/H12026（FY2026上半年）/g, '2026年上半年')
    .replace(/H12026/g, '2026年上半年')
    .replace(/未在本地语料命中/g, '尚未收录相关资料，暂无法核实')
    .replace(/快照中为空/g, '已发布研究数据中暂无可用数据')
    .replace(/MCP response/gi, '数据来源记录')
    .replace(/authenticated_api/gi, '授权数据访问')
    .replace(/fiscal_year=(\d{4})/gi, '$1财年')
    .replace(/原始响应/g, '数据来源记录')
    .replace(/missing_reason/gi, '缺少原因说明')
    .replace(/\bpair\b/gi, '对照公司')
    .replace(/\bevent\b/gi, '事件')
  return text
}

export function humanizeScope(scope: string | null | undefined) {
  if (!scope) return '口径未注明'
  const known: Record<string, string> = {
    consolidated_total: '集团合并口径',
    attributable_to_parent: '归属于母公司股东',
    consolidated_operating_cash_flow: '合并经营现金流',
    consolidated_net_profit: '合并净利润',
    'consolidated_net_profit同比，负基期不输出常规增长率': '合并净利润同比；基期为负时不计算常规增幅',
    'parent_net_profit同比，负基期不输出常规增长率': '归母净利润同比；基期为负时不计算常规增幅',
    'revenue同比，负基期不输出常规增长率': '营业收入同比；基期为负时不计算常规增幅',
    'consolidated_ocf / consolidated_net_profit': '合并经营现金流 ÷ 合并净利润',
    cash_paid_to_acquire_fixed_intangible_other_long_term_assets: '购建固定资产等长期资产支付的现金',
    cash_capital_expenditures_excludes_capitalized_software: '现金资本开支（不含资本化软件）',
    GAAP_net_income_not_EPS: 'GAAP 净利润（非每股收益）',
    currency_units: '原币金额',
    percent: '百分比',
    pct: '百分比',
    percentage_points: '百分点',
    ratio: '比率',
    count: '数量',
  }
  return known[scope] ?? scope.replaceAll('_', ' ')
}

export function formatNumber(value: number, digits = 2) {
  return new Intl.NumberFormat('zh-CN', { maximumFractionDigits: digits, minimumFractionDigits: 0 }).format(value)
}

export function formatMetric(metric: Metric | undefined, _company: Company) {
  if (!metric || metric.value === null || metric.value === undefined) {
    return '暂无可核验数据'
  }
  const value = metric.value
  if (metric.unit === 'currency_units') {
    if (metric.currency === 'CNY') {
      if (Math.abs(value) >= 100_000_000) return `¥${formatNumber(value / 100_000_000)} 亿`
      if (Math.abs(value) >= 10_000) return `¥${formatNumber(value / 10_000)} 万`
      return `¥${formatNumber(value)}`
    }
    if (metric.currency === 'USD') {
      if (Math.abs(value) >= 1_000_000_000) return `$${formatNumber(value / 1_000_000_000)} B`
      if (Math.abs(value) >= 1_000_000) return `$${formatNumber(value / 1_000_000)} M`
      return `$${formatNumber(value)}`
    }
    return `${formatNumber(value)} ${metric.currency ?? ''}`.trim()
  }
  if (metric.unit === 'percent' || metric.unit === 'pct') return `${formatNumber(value)}%`
  if (metric.unit === 'percentage_points') return `${formatNumber(value)} 个百分点`
  if (metric.unit === 'ratio') return `${formatNumber(value)}×`
  return `${formatNumber(value)}${metric.unit === 'count' ? '' : ` ${metric.unit}`}`
}

export function metricByName(company: Company, name: string) {
  return company.metrics.find((metric) => metric.name === name)
}

export function primaryMetrics(company: Company) {
  return [
    { key: 'relevant_revenue_share', label: company.relevant_revenue_share?.label ?? 'AI主题相关收入占比', metric: company.relevant_revenue_share ?? undefined, note: 'AI专项收入；母类别占比另列' },
    { key: 'revenue_yoy', label: company.revenue_yoy?.label ?? '营业收入同比', metric: company.revenue_yoy ?? undefined, note: '集团营业收入同比' },
    { key: 'gross_margin', label: company.gross_margin?.label ?? '集团毛利率', metric: company.gross_margin ?? undefined, note: '合并口径' },
    { key: 'net_profit_yoy', label: company.net_profit_yoy?.label ?? '净利润同比', metric: company.net_profit_yoy ?? undefined, note: '合并净利润同比' },
  ]
}

export function companyPeriod(company: Company) {
  const first = company.metrics.find((metric) => metric.period)
  return first?.period ?? '暂未展开'
}

export function displayTicker(company: Company) {
  return `${company.ticker} · ${company.exchange}`
}

export function graphLabel(company: Company) {
  return company.market === 'US' ? company.ticker : company.name
}

export function edgeLabel(type: string) {
  if (type === 'technology') return '环节关系'
  if (type === 'industry_membership') return '公司归属'
  return '分类层级'
}

export function branchLabel(snapshot: Snapshot, branchId: string | null | undefined) {
  return snapshot.graph.nodes.find((node) => node.id === branchId)?.label ?? '待核验环节'
}

/** Sort companies: numeric rank asc first; missing rank falls back to focus/demo_priority then name. */
export function fallbackPriority(company: Company, focusIds?: Set<string>): number {
  if (focusIds?.has(company.id) || company.demo_priority === 'focus') return 0
  if (company.demo_priority === 'deep') return 1
  if (company.research_status === 'reviewed') return 2
  return 3
}

export function compareCompanies(a: Company, b: Company, focusIds?: Set<string>): number {
  const ar = typeof a.rank === 'number' && Number.isFinite(a.rank) ? a.rank : null
  const br = typeof b.rank === 'number' && Number.isFinite(b.rank) ? b.rank : null
  if (ar !== null && br !== null && ar !== br) return ar - br
  if (ar !== null && br === null) return -1
  if (ar === null && br !== null) return 1
  const pri = fallbackPriority(a, focusIds) - fallbackPriority(b, focusIds)
  if (pri) return pri
  return a.name.localeCompare(b.name, 'zh-CN')
}

/** Map API / snake_case missing_reason codes to retail Chinese. Already-Chinese strings pass through. */
export function humanizeMissingReason(reason: string | null | undefined): string {
  if (!reason) return '原因未注明'
  const trimmed = reason.trim()
  if (!trimmed) return '原因未注明'
  const known: Record<string, string> = {
    weight_api_unavailable: '权重数据暂不可用',
    legacy_empty_array: '本榜暂无条目',
    mkt_cap_api_unavailable: '市值数据暂不可用',
    rank_api_unavailable: '排名数据暂不可用',
    not_exported: '暂未提供',
    no_data: '暂无数据',
    unavailable: '暂不可用',
    pending: '待补充',
    null: '未取得',
    not_disclosed: '未披露',
    unverified: '未核验',
    segment_not_split: '未拆分到本环节',
    no_narrow_revenue: '暂无与主题直接相关的专项收入',
    currency_mismatch: '币种不一致',
    period_mismatch: '报告期未对齐',
    demo_not_analyzable: '该概念暂未开放分析',
    analysis_disabled: '该概念暂未开放分析',
    not_analyzable: '该概念暂未开放分析',
  }
  if (known[trimmed]) return known[trimmed]
  // Paths / dotted API keys / response.* / thscode=… / P2 raw — never dump to retail UI
  if (
    /response\.data|\.[a-z_]+\[|thscode\s*=|\bthscode\b|parent_id|company_id|deep_linked|missing_reason|\bP2\b|assessment|\bclaims\b|\bpair\b/i.test(
      trimmed,
    )
  ) {
    return '暂缺'
  }
  // Already human Chinese (contains CJK, or no snake/camel machine token)
  if (/[\u4e00-\u9fff]/.test(trimmed)) return trimmed
  if (!/[a-z]+_[a-z]/.test(trimmed) && !/^[a-z][a-z0-9_]*$/i.test(trimmed) && !/^[A-Z][a-zA-Z0-9]*$/.test(trimmed)) {
    return trimmed
  }
  // Unknown machine code → soft Chinese, do not dump raw token
  return '暂缺'
}

/** Hide raw API field names in retail copy. */
export function humanizeFieldLabel(field: string): string {
  const known: Record<string, string> = {
    aligned_period: '对齐报告期',
    amount_compare_allowed: '是否允许金额对比',
    ratio_compare_allowed: '是否允许比率对比',
    source_ids: '来源',
    missing_reason: '暂缺原因',
    empty_reason_zh: '空态说明',
    industry_membership: '产业链归属',
    thscode: '证券代码',
    ticker: '证券代码',
    branch_id: '分支',
    segment_id: '环节',
    assessment: '概念判断',
    claims: '事实主张',
    pair: '可比对照',
    pairs: '可比对照',
    parent_id: '上级概念',
    parent: '上级',
    level: '层级',
    deep_linked: '是否已深核',
    analysis_enabled: '可否分析',
    company_id: '公司',
    weight_api_unavailable: '权重数据暂不可用',
    data_hash: '数据包',
    research_version: '研究版本',
    'response.data': '返回数据',
    'P2 raw': '原始字段',
  }
  if (known[field]) return known[field]
  // Never echo API paths / machine tokens into labels
  if (/response\.data|thscode|missing_reason|\bP2\b|\bpair\b|company_id|parent_id/i.test(field)) {
    return '相关字段'
  }
  return humanizeMissingReason(field)
}

/** Concept hierarchy chip for retail: never show raw parent_id / level N / 主题根 jargon. */
export function humanizeConceptHierarchy(
  concept: { level?: number | null; parent_id?: string | null; name?: string | null },
  parentName?: string | null,
): string {
  const level = typeof concept.level === 'number' ? concept.level : null
  const levelZh =
    level === null ? '' : level <= 0 ? '主题' : `第 ${level} 层`
  if (parentName) {
    return levelZh ? `${levelZh} · 上级「${parentName}」` : `上级「${parentName}」`
  }
  if (concept.parent_id) {
    // Parent id present but name unresolved — omit raw id
    return levelZh || '子概念'
  }
  return levelZh || '主题'
}


/** Prefer empty_reason_zh; fall back to humanized missing_reason snake_case. */
export function boardEmptyReasonZh(
  board: { empty_reason_zh?: string | null; missing_reason?: string | null } | null | undefined,
  fallback = '本榜暂不可用',
): string {
  const zh = board?.empty_reason_zh?.trim()
  if (zh) return zh
  if (board?.missing_reason) return humanizeMissingReason(board.missing_reason)
  return fallback
}
