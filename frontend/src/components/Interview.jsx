import React, { useState } from 'react'
import { api } from '../api.js'

export default function Interview({ initialQuestion, role, onComplete }) {
  const [current, setCurrent] = useState(initialQuestion)
  const [answer, setAnswer] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [showContext, setShowContext] = useState(false)

  async function handleSubmit() {
    if (!answer.trim()) {
      setError('Write an answer before continuing.')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const next = await api.submitAnswer(current.session_id, answer)
      if (next.status === 'completed') {
        onComplete(next.session_id)
        return
      }
      setCurrent(next)
      setAnswer('')
      setShowContext(false)
    } catch (err) {
      setError(err.message || 'Could not submit that answer.')
    } finally {
      setSubmitting(false)
    }
  }

  const progress = Math.round(((current.question_number - 1) / current.total_questions) * 100)

  return (
    <section className="panel interview-panel">
      <div className="progress-row">
        <div className="progress-label">
          Question {current.question_number} of {current.total_questions}
          <span className="role-tag">{role?.replace('_', ' ')}</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <h2 className="question-text">{current.question_text}</h2>

      {current.topic && (
        <button className="context-toggle" onClick={() => setShowContext((v) => !v)}>
          {showContext ? 'Hide' : 'Show'} retrieved source ({current.topic.replace(/_/g, ' ')})
        </button>
      )}

      {showContext && (
        <div className="context-box">
          {current.retrieved_context.map((chunk, idx) => (
            <div className="context-item" key={idx}>
              <div className="context-source">{chunk.source.replace(/_/g, ' ')} · relevance {chunk.score.toFixed(2)}</div>
              <p>{chunk.snippet}…</p>
            </div>
          ))}
        </div>
      )}

      <textarea
        className="answer-box"
        rows={7}
        placeholder="Type your answer here…"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
      />

      {error && <div className="error-banner">{error}</div>}

      <button className="primary-btn" onClick={handleSubmit} disabled={submitting}>
        {submitting
          ? 'Generating next question…'
          : current.question_number === current.total_questions
          ? 'Submit final answer'
          : 'Submit & continue'}
      </button>
    </section>
  )
}
