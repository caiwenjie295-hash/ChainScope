import { useEffect, useMemo, useRef, useState } from 'react'
import { Search, X } from 'lucide-react'
import type { Company, Snapshot } from './types'
import { GRADE_LABELS, compareCompanies } from './format'

interface SegmentSheetProps {
  snapshot: Snapshot
  segmentId: string
  selectedCompanyId: string
  showCandidates: boolean
  onToggleCandidates: (next: boolean) => void
  onSelectCompany: (id: string) => void
  onClose: () => void
}

function isCandidate(company: Company): boolean {
  return company.demo_priority === 'candidate' || company.research_status === 'candidate'
}

function marketName(company: Company): string {
  return company.market === 'CN' ? '中国上市市场' : '美国上市市场'
}

export function SegmentSheet({
  snapshot,
  segmentId,
  selectedCompanyId,
  showCandidates,
  onToggleCandidates,
  onSelectCompany,
  onClose,
}: SegmentSheetProps) {
  const [query, setQuery] = useState('')
  const panelRef = useRef<HTMLDivElement>(null)
  const closeRef = useRef<HTMLButtonElement>(null)
  const returnFocusRef = useRef<HTMLElement | null>(null)
  const onCloseRef = useRef(onClose)
  onCloseRef.current = onClose
  const segment = snapshot.graph.nodes.find((node) => node.id === segmentId)
  const companies = useMemo(() => {
    const focusIds = new Set(snapshot.overview?.focus_company_ids ?? [])
    return snapshot.companies
      .filter((company) => company.segment_id === segmentId)
      .filter((company) => showCandidates || !isCandidate(company))
      .filter((company) => {
        const needle = query.trim().toLocaleLowerCase()
        return !needle || (company.name + ' ' + company.ticker).toLocaleLowerCase().includes(needle)
      })
      .sort((a, b) => compareCompanies(a, b, focusIds))
  }, [snapshot, segmentId, showCandidates, query])
  const candidateCount = snapshot.companies.filter((company) => company.segment_id === segmentId && isCandidate(company)).length
  const totalCount = snapshot.companies.filter((company) => company.segment_id === segmentId).length

  const restoreFocus = () => window.requestAnimationFrame(() => returnFocusRef.current?.focus({ preventScroll: true }))

  useEffect(() => {
    returnFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null
    closeRef.current?.focus({ preventScroll: true })
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onCloseRef.current()
        restoreFocus()
        return
      }
      if (event.key !== 'Tab' || !panelRef.current) return
      const items = Array.from(panelRef.current.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled]), [href], [tabindex]:not([tabindex="-1"])'))
      if (items.length === 0) return
      const first = items[0]
      const last = items[items.length - 1]
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const closeAndRestore = () => {
    onCloseRef.current()
    restoreFocus()
  }

  return (
    <div className="segment-sheet" role="dialog" aria-modal="true" aria-labelledby="segment-sheet-title">
      <div className="segment-sheet-backdrop" aria-hidden="true" />
      <div ref={panelRef} className="segment-sheet-panel">
        <header className="segment-sheet-header">
          <div>
            <span className="zone-kicker">环节公司</span>
            <h3 id="segment-sheet-title">公司</h3>
            <p>{segment?.label ?? '产业环节'} · 共 {totalCount} 家</p>
          </div>
          <button ref={closeRef} type="button" className="sheet-close" onClick={closeAndRestore} aria-label="关闭公司列表">
            <X size={18} aria-hidden="true" />
            <span>关闭</span>
          </button>
        </header>

        <div className="segment-toolbar">
          <label className="segment-search" htmlFor="segment-company-search">
            <Search size={16} aria-hidden="true" />
            <span className="sr-only">搜索企业名称或代码</span>
            <input
              id="segment-company-search"
              type="search"
              placeholder="搜索名称或代码"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
          {candidateCount > 0 && (
            <label className="candidate-toggle">
              <input type="checkbox" checked={showCandidates} onChange={(event) => onToggleCandidates(event.target.checked)} />
              <span>显示候选（{candidateCount}）</span>
            </label>
          )}
        </div>

        <ul className="segment-company-list" aria-label="环节公司列表">
          {companies.length === 0 && (
            <li className="segment-empty">
              {query.trim() ? '没有匹配的公司，请调整搜索词。' : '当前没有可显示的公司。'}
            </li>
          )}
          {companies.map((company) => {
            const selected = company.id === selectedCompanyId
            const grade = company.assessment?.grade ?? 'E'
            const status = isCandidate(company) ? '广度候选' : '已研究'
            return (
              <li key={company.id}>
                <button
                  type="button"
                  className={'segment-company-item' + (selected ? ' is-selected' : '') + (isCandidate(company) ? ' is-candidate' : '')}
                  aria-pressed={selected}
                  onClick={() => onSelectCompany(company.id)}
                >
                  <span className="segment-company-main">
                    <strong>{company.name}</strong>
                    <small>{company.ticker} · {marketName(company)} · {company.exchange}</small>
                  </span>
                  <span className="segment-company-meta">
                    <span className={'evidence-chip evidence-' + grade.toLocaleLowerCase()}>
                      <strong>{grade}</strong>
                      <span>{GRADE_LABELS[grade] ?? '待核验'}</span>
                    </span>
                    <em>{status}</em>
                  </span>
                </button>
              </li>
            )
          })}
        </ul>
        <footer className="sheet-hint">选择公司后查看基础信息；点击「AI智能总结」可展开已有研究内容。</footer>
      </div>
    </div>
  )
}
