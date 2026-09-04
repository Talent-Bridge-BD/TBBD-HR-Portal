function getClaim(claims, types) {
  if (!Array.isArray(claims)) return ''

  const normalizedTypes = types.map((type) => type.toLowerCase())

  const match = claims.find((claim) =>
    normalizedTypes.includes(String(claim?.typ || '').toLowerCase())
  )

  return match?.val || ''
}

function getInitials(name) {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0])
      .join('')
      .toUpperCase() || 'E'
  )
}

export async function getAuthenticatedEmployee() {
  try {
    const response = await fetch('/.auth/me', {
      credentials: 'include',
      cache: 'no-store',
    })

    if (!response.ok) {
      throw new Error(`Authentication lookup failed: ${response.status}`)
    }

    const data = await response.json()

    const user = Array.isArray(data)
      ? data[0]
      : data?.clientPrincipal || data

    if (!user) {
      return {
        displayName: 'Employee',
        initials: 'E',
        email: '',
        authenticated: false,
      }
    }

    const claims = user?.claims || user?.user_claims || []

    const claimName = getClaim(claims, [
      'name',
      'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
    ])

    const claimEmail = getClaim(claims, [
      'email',
      'preferred_username',
      'upn',
      'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
    ])

    const userId = user?.user_id || user?.userId || ''

    const email =
      claimEmail ||
      (userId.includes('@') ? userId : '')

    const displayName =
      claimName ||
      user?.userDetails ||
      email ||
      userId ||
      'Employee'

    return {
      displayName,
      initials: getInitials(displayName),
      email,
      authenticated: true,
    }
  } catch (error) {
    console.warn('Unable to load authenticated employee identity.', error)

    const fallbackName = import.meta.env.VITE_EMPLOYEE_NAME || 'Employee'

    return {
      displayName: fallbackName,
      initials: getInitials(fallbackName),
      email: '',
      authenticated: false,
    }
  }
}

export function getEmployeeDisplayName() {
  return import.meta.env.VITE_EMPLOYEE_NAME || 'Employee'
}
