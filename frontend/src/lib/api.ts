import type { Run, RunList } from './types'
import { wake } from './wake'

const API_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:5100').replace(/\/+$/, '')

const SLOW_MS = 5000
const TIMEOUT_MS = 120_000

export class ApiError extends Error {
  status: number
  code: string
  details: { field: string; message: string }[]

  constructor(message: string, status: number, code: string, details: ApiError['details'] = []) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

export async function toApiError(res: Response): Promise<ApiError> {
  const body = await res.json().catch(() => null)
  const error = body?.error
  return new ApiError(
    typeof error?.message === 'string' ? error.message : `Request failed (${res.status}).`,
    res.status,
    typeof error?.code === 'string' ? error.code : 'http_error',
    Array.isArray(error?.details) ? error.details : [],
  )
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  detectColdStart = true,
): Promise<T> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS)
  let flagged = false
  const slowTimer = detectColdStart
    ? setTimeout(() => {
        flagged = true
        wake.start()
      }, SLOW_MS)
    : undefined

  try {
    const res = await fetch(`${API_URL}${path}`, { ...init, signal: controller.signal })
    if (!res.ok) throw await toApiError(res)
    return (await res.json()) as T
  } catch (err) {
    if (err instanceof ApiError) throw err
    throw new ApiError(
      controller.signal.aborted
        ? 'The server took too long to respond. Please try again.'
        : 'Could not reach the server. Check your connection and try again.',
      0,
      'network_error',
    )
  } finally {
    clearTimeout(timeout)
    clearTimeout(slowTimer)
    if (flagged) wake.end()
  }
}

export const api = {
  listRuns: (limit = 20, offset = 0) =>
    request<RunList>(`/api/runs?limit=${limit}&offset=${offset}`),
  getRun: (id: number | string) => request<Run>(`/api/runs/${encodeURIComponent(id)}`),
  // Ranking + AI summaries legitimately take a while, so don't treat slowness as a cold start.
  createRun: (form: FormData) => request<Run>('/api/runs', { method: 'POST', body: form }, false),
  csvUrl: (id: number) => `${API_URL}/api/runs/${id}/results.csv`,
}
