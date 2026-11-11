import { ArrowLeft, Download, Plus, Sparkles, Users } from 'lucide-react'
import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  CategoryBadge,
  EmptyState,
  ErrorState,
  ScoreMeter,
  Skeleton,
  SkillChips,
  buttonPrimary,
  buttonSecondary,
} from '../components/ui'
import { ApiError, api } from '../lib/api'
import { candidateLabel, formatDate, formatScore, plural } from '../lib/format'
import type { CandidateResult, Run } from '../lib/types'
import { useAsync } from '../lib/useAsync'
import { NotFoundPage } from './NotFound'

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="min-w-0 px-3 py-3 sm:px-5 sm:py-4">
      <dt className="text-xs font-semibold tracking-wide text-ink-muted uppercase">{label}</dt>
      <dd className="tabular mt-1 font-mono text-xl font-semibold sm:text-2xl">{value}</dd>
      {hint && <dd className="mt-0.5 line-clamp-2 text-xs text-ink-muted sm:truncate">{hint}</dd>}
    </div>
  )
}

function CandidateCard({ result, showSummary }: { result: CandidateResult; showSummary: boolean }) {
  const hasSignals = result.education.length > 0 || result.experience.length > 0
  return (
    <li className="rounded-lg border border-line bg-surface shadow-card">
      <article
        aria-labelledby={`candidate-${result.rank}`}
        className="grid gap-x-5 p-5 sm:grid-cols-[3.5rem_1fr] sm:p-6"
      >
        <p
          className={`tabular font-mono text-3xl leading-none font-semibold sm:text-4xl ${
            result.rank === 1 ? 'text-brand' : 'text-ink-muted'
          }`}
        >
          <span className="sr-only">Rank {result.rank}</span>
          <span aria-hidden="true">{String(result.rank).padStart(2, '0')}</span>
        </p>
        <div className="mt-3 min-w-0 sm:mt-0">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            <h3
              id={`candidate-${result.rank}`}
              className="min-w-0 text-lg font-semibold break-words"
            >
              {candidateLabel(result.filename)}
            </h3>
            <CategoryBadge category={result.category} />
          </div>
          <p className="mt-0.5 truncate text-xs text-ink-muted" title={result.filename}>
            {result.filename}
          </p>

          <div className="mt-4">
            <span className="sr-only">Match score {formatScore(result.score)} out of 100</span>
            <ScoreMeter score={result.score} category={result.category} />
          </div>

          {showSummary && (
            <div className="mt-5 rounded-md border-l-4 border-accent/70 bg-accent-soft/60 px-4 py-3">
              <p className="flex items-center gap-1.5 text-xs font-semibold tracking-wide text-accent uppercase">
                <Sparkles className="size-3.5" aria-hidden="true" /> AI fit summary
              </p>
              <p className="mt-1.5 text-sm leading-relaxed">
                {result.summary ?? (
                  <span className="text-ink-muted">
                    No AI summary for this candidate. The score and skills below are unaffected.
                  </span>
                )}
              </p>
            </div>
          )}

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div>
              <h4 className="mb-2 text-sm font-semibold">
                Matched skills{' '}
                <span className="tabular font-normal text-ink-muted">
                  ({result.matched_skills.length})
                </span>
              </h4>
              <SkillChips
                skills={result.matched_skills}
                variant="matched"
                empty="None of the role's skills appear in this resume."
              />
            </div>
            <div>
              <h4 className="mb-2 text-sm font-semibold">
                Missing skills{' '}
                <span className="tabular font-normal text-ink-muted">
                  ({result.missing_skills.length})
                </span>
              </h4>
              <SkillChips
                skills={result.missing_skills}
                variant="missing"
                empty="Covers every skill the role asks for."
              />
            </div>
          </div>

          {hasSignals && (
            <details className="group mt-5 border-t border-line pt-4">
              <summary className="cursor-pointer rounded-sm py-1.5 text-sm font-semibold text-brand select-none hover:underline">
                Education and experience signals
              </summary>
              <div className="mt-3 grid gap-4 text-sm md:grid-cols-2">
                {(
                  [
                    ['Education', result.education],
                    ['Experience', result.experience],
                  ] as const
                ).map(([label, items]) => (
                  <div key={label}>
                    <h5 className="font-semibold">{label}</h5>
                    {items.length ? (
                      <ul className="mt-1.5 list-disc space-y-1 pl-5 text-ink-muted">
                        {items.slice(0, 6).map((item) => (
                          <li key={item} className="break-words">
                            {item}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="mt-1.5 text-ink-muted">No signals found.</p>
                    )}
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      </article>
    </li>
  )
}

function RunView({ run }: { run: Run }) {
  const scores = run.results.map((r) => r.score)
  const avg = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null
  const top = run.results[0]
  const hasSummaries = run.results.some((r) => r.summary)

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
      <Link
        to="/history"
        className="inline-flex min-h-9 items-center gap-1.5 rounded-sm text-sm font-semibold text-ink-muted hover:text-ink"
      >
        <ArrowLeft className="size-4" aria-hidden="true" /> All shortlists
      </Link>

      <div className="mt-3 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
        <div className="min-w-0">
          <h1 className="text-3xl font-bold tracking-tight break-words sm:text-4xl">{run.title}</h1>
          <p className="mt-2 text-sm text-ink-muted">
            {formatDate(run.created_at)} · {plural(run.results.length, 'resume')} ·{' '}
            {run.method === 'tfidf' ? 'TF-IDF match' : 'Semantic match'}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <a href={api.csvUrl(run.id)} className={buttonSecondary} download>
            <Download className="size-4" aria-hidden="true" /> Export CSV
          </a>
          <Link to="/" className={buttonPrimary}>
            <Plus className="size-4" aria-hidden="true" /> New screening
          </Link>
        </div>
      </div>

      <dl className="mt-8 grid grid-cols-3 divide-x divide-line rounded-lg border border-line bg-surface shadow-card">
        <Stat
          label="Top match"
          value={formatScore(top?.score)}
          hint={top ? candidateLabel(top.filename) : undefined}
        />
        <Stat
          label="Average score"
          value={formatScore(avg)}
          hint={`across ${plural(scores.length, 'resume')}`}
        />
        <Stat
          label="Skills required"
          value={String(run.job_skills.length)}
          hint={`${run.skill_coverage.matched} matched · ${run.skill_coverage.missing} missing`}
        />
      </dl>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_20rem]">
        <section aria-labelledby="ranking-heading" className="order-2 lg:order-1">
          <h2 id="ranking-heading" className="text-xl font-semibold">
            Ranked candidates
          </h2>
          {run.results.length > 0 && !hasSummaries && (
            <p className="mt-2 flex items-start gap-1.5 text-sm text-ink-muted">
              <Sparkles className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden="true" />
              AI fit summaries were unavailable for this run. Match scores and skills are
              unaffected.
            </p>
          )}
          {run.results.length ? (
            <ol className="mt-4 space-y-4">
              {run.results.map((result) => (
                <CandidateCard key={result.rank} result={result} showSummary={hasSummaries} />
              ))}
            </ol>
          ) : (
            <div className="mt-4">
              <EmptyState
                icon={<Users className="size-5" aria-hidden="true" />}
                title="No candidates"
              >
                This run has no stored results. Start a new screening to rank resumes again.
              </EmptyState>
            </div>
          )}
        </section>

        <aside className="order-1 space-y-6 lg:order-2" aria-label="Job details">
          <div className="rounded-lg border border-line bg-surface p-5">
            <h2 className="text-base font-semibold">Skills this role asks for</h2>
            <div className="mt-3">
              <SkillChips
                skills={run.job_skills}
                variant="neutral"
                empty="No tracked skills were detected in this job description, so ranking relies on the semantic score."
              />
            </div>
          </div>
          <details className="rounded-lg border border-line bg-surface p-5">
            <summary className="cursor-pointer text-base font-semibold select-none">
              Job description
            </summary>
            <p className="mt-3 max-h-96 overflow-y-auto text-sm leading-relaxed whitespace-pre-line text-ink-muted">
              {run.job_description}
            </p>
          </details>
        </aside>
      </div>
    </div>
  )
}

function RunSkeleton() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6" aria-hidden="true">
      <Skeleton className="h-4 w-28" />
      <Skeleton className="mt-4 h-9 w-2/3 max-w-md" />
      <Skeleton className="mt-3 h-4 w-1/2 max-w-xs" />
      <Skeleton className="mt-8 h-24 w-full" />
      <div className="mt-6 space-y-4">
        {[0, 1, 2].map((i) => (
          <Skeleton key={i} className="h-56 w-full" />
        ))}
      </div>
    </div>
  )
}

export function RunPage() {
  const { id = '' } = useParams()
  const valid = /^\d+$/.test(id)
  const run = useAsync(
    () => (valid ? api.getRun(id) : Promise.reject(new ApiError('Not found', 404, 'not_found'))),
    [id],
  )

  useEffect(() => {
    if (run.status === 'success') document.title = `${run.data.title} · Shortlister`
    return () => {
      document.title = 'Resume Shortlister · AI resume screening'
    }
  }, [run.status, run.data])

  if (run.status === 'loading')
    return (
      <>
        <p role="status" className="sr-only">
          Loading shortlist
        </p>
        <RunSkeleton />
      </>
    )
  if (run.status === 'error') {
    if (run.error instanceof ApiError && run.error.status === 404)
      return <NotFoundPage what="shortlist" />
    return (
      <div className="mx-auto max-w-xl px-4 py-16">
        <ErrorState message={run.error.message} onRetry={run.retry} />
      </div>
    )
  }
  return <RunView run={run.data} />
}
