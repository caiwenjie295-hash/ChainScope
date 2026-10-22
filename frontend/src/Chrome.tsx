import { useState } from 'react'
import { ChevronDown, Link, Network, Boxes, Activity } from 'lucide-react'
import type { ReactNode } from 'react'
import type { Snapshot } from './types'

export type PageKey = 'graph' | 'architecture' | 'cost' | 'prodLoop'

const navItems: Array<{ href: string; key: PageKey; label: string; icon: typeof Network }> = [
  { href: '/', key: 'graph', label: '研究', icon: Network },
  { href: '/agent_architecture.html', key: 'architecture', label: '研究流程', icon: Boxes },
  { href: '/cost_performance.html', key: 'cost', label: '成本与验证', icon: Activity },
]

export function Header({ page, snapshot }: { page: PageKey; snapshot?: Snapshot }) {
  return (
    <header className="topbar">
      <a className="brand" href="/" aria-label="ChainScope 产业透镜首页">
        <span className="brand-mark" aria-hidden="true"><span /><span /><span /><span /></span>
        <span className="brand-wordmark">Chain<span>Scope</span></span>
        <span className="brand-cn">产业透镜</span>
      </a>
      <nav className="primary-nav" aria-label="主导航">
        {navItems.map(({ href, key, label, icon: Icon }) => (
          <a key={key} href={href} className={`nav-link${page === key ? ' is-active' : ''}`} aria-current={page === key ? 'page' : undefined}>
            <Icon size={15} strokeWidth={1.7} aria-hidden="true" />
            <span>{label}</span>
          </a>
        ))}
      </nav>
      <div className="topbar-status">
        {snapshot && <span className="as-of">数据截至 {snapshot.meta.as_of}</span>}
        <span className="ui-version">v{__APP_VERSION__}</span>
      </div>
    </header>
  )
}

export function ReleaseMeta({ snapshot }: { snapshot: Snapshot }) {
  const [open, setOpen] = useState(false)
  // Customer footer: no data_hash / commit / internal package ids in summary or body.
  return (
    <details className="release-meta" onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
      <summary>
        版本详情 <ChevronDown size={12} aria-hidden="true" className={open ? 'is-open' : ''} />
      </summary>
      <div className="release-meta-body">
        <span>界面 v{__APP_VERSION__}</span>
        <span>研究数据截至 {snapshot.meta.as_of}</span>
      </div>
    </details>
  )
}

export function PageFrame({ page, snapshot, children }: { page: PageKey; snapshot: Snapshot; children: ReactNode }) {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">跳到主要内容</a>
      <Header page={page} snapshot={snapshot} />
      {children}
    </div>
  )
}

export function PageFooter({ snapshot }: { snapshot: Snapshot }) {
  return (
    <footer className="page-footer">
      <span>ChainScope 产业透镜</span>
      <span>
        当前展示已发布的研究内容 ·{' '}
        <a className="text-link" href="/prod_loop.html">查看流程说明</a>
        {' '}· 数据截至 {snapshot.meta.as_of} · 不构成投资建议。
      </span>
      <ReleaseMeta snapshot={snapshot} />
    </footer>
  )
}

export function brandMark() {
  return <span className="brand-mark" aria-hidden="true"><span /><span /><span /><span /></span>
}

export function InternalLink({ href, children }: { href: string; children: ReactNode }) {
  return <a href={href} className="text-link">{children}<Link size={12} aria-hidden="true" /></a>
}
