export async function getCurrentUser() {
  const response = await fetch('/api/me', {
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error(`Authentication request failed: ${response.status}`)
  }

  return response.json()
}

export function hasRole(auth, role) {
  return Boolean(auth?.roles?.includes(role))
}
