import { BaseApi } from './base/BaseApi'
import type {
  Session,
  CreateSessionRequest,
  UpdateCodeRequest,
  UpdateLanguageRequest
} from './types'

/**
 * API class for managing interview sessions
 */
export class SessionsApi extends BaseApi {
  private readonly basePath = '/api/sessions'

  /**
   * Create a new interview session
   */
  async createSession(request: CreateSessionRequest): Promise<Session> {
    return this.post<Session>(this.basePath, request)
  }

  /**
   * Get session by ID
   */
  async getSession(sessionId: string): Promise<Session> {
    return this.get<Session>(`${this.basePath}/${sessionId}`)
  }

  /**
   * Update code in session
   */
  async updateCode(sessionId: string, request: UpdateCodeRequest): Promise<Session> {
    return this.put<Session>(`${this.basePath}/${sessionId}/code`, request)
  }

  /**
   * Update language in session
   */
  async updateLanguage(sessionId: string, request: UpdateLanguageRequest): Promise<Session> {
    return this.put<Session>(`${this.basePath}/${sessionId}/language`, request)
  }

  /**
   * Delete session
   */
  async deleteSession(sessionId: string): Promise<void> {
    return this.delete<void>(`${this.basePath}/${sessionId}`)
  }

  /**
   * Get all sessions (if needed in the future)
   */
  async getAllSessions(): Promise<Session[]> {
    return this.get<Session[]>(this.basePath)
  }
}
