import { defineConfig, loadEnv } from 'vite'
import { resolve } from 'path'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],

    build: {
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html'),
          redirect: resolve(__dirname, 'redirect.html'),
        },
      },
    },

    server: {
      proxy: {
        '/mcp': {
          target:
            'https://tbbd-hr-copilot.loyaltrademanagement.com',
          changeOrigin: true,
          secure: true,
        },

        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
