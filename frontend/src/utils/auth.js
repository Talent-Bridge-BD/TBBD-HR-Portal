import {
  InteractionRequiredAuthError,
} from '@azure/msal-browser'

import {
  msalInstance,
  loginRequest,
} from './msal'

import {
  candidateMsalInstance,
  candidateLoginRequest,
} from './candidateMsal'

let candidateInitializationPromise = null

const candidateStartPage = () =>
  `${window.location.origin}/?authMode=candidate`

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

export async function initializeCandidateMsal() {
  if (!candidateInitializationPromise) {
    candidateInitializationPromise = (async () => {
      await candidateMsalInstance.initialize()

      const redirectResult =
        await candidateMsalInstance.handleRedirectPromise()

      if (redirectResult?.account) {
        candidateMsalInstance.setActiveAccount(redirectResult.account)
      }

      const accounts = candidateMsalInstance.getAllAccounts()

      if (
        !candidateMsalInstance.getActiveAccount() &&
        accounts.length === 1
      ) {
        candidateMsalInstance.setActiveAccount(accounts[0])
      }

      return candidateMsalInstance.getActiveAccount()
    })()
  }

  return candidateInitializationPromise
}

export async function signIn() {
  await msalInstance.loginRedirect({
    ...loginRequest,
    prompt: 'select_account',
  })
}

export async function candidateSignIn() {
  await initializeCandidateMsal()

  await candidateMsalInstance.loginRedirect({
    ...candidateLoginRequest,
    prompt: 'select_account',
    redirectStartPage: candidateStartPage(),
  })
}

export async function candidateRegister() {
  await initializeCandidateMsal()

  await candidateMsalInstance.loginRedirect({
    ...candidateLoginRequest,
    prompt: 'create',
    redirectStartPage: candidateStartPage(),
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

export async function getCandidateAccessToken() {
  await initializeCandidateMsal()

  const account = candidateMsalInstance.getActiveAccount()

  if (!account) {
    throw new Error('No authenticated candidate account is available')
  }

  try {
    const result = await candidateMsalInstance.acquireTokenSilent({
      ...candidateLoginRequest,
      account,
    })

    return result.accessToken
  } catch (error) {
    if (error instanceof InteractionRequiredAuthError) {
      await candidateMsalInstance.acquireTokenRedirect({
        ...candidateLoginRequest,
        account,
        redirectStartPage: candidateStartPage(),
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

  if (!accessToken) return null

  return fetchCurrentUser({
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
}

export async function getCandidateCurrentUser() {
  await initializeCandidateMsal()

  if (!candidateMsalInstance.getActiveAccount()) {
    return fetchCurrentUser()
  }

  const accessToken = await getCandidateAccessToken()

  if (!accessToken) return null

  return fetchCurrentUser({
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
}

export async function authenticatedFetch(url, options = {}) {
  const headers = new Headers(options.headers || {})

  const candidateMode =
    import.meta.env.DEV &&
    (
      new URLSearchParams(window.location.search).get('authMode') === 'candidate' ||
      Boolean(candidateMsalInstance.getActiveAccount())
    )

  if (candidateMode) {
    const accessToken = await getCandidateAccessToken()

    if (!accessToken) {
      throw new Error(
        'Candidate authentication is redirecting. Please try again after sign-in completes.'
      )
    }

    headers.set('Authorization', `Bearer ${accessToken}`)
  } else {
    const account = msalInstance.getActiveAccount()

    if (account) {
      const accessToken = await getAccessToken()

      if (!accessToken) {
        throw new Error(
          'Authentication is redirecting. Please try again after sign-in completes.'
        )
      }

      headers.set('Authorization', `Bearer ${accessToken}`)
    }
  }

  return fetch(url, {
    ...options,
    credentials: 'include',
    headers,
  })
}
