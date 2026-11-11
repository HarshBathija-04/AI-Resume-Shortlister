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
      .replace(/_+/g, ' ')
      .trim() || filename
  )
}

export const plural = (count: number, noun: string) => `${count} ${noun}${count === 1 ? '' : 's'}`
