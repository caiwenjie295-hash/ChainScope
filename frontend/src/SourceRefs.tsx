import { ChevronDown, ExternalLink, LockKeyhole } from 'lucide-react'
import type { Snapshot } from './types'
import { customerCopy, formatDate } from './format'

function locatorLabel(locator: string | null | undefined) {
  if (!locator) return ''
  const page = locator.match(/^(?:p|PDF page\s*)(\d+)$/i)
  if (page) return `第 ${page[1]} 页`
  const fiscalYear = locator.match(/^fiscal_year=(\d{4})$/i)
  if (fiscalYear) return `${fiscalYear[1]} 财年`
  if (/mcp response/i.test(locator)) return '访问记录'
  return ''
}

function accessLabel(access: string | null | undefined) {
  const value = (access || '').toLocaleLowerCase()
  if (value.includes('authenticated_api')) return '授权数据接口'
  if (value.includes('mcp')) return '授权数据访问'
  if (value.includes('internal') || value.includes('local')) return '本地研究资料'
  return '受限访问资料'
}

function hasRestrictedAccess(access: string | null | undefined) {
  const value = (access || '').toLocaleLowerCase()
  return ['authenticated_api', 'mcp', 'internal', 'local', 'restricted', 'authorized'].some((key) => value.includes(key))
}

function sourceHref(url: string, locator: string | null | undefined) {
  const page = locator?.match(/^(?:p|PDF page\s*)(\d+)$/i)?.[1]
  if (!page || !/\.pdf(?:$|[?#])/i.test(url)) return url
  try {
    const target = new URL(url)
    target.hash = `page=${page}`
    return target.toString()
  } catch {
    return `${url}#page=${page}`
  }
}

export function SourceRefs({ ids, snapshot, maxVisible = 2 }: { ids: string[]; snapshot: Snapshot; maxVisible?: number }) {
  const unique = [...new Set(ids)].filter(Boolean)
  if (unique.length === 0) return <span className="source-state">本步骤未附来源</span>
  const visible = unique.slice(0, maxVisible)
  const remaining = unique.slice(maxVisible)
  const renderRef = (id: string) => {
    const source = snapshot.sources[id]
    if (!source) return <span key={id} className="source-chip source-missing" title="来源待核验">来源待核验</span>
    const title = customerCopy(source.title) || '来源记录'
    if (source.url && !hasRestrictedAccess(source.access)) {
      const locator = locatorLabel(source.locator)
      return (
        <a key={id} className="source-chip source-public" href={sourceHref(source.url, source.locator)} target="_blank" rel="noreferrer" title={`${title}${locator ? ` · ${locator}` : ''}`}>
          <ExternalLink size={11} aria-hidden="true" />
          <span>{title}{locator ? ` · ${locator}` : ''}</span>
          {source.published_at && <time dateTime={source.published_at}>{formatDate(source.published_at)}</time>}
        </a>
      )
    }
    const locator = locatorLabel(source.locator)
    const access = accessLabel(source.access)
    return (
      <details key={id} className="source-local">
        <summary className="source-chip source-restricted" title={`${access}${locator ? ` · ${locator}` : ''}`}>
          <LockKeyhole size={11} aria-hidden="true" />
          <span>{access} · {title}{locator ? ` · ${locator}` : ''}</span>
        </summary>
        <div className="source-boundary">
          <strong>{title}</strong>
          <span>{access} · 本地研究存档</span>
          <span>{source.published_at ? formatDate(source.published_at) : '来源日期未注明'}</span>
          {source.excerpt ? <blockquote>{customerCopy(source.excerpt)}</blockquote> : <p>此来源没有公开链接或可展示摘录；进一步核验需要相应数据权限。</p>}
        </div>
      </details>
    )
  }
  return (
    <div className="source-refs" aria-label="来源">
      {visible.map(renderRef)}
      {remaining.length > 0 && <details className="source-more"><summary>另有 {remaining.length} 条来源 <ChevronDown size={11} aria-hidden="true" /></summary><div className="source-refs">{remaining.map(renderRef)}</div></details>}
    </div>
  )
}
