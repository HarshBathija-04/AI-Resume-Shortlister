import { FileText, Loader2, Upload, X } from 'lucide-react'
import { useEffect, useId, useRef, useState, type DragEvent, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { ApiError, api } from '../lib/api'
import { MAX_FILES, MAX_JD_CHARS, MIN_JD_CHARS, addFiles, formatBytes } from '../lib/files'
import { buttonPrimary } from './ui'

const STEPS = [
  'Reading resumes',
  'Scoring semantic match',
  'Comparing skills',
  'Writing AI summaries',
]

export function UploadForm() {
  const navigate = useNavigate()
  const ids = { title: useId(), jd: useId(), files: useId(), jdHelp: useId(), filesHelp: useId() }
  const inputRef = useRef<HTMLInputElement>(null)
  const [title, setTitle] = useState('')
  const [jd, setJd] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [dragging, setDragging] = useState(false)
  const [errors, setErrors] = useState<{ jd?: string; files?: string; form?: string }>({})
  const [submitting, setSubmitting] = useState(false)
  const [step, setStep] = useState(0)

  useEffect(() => {
    if (!submitting) return
    const timer = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 2500)
    return () => clearInterval(timer)
  }, [submitting])

  function pick(incoming: File[]) {
    const { accepted, rejected } = addFiles(files, incoming)
    setFiles(accepted)
    if (accepted.length) setErrors((e) => ({ ...e, files: undefined }))
    if (rejected.length)
      toast.error(rejected.length === 1 ? rejected[0] : `${rejected.length} files skipped`, {
        description: rejected.length > 1 ? rejected.join('\n') : undefined,
      })
  }

  function onDrop(event: DragEvent) {
    event.preventDefault()
    setDragging(false)
    pick(Array.from(event.dataTransfer.files))
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    const next: typeof errors = {}
    if (jd.trim().length < MIN_JD_CHARS)
      next.jd = `Paste the job description (at least ${MIN_JD_CHARS} characters).`
    if (!files.length) next.files = 'Add at least one resume (PDF or DOCX).'
    setErrors(next)
    if (next.jd || next.files) return

    const form = new FormData()
    if (title.trim()) form.append('title', title.trim())
    form.append('job_description', jd)
    files.forEach((file) => form.append('resumes', file))

    setStep(0)
    setSubmitting(true)
    try {
      const run = await api.createRun(form)
      toast.success('Shortlist ready', { description: `${run.results.length} resumes ranked.` })
      navigate(`/runs/${run.id}`)
    } catch (err) {
      const apiErr = err instanceof ApiError ? err : null
      const fieldErr = apiErr?.details.find((d) => d.field === 'job_description')
      setErrors({ form: apiErr?.message ?? 'Something went wrong.', jd: fieldErr?.message })
      toast.error(apiErr?.message ?? 'Could not create the shortlist')
      setSubmitting(false)
    }
  }

  const jdLength = jd.trim().length

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      aria-busy={submitting}
      className="rounded-lg border border-line bg-surface p-5 shadow-card sm:p-6"
    >
      <h2 className="text-xl font-semibold">New screening</h2>
      <p className="mt-1 text-sm text-ink-muted">Everything is ranked in a single run.</p>

      <div className="mt-5 space-y-5">
        <div>
          <label htmlFor={ids.title} className="text-sm font-semibold">
            Role title <span className="font-normal text-ink-muted">(optional)</span>
          </label>
          <input
            id={ids.title}
            value={title}
            maxLength={120}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Backend Engineer, Platform team"
            className="mt-1.5 block min-h-11 w-full rounded-md border border-line-strong bg-surface px-3 text-sm placeholder:text-ink-muted/70 focus-visible:border-brand"
          />
        </div>

        <div>
          <div className="flex items-baseline justify-between gap-2">
            <label htmlFor={ids.jd} className="text-sm font-semibold">
              Job description
            </label>
            <span className="tabular text-xs text-ink-muted" aria-hidden="true">
              {jdLength.toLocaleString()} / {MAX_JD_CHARS.toLocaleString()}
            </span>
          </div>
          <textarea
            id={ids.jd}
            value={jd}
            maxLength={MAX_JD_CHARS}
            onChange={(e) => setJd(e.target.value)}
            rows={8}
            required
            aria-invalid={!!errors.jd}
            aria-describedby={ids.jdHelp}
            placeholder="Paste responsibilities, required skills and nice-to-haves…"
            className="mt-1.5 block w-full resize-y rounded-md border border-line-strong bg-surface px-3 py-2.5 text-sm leading-relaxed placeholder:text-ink-muted/70 focus-visible:border-brand aria-invalid:border-poor"
          />
          <p
            id={ids.jdHelp}
            className={`mt-1.5 text-xs ${errors.jd ? 'text-poor' : 'text-ink-muted'}`}
          >
            {errors.jd ?? 'Skills listed here drive the matched / missing analysis.'}
          </p>
        </div>

        <div>
          <span id={ids.files} className="text-sm font-semibold">
            Resumes
          </span>
          <label
            onDragOver={(e) => {
              e.preventDefault()
              setDragging(true)
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            className={`mt-1.5 flex cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed px-4 py-7 text-center transition-colors duration-150 focus-within:border-brand focus-within:bg-brand-soft/50 ${
              dragging
                ? 'border-brand bg-brand-soft'
                : errors.files
                  ? 'border-poor/60 bg-poor-soft/40'
                  : 'border-line-strong bg-paper hover:border-brand/60'
            }`}
          >
            <Upload className="size-6 text-brand" aria-hidden="true" />
            <span className="mt-2 text-sm font-semibold">
              Drop files here or{' '}
              <span className="text-brand underline underline-offset-4">browse</span>
            </span>
            <span className="mt-1 text-xs text-ink-muted">
              PDF or DOCX · up to {MAX_FILES} files · 5 MB each
            </span>
            <input
              ref={inputRef}
              type="file"
              multiple
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              aria-labelledby={ids.files}
              aria-describedby={ids.filesHelp}
              className="sr-only"
              onChange={(e) => {
                pick(Array.from(e.target.files ?? []))
                e.target.value = ''
              }}
            />
          </label>
          <p
            id={ids.filesHelp}
            className={`mt-1.5 text-xs ${errors.files ? 'text-poor' : 'text-ink-muted'}`}
          >
            {errors.files ?? `${files.length} of ${MAX_FILES} added`}
          </p>

          {files.length > 0 && (
            <ul className="mt-3 divide-y divide-line rounded-md border border-line">
              {files.map((file) => (
                <li
                  key={`${file.name}:${file.size}`}
                  className="flex items-center gap-3 py-1.5 pr-1.5 pl-3"
                >
                  <FileText className="size-4 shrink-0 text-ink-muted" aria-hidden="true" />
                  <span className="min-w-0 flex-1 truncate text-sm" title={file.name}>
                    {file.name}
                  </span>
                  <span className="tabular shrink-0 text-xs text-ink-muted">
                    {formatBytes(file.size)}
                  </span>
                  <button
                    type="button"
                    onClick={() => setFiles((list) => list.filter((f) => f !== file))}
                    aria-label={`Remove ${file.name}`}
                    className="inline-flex size-9 shrink-0 items-center justify-center rounded-md text-ink-muted transition-colors hover:bg-sunken hover:text-ink"
                  >
                    <X className="size-4" aria-hidden="true" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {errors.form && (
        <p role="alert" className="mt-5 rounded-md bg-poor-soft px-3 py-2 text-sm text-poor">
          {errors.form}
        </p>
      )}

      <button type="submit" disabled={submitting} className={`${buttonPrimary} mt-6 w-full`}>
        {submitting ? (
          <>
            <Loader2 className="size-4 animate-spin" aria-hidden="true" /> {STEPS[step]}…
          </>
        ) : (
          'Rank resumes'
        )}
      </button>
      <p role="status" className="sr-only">
        {submitting ? `${STEPS[step]}` : ''}
      </p>
      {submitting && (
        <p className="mt-2 text-center text-xs text-ink-muted">
          This usually takes 10–30 seconds (longer if the server was asleep).
        </p>
      )}
    </form>
  )
}
