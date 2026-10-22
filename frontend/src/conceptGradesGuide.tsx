/**
 * 只读摘自 docs/CONCEPT_GRADES.md（concept_grades_doc_revision: 2026-10-21.align-cas14-wind）。
 * 前端不自创分级标准；修订以文档冻结为准。
 */
import { ChevronDown, CircleHelp, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

export const CONCEPT_GRADES_DOC_REVISION = '2026-10-21.align-cas14-wind'

/** 与冻结文档 §2 定义一致的短释义（展示用）。 */
export const GRADE_DEFINITIONS: Array<{ grade: string; meaning: string }> = [
  { grade: 'A', meaning: '该概念口径有可核验专项收入数字（非集团总额冒充）。' },
  { grade: 'B', meaning: '有商业业务/销售交付证据，窄口径收入未知或未披露。' },
  { grade: 'C', meaning: '有产品发布、订单或项目进展，尚未核实销售交付。' },
  { grade: 'D', meaning: '仅战略表态、合作意向，无产品与收入证据。' },
  { grade: 'E', meaning: '证据不足或未核验；不等于证明公司没有该业务。' },
]

/** Always-visible retail callout next to A–E (not credit rating). */
export function GradeLadderCallout() {
  return (
    <p className="c-grade-ladder-callout" role="note">
      <strong>证据阶梯，非信用评级</strong>
      <span>A–E 表示「公司 ↔ 概念」证据强度，不是信用分、也不是监管官方评级。</span>
    </p>
  )
}

export function GradeDefinitionPanel({ compact = false }: { compact?: boolean }) {
  return (
    <details className={`c-grade-guide${compact ? ' is-compact' : ''}`}>
      <summary>
        证据阶梯说明 · 本产品定义 / 外部对照
        <ChevronDown size={13} aria-hidden="true" />
      </summary>
      <div className="c-grade-guide-body">
        <p className="c-grade-guide-disclaimer">
          <strong>证据阶梯，非信用评级。</strong>
          A–E 是本产品「公司 ↔ 概念」证据强度阶梯，<strong>不是</strong>信用评级，也不是证监会/交易所官方评级。
          监管层没有「概念股 A–E 国标」；字母名称保留为产品口径。
        </p>

        <h4>本产品定义</h4>
        <ul className="c-grade-def-list">
          {GRADE_DEFINITIONS.map((row) => (
            <li key={row.grade}>
              <span className={`c-grade-badge grade-${row.grade.toLowerCase()}`} aria-hidden="true">
                {row.grade}
              </span>
              <span>{row.meaning}</span>
            </li>
          ))}
        </ul>

        <h4>与外部口径对照（非等价）</h4>
        <ul className="c-grade-align-list">
          <li>
            <strong>收入确认（CAS14）</strong>
            ：客户取得控制权时确认收入 → A 须为已确认/已披露收入类证据；订单、意向、产品发布不能当 A。
          </li>
          <li>
            <strong>分部 / 分产品披露（IFRS 8 等精神）</strong>
            ：禁止用集团总收入冒充窄概念专项 A。
          </li>
          <li>
            <strong>Wind 概念成份实践</strong>
            ：主营相关度 ≥30%≈「强相关」仅作对照，<strong>不自动等于 A</strong>；A 仍要可核验专项收入数字。
          </li>
        </ul>

        <p className="c-grade-guide-meta">
          研究结论供核验 · 不构成投资建议
        </p>
      </div>
    </details>
  )
}

const FULL_GRADE_RULES = [
  { grade: 'A', meaning: '该概念口径有可核验的收入数值。收入来源须对应概念专项口径，不能用集团合并总额或过宽母类别收入替代；订单、意向和产品发布不能作为 A 级收入证据。' },
  { grade: 'B', meaning: '有商业业务或销售交付证据，但窄口径收入未知或未披露。不能据此表述为已证明该概念的收入规模。' },
  { grade: 'C', meaning: '有产品发布、订单或项目进展，尚未核实销售交付。订单不能直接当作已交付业务或收入。' },
  { grade: 'D', meaning: '仅有战略表态、合作意向或生态名单，没有产品与收入证据。' },
  { grade: 'E', meaning: '本轮证据不足或尚未核验；这不代表已证明公司没有相关业务。' },
]

export function GradeHelpButton() {
  const [open, setOpen] = useState(false)
  const buttonRef = useRef<HTMLButtonElement>(null)
  const closeRef = useRef<HTMLButtonElement>(null)
  const dialogRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    closeRef.current?.focus()
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        setOpen(false)
        return
      }
      if (event.key !== 'Tab' || !dialogRef.current) return
      const focusable = Array.from(dialogRef.current.querySelectorAll<HTMLElement>('button, a[href], [tabindex]:not([tabindex="-1"])'))
      if (focusable.length === 0) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      if (buttonRef.current?.isConnected) buttonRef.current.focus({ preventScroll: true })
    }
  }, [open])

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        className="grade-help-button"
        aria-label="查看 A 至 E 概念可信度标准"
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={() => setOpen(true)}
      >
        <CircleHelp size={17} aria-hidden="true" />
      </button>
      {open && (
        <div className="grade-help-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false) }}>
          <section ref={dialogRef} className="grade-help-dialog" role="dialog" aria-modal="true" aria-labelledby="grade-help-title">
            <header className="grade-help-header">
              <div>
                <span className="zone-kicker">产品证据阶梯</span>
                <h2 id="grade-help-title">A–E 概念可信度标准</h2>
              </div>
              <button ref={closeRef} type="button" className="grade-help-close" aria-label="关闭等级说明" onClick={() => setOpen(false)}>
                <X size={18} aria-hidden="true" />
              </button>
            </header>
            <p className="grade-help-disclaimer">
              A–E 衡量公司与研究概念之间的证据强度，是本产品定义，不是信用评级，也不是监管机构或交易所的官方评级。
            </p>
            <ol className="grade-help-list">
              {FULL_GRADE_RULES.map((row) => (
                <li key={row.grade}>
                  <span className={'c-grade-badge grade-' + row.grade.toLocaleLowerCase()} aria-label={'等级 ' + row.grade}>{row.grade}</span>
                  <div><strong>{row.grade} 级 · {GRADE_DEFINITIONS.find((item) => item.grade === row.grade)?.meaning}</strong><p>{row.meaning}</p></div>
                </li>
              ))}
            </ol>
            <p className="grade-help-meta">未披露或缺少专项收入时保留较低等级与说明，不以集团总收入替代概念专项收入。</p>
          </section>
        </div>
      )}
    </>
  )
}
