const isProduction = import.meta.env.PROD;

export const config = {
  apiBase: isProduction
    ? '' // Empty string = same origin (relative URLs)
    : import.meta.env.VITE_API_BASE || 'http://localhost:8000',

  wsUrl: isProduction
    ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`
    : import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
};
