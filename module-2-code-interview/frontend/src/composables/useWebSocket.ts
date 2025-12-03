import { config } from '@/config'

interface WebSocketCallbacks {
  onCodeUpdated?: (data: { sessionId: string; code: string; timestamp: string }) => void
  onLanguageChanged?: (data: { sessionId: string; language: string; timestamp: string }) => void
  onConnected?: (data: { clientId: string }) => void
}

export const useWebSocket = () => {
  let socket: WebSocket | null = null
  let clientId: string | null = null
  let currentSessionId: string | null = null

  const getClientId = () => clientId

  const joinSession = (sessionId: string, callbacks: WebSocketCallbacks) => {
    if (typeof window === 'undefined') return null

    // Close existing connection if any
    if (socket) {
      socket.close()
    }

    currentSessionId = sessionId

    // Build WebSocket URL
    const wsUrl = config.wsUrl || 'ws://localhost:8000'
    const url = `${wsUrl}/ws/${sessionId}`

    socket = new WebSocket(url)

    socket.onopen = () => {
      console.log('WebSocket connected to session:', sessionId)
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        switch (data.event) {
          case 'connected':
            clientId = data.clientId
            if (callbacks.onConnected) {
              callbacks.onConnected(data)
            }
            break
          case 'code.updated':
            if (callbacks.onCodeUpdated) {
              callbacks.onCodeUpdated(data)
            }
            break
          case 'language.changed':
            if (callbacks.onLanguageChanged) {
              callbacks.onLanguageChanged(data)
            }
            break
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    socket.onclose = () => {
      console.log('WebSocket disconnected')
    }

    return socket
  }

  const leaveSession = (sessionId: string) => {
    if (socket && currentSessionId === sessionId) {
      socket.close()
      socket = null
      currentSessionId = null
      clientId = null
    }
  }

  const disconnect = () => {
    if (socket) {
      socket.close()
      socket = null
      currentSessionId = null
      clientId = null
    }
  }

  return {
    joinSession,
    leaveSession,
    disconnect,
    getClientId,
  }
}
