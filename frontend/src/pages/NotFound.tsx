import { Link } from 'react-router-dom'
import { buttonPrimary } from '../components/ui'

export function NotFoundPage({ what = 'page' }: { what?: string }) {
  return (
    <div className="mx-auto max-w-xl px-4 py-20 text-center">
      <p className="tabular font-mono text-5xl font-semibold text-line-strong">404</p>
      <h1 className="mt-4 text-3xl font-bold">This {what} does not exist</h1>
      <p className="mt-3 text-ink-muted">It may have been removed, or the link is mistyped.</p>
      <Link to="/" className={`${buttonPrimary} mt-8`}>
        Start a new screening
      </Link>
    </div>
  )
}
