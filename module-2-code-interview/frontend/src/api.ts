import { config } from './config'

export interface Session {
  session_id: string
  language: string
  code: string
  created_at?: string
  updated_at?: string
}

const apiBase = config.apiBase

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${apiBase}${path}`
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`)
  }

  return response.json()
}

export const api = {
  createSession(language: string = 'javascript', code: string = ''): Promise<Session> {
    return request('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ language, code }),
    })
  },

  getSession(sessionId: string): Promise<Session> {
    return request(`/api/sessions/${sessionId}`)
  },

  updateCode(sessionId: string, code: string, clientId?: string): Promise<Session> {
    const url = clientId
      ? `/api/sessions/${sessionId}/code?client_id=${clientId}`
      : `/api/sessions/${sessionId}/code`
    return request(url, {
      method: 'PUT',
      body: JSON.stringify({ code }),
    })
  },

  updateLanguage(sessionId: string, language: string, clientId?: string): Promise<Session> {
    const url = clientId
      ? `/api/sessions/${sessionId}/language?client_id=${clientId}`
      : `/api/sessions/${sessionId}/language`
    return request(url, {
      method: 'PUT',
      body: JSON.stringify({ language }),
    })
  },
}
