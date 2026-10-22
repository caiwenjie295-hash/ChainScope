import { useEffect, useRef } from 'react'
import type { Company, DetailTab, Snapshot } from './types'
import CompanyInspector from './CompanyInspector'

interface CompanyDrawerProps {
  snapshot: Snapshot
  company: Company
  tab: DetailTab
  pairId: string
  eventStepId: string
  onTab: (tab: DetailTab) => void
  onPair: (pair: string) => void
  onEventStep: (step: string) => void
  onClose: () => void
  returnFocusTarget?: HTMLElement | SVGElement | null
}

export function CompanyDrawer(props: CompanyDrawerProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    const activeElement = document.activeElement
    const returnTarget = props.returnFocusTarget ?? (activeElement instanceof HTMLElement || activeElement instanceof SVGElement ? activeElement : null)
    dialog.showModal()
    dialog.querySelector<HTMLElement>('.close-inspector')?.focus({ preventScroll: true })
    return () => {
      if (dialog.open) dialog.close()
      // Wait until the native modal has left the top layer and React has
      // removed the drawer before returning focus to the control that opened it.
      requestAnimationFrame(() => {
        if (!dialog.open && returnTarget?.isConnected) returnTarget.focus({ preventScroll: true })
      })
    }
  }, [props.returnFocusTarget])

  return (
    <dialog
      ref={dialogRef}
      className="research-drawer"
      aria-labelledby="drawer-company-title"
      onCancel={(event) => { event.preventDefault(); props.onClose() }}
      onClick={(event) => { if (event.target === event.currentTarget) props.onClose() }}
    >
      <CompanyInspector {...props} />
    </dialog>
  )
}
