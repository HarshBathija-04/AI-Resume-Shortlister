export const MAX_FILES = 12
export const MAX_FILE_BYTES = 5 * 1024 * 1024
export const MIN_JD_CHARS = 30
export const MAX_JD_CHARS = 20_000

const ALLOWED = ['.pdf', '.docx']

export interface FileCheck {
  accepted: File[]
  rejected: string[]
}

/** Merge newly picked files into the current list, skipping duplicates and invalid files. */
export function addFiles(current: File[], incoming: File[]): FileCheck {
  const accepted = [...current]
  const rejected: string[] = []
  const key = (f: File) => `${f.name}:${f.size}`
  const seen = new Set(current.map(key))

  for (const file of incoming) {
    const name = file.name.toLowerCase()
    if (!ALLOWED.some((ext) => name.endsWith(ext))) {
      rejected.push(`${file.name}: only PDF and DOCX files are supported`)
    } else if (file.size > MAX_FILE_BYTES) {
      rejected.push(`${file.name}: larger than 5 MB`)
    } else if (seen.has(key(file))) {
      continue
    } else if (accepted.length >= MAX_FILES) {
      rejected.push(`${file.name}: a run holds at most ${MAX_FILES} resumes`)
    } else {
      accepted.push(file)
      seen.add(key(file))
    }
  }
  return { accepted, rejected }
}

export function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
