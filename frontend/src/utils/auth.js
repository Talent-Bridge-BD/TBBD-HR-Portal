import {
  InteractionRequiredAuthError,
} from '@azure/msal-browser'

import {
  msalInstance,
  loginRequest,
} from './msal'


export async function initializeMsal() {
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
  const sessionResponse = await fetch('/api/me', {
    credentials: 'include',
  })

  if (sessionResponse.ok) {
    const sessionUser = await sessionResponse.json()

    if (sessionUser?.authenticated) {
      return sessionUser
    }
  } else if (sessionResponse.status !== 401) {
    throw new Error(
      `Session authentication request failed: ${sessionResponse.status}`
    )
  }

  const accessToken = await getAccessToken()

  if (!accessToken) {
    return null
  }

  const tokenResponse = await fetch('/api/me', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    credentials: 'include',
  })

  if (!tokenResponse.ok) {
    throw new Error(
      `Bearer authentication request failed: ${tokenResponse.status}`
    )
  }

  return tokenResponse.json()
}

export async function authenticatedFetch(url, options = {}) {
  const accessToken = await getAccessToken()

  const headers = new Headers(options.headers || {})

  headers.set(
    'Authorization',
    `Bearer ${accessToken}`
  )

  return fetch(url, {
    ...options,
    credentials: 'include',
    headers,
  })
}