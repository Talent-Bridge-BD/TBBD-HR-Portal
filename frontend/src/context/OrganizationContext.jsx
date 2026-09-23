import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { authenticatedFetch } from '../utils/auth'

const STORAGE_KEY = 'tbbd.selectedOrganizationId'

const OrganizationContext = createContext(null)

function isAdministrator(auth) {
  return auth?.roles?.includes('Administrator')
}

function isOrganizationScopedRole(auth) {
  return (
    auth?.roles?.includes('HR Manager') ||
    auth?.roles?.includes('Employer Manager')
  )
}

export function OrganizationProvider({ auth, children }) {
  const administrator = isAdministrator(auth)
  const organizationScoped = isOrganizationScopedRole(auth)

  const [availableOrganizations, setAvailableOrganizations] = useState([])
  const [selectedOrganizationId, setSelectedOrganizationIdState] = useState(
    () => window.localStorage.getItem(STORAGE_KEY) || '',
  )
  const [organizationLoading, setOrganizationLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    async function loadOrganizations() {
      if (!auth?.authenticated) {
        if (mounted) {
          setAvailableOrganizations([])
          setOrganizationLoading(false)
        }
        return
      }

      if (administrator) {
        try {
          const response = await authenticatedFetch('/api/organizations')

          if (!response.ok) {
            throw new Error(
              `Organization request failed: ${response.status}`,
            )
          }

          const data = await response.json()

          if (mounted) {
            setAvailableOrganizations(data?.organizations || [])
          }
        } catch (error) {
          console.error('Failed to load organizations:', error)

          if (mounted) {
            setAvailableOrganizations([])
          }
        } finally {
          if (mounted) {
            setOrganizationLoading(false)
          }
        }

        return
      }

      if (organizationScoped) {
        const organizationIds = Array.isArray(auth.organization_ids)
          ? auth.organization_ids
          : []

        const organizations = organizationIds.map((id) => ({
          id,
          name: id,
          status: 'active',
        }))

        if (mounted) {
          setAvailableOrganizations(organizations)
          setOrganizationLoading(false)
        }

        return
      }

      if (mounted) {
        setAvailableOrganizations([])
        setOrganizationLoading(false)
      }
    }

    loadOrganizations()

    return () => {
      mounted = false
    }
  }, [auth, administrator, organizationScoped])

  useEffect(() => {
    if (organizationLoading) {
      return
    }

    if (!availableOrganizations.length) {
      setSelectedOrganizationIdState('')
      window.localStorage.removeItem(STORAGE_KEY)
      return
    }

    const savedOrganizationIsAvailable = availableOrganizations.some(
      (organization) => organization.id === selectedOrganizationId,
    )

    if (savedOrganizationIsAvailable) {
      return
    }

    if (!administrator && availableOrganizations.length === 1) {
      setSelectedOrganizationIdState(availableOrganizations[0].id)
      window.localStorage.setItem(
        STORAGE_KEY,
        availableOrganizations[0].id,
      )
      return
    }

    setSelectedOrganizationIdState('')
    window.localStorage.removeItem(STORAGE_KEY)
  }, [
    administrator,
    availableOrganizations,
    organizationLoading,
    selectedOrganizationId,
  ])

  function setSelectedOrganizationId(organizationId) {
    const isAvailable = availableOrganizations.some(
      (organization) => organization.id === organizationId,
    )

    if (!isAvailable) {
      return
    }

    setSelectedOrganizationIdState(organizationId)
    window.localStorage.setItem(STORAGE_KEY, organizationId)
  }

  const selectedOrganization = useMemo(
    () =>
      availableOrganizations.find(
        (organization) => organization.id === selectedOrganizationId,
      ) || null,
    [availableOrganizations, selectedOrganizationId],
  )

  const requiresOrganizationSelection =
    !organizationLoading &&
    availableOrganizations.length > 0 &&
    !selectedOrganizationId

  const value = useMemo(
    () => ({
      availableOrganizations,
      selectedOrganizationId,
      selectedOrganization,
      organizationLoading,
      requiresOrganizationSelection,
      setSelectedOrganizationId,
    }),
    [
      availableOrganizations,
      selectedOrganizationId,
      selectedOrganization,
      organizationLoading,
      requiresOrganizationSelection,
    ],
  )

  return (
    <OrganizationContext.Provider value={value}>
      {children}
    </OrganizationContext.Provider>
  )
}

export function useOrganization() {
  const context = useContext(OrganizationContext)

  if (!context) {
    throw new Error(
      'useOrganization must be used inside OrganizationProvider',
    )
  }

  return context
}
