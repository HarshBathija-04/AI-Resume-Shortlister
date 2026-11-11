import { AlertTriangle, RotateCw } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { categoryBar, categoryStyles, formatScore } from '../lib/format'
import type { Category } from '../lib/types'

export const buttonBase =
  'inline-flex min-h-11 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold transition-[background-color,color,box-shadow,transform] duration-150 ease-out active:scale-[0.97] disabled:pointer-events-none disabled:opacity-60'
export const buttonPrimary = `${buttonBase} bg-brand text-white shadow-sm hover:bg-brand-strong`
export const buttonSecondary = `${buttonBase} border border-line-strong bg-surface text-ink hover:bg-sunken`

export function CategoryBadge({ category }: { category: Category }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${categoryStyles[category]}`}
    >
      {category}
    </span>
  )
}

export function ScoreMeter({ score, category }: { score: number; category: Category }) {
  const width = Math.min(100, Math.max(0, score))
  return (
    <div className="flex items-center gap-3">
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-sunken" aria-hidden="true">
        <div
          className={`h-full rounded-full ${categoryBar[category]}`}
          style={{ width: `${width}%` }}
        />
      </div>
      <span className="tabular w-16 text-right font-mono text-sm font-semibold">
        {formatScore(score)}
        <span className="text-ink-muted">/100</span>
      </span>
    </div>
  )
}

export function SkillChips({
  skills,
  variant,
  empty,
}: {
  skills: string[]
  variant: 'matched' | 'missing' | 'neutral'
  empty: string
}) {
  if (!skills.length) return <p className="text-sm text-ink-muted">{empty}</p>
  const style = {
    matched: 'border-brand/25 bg-brand-soft text-brand-strong',
    missing: 'border-dashed border-poor/50 bg-surface text-poor',
    neutral: 'border-line bg-surface text-ink',
  }[variant]
  return (
    <ul className="flex flex-wrap gap-1.5">
      {skills.map((skill) => (
        <li key={skill} className={`rounded-sm border px-2 py-0.5 text-xs font-medium ${style}`}>
          {variant === 'missing' && <span className="sr-only">Missing: </span>}
          {skill}
        </li>
      ))}
    </ul>
  )
}

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-sunken ${className}`} aria-hidden="true" />
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="rounded-lg border border-poor/30 bg-poor-soft/60 p-6 text-center">
      <AlertTriangle className="mx-auto size-6 text-poor" aria-hidden="true" />
      <p className="mt-3 font-medium text-ink">{message}</p>
      {onRetry && (
        <button type="button" onClick={onRetry} className={`${buttonSecondary} mt-4`}>
          <RotateCw className="size-4" aria-hidden="true" /> Try again
        </button>
      )}
    </div>
  )
}

export function EmptyState({
  icon,
  title,
  children,
}: {
  icon: ReactNode
  title: string
  children?: ReactNode
}) {
  return (
    <div className="rounded-lg border border-dashed border-line-strong bg-surface/60 p-8 text-center">
      <div className="mx-auto flex size-11 items-center justify-center rounded-full bg-brand-soft text-brand">
        {icon}
      </div>
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      {children && <div className="mt-2 text-sm text-ink-muted">{children}</div>}
    </div>
  )
}

export function TextLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <Link
      to={to}
      className="font-semibold text-brand underline-offset-4 hover:underline focus-visible:underline"
    >
      {children}
    </Link>
  )
}
