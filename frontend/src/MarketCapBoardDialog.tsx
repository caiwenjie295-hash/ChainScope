import { useEffect, useMemo, useRef } from 'react'
import { X } from 'lucide-react'
import type { Company, ConceptNode, ConceptRankEntry, RankBoard, RankItem, Snapshot } from './types'
import { GRADE_LABELS, boardEmptyReasonZh, formatDate } from './format'

interface MarketCapBoardDialogProps {
  snapshot: Snapshot
  concept: ConceptNode
  onClose: () => void
  onSelectCompany: (company: Company) => void
}

function normalizeBoard(concept: ConceptNode): RankBoard | null {
  const raw = concept.rank_by_mkt_cap
  if (!raw) return null
  if (Array.isArray(raw)) {
    const entries = raw as ConceptRankEntry[]
    return {
      metric: 'mkt_cap',
      metric_label: '市值',
      as_of: entries.find((entry) => entry.as_of)?.as_of ?? null,
      unit: null,
      items: entries.map((entry) => ({
        rank: entry.rank,
        company_id: entry.company_id,
        name: entry.name,
        thscode: entry.thscode ?? null,
        value: entry.value ?? entry.metric ?? null,
        value_display: entry.value_display ?? null,
      })),
      missing_reason: entries.length ? null : 'empty_board',
    }
  }
  const board = raw as RankBoard
  return {
    ...board,
    items: Array.isArray(board.items) ? board.items : [],
  }
}

function formatUnit(unit: string | null): string {
  if (unit === 'CNY') return '人民币'
  if (unit === 'USD') return '美元'
  return unit || '榜单原单位'
}

function formatValue(item: RankItem, unit: string | null): string {
  if (item.value_display) return item.value_display
  if (item.value == null || !Number.isFinite(item.value)) return '未披露'
  const value = Math.abs(item.value)
  const prefix = unit === 'USD' ? '$' : unit === 'CNY' ? '¥' : ''
  if (value >= 1e12) return prefix + (item.value / 1e12).toFixed(2) + '万亿'
  if (value >= 1e8) return prefix + (item.value / 1e8).toFixed(2) + '亿'
  if (value >= 1e4) return prefix + (item.value / 1e4).toFixed(2) + '万'
  return prefix + String(item.value)
}

export function MarketCapBoardDialog({ snapshot, concept, onClose, onSelectCompany }: MarketCapBoardDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const board = useMemo(() => normalizeBoard(concept), [concept])
  const companyById = useMemo(() => new Map(snapshot.companies.map((company) => [company.id, company])), [snapshot.companies])
  const companyByTicker = useMemo(() => new Map(snapshot.companies.map((company) => [company.ticker.toUpperCase(), company])), [snapshot.companies])
  const rows = [...(board?.items ?? [])].sort((left, right) => left.rank - right.rank).slice(0, 10)

  useEffect(() => {
    const dialog = dialogRef.current
    if (dialog && !dialog.open) dialog.showModal()
  }, [])

  const close = () => {
    if (dialogRef.current?.open) dialogRef.current.close()
    onClose()
  }

  return (
    <dialog
      ref={dialogRef}
      className="market-board-dialog"
      aria-labelledby="market-board-title"
      onCancel={(event) => { event.preventDefault(); close() }}
      onClick={(event) => { if (event.target === event.currentTarget) close() }}
    >
      <div className="market-board-panel">
        <header className="market-board-header">
          <div>
            <span className="zone-kicker">AI 概念</span>
            <h2 id="market-board-title">全概念市值榜</h2>
            <p>
              显示前 {Math.min(rows.length, 10)} 名 · 范围：AI 概念成分股
              {board?.as_of ? ' · 截至 ' + formatDate(board.as_of) : ''}
              {' · 币种：' + formatUnit(board?.unit ?? null)}
            </p>
          </div>
          <button type="button" className="sheet-close" onClick={close} aria-label="关闭全概念市值榜">
            <X size={18} aria-hidden="true" />
            <span>关闭</span>
          </button>
        </header>
        {!board ? (
          <p className="market-board-empty" role="status">当前 AI 概念没有可展示的市值榜。</p>
        ) : rows.length === 0 ? (
          <p className="market-board-empty" role="status">{boardEmptyReasonZh(board, '当前 AI 概念没有可展示的市值榜。')}</p>
        ) : (
          <ol className="market-board-list" aria-label="AI 概念市值排名前十">
            {rows.map((item) => {
              const byId = item.company_id ? companyById.get(item.company_id) : undefined
              const byTicker = (item.thscode || item.ticker) ? companyByTicker.get((item.thscode || item.ticker || '').toUpperCase()) : undefined
              const company = byId ?? byTicker
              const name = item.name || company?.name || '公司名称待核对'
              const code = company?.ticker || item.ticker || item.thscode || '证券代码待核对'
              const hasDeepDetail = Boolean(company && item.deep_linked !== false && (
                item.deep_linked === true || company.research_status === 'reviewed'
              ))
              const row = (
                <>
                  <span className="market-board-rank">{item.rank}</span>
                  <span className="market-board-company">
                    <strong>{name}</strong>
                    <small>{code}{company ? ' · ' + (company.market === 'CN' ? '中国上市市场' : '美国上市市场') : ''}</small>
                  </span>
                  <span className="market-board-value">{formatValue(item, board.unit)}</span>
                  {company && <span className={'evidence-chip evidence-' + (company.assessment?.grade ?? 'E').toLocaleLowerCase()}>
                    <strong>{company.assessment?.grade ?? 'E'}</strong>
                    <span>{GRADE_LABELS[company.assessment?.grade ?? 'E'] ?? '待核验'}</span>
                  </span>}
                </>
              )
              return (
                <li key={(item.company_id || item.thscode || item.name || 'row') + '-' + item.rank}>
                  {hasDeepDetail && company ? (
                    <button type="button" className="market-board-row" onClick={() => onSelectCompany(company)}>{row}</button>
                  ) : (
                    <div className="market-board-row is-list-only" aria-label={name + '，暂无已验证详情'}>
                      {row}
                      <span className="market-board-detail-hint">暂无详情</span>
                    </div>
                  )}
                </li>
              )
            })}
          </ol>
        )}
      </div>
    </dialog>
  )
}
