import type { EvaluatedQuestion } from '../types'
import './Results.css'

type Props = {
  finalScore: number
  evaluated: EvaluatedQuestion[]
  onReset: () => void
}

function scoreClass(pct: number) {
  if (pct >= 80) return 'high'
  if (pct >= 50) return 'mid'
  return 'low'
}

function feedbackIcon(pct: number) {
  if (pct === 100) return '✓'
  if (pct === 0)   return '✗'
  return '◐'
}

export function Results({ finalScore, evaluated, onReset }: Props) {
  const pct = Math.round(finalScore * 100)
  const correct = evaluated.filter((q) => Math.round(q.score * 100) === 100).length

  return (
    <div className="results">
      <div className="results-actions no-print">
        <button className="btn btn-ghost" onClick={onReset}>
          Try another topic
        </button>
        <button className="btn" onClick={() => window.print()}>
          ↓ Download
        </button>
      </div>

      <div className="score-card card">
        <div className="score-label">Final Score</div>
        <div className={`score-value ${scoreClass(pct)}`}>{pct}%</div>
        <div className="score-tally">
          {correct} / {evaluated.length} correct
        </div>
      </div>

      {evaluated.map((q, i) => {
        const qPct = Math.round(q.score * 100)
        const cls = scoreClass(qPct)
        return (
          <div key={i} className={`result-card card result-${cls}`}>
            <div className="rc-meta">
              <span className="rc-num">Q{i + 1}</span>
              <span className={`score-badge ${cls}`}>{qPct}%</span>
            </div>

            <p className="rc-question">{q.question}</p>

            <div className="rc-answer">
              <span className="rc-answer-label">Your answer</span>
              <span className="rc-answer-text">{q.user_answer || '—'}</span>
            </div>

            <div className={`rc-feedback rc-feedback-${cls}`}>
              <span className="rc-feedback-icon" aria-hidden="true">
                {feedbackIcon(qPct)}
              </span>
              <p className="rc-feedback-text">{q.feedback}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
