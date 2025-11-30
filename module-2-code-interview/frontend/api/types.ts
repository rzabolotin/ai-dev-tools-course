/**
 * Common types for API
 */

export interface ApiResponse<T = any> {
  data: T
  message?: string
}

export interface ApiError {
  message: string
  code?: string | number
  details?: any
}

export interface RequestConfig {
  headers?: Record<string, string>
  query?: Record<string, any>
  timeout?: number
}

/**
 * Session types
 */
export interface Session {
  session_id: string
  language: string
  code: string
  created_at?: string
  updated_at?: string
}

export interface CreateSessionRequest {
  language?: string
  code?: string
}

export interface UpdateCodeRequest {
  code: string
}

export interface UpdateLanguageRequest {
  language: string
}

/**
 * Health check types
 */
export interface HealthStatus {
  status: string
  timestamp: string
}
