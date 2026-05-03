export type Question = {
  question: string
  question_type: 'mcq' | 'free'
  options?: string[]
}

export type EvaluatedQuestion = {
  question: string
  question_type: 'mcq' | 'free'
  user_answer: string
  score: number
  feedback: string
}

export type StartResponse = {
  session_id: string
  questions: Question[]
}

export type SubmitResponse = {
  final_score: number
  evaluated: EvaluatedQuestion[]
}
