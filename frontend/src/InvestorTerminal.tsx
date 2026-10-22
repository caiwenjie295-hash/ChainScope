import { useEffect, useMemo, useRef, useState } from 'react'
import { ArrowLeft, BarChart3, Sparkles } from 'lucide-react'
import type { ConceptNode, LocationState, Snapshot } from './types'
import { PageFooter, PageFrame } from './Chrome'
import GraphCanvas from './GraphCanvas'
import { SegmentSheet } from './SegmentSheet'
import { CompanyZone } from './CompanyZone'
import { MarketCapBoardDialog } from './MarketCapBoardDialog'

interface InvestorTerminalProps {
  snapshot: Snapshot
  location: LocationState
  updateLocation: (patch: Partial<LocationState>) => void
}

const CONCEPT_OPTIONS = [
  { key: 'ai', label: 'AI', available: true },
  { key: 'liquor', label: '白酒', available: false },
  { key: 'smart-driving', label: '智能驾驶', available: false },
  { key: 'medicine', label: '医药', available: false },
  { key: 'new-energy', label: '新能源', available: false },
  { key: 'semiconductor', label: '半导体', available: false },
  { key: 'robotics', label: '机器人', available: false },
] as const

function resolveAiRoot(snapshot: Snapshot): ConceptNode | null {
  const concept = snapshot.concepts?.find((item) => item.id === 'concept.ai')
    ?? snapshot.concepts?.find((item) => item.parent_id === null && item.name.toLocaleLowerCase() === 'ai')
  if (concept) return concept
  const theme = snapshot.graph.nodes.find((node) => node.type === 'theme')
  if (!theme) return null
  return {
    id: theme.id,
    name: theme.label,
    parent_id: null,
    level: 0,
    company_count: snapshot.companies.length,
    analysis_enabled: true,
  }
}

function ConceptBoard({
  selected,
  compact,
  analyzing,
  onSelect,
  onAnalyze,
  onBack,
  onOpenBoard,
}: {
  selected: boolean
  compact: boolean
  analyzing: boolean
  onSelect: () => void
  onAnalyze: () => void
  onBack: () => void
  onOpenBoard: () => void
}) {
  return (
    <section className="zone zone-a" aria-labelledby="zone-a-title">
      <div className="zone-head concept-page-heading">
        <span className="zone-index zone-index-wide">研究</span>
        <div>
          <span className="zone-kicker">产业研究 · 跨市场公司信息</span>
          <h1 id="zone-a-title">产业链跨市场与公司研究ChainScope</h1>
        </div>
        {compact && (
          <button type="button" className="secondary-link" onClick={onBack}>
            <ArrowLeft size={14} aria-hidden="true" />
            返回概念
          </button>
        )}
      </div>

      <article className="concept-board">
        <div className="concept-board-heading">
          <div>
            <span className="zone-kicker">研究入口</span>
            <h2>概念板块</h2>
            {compact && <p className="compact-event">当前研究方向：AI</p>}
          </div>
          <button type="button" className="secondary-link market-board-entry" onClick={onOpenBoard}>
            <BarChart3 size={15} aria-hidden="true" />
            全概念市值榜
          </button>
        </div>

        {!compact && (
          <>
            <div className="concept-option-grid" role="group" aria-label="选择概念板块">
              {CONCEPT_OPTIONS.map((option) => option.available ? (
                <button
                  key={option.key}
                  type="button"
                  className={'concept-option' + (selected ? ' is-selected' : '')}
                  aria-pressed={selected}
                  onClick={onSelect}
                >
                  <strong>{option.label}</strong>
                  <span>{selected ? '已选择' : '选择此概念'}</span>
                </button>
              ) : (
                <div key={option.key} className="concept-option is-demo" aria-disabled="true">
                  <strong>{option.label}</strong>
                  <span>Demo，暂无分析</span>
                </div>
              ))}
            </div>
            <div className="motive-cta-row">
              <button
                type="button"
                className="primary-cta"
                disabled={!selected || analyzing}
                aria-busy={analyzing}
                title={analyzing ? '正在整理已发布产业结构' : selected ? '显示已发布的 AI 产业结构' : '请先选择 AI'}
                onClick={onAnalyze}
              >
                <Sparkles size={16} aria-hidden="true" />
                {analyzing ? '分析中…' : '开始分析'}
              </button>
              {!selected && <span className="cta-hint">选择 AI 后查看产业结构</span>}
            </div>
          </>
        )}
      </article>
    </section>
  )
}

export function InvestorTerminal({ snapshot, location, updateLocation }: InvestorTerminalProps) {
  const [sheetOpen, setSheetOpen] = useState(false)
  const [marketBoardOpen, setMarketBoardOpen] = useState(false)
  const [analysisThinking, setAnalysisThinking] = useState(false)
  const [analysisStep, setAnalysisStep] = useState(0)
  const analysisTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const analysisStepRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const aiRoot = useMemo(() => resolveAiRoot(snapshot), [snapshot])
  const selected = Boolean(aiRoot && location.conceptId === aiRoot.id)
    || Boolean(aiRoot && location.analysisStarted && !location.conceptId)
  const companyById = useMemo(() => new Map(snapshot.companies.map((company) => [company.id, company])), [snapshot])
  const activeCompany = location.company ? companyById.get(location.company) ?? null : null
  const activeSegment = location.segment && location.segment !== 'all' ? location.segment : ''
  const phase = analysisThinking
    ? 'S0'
    : !location.analysisStarted
    ? 'S0'
    : sheetOpen
      ? 'S2'
      : activeCompany && location.summaryExpanded
        ? 'S4'
        : activeCompany
          ? 'S3'
          : 'S1'

  const selectAi = () => {
    if (!aiRoot) return
    if (analysisTimerRef.current) clearTimeout(analysisTimerRef.current)
    if (analysisStepRef.current) clearInterval(analysisStepRef.current)
    setAnalysisThinking(false)
    updateLocation({ conceptId: aiRoot.id })
  }

  const revealGraph = () => {
    if (!selected || !aiRoot || analysisThinking || location.analysisStarted) return
    setSheetOpen(false)
    setAnalysisThinking(true)
    setAnalysisStep(0)
    if (analysisStepRef.current) clearInterval(analysisStepRef.current)
    analysisStepRef.current = setInterval(() => setAnalysisStep((step) => Math.min(step + 1, 2)), 900)
    if (analysisTimerRef.current) clearTimeout(analysisTimerRef.current)
    analysisTimerRef.current = setTimeout(() => {
      if (analysisStepRef.current) clearInterval(analysisStepRef.current)
      analysisStepRef.current = null
      analysisTimerRef.current = null
      setAnalysisThinking(false)
      updateLocation({
        conceptId: aiRoot.id,
        analysisStarted: true,
        company: '',
        segment: 'all',
        summaryExpanded: false,
      })
    }, 3000)
  }

  const returnToConcepts = () => {
    if (analysisTimerRef.current) clearTimeout(analysisTimerRef.current)
    if (analysisStepRef.current) clearInterval(analysisStepRef.current)
    analysisTimerRef.current = null
    analysisStepRef.current = null
    setAnalysisThinking(false)
    setSheetOpen(false)
    updateLocation({
      conceptId: '',
      analysisStarted: false,
      company: '',
      segment: 'all',
      summaryExpanded: false,
    })
  }

  useEffect(() => {
    return () => {
      if (analysisTimerRef.current) clearTimeout(analysisTimerRef.current)
      if (analysisStepRef.current) clearInterval(analysisStepRef.current)
    }
  }, [])

  useEffect(() => {
    if (!analysisThinking || (selected && !location.analysisStarted)) return
    if (analysisTimerRef.current) clearTimeout(analysisTimerRef.current)
    if (analysisStepRef.current) clearInterval(analysisStepRef.current)
    analysisTimerRef.current = null
    analysisStepRef.current = null
    setAnalysisThinking(false)
    setAnalysisStep(0)
  }, [analysisThinking, location.analysisStarted, selected])

  useEffect(() => {
    if (!analysisThinking) return
    const frame = window.requestAnimationFrame(() => {
      if (window.matchMedia('(max-width: 860px)').matches) {
        document.getElementById('zone-b-title')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    })
    return () => window.cancelAnimationFrame(frame)
  }, [analysisThinking])

  const openSegment = (segmentId: string) => {
    setSheetOpen(true)
    updateLocation({ segment: segmentId })
  }

  const selectCompany = (id: string) => {
    setSheetOpen(false)
    updateLocation({ company: id, summaryExpanded: false })
  }

  return (
    <PageFrame page="graph" snapshot={snapshot}>
      <main id="main-content" className="investor-page stage-flow" data-phase={phase}>
        <ConceptBoard
          selected={selected}
          compact={location.analysisStarted}
          analyzing={analysisThinking}
          onSelect={selectAi}
          onAnalyze={revealGraph}
          onBack={returnToConcepts}
          onOpenBoard={() => setMarketBoardOpen(true)}
        />

        <section className={'zone zone-b' + (location.analysisStarted ? ' is-active' : ' is-placeholder')} aria-labelledby="zone-b-title">
          <div className="zone-head">
            <span className="zone-index zone-index-wide">结构</span>
            <div>
              <h2 id="zone-b-title">产业结构</h2>
              <p>{location.analysisStarted ? '选择产业环节查看对应公司。' : '选择 AI 并开始分析后显示产业结构。'}</p>
            </div>
          </div>
          {location.analysisStarted ? (
            <div className="zone-b-body">
              <GraphCanvas snapshot={snapshot} activeSegment={activeSegment} onSelectSegment={openSegment} />
              {sheetOpen && activeSegment && (
                <SegmentSheet
                  snapshot={snapshot}
                  segmentId={activeSegment}
                  selectedCompanyId={location.company}
                  showCandidates={location.showCandidates}
                  onToggleCandidates={(next) => updateLocation({ showCandidates: next })}
                  onSelectCompany={selectCompany}
                  onClose={() => setSheetOpen(false)}
                />
              )}
            </div>
          ) : analysisThinking ? (
            <div className="zone-placeholder-body map-placeholder is-thinking" role="status" aria-live="polite">
              <div className="think-pulse" aria-hidden="true" />
              <p>正在整理已发布产业结构…</p>
              <ul className="think-steps">
                <li className={analysisStep >= 0 ? 'is-on' : ''}>梳理相关公司与产业环节</li>
                <li className={analysisStep >= 1 ? 'is-on' : ''}>整理已有归属与证据边界</li>
                <li className={analysisStep >= 2 ? 'is-on' : ''}>展示已发布研究结构</li>
              </ul>
            </div>
          ) : (
            <div className="zone-placeholder-body map-placeholder">
              <div className="map-silhouette" aria-hidden="true"><span /><span /><span /></div>
              <p>等待开始分析</p>
              <span>选择 AI 后点击「开始分析」，查看已发布产业结构。</span>
            </div>
          )}
        </section>

        <CompanyZone
          snapshot={snapshot}
          company={activeCompany}
          summaryExpanded={location.summaryExpanded}
          onExpandSummary={() => updateLocation({ summaryExpanded: true })}
          onClearBody={activeCompany ? () => updateLocation({ company: '', summaryExpanded: false }) : undefined}
        />

        {marketBoardOpen && aiRoot && (
          <MarketCapBoardDialog
            snapshot={snapshot}
            concept={aiRoot}
            onClose={() => setMarketBoardOpen(false)}
            onSelectCompany={(company) => {
              setMarketBoardOpen(false)
              updateLocation({
                analysisStarted: true,
                conceptId: aiRoot.id,
                company: company.id,
                segment: company.segment_id || 'all',
                summaryExpanded: false,
              })
            }}
          />
        )}
      </main>
      <PageFooter snapshot={snapshot} />
    </PageFrame>
  )
}
