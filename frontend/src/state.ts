import type { DetailTab, LocationState, MarketFilter } from './types'

const tabs = new Set<DetailTab>(['overview', 'evidence', 'compare', 'event'])

export function readLocationState(defaultCompany = ''): LocationState {
  const query = new URLSearchParams(window.location.search)
  const market = query.get('market') === 'CN' ? 'CN' : 'all'
  const tabValue = query.get('tab') as DetailTab | null
  return {
    conceptId: query.get('concept') ?? '',
    analysisStarted: query.get('stage') === 'structure',
    summaryExpanded: query.get('summary') === '1' && Boolean(query.get('company')),
    market,
    branch: query.get('branch') ?? 'all',
    segment: query.get('segment') ?? 'all',
    company: query.get('company') ?? defaultCompany,
    tab: tabValue && tabs.has(tabValue) ? tabValue : 'overview',
    pair: query.get('pair') ?? 'envicool_vrt',
    event: query.get('event') ?? '',
    query: query.get('q') ?? '',
    showCandidates: query.get('candidates') === '1',
  }
}

export function writeLocationState(state: LocationState, mode: 'replace' | 'push' = 'replace') {
  const params = new URLSearchParams()
  if (state.conceptId) params.set('concept', state.conceptId)
  if (state.analysisStarted) params.set('stage', 'structure')
  if (state.summaryExpanded && state.company) params.set('summary', '1')
  if (state.market !== 'all') params.set('market', state.market)
  if (state.branch !== 'all') params.set('branch', state.branch)
  if (state.segment !== 'all') params.set('segment', state.segment)
  if (state.company) params.set('company', state.company)
  if (state.tab !== 'overview') params.set('tab', state.tab)
  if (state.pair && state.pair !== 'envicool_vrt') params.set('pair', state.pair)
  if (state.event) params.set('event', state.event)
  if (state.query.trim()) params.set('q', state.query.trim())
  if (state.showCandidates) params.set('candidates', '1')
  const suffix = params.size ? `?${params.toString()}` : ''
  const target = `${window.location.pathname}${suffix}`
  if (`${window.location.pathname}${window.location.search}` === target) return
  const method = mode === 'push' ? 'pushState' : 'replaceState'
  window.history[method]({ chainscope: true }, '', target)
}

export function isMarketFilter(value: MarketFilter | string): value is MarketFilter {
  return value === 'all' || value === 'CN'
}
