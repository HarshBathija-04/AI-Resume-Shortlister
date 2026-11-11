import { History, Loader2, Plus } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import { useServerWaking } from '../lib/wake'

const navClass = ({ isActive }: { isActive: boolean }) =>
  `inline-flex min-h-11 items-center gap-1.5 rounded-md px-3 text-sm font-semibold transition-colors duration-150 ${
    isActive ? 'bg-brand-soft text-brand-strong' : 'text-ink-muted hover:bg-sunken hover:text-ink'
  }`

function Logo() {
  return (
    <span className="flex items-center gap-2.5">
      <svg viewBox="0 0 32 32" className="size-8" aria-hidden="true">
        <rect width="32" height="32" rx="8" fill="var(--color-brand)" />
        <rect x="8" y="8" width="16" height="3" rx="1.5" fill="#f7f5f0" />
        <rect x="8" y="14.5" width="11" height="3" rx="1.5" fill="#f7f5f0" opacity=".8" />
        <rect x="8" y="21" width="6" height="3" rx="1.5" fill="#e8a25a" />
      </svg>
      <span className="font-display text-lg font-bold tracking-tight">Shortlister</span>
    </span>
  )
}

function WakeBanner() {
  const waking = useServerWaking()
  if (!waking) return null
  return (
    <div role="status" className="border-b border-accent/20 bg-accent-soft">
      <p className="mx-auto flex max-w-6xl items-center gap-2 px-4 py-2.5 text-sm text-accent sm:px-6">
        <Loader2 className="size-4 shrink-0 animate-spin" aria-hidden="true" />
        Waking up the server. The free hosting tier sleeps when idle, so the first request can take
        up to a minute.
      </p>
    </div>
  )
}

export function Layout() {
  return (
    <div className="flex min-h-dvh flex-col">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-md focus:bg-surface focus:px-4 focus:py-2 focus:shadow-pop"
      >
        Skip to content
      </a>
      <header className="sticky top-0 z-20 border-b border-line bg-paper/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-2 px-4 py-2 sm:px-6">
          <NavLink to="/" aria-label="Shortlister home" className="rounded-md">
            <Logo />
          </NavLink>
          <nav aria-label="Main" className="flex items-center gap-1">
            <NavLink to="/" end className={navClass}>
              <Plus className="size-4" aria-hidden="true" />
              <span>
                New<span className="hidden sm:inline"> screening</span>
              </span>
            </NavLink>
            <NavLink to="/history" className={navClass}>
              <History className="size-4" aria-hidden="true" />
              History
            </NavLink>
          </nav>
        </div>
      </header>
      <WakeBanner />
      <main id="main" className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-6 text-sm text-ink-muted sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p>Built by Harsh Bathija. Scores are a screening aid, not a hiring decision.</p>
          <a
            href="https://github.com/HarshBathija-04/AI-Resume-Shortlister"
            className="font-semibold text-ink underline-offset-4 hover:underline"
            target="_blank"
            rel="noreferrer"
          >
            Source on GitHub
          </a>
        </div>
      </footer>
    </div>
  )
}
