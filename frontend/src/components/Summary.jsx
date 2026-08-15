import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

const QUALITY_LABEL = { weak: 'Needs depth', adequate: 'Solid', strong: 'Strong' }

export default function Summary({ sessionId, onRestart }) {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .getSummary(sessionId)
      .then(setSummary)
      .catch((err) => setError(err.message || 'Could not load the summary.'))
  }, [sessionId])

  if (error) return <div className="panel"><div className="error-banner">{error}</div></div>
  if (!summary) return <div className="panel"><p className="muted">Loading summary…</p></div>

  const { insights } = summary

  return (
    <section className="panel summary-panel">
      <h1 className="panel-title">Interview summary</h1>
      <p className="panel-subtitle">
        {summary.role.replace(/_/g, ' ')} · {summary.questions_answered}/{summary.total_questions} questions answered
      </p>

      <div className="insight-grid">
        <div className="insight-card">
          <div className="insight-value">{insights.completion_rate}</div>
          <div className="insight-label">Completion</div>
        </div>
        <div className="insight-card">
          <div className="insight-value">{insights.average_answer_length_words}</div>
          <div className="insight-label">Avg. words / answer</div>
        </div>
        <div className="insight-card">
          <div className="insight-value">{insights.topics_covered.length}</div>
          <div className="insight-label">Topics covered</div>
        </div>
        <div className="insight-card">
          <div className="insight-value">{insights.quality_breakdown.strong}</div>
          <div className="insight-label">Strong answers</div>
        </div>
      </div>

      <div className="topics-covered">
        {insights.topics_covered.map((t) => (
          <span className="skill-chip" key={t}>{t.replace(/_/g, ' ')}</span>
        ))}
      </div>

      <div className="qa-list">
        {summary.qa_items.map((item) => (
          <div className="qa-item" key={item.question_number}>
            <div className="qa-item-header">
              <span>Q{item.question_number}</span>
              {item.answer_quality && (
                <span className={`quality-badge ${item.answer_quality}`}>
                  {QUALITY_LABEL[item.answer_quality] || item.answer_quality}
                </span>
              )}
            </div>
            <p className="qa-question">{item.question_text}</p>
            <p className="qa-answer">{item.answer_text || <em>No answer recorded.</em>}</p>
          </div>
        ))}
      </div>

      <button className="primary-btn" onClick={onRestart}>Start a new interview</button>
    </section>
  )
}
