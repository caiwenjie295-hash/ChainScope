import { useCallback, useEffect, useState } from 'react'
import { CircleHelp } from 'lucide-react'
import { loadSnapshot } from './data'
import { readLocationState, writeLocationState } from './state'
import type { LocationState, Snapshot } from './types'
import { Header } from './Chrome'
import type { PageKey } from './Chrome'
import { InvestorTerminal } from './InvestorTerminal'
import { ArchitecturePage, CostPage, ProdLoopPage } from './InfoPages'

function currentPage(): PageKey {
  const path = window.location.pathname
  if (path.endsWith('/agent_architecture.html')) return 'architecture'
  if (path.endsWith('/cost_performance.html')) return 'cost'
  if (path.endsWith('/prod_loop.html')) return 'prodLoop'
  return 'graph'
}

function LoadingScreen({ page }: { page: PageKey }) {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">跳到主要内容</a>
      <Header page={page} />
      <main id="main-content" className="state-screen" aria-live="polite">
        <div className="loading-pulse" aria-hidden="true" />
        <h1>正在加载研究数据…</h1>
        <p>请稍候，正在打开研究数据。</p>
      </main>
    </div>
  )
}

function ErrorScreen({ page, message }: { page: PageKey; message: string }) {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">跳到主要内容</a>
      <Header page={page} />
      <main id="main-content" className="state-screen error-screen" role="alert">
        <div className="error-icon"><CircleHelp size={22} aria-hidden="true" /></div>
        <h1>暂时无法打开研究数据</h1>
        <p>{message}</p>
        <p className="error-next-step">请稍后重试，或重新加载页面。</p>
        <button className="primary-button" type="button" onClick={() => window.location.reload()}>重新加载</button>
      </main>
    </div>
  )
}

function App() {
  const page = currentPage()
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [error, setError] = useState('')
  const [location, setLocation] = useState<LocationState>(() => readLocationState())

  useEffect(() => {
    loadSnapshot().then((data) => {
      setSnapshot(data)
      setLocation((current) => {
        const company = data.companies.some((item) => item.id === current.company) ? current.company : ''
        const aiRoot = data.concepts?.find((item) => item.id === 'concept.ai')
          ?? data.concepts?.find((item) => item.parent_id === null && item.name.toLocaleLowerCase() === 'ai')
        const conceptId = data.concepts?.some((item) => item.id === current.conceptId)
          ? current.conceptId
          : (current.analysisStarted ? aiRoot?.id ?? '' : '')
        return { ...current, company, conceptId, summaryExpanded: Boolean(company && current.summaryExpanded) }
      })
    }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : '发生未知读取错误。'))
  }, [])

  const updateLocation = useCallback((patch: Partial<LocationState>) => {
    setLocation((current) => {
      const next = { ...current, ...patch }
      const shouldPush =
        (patch.analysisStarted !== undefined && patch.analysisStarted !== current.analysisStarted) ||
        (patch.company !== undefined && patch.company !== current.company) ||
        (patch.summaryExpanded !== undefined && patch.summaryExpanded !== current.summaryExpanded)
      writeLocationState(next, shouldPush ? 'push' : 'replace')
      return next
    })
  }, [])

  useEffect(() => {
    const onPopState = () => setLocation(readLocationState())
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  useEffect(() => {
    const titles: Record<PageKey, string> = { graph: '研究 · ChainScope', architecture: '流程与证据 · ChainScope', cost: '成本核算 · ChainScope', prodLoop: '产品说明 · ChainScope' }
    document.title = titles[page]
  }, [page])

  if (!snapshot && !error) return <LoadingScreen page={page} />
  if (error || !snapshot) return <ErrorScreen page={page} message={error || '研究数据为空。'} />
  if (page === 'architecture') return <ArchitecturePage snapshot={snapshot} />
  if (page === 'cost') return <CostPage snapshot={snapshot} />
  if (page === 'prodLoop') return <ProdLoopPage snapshot={snapshot} />
  return <InvestorTerminal snapshot={snapshot} location={location} updateLocation={updateLocation} />
}

export default App
