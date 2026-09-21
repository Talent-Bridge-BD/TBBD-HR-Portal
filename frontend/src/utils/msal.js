import { PublicClientApplication } from '@azure/msal-browser'

const HTTP = 'http' + '://'
const HTTPS = 'https' + '://'

export const TBBD_CLIENT_ID =
  '16835108-56db-49f8-a566-a52bc0691cec'

export const TBBD_TENANT_ID =
  '319c9d59-c5f1-48d3-af49-4f959b5e02c1'

export const TBBD_API_SCOPE =
  'api://' +
  TBBD_CLIENT_ID +
  '/access_as_user'

export const TBBD_REDIRECT_URI =
  import.meta.env.DEV
    ? HTTP + 'localhost:5173/redirect.html'
    : HTTPS + 'portal.talentbridgebd.com/redirect.html'

export const msalConfig = {
  auth: {
    clientId: TBBD_CLIENT_ID,
    authority:
      HTTPS +
      'login.microsoftonline.com/' +
      TBBD_TENANT_ID,
    redirectUri: TBBD_REDIRECT_URI,
    postLogoutRedirectUri:
      import.meta.env.DEV
        ? HTTP + 'localhost:5173'
        : HTTPS + 'portal.talentbridgebd.com',
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
}

export const loginRequest = {
  scopes: [TBBD_API_SCOPE],
}

export const msalInstance =
  new PublicClientApplication(msalConfig)
