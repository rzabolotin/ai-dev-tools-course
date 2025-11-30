// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss'
  ],

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      wsUrl: process.env.NUXT_PUBLIC_WS_URL || 'ws://localhost:8080',
    }
  },

  app: {
    head: {
      title: 'Code Interview Platform',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Real-time collaborative coding interview platform' }
      ],
    }
  },

  vite: {
    optimizeDeps: {
      include: ['monaco-editor']
    }
  },

  compatibilityDate: '2024-01-01'
})
