import type { Category } from './types'

export function formatDate(iso: string) {
  return new Intl.DateTimeFormat('en', { dateStyle: 'medium', timeStyle: 'short' }).format(
    new Date(iso),
  )
}

export function formatScore(score: number | null | undefined) {
  return score == null ? '–' : score.toFixed(1)
}

/** Drop the extension and tidy separators so file names read like candidate labels. */
export function candidateLabel(filename: string) {
  return (
    filename
      .replace(/\.(pdf|docx)$/i, '')
      .replace(/[_]+/g, ' ')
      .trim() || filename
  )
}

export const methodLabel = (method: string) =>
  method === 'tfidf' ? 'TF-IDF match' : 'Semantic match'

export const categoryStyles: Record<Category, string> = {
  Excellent: 'bg-excellent-soft text-excellent',
  Good: 'bg-good-soft text-good',
  Average: 'bg-average-soft text-average',
  Poor: 'bg-poor-soft text-poor',
}

export const categoryBar: Record<Category, string> = {
  Excellent: 'bg-excellent',
  Good: 'bg-good',
  Average: 'bg-average',
  Poor: 'bg-poor',
}
