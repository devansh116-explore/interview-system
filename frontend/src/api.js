const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function handle(response) {
  if (!response.ok) {
    let detail = 'Request failed.'
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch (_) {
      // response wasn't JSON — keep default message
    }
    throw new Error(detail)
  }
  return response.json()
}

export const api = {
  getRoles: () => fetch(`${BASE_URL}/api/roles`).then(handle),

  uploadResume: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return fetch(`${BASE_URL}/api/resume/upload`, {
      method: 'POST',
      body: formData,
    }).then(handle)
  },

  startInterview: (candidateId, role) =>
    fetch(`${BASE_URL}/api/interview/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate_id: candidateId, role }),
    }).then(handle),

  submitAnswer: (sessionId, answerText) =>
    fetch(`${BASE_URL}/api/interview/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, answer_text: answerText }),
    }).then(handle),

  getSummary: (sessionId) =>
    fetch(`${BASE_URL}/api/interview/summary/${sessionId}`).then(handle),
}
