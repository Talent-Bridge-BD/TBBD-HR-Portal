import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  const localCandidateAuth =
    env.TBBD_LOCAL_CANDIDATE_AUTH === 'true'

  const candidatePrincipal = {
    auth_typ: 'aad',
    claims: [
      {
        typ: 'http://schemas.microsoft.com/identity/claims/objectidentifier',
        val: 'local-candidate-001',
      },
      {
        typ: 'groups',
        val: '0869b2d7-2fa1-4c4a-acfd-f5370cf955a6',
      },
      {
        typ: 'name',
        val: 'Local Test Candidate',
      },
      {
        typ: 'preferred_username',
        val: 'candidate@example.test',
      },
    ],
  }

  const encodedCandidatePrincipal = Buffer.from(
    JSON.stringify(candidatePrincipal),
  ).toString('base64')

  return {
    plugins: [react()],

    server: {
      proxy: {
        '/mcp': {
          target: 'https://tbbd-hr-copilot.loyaltrademanagement.com',
          changeOrigin: true,
          secure: true,
        },

        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,

          configure: (proxy) => {
            if (!localCandidateAuth) {
              return
            }

            proxy.on('proxyReq', (proxyReq) => {
              proxyReq.setHeader(
                'X-MS-CLIENT-PRINCIPAL-ID',
                'local-candidate-001',
              )

              proxyReq.setHeader(
                'X-MS-CLIENT-PRINCIPAL-NAME',
                'candidate@example.test',
              )

              proxyReq.setHeader(
                'X-MS-CLIENT-PRINCIPAL',
                encodedCandidatePrincipal,
              )
            })
          },
        },
      },
    },
  }
})
