import { describe, it, expect, beforeEach, vi } from 'vitest'
import { api, type Session } from './api'

describe('API Module', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  describe('createSession', () => {
    it('should create a new session with default values', async () => {
      const mockSession: Session = {
        session_id: 'test123',
        language: 'javascript',
        code: '',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await api.createSession()

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sessions',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          }),
          body: JSON.stringify({ language: 'javascript', code: '' }),
        })
      )
      expect(result).toEqual(mockSession)
    })

    it('should create a session with custom language and code', async () => {
      const mockSession: Session = {
        session_id: 'test456',
        language: 'python',
        code: 'print("hello")',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await api.createSession('python', 'print("hello")')

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sessions',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ language: 'python', code: 'print("hello")' }),
        })
      )
      expect(result).toEqual(mockSession)
    })

    it('should throw error on failed request', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      await expect(api.createSession()).rejects.toThrow('API Error: 500')
    })
  })

  describe('getSession', () => {
    it('should fetch a session by ID', async () => {
      const mockSession: Session = {
        session_id: 'test789',
        language: 'typescript',
        code: 'const x = 1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await api.getSession('test789')

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sessions/test789',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          }),
        })
      )
      expect(result).toEqual(mockSession)
    })

    it('should throw error when session not found', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
      })

      await expect(api.getSession('nonexistent')).rejects.toThrow('API Error: 404')
    })
  })

  describe('updateCode', () => {
    it('should update code without client_id', async () => {
      const mockSession: Session = {
        session_id: 'test123',
        language: 'javascript',
        code: 'console.log("updated")',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:01Z',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await api.updateCode('test123', 'console.log("updated")')

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sessions/test123/code',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ code: 'console.log("updated")' }),
        })
      )
      expect(result).toEqual(mockSession)
    })

    it('should update code with client_id', async () => {
      const mockSession: Session = {
        session_id: 'test123',
        language: 'javascript',
        code: 'console.log("updated")',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:01Z',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await api.updateCode('test123', 'console.log("updated")', 'client-abc')

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sessions/test123/code?client_id=client-abc',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ code: 'console.log("updated")' }),
        })
      )
      expect(result).toEqual(mockSession)
    })
  })

  describe('updateLanguage', () => {
    it('should update language without client_id', async () => {
      const mockSession: Session = {
        session_id: 'test123',
        language: 'python',
        code: '',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:01Z',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await api.updateLanguage('test123', 'python')

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sessions/test123/language',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ language: 'python' }),
        })
      )
      expect(result).toEqual(mockSession)
    })

    it('should update language with client_id', async () => {
      const mockSession: Session = {
        session_id: 'test123',
        language: 'python',
        code: '',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:01Z',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await api.updateLanguage('test123', 'python', 'client-xyz')

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sessions/test123/language?client_id=client-xyz',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ language: 'python' }),
        })
      )
      expect(result).toEqual(mockSession)
    })
  })
})
