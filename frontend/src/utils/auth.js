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
    prompt: 'select_account',
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
      await msalInstance.acquireTokenRedirect({
        ...loginRequest,
        account,
      })

      return null
    }

    throw error
  }
}


async function fetchCurrentUser(options = {}) {
  const response = await fetch('/api/me', {
    ...options,
    credentials: 'include',
  })

  if (response.status === 401) {
    return {
      authenticated: false,
      user: null,
      roles: [],
    }
  }

  if (!response.ok) {
    throw new Error(
      `Authentication request failed: ${response.status}`
    )
  }

  return response.json()
}


export async function getCurrentUser() {
  const account = msalInstance.getActiveAccount()

  if (!account) {
    return fetchCurrentUser()
  }

  const accessToken = await getAccessToken()

  if (!accessToken) {
    return null
  }

  return fetchCurrentUser({
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
}


export async function authenticatedFetch(url, options = {}) {
  const headers = new Headers(options.headers || {})
  const account = msalInstance.getActiveAccount()

  if (account) {
    const accessToken = await getAccessToken()

    if (!accessToken) {
      throw new Error(
        'Authentication is being redirected. Please try again after sign-in completes.'
      )
    }

    headers.set('Authorization', `Bearer ${accessToken}`)
  }

  return fetch(url, {
    ...options,
    credentials: 'include',
    headers,
  })
}
