import { useState } from 'react'
import type { LlmProvider, QuizConfig } from '../types'
import './TopicForm.css'

type Props = {
  onStart: (topic: string, config: QuizConfig) => void
}

const LLM_PROVIDERS: { value: LlmProvider; label: string }[] = [
  { value: 'anthropic', label: 'Anthropic (Claude)' },
  { value: 'openai', label: 'OpenAI (GPT)' },
]

export function TopicForm({ onStart }: Props) {
  const [topic, setTopic] = useState('')
  const [llmProvider, setLlmProvider] = useState<LlmProvider>('anthropic')
  const [llmApiKey, setLlmApiKey] = useState('')
  const [embeddingsApiKey, setEmbeddingsApiKey] = useState('')

  const canSubmit = Boolean(topic.trim() && llmApiKey.trim() && embeddingsApiKey.trim())

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!canSubmit) return
    onStart(topic.trim(), {
      llmProvider,
      llmApiKey: llmApiKey.trim(),
      embeddingsApiKey: embeddingsApiKey.trim(),
    })
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

          <div className="field-group">
            <label className="field-label" htmlFor="llm-provider">Model provider</label>
            <select
              id="llm-provider"
              className="topic-input"
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value as LlmProvider)}
            >
              {LLM_PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
            <input
              type="password"
              className="topic-input"
              placeholder="Your model provider API key"
              value={llmApiKey}
              onChange={(e) => setLlmApiKey(e.target.value)}
              autoComplete="off"
              required
            />
          </div>

          <div className="field-group">
            <label className="field-label">Embeddings provider</label>
            <p className="field-fixed-value">OpenAI</p>
            <input
              type="password"
              className="topic-input"
              placeholder="Your OpenAI API key (used for embeddings)"
              value={embeddingsApiKey}
              onChange={(e) => setEmbeddingsApiKey(e.target.value)}
              autoComplete="off"
              required
            />
          </div>

          <p className="topic-note">
            Your API keys are sent only with this request and are never stored on our servers.
          </p>

          <button type="submit" className="btn btn-full" disabled={!canSubmit}>
            Start Quiz
          </button>
        </form>
      </div>
    </div>
  )
}
