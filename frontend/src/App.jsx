import React, { useState } from 'react'
import ResumeUpload from './components/ResumeUpload.jsx'
import RoleSelect from './components/RoleSelect.jsx'
import Interview from './components/Interview.jsx'
import Summary from './components/Summary.jsx'

// The whole app is a single explicit state machine over four stages.
// Keeping the current stage as one string (rather than scattering
// booleans) means there is exactly one source of truth for "where the
// candidate is" in the flow, and each stage's data lives right beside
// the stage that produced it.
const STAGES = {
  UPLOAD: 'upload',
  ROLE: 'role',
  INTERVIEW: 'interview',
  SUMMARY: 'summary',
}

export default function App() {
  const [stage, setStage] = useState(STAGES.UPLOAD)
  const [candidate, setCandidate] = useState(null) // { candidate_id, extracted_skills, ... }
  const [role, setRole] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [firstQuestion, setFirstQuestion] = useState(null)

  function handleResumeParsed(candidateData) {
    setCandidate(candidateData)
    setStage(STAGES.ROLE)
  }

  function handleRoleChosen(roleId, questionOut) {
    setRole(roleId)
    setSessionId(questionOut.session_id)
    setFirstQuestion(questionOut)
    setStage(STAGES.INTERVIEW)
  }

  function handleInterviewComplete(finishedSessionId) {
    setSessionId(finishedSessionId)
    setStage(STAGES.SUMMARY)
  }

  function handleRestart() {
    setCandidate(null)
    setRole(null)
    setSessionId(null)
    setStage(STAGES.UPLOAD)
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">◆</span>
          <span className="brand-name">Aptitude</span>
        </div>
        <ol className="stage-track">
          <li className={stage === STAGES.UPLOAD ? 'active' : (stage !== STAGES.UPLOAD ? 'done' : '')}>01 Resume</li>
          <li className={stage === STAGES.ROLE ? 'active' : ([STAGES.INTERVIEW, STAGES.SUMMARY].includes(stage) ? 'done' : '')}>02 Role</li>
          <li className={stage === STAGES.INTERVIEW ? 'active' : (stage === STAGES.SUMMARY ? 'done' : '')}>03 Interview</li>
          <li className={stage === STAGES.SUMMARY ? 'active' : ''}>04 Summary</li>
        </ol>
      </header>

      <main className="app-main">
        {stage === STAGES.UPLOAD && <ResumeUpload onParsed={handleResumeParsed} />}
        {stage === STAGES.ROLE && candidate && (
          <RoleSelect candidate={candidate} onStarted={handleRoleChosen} />
        )}
        {stage === STAGES.INTERVIEW && sessionId && firstQuestion && (
          <Interview
            initialQuestion={firstQuestion}
            role={role}
            onComplete={handleInterviewComplete}
          />
        )}
        {stage === STAGES.SUMMARY && sessionId && (
          <Summary sessionId={sessionId} onRestart={handleRestart} />
        )}
      </main>
    </div>
  )
}
