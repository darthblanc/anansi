import { useState } from 'react'
import { TopicForm } from './components/TopicForm'
import { QuizView } from './components/QuizView'
import { Results } from './components/Results'
import { startQuiz, submitQuiz } from './api'
import type { Question, EvaluatedQuestion } from './types'
import './App.css'

type Stage =
  | { name: 'topic' }
  | { name: 'generating' }
  | { name: 'quiz'; sessionId: string; questions: Question[] }
  | { name: 'evaluating' }
  | { name: 'results'; finalScore: number; evaluated: EvaluatedQuestion[] }

export default function App() {
  const [stage, setStage] = useState<Stage>({ name: 'topic' })
  const [error, setError] = useState<string | null>(null)

  async function handleStart(topic: string) {
    setError(null)
    setStage({ name: 'generating' })
    try {
      const data = await startQuiz(topic)
      setStage({ name: 'quiz', sessionId: data.session_id, questions: data.questions })
    } catch {
      setError('Failed to generate quiz. Check your API key and wiki path.')
      setStage({ name: 'topic' })
    }
  }

  async function handleSubmit(sessionId: string, answers: string[]) {
    setError(null)
    setStage({ name: 'evaluating' })
    try {
      const data = await submitQuiz(sessionId, answers)
      setStage({ name: 'results', finalScore: data.final_score, evaluated: data.evaluated })
    } catch {
      setError('Failed to evaluate answers.')
      setStage({ name: 'topic' })
    }
  }

  return (
    <div className="app">
      <header className="app-header no-print">
        <span className="logo">
          <span className="logo-icon">🕷️</span>
          Anansi
        </span>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {stage.name === 'topic' && (
        <TopicForm onStart={handleStart} />
      )}
      {stage.name === 'generating' && (
        <Spinner message="Generating quiz…" />
      )}
      {stage.name === 'quiz' && (
        <QuizView
          questions={stage.questions}
          onSubmit={(answers) => handleSubmit(stage.sessionId, answers)}
        />
      )}
      {stage.name === 'evaluating' && (
        <Spinner message="Evaluating your answers…" />
      )}
      {stage.name === 'results' && (
        <Results
          finalScore={stage.finalScore}
          evaluated={stage.evaluated}
          onReset={() => setStage({ name: 'topic' })}
        />
      )}
    </div>
  )
}

function Spinner({ message }: { message: string }) {
  return (
    <div className="spinner-wrap">
      <div className="spinner" />
      <p className="spinner-msg">{message}</p>
    </div>
  )
}
