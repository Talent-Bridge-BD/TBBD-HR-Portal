import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  const localCandidateAuth =
    env.TBBD_LOCAL_CANDIDATE_AUTH === 'true'
  const localRole = env.TBBD_LOCAL_ROLE || 'Candidate'

  const localPrincipal =
    localRole === 'Administrator'
      ? {
          auth_typ: 'aad',
          claims: [
            {
              typ: 'http://schemas.microsoft.com/identity/claims/objectidentifier',
              val: 'local-administrator-001',
            },
            {
              typ: 'groups',
              val: '2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66',
            },
            {
              typ: 'name',
              val: 'Local Test Administrator',
            },
            {
              typ: 'preferred_username',
              val: 'administrator@example.test',
            },
          ],
        }
      : {
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

  const encodedLocalPrincipal = Buffer.from(
    JSON.stringify(localPrincipal),
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
                localRole === 'Administrator'
                  ? 'local-administrator-001'
                  : 'local-candidate-001',
              )

              proxyReq.setHeader(
                'X-MS-CLIENT-PRINCIPAL-NAME',
                localRole === 'Administrator'
                  ? 'administrator@example.test'
                  : 'candidate@example.test',
              )

              proxyReq.setHeader(
                'X-MS-CLIENT-PRINCIPAL',
                encodedLocalPrincipal,
              )
            })
          },
        },
      },
    },
  }
})
