import { FolderOpen, ListChecks, ScanSearch, Sparkles } from 'lucide-react'
import { RunRows, RunRowsSkeleton } from '../components/RunList'
import { UploadForm } from '../components/UploadForm'
import { EmptyState, ErrorState, TextLink } from '../components/ui'
import { api } from '../lib/api'
import { useAsync } from '../lib/useAsync'

const FEATURES = [
  {
    icon: ScanSearch,
    title: 'Semantic match score',
    body: 'Each resume is embedded with MiniLM and compared to the role, so related wording still counts.',
  },
  {
    icon: ListChecks,
    title: 'Matched and missing skills',
    body: 'See which required skills each candidate shows, and which gaps to probe in the interview.',
  },
  {
    icon: Sparkles,
    title: 'AI fit summary',
    body: 'A two-sentence read on strongest evidence and biggest gap, generated per candidate.',
  },
]

export function HomePage() {
  const recent = useAsync(() => api.listRuns(3), [])

  return (
    <>
      <section className="mx-auto grid max-w-6xl gap-10 px-4 pt-10 pb-14 sm:px-6 lg:grid-cols-[1fr_minmax(0,30rem)] lg:gap-14 lg:pt-16">
        <div className="lg:pt-6">
          <p className="text-sm font-semibold tracking-wide text-brand uppercase">
            AI resume screening
          </p>
          <h1 className="mt-3 text-4xl leading-[1.08] font-bold tracking-tight sm:text-5xl">
            Rank every resume against the job, in one pass.
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-ink-muted">
            Upload up to 12 resumes and paste the job description. You get a ranked shortlist with a
            match score, a skill-gap breakdown and an AI summary for each candidate.
          </p>

          <ul className="mt-9 space-y-5">
            {FEATURES.map(({ icon: Icon, title, body }) => (
              <li key={title} className="flex gap-4">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-md bg-brand-soft text-brand">
                  <Icon className="size-5" aria-hidden="true" />
                </span>
                <span>
                  <span className="block font-semibold">{title}</span>
                  <span className="block text-sm leading-relaxed text-ink-muted">{body}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>

        <UploadForm />
      </section>

      <section aria-labelledby="recent-heading" className="border-t border-line bg-sunken/50">
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
          <div className="flex items-baseline justify-between gap-4">
            <h2 id="recent-heading" className="text-2xl font-semibold">
              Recent shortlists
            </h2>
            <TextLink to="/history">View all</TextLink>
          </div>
          <div className="mt-5">
            {recent.status === 'loading' && <RunRowsSkeleton />}
            {recent.status === 'error' && (
              <ErrorState message={recent.error.message} onRetry={recent.retry} />
            )}
            {recent.status === 'success' &&
              (recent.data.items.length ? (
                <RunRows runs={recent.data.items} />
              ) : (
                <EmptyState
                  icon={<FolderOpen className="size-5" aria-hidden="true" />}
                  title="No shortlists yet"
                >
                  Your first run will appear here once you rank some resumes.
                </EmptyState>
              ))}
          </div>
        </div>
      </section>
    </>
  )
}
