import { FolderOpen, Loader2 } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { RunRows, RunRowsSkeleton } from '../components/RunList'
import { EmptyState, ErrorState, TextLink, buttonSecondary } from '../components/ui'
import { api } from '../lib/api'
import type { RunSummary } from '../lib/types'
import { useAsync } from '../lib/useAsync'

const PAGE = 20

export function HistoryPage() {
  const first = useAsync(() => api.listRuns(PAGE, 0), [])
  const [more, setMore] = useState<RunSummary[]>([])
  const [loadingMore, setLoadingMore] = useState(false)

  const runs = first.status === 'success' ? [...first.data.items, ...more] : []
  const total = first.status === 'success' ? first.data.total : 0

  async function loadMore() {
    setLoadingMore(true)
    try {
      const page = await api.listRuns(PAGE, runs.length)
      setMore((m) => [...m, ...page.items])
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Could not load more runs')
    } finally {
      setLoadingMore(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Shortlist history</h1>
      <p className="mt-2 text-ink-muted">
        Every screening run is saved with its ranking, skills and AI summaries.
      </p>

      <div className="mt-8">
        {first.status === 'loading' && <RunRowsSkeleton rows={6} />}
        {first.status === 'error' && (
          <ErrorState message={first.error.message} onRetry={first.retry} />
        )}
        {first.status === 'success' &&
          (runs.length ? (
            <>
              <RunRows runs={runs} />
              <div className="mt-6 flex flex-col items-center gap-3">
                <p className="tabular text-sm text-ink-muted">
                  Showing {runs.length} of {total}
                </p>
                {runs.length < total && (
                  <button
                    type="button"
                    onClick={loadMore}
                    disabled={loadingMore}
                    className={buttonSecondary}
                  >
                    {loadingMore && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
                    Load more
                  </button>
                )}
              </div>
            </>
          ) : (
            <EmptyState
              icon={<FolderOpen className="size-5" aria-hidden="true" />}
              title="No shortlists yet"
            >
              <TextLink to="/">Rank your first set of resumes</TextLink>
            </EmptyState>
          ))}
      </div>
    </div>
  )
}
