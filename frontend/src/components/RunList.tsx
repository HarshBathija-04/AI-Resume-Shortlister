import { ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { candidateLabel, formatDate, formatScore, plural } from '../lib/format'
import type { RunSummary } from '../lib/types'
import { Skeleton } from './ui'

export function RunRows({ runs }: { runs: RunSummary[] }) {
  return (
    <ul className="divide-y divide-line overflow-hidden rounded-lg border border-line bg-surface shadow-card">
      {runs.map((run) => (
        <li key={run.id}>
          <Link
            to={`/runs/${run.id}`}
            className="group grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-1 px-4 py-4 transition-colors duration-150 hover:bg-paper focus-visible:bg-paper focus-visible:outline-offset-[-2px] sm:grid-cols-[1fr_12rem_6rem_auto] sm:px-5"
          >
            <span className="min-w-0">
              <span className="block truncate font-semibold group-hover:text-brand">
                {run.title}
              </span>
              <span className="block text-sm text-ink-muted">
                {formatDate(run.created_at)} · {plural(run.resume_count, 'resume')}
                <span className="sm:hidden"> · best {formatScore(run.top_score)}</span>
              </span>
            </span>
            <span className="hidden min-w-0 text-sm sm:block">
              <span className="block text-xs text-ink-muted">Top candidate</span>
              <span className="block truncate">
                {run.top_candidate ? candidateLabel(run.top_candidate) : '–'}
              </span>
            </span>
            <span className="hidden text-right sm:block">
              <span className="block text-xs text-ink-muted">Best score</span>
              <span className="tabular font-mono font-semibold">{formatScore(run.top_score)}</span>
            </span>
            <ChevronRight
              className="size-5 text-ink-muted transition-transform duration-150 group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Link>
        </li>
      ))}
    </ul>
  )
}

export function RunRowsSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div
      className="divide-y divide-line rounded-lg border border-line bg-surface"
      aria-hidden="true"
    >
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="flex items-center gap-4 px-5 py-4">
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-2/3 max-w-72" />
            <Skeleton className="h-3 w-1/3 max-w-40" />
          </div>
          <Skeleton className="hidden h-8 w-24 sm:block" />
        </div>
      ))}
    </div>
  )
}
