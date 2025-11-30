import { SessionsApi, HealthApi } from '~/api'
import type { Session } from '~/api'

/**
 * Composable for API access
 * Provides a convenient interface to API classes
 */
export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  // Initialize API classes
  const sessionsApi = new SessionsApi(apiBase)
  const healthApi = new HealthApi(apiBase)

  // Wrapper methods for backward compatibility
  const createSession = async (language: string = 'javascript', code: string = ''): Promise<Session> => {
    return sessionsApi.createSession({ language, code })
  }

  const getSession = async (sessionId: string): Promise<Session> => {
    return sessionsApi.getSession(sessionId)
  }

  const updateCode = async (sessionId: string, code: string): Promise<Session> => {
    return sessionsApi.updateCode(sessionId, { code })
  }

  const updateLanguage = async (sessionId: string, language: string): Promise<Session> => {
    return sessionsApi.updateLanguage(sessionId, { language })
  }

  return {
    // Direct access to API classes
    sessions: sessionsApi,
    health: healthApi,

    // Backward compatible methods
    createSession,
    getSession,
    updateCode,
    updateLanguage,
  }
}
