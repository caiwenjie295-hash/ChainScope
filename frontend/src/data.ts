import type { Snapshot } from './types'

export async function loadSnapshot(): Promise<Snapshot> {
  const response = await fetch('/data/snapshot.json', { cache: 'no-cache' })
  if (!response.ok) throw new Error(`快照读取失败（HTTP ${response.status}）`)
  const value = (await response.json()) as Snapshot
  if (
    value?.schema_version !== 'frontend.1' ||
    !Array.isArray(value?.companies) ||
    !Array.isArray(value?.graph?.nodes) ||
    !Array.isArray(value?.graph?.edges) ||
    !value?.meta?.research_version
  ) {
    throw new Error('研究数据结构不完整，请稍后重试或检查发布的数据文件。')
  }
  return value
}
