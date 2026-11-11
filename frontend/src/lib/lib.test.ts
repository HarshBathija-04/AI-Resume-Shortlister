import { describe, expect, it } from 'vitest'
import { toApiError } from './api'
import { MAX_FILES, addFiles } from './files'
import { candidateLabel, formatScore, plural } from './format'

const file = (name: string, size = 1000) => new File([new Uint8Array(size)], name)

describe('addFiles', () => {
  it('accepts pdf/docx and rejects other types and oversize files', () => {
    const big = file('big.pdf', 6 * 1024 * 1024)
    const { accepted, rejected } = addFiles([], [file('a.PDF'), file('b.docx'), file('c.txt'), big])
    expect(accepted.map((f) => f.name)).toEqual(['a.PDF', 'b.docx'])
    expect(rejected).toHaveLength(2)
  })

  it('skips duplicates and enforces the file cap', () => {
    const a = file('a.pdf')
    expect(addFiles([a], [file('a.pdf')]).accepted).toHaveLength(1)
    const many = Array.from({ length: MAX_FILES + 2 }, (_, i) => file(`r${i}.pdf`))
    const result = addFiles([], many)
    expect(result.accepted).toHaveLength(MAX_FILES)
    expect(result.rejected).toHaveLength(2)
  })
})

describe('toApiError', () => {
  it('reads the backend error envelope', async () => {
    const res = new Response(
      JSON.stringify({
        error: {
          code: 'validation_error',
          message: 'Bad',
          details: [{ field: 'x', message: 'y' }],
        },
      }),
      { status: 400 },
    )
    const err = await toApiError(res)
    expect(err).toMatchObject({ status: 400, code: 'validation_error', message: 'Bad' })
    expect(err.details).toHaveLength(1)
  })

  it('falls back when the body is not JSON', async () => {
    const err = await toApiError(new Response('<html>', { status: 502 }))
    expect(err).toMatchObject({ status: 502, code: 'http_error', message: 'Request failed (502).' })
  })
})

describe('format helpers', () => {
  it('formats scores and candidate labels', () => {
    expect(formatScore(81.816)).toBe('81.8')
    expect(formatScore(null)).toBe('–')
    expect(candidateLabel('jane_doe_cv.pdf')).toBe('jane doe cv')
    expect(plural(1, 'resume')).toBe('1 resume')
    expect(plural(3, 'resume')).toBe('3 resumes')
  })
})
