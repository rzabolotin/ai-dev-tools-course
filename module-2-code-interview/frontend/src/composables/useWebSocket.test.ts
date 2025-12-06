import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useWebSocket } from './useWebSocket';

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('joinSession', () => {
    it('should create WebSocket connection with correct URL', () => {
      const { joinSession } = useWebSocket();
      const socket = joinSession('test-session-123', {});

      expect(socket).toBeDefined();
      expect(socket?.url).toContain('ws://localhost:8000/ws/test-session-123');
    });

    it('should call onConnected callback when connected event is received', async () => {
      const { joinSession } = useWebSocket();
      const onConnected = vi.fn();
      const socket = joinSession('test-session-123', { onConnected });

      // Wait for connection to establish
      await new Promise((resolve) => setTimeout(resolve, 10));

      // Simulate server sending connected event
      const mockEvent = {
        data: JSON.stringify({ event: 'connected', clientId: 'client-abc-123' }),
      };
      socket?.onmessage?.(mockEvent as MessageEvent);

      expect(onConnected).toHaveBeenCalledWith({
        event: 'connected',
        clientId: 'client-abc-123',
      });
    });

    it('should store clientId when connected event is received', async () => {
      const { joinSession, getClientId } = useWebSocket();
      const socket = joinSession('test-session-123', {});

      await new Promise((resolve) => setTimeout(resolve, 10));

      const mockEvent = {
        data: JSON.stringify({ event: 'connected', clientId: 'client-xyz-456' }),
      };
      socket?.onmessage?.(mockEvent as MessageEvent);

      expect(getClientId()).toBe('client-xyz-456');
    });

    it('should call onCodeUpdated callback when code.updated event is received', async () => {
      const { joinSession } = useWebSocket();
      const onCodeUpdated = vi.fn();
      const socket = joinSession('test-session-123', { onCodeUpdated });

      await new Promise((resolve) => setTimeout(resolve, 10));

      const mockData = {
        event: 'code.updated',
        sessionId: 'test-session-123',
        code: 'console.log("Hello")',
        timestamp: '2024-01-01T00:00:00Z',
      };
      const mockEvent = {
        data: JSON.stringify(mockData),
      };
      socket?.onmessage?.(mockEvent as MessageEvent);

      expect(onCodeUpdated).toHaveBeenCalledWith({
        event: 'code.updated',
        sessionId: 'test-session-123',
        code: 'console.log("Hello")',
        timestamp: '2024-01-01T00:00:00Z',
      });
    });

    it('should call onLanguageChanged callback when language.changed event is received', async () => {
      const { joinSession } = useWebSocket();
      const onLanguageChanged = vi.fn();
      const socket = joinSession('test-session-123', { onLanguageChanged });

      await new Promise((resolve) => setTimeout(resolve, 10));

      const mockData = {
        event: 'language.changed',
        sessionId: 'test-session-123',
        language: 'python',
        timestamp: '2024-01-01T00:00:00Z',
      };
      const mockEvent = {
        data: JSON.stringify(mockData),
      };
      socket?.onmessage?.(mockEvent as MessageEvent);

      expect(onLanguageChanged).toHaveBeenCalledWith({
        event: 'language.changed',
        sessionId: 'test-session-123',
        language: 'python',
        timestamp: '2024-01-01T00:00:00Z',
      });
    });

    it('should handle invalid JSON gracefully', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { joinSession } = useWebSocket();
      const socket = joinSession('test-session-123', {});

      await new Promise((resolve) => setTimeout(resolve, 10));

      const mockEvent = {
        data: 'invalid json {',
      };
      socket?.onmessage?.(mockEvent as MessageEvent);

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to parse WebSocket message:',
        expect.any(Error)
      );

      consoleSpy.mockRestore();
    });

    it('should close existing connection when joining new session', async () => {
      const { joinSession } = useWebSocket();

      const socket1 = joinSession('session-1', {});
      await new Promise((resolve) => setTimeout(resolve, 10));

      const closeSpy = vi.spyOn(socket1 as WebSocket, 'close');

      joinSession('session-2', {});

      expect(closeSpy).toHaveBeenCalled();
    });

    it('should return null in server-side rendering context', () => {
      const originalWindow = global.window;
      // @ts-expect-error - Testing SSR context where window is undefined
      delete global.window;

      const { joinSession } = useWebSocket();
      const socket = joinSession('test-session-123', {});

      expect(socket).toBeNull();

      global.window = originalWindow;
    });
  });

  describe('leaveSession', () => {
    it('should close WebSocket connection for current session', async () => {
      const { joinSession, leaveSession, getClientId } = useWebSocket();

      const socket = joinSession('test-session-123', {});
      await new Promise((resolve) => setTimeout(resolve, 10));

      const mockEvent = {
        data: JSON.stringify({ event: 'connected', clientId: 'client-abc' }),
      };
      socket?.onmessage?.(mockEvent as MessageEvent);

      expect(getClientId()).toBe('client-abc');

      const closeSpy = vi.spyOn(socket as WebSocket, 'close');
      leaveSession('test-session-123');

      expect(closeSpy).toHaveBeenCalled();
      expect(getClientId()).toBeNull();
    });

    it('should not close connection if session ID does not match', async () => {
      const { joinSession, leaveSession } = useWebSocket();

      const socket = joinSession('test-session-123', {});
      await new Promise((resolve) => setTimeout(resolve, 10));

      const closeSpy = vi.spyOn(socket as WebSocket, 'close');
      leaveSession('different-session');

      expect(closeSpy).not.toHaveBeenCalled();
    });
  });

  describe('disconnect', () => {
    it('should close WebSocket connection and reset state', async () => {
      const { joinSession, disconnect, getClientId } = useWebSocket();

      const socket = joinSession('test-session-123', {});
      await new Promise((resolve) => setTimeout(resolve, 10));

      const mockEvent = {
        data: JSON.stringify({ event: 'connected', clientId: 'client-xyz' }),
      };
      socket?.onmessage?.(mockEvent as MessageEvent);

      expect(getClientId()).toBe('client-xyz');

      const closeSpy = vi.spyOn(socket as WebSocket, 'close');
      disconnect();

      expect(closeSpy).toHaveBeenCalled();
      expect(getClientId()).toBeNull();
    });

    it('should handle disconnect when no connection exists', () => {
      const { disconnect } = useWebSocket();

      // Should not throw error
      expect(() => disconnect()).not.toThrow();
    });
  });

  describe('getClientId', () => {
    it('should return null when not connected', () => {
      const { getClientId } = useWebSocket();

      expect(getClientId()).toBeNull();
    });

    it('should return clientId after connection established', async () => {
      const { joinSession, getClientId } = useWebSocket();

      const socket = joinSession('test-session-123', {});
      await new Promise((resolve) => setTimeout(resolve, 10));

      const mockEvent = {
        data: JSON.stringify({ event: 'connected', clientId: 'unique-client-id' }),
      };
      socket?.onmessage?.(mockEvent as MessageEvent);

      expect(getClientId()).toBe('unique-client-id');
    });
  });

  describe('multiple callbacks', () => {
    it('should call multiple callbacks when registered', async () => {
      const { joinSession } = useWebSocket();
      const onConnected = vi.fn();
      const onCodeUpdated = vi.fn();
      const onLanguageChanged = vi.fn();

      const socket = joinSession('test-session-123', {
        onConnected,
        onCodeUpdated,
        onLanguageChanged,
      });

      await new Promise((resolve) => setTimeout(resolve, 10));

      // Test connected event
      socket?.onmessage?.({
        data: JSON.stringify({ event: 'connected', clientId: 'client-1' }),
      } as MessageEvent);
      expect(onConnected).toHaveBeenCalledTimes(1);

      // Test code updated event
      socket?.onmessage?.({
        data: JSON.stringify({
          event: 'code.updated',
          sessionId: 'test-session-123',
          code: 'new code',
          timestamp: '2024-01-01T00:00:00Z',
        }),
      } as MessageEvent);
      expect(onCodeUpdated).toHaveBeenCalledTimes(1);

      // Test language changed event
      socket?.onmessage?.({
        data: JSON.stringify({
          event: 'language.changed',
          sessionId: 'test-session-123',
          language: 'typescript',
          timestamp: '2024-01-01T00:00:01Z',
        }),
      } as MessageEvent);
      expect(onLanguageChanged).toHaveBeenCalledTimes(1);
    });
  });
});
