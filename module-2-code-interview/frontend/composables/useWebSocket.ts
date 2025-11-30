import Echo from 'laravel-echo'
import Pusher from 'pusher-js'

declare global {
  interface Window {
    Pusher: any
    Echo: Echo | null
  }
}

export const useWebSocket = () => {
  const config = useRuntimeConfig()

  const initEcho = () => {
    if (process.client && !window.Echo) {
      window.Pusher = Pusher

      window.Echo = new Echo({
        broadcaster: 'reverb',
        key: 'local-key',
        wsHost: 'localhost',
        wsPort: 8080,
        wssPort: 8080,
        forceTLS: false,
        enabledTransports: ['ws', 'wss'],
        disableStats: true,
      })
    }

    return window.Echo
  }

  const joinSession = (
    sessionId: string,
    callbacks: {
      onCodeUpdated?: (data: any) => void
      onLanguageChanged?: (data: any) => void
    }
  ) => {
    const echo = initEcho()
    if (!echo) return null

    const channel = echo.channel(`session.${sessionId}`)

    if (callbacks.onCodeUpdated) {
      channel.listen('code.updated', callbacks.onCodeUpdated)
    }

    if (callbacks.onLanguageChanged) {
      channel.listen('language.changed', callbacks.onLanguageChanged)
    }

    return channel
  }

  const leaveSession = (sessionId: string) => {
    if (window.Echo) {
      window.Echo.leave(`session.${sessionId}`)
    }
  }

  const disconnect = () => {
    if (window.Echo) {
      window.Echo.disconnect()
      window.Echo = null
    }
  }

  return {
    initEcho,
    joinSession,
    leaveSession,
    disconnect,
  }
}
