import { useState } from 'react'
import type { Question } from '../types'
import './QuizView.css'

const LETTERS = ['A', 'B', 'C', 'D']

type Props = {
  questions: Question[]
  onSubmit: (answers: string[]) => void
}

export function QuizView({ questions, onSubmit }: Props) {
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState<string[]>(Array(questions.length).fill(''))

  function setAnswer(index: number, value: string) {
    setAnswers((prev) => {
      const next = [...prev]
      next[index] = value
      return next
    })
  }

  const allAnswered = answers.every((a) => a.trim() !== '')
  const q = questions[current]
  const isFirst = current === 0
  const isLast = current === questions.length - 1

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (allAnswered) onSubmit(answers)
  }

  return (
    <form onSubmit={handleSubmit} className="quiz-form">
      {/* Bubble nav */}
      <div className="bubbles">
        {questions.map((_, i) => (
          <button
            key={i}
            type="button"
            className={[
              'bubble',
              i === current ? 'bubble-active' : '',
              answers[i].trim() ? 'bubble-answered' : '',
            ].filter(Boolean).join(' ')}
            onClick={() => setCurrent(i)}
            aria-label={`Question ${i + 1}`}
            aria-current={i === current ? 'step' : undefined}
          >
            {i + 1}
          </button>
        ))}
      </div>

      {/* Question */}
      <div className="question-card card">
        <div className="question-label">
          {q.question_type === 'mcq' ? 'Multiple choice' : 'Free answer'}
        </div>
        <p className="question-text">{q.question}</p>

        {q.question_type === 'mcq' && q.options ? (
          <div className="options">
            {q.options.map((opt, j) => (
              <label
                key={j}
                className={`option ${answers[current] === LETTERS[j] ? 'option-selected' : ''}`}
              >
                <input
                  type="radio"
                  name={`q${current}`}
                  value={LETTERS[j]}
                  checked={answers[current] === LETTERS[j]}
                  onChange={() => setAnswer(current, LETTERS[j])}
                />
                <span className="option-letter">{LETTERS[j]}</span>
                <span className="option-text">{opt}</span>
              </label>
            ))}
          </div>
        ) : (
          <textarea
            className="free-input"
            placeholder="Your answer…"
            value={answers[current]}
            onChange={(e) => setAnswer(current, e.target.value)}
            rows={4}
          />
        )}
      </div>

      {/* Navigation */}
      <div className="quiz-nav">
        <button
          type="button"
          className="btn btn-ghost"
          onClick={() => setCurrent((i) => i - 1)}
          disabled={isFirst}
        >
          ← Back
        </button>

        {isLast ? (
          <button type="submit" className="btn" disabled={!allAnswered}>
            Submit Answers
          </button>
        ) : (
          <button
            type="button"
            className="btn"
            onClick={() => setCurrent((i) => i + 1)}
          >
            Next →
          </button>
        )}
      </div>

      {/* Answered counter */}
      <p className="answered-count">
        {answers.filter((a) => a.trim()).length} / {questions.length} answered
      </p>
    </form>
  )
}
