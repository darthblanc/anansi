import { useState } from 'react'
import './TopicForm.css'

type Props = {
  onStart: (topic: string) => void
}

export function TopicForm({ onStart }: Props) {
  const [topic, setTopic] = useState('')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (topic.trim()) onStart(topic.trim())
  }

  return (
    <div className="topic-wrap">
      <div className="card topic-card">
        <h1 className="topic-title">What would you like to be quizzed on?</h1>
        <p className="topic-sub">Anansi will generate questions from your knowledge base.</p>
        <form onSubmit={handleSubmit} className="topic-form">
          <input
            type="text"
            className="topic-input"
            placeholder="e.g. multi-agent systems"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            autoFocus
            required
          />
          <button type="submit" className="btn btn-full" disabled={!topic.trim()}>
            Start Quiz
          </button>
        </form>
      </div>
    </div>
  )
}
