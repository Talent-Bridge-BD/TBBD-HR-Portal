import {
  InteractionRequiredAuthError,
} from '@azure/msal-browser'

import {
  msalInstance,
  loginRequest,
} from './msal'


const CANDIDATE_TOKEN_KEY = 'tbbd_candidate_auth_token'

const CANDIDATE_MODE_KEY = 'tbbd_candidate_auth_mode'

function isCandidateMode() {
  return new URLSearchParams(window.location.search).get('authMode') === 'candidate'
    || sessionStorage.getItem(CANDIDATE_MODE_KEY) === 'true'
}

function captureCandidateToken() {
  const fragment = window.location.hash.startsWith('#')
    ? window.location.hash.slice(1)
    : window.location.hash
  const encoded = new URLSearchParams(fragment).get('token')

  if (encoded) {
    try {
      const payload = JSON.parse(encoded)
      if (payload.authenticationToken) {
        sessionStorage.setItem(CANDIDATE_TOKEN_KEY, payload.authenticationToken)
      }
    } catch {
      console.error('Could not parse candidate authentication response.')
    }

    window.history.replaceState(
      null, document.title, window.location.pathname + window.location.search
    )
  }

  return sessionStorage.getItem(CANDIDATE_TOKEN_KEY)
}

export async function initializeMsal() {
  captureCandidateToken()
  await msalInstance.initialize()

  const redirectResult =
    await msalInstance.handleRedirectPromise()

  if (redirectResult?.account) {
    msalInstance.setActiveAccount(redirectResult.account)
  }

  const accounts = msalInstance.getAllAccounts()

  if (!msalInstance.getActiveAccount() && accounts.length === 1) {
    msalInstance.setActiveAccount(accounts[0])
  }

  return msalInstance.getActiveAccount()
}


export async function signIn() {
  await msalInstance.loginRedirect({
    ...loginRequest,
    prompt: "select_account",
  })
}


export async function signOut() {
  await msalInstance.logoutRedirect()
}


export async function getAccessToken() {
  const account = msalInstance.getActiveAccount()

  if (!account) {
    throw new Error('No authenticated Entra account is available')
  }

  try {
    const result = await msalInstance.acquireTokenSilent({
      ...loginRequest,
      account,
    })

    return result.accessToken

  } catch (error) {

    if (error instanceof InteractionRequiredAuthError) {
      await msalInstance.acquireTokenRedirect(loginRequest)
      return null
    }

    throw error
  }
}


export async function getCurrentUser() {
  const response = await authenticatedFetch('/api/me')

  if (!response.ok) {
    throw new Error(`Authentication request failed: ${response.status}`)
  }

  const user = await response.json()

  if (isCandidateMode() &&
      (!user?.authenticated || !user?.roles?.includes('Candidate'))) {
    throw new Error('Candidate session is not authenticated. Please sign in again.')
  }

  return user
}

export async function authenticatedFetch(url, options = {}) {
  const headers = new Headers(options.headers || {})

  if (isCandidateMode()) {
    headers.delete('Authorization')
    headers.delete('X-ZUMO-AUTH')
    return fetch(url, { ...options, credentials: 'include', headers })
  }

  const accessToken = await getAccessToken()
  headers.set('Authorization', `Bearer ${accessToken}`)
  return fetch(url, { ...options, credentials: 'include', headers })
}
