import type { QuizConfig, StartResponse, SubmitResponse } from './types'

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`)
  return res.json()
}

export const startQuiz = (topic: string, config: QuizConfig) =>
  post<StartResponse>('/api/quiz/start', {
    topic,
    llm_provider: config.llmProvider,
    llm_api_key: config.llmApiKey,
    embeddings_provider: 'openai',
    embeddings_api_key: config.embeddingsApiKey,
  })

export const submitQuiz = (session_id: string, answers: string[]) =>
  post<SubmitResponse>('/api/quiz/submit', { session_id, answers })
