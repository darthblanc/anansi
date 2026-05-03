import type { StartResponse, SubmitResponse } from './types'

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`)
  return res.json()
}

export const startQuiz = (topic: string) =>
  post<StartResponse>('/api/quiz/start', { topic })

export const submitQuiz = (session_id: string, answers: string[]) =>
  post<SubmitResponse>('/api/quiz/submit', { session_id, answers })
