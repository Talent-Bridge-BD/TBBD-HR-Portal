import { PublicClientApplication } from '@azure/msal-browser'

const HTTP = 'http' + '://'
const HTTPS = 'https' + '://'

export const CANDIDATE_TENANT_ID =
  'c8573333-aad0-4a28-8e40-c20e17989f61'

export const CANDIDATE_CLIENT_ID =
  'f9ba8736-f7fa-4553-a305-5b187f0c4152'

export const CANDIDATE_API_SCOPE =
  'api://' + CANDIDATE_CLIENT_ID + '/access_as_user'

export const CANDIDATE_REDIRECT_URI =
  import.meta.env.DEV
    ? HTTP + 'localhost:5173/redirect.html'
    : HTTPS + 'portal.talentbridgebd.com/redirect.html'

export const candidateMsalConfig = {
  auth: {
    clientId: CANDIDATE_CLIENT_ID,
    authority:
      HTTPS +
      'tbbdexternal.ciamlogin.com/c8573333-aad0-4a28-8e40-c20e17989f61/',
    knownAuthorities: [
      'tbbdexternal.ciamlogin.com',
      'c8573333-aad0-4a28-8e40-c20e17989f61.ciamlogin.com',
    ],
    redirectUri: CANDIDATE_REDIRECT_URI,
    postLogoutRedirectUri: import.meta.env.DEV
      ? HTTP + 'localhost:5173/?authMode=candidate'
      : HTTPS + 'portal.talentbridgebd.com/?authMode=candidate',
    navigateToLoginRequestUrl: true,
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
}

export const candidateLoginRequest = {
  scopes: [CANDIDATE_API_SCOPE],
}

export const candidateMsalInstance =
  new PublicClientApplication(candidateMsalConfig)
