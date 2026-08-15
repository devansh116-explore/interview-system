import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function RoleSelect({ candidate, onStarted }) {
  const [roles, setRoles] = useState([])
  const [selected, setSelected] = useState(null)
  const [loadingRoles, setLoadingRoles] = useState(true)
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .getRoles()
      .then((data) => {
        setRoles(data)
        if (data.length) setSelected(data[0].role_id)
      })
      .catch((err) => setError(err.message || 'Could not load available roles.'))
      .finally(() => setLoadingRoles(false))
  }, [])

  async function handleStart() {
    if (!selected) return
    setStarting(true)
    setError('')
    try {
      const question = await api.startInterview(candidate.candidate_id, selected)
      onStarted(selected, question)
    } catch (err) {
      setError(err.message || 'Could not start the interview.')
    } finally {
      setStarting(false)
    }
  }

  return (
    <section className="panel">
      <h1 className="panel-title">Choose the role you're interviewing for</h1>
      <p className="panel-subtitle">Questions will be pulled from that role's knowledge base and shaped by what we found on your resume.</p>

      {candidate.extracted_skills?.length > 0 && (
        <div className="skill-chip-row">
          {candidate.extracted_skills.slice(0, 12).map((skill) => (
            <span className="skill-chip" key={skill}>{skill}</span>
          ))}
        </div>
      )}

      {loadingRoles && <p className="muted">Loading roles…</p>}

      <div className="role-grid">
        {roles.map((role) => (
          <button
            key={role.role_id}
            className={`role-card ${selected === role.role_id ? 'selected' : ''}`}
            onClick={() => setSelected(role.role_id)}
          >
            <div className="role-label">{role.label}</div>
            <div className="role-meta">{role.document_count} knowledge documents</div>
          </button>
        ))}
      </div>

      {error && <div className="error-banner">{error}</div>}

      <button className="primary-btn" onClick={handleStart} disabled={!selected || starting}>
        {starting ? 'Preparing your first question…' : 'Begin interview'}
      </button>
    </section>
  )
}
