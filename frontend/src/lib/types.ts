export type Category = 'Excellent' | 'Good' | 'Average' | 'Poor'

export interface CandidateResult {
  rank: number
  filename: string
  score: number
  category: Category
  matched_skills: string[]
  missing_skills: string[]
  education: string[]
  experience: string[]
  summary: string | null
}

export interface Run {
  id: number
  title: string
  job_description: string
  method: 'semantic' | 'tfidf'
  job_skills: string[]
  created_at: string
  results: CandidateResult[]
  skill_coverage: { matched: number; missing: number }
}

export interface RunSummary {
  id: number
  title: string
  method: Run['method']
  created_at: string
  resume_count: number
  top_score: number | null
  top_candidate: string | null
}

export interface RunList {
  items: RunSummary[]
  total: number
}
