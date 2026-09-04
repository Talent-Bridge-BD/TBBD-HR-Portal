import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/mcp': {
        target: 'https://tbbd-hr-copilot.loyaltrademanagement.com',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
