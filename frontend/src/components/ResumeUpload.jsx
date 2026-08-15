import React, { useRef, useState } from 'react'
import { api } from '../api.js'

export default function ResumeUpload({ onParsed }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  function handleFileChange(e) {
    const selected = e.target.files?.[0]
    setError('')
    if (!selected) return
    const ext = selected.name.split('.').pop().toLowerCase()
    if (!['pdf', 'txt'].includes(ext)) {
      setError('Please upload a .pdf or .txt resume.')
      return
    }
    setFile(selected)
  }

  async function handleSubmit() {
    if (!file) {
      setError('Choose a resume file first.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const result = await api.uploadResume(file)
      onParsed(result)
    } catch (err) {
      setError(err.message || 'Could not process that resume.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel">
      <h1 className="panel-title">Start with your resume</h1>
      <p className="panel-subtitle">
        Upload a PDF or plain-text resume. The system reads it to pick topics and set the
        difficulty of the questions you'll get.
      </p>

      <div
        className={`dropzone ${file ? 'has-file' : ''}`}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileChange}
          hidden
        />
        {file ? (
          <div className="dropzone-file">
            <span className="file-icon">📄</span>
            <div>
              <div className="file-name">{file.name}</div>
              <div className="file-hint">Click to choose a different file</div>
            </div>
          </div>
        ) : (
          <div className="dropzone-empty">
            <span className="file-icon">⇧</span>
            <div className="file-name">Drop your resume here, or click to browse</div>
            <div className="file-hint">.pdf or .txt</div>
          </div>
        )}
      </div>

      {error && <div className="error-banner">{error}</div>}

      <button className="primary-btn" onClick={handleSubmit} disabled={loading}>
        {loading ? 'Reading resume…' : 'Continue'}
      </button>
    </section>
  )
}
