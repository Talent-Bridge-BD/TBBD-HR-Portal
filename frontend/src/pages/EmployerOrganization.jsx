import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { authenticatedFetch } from '../utils/auth'
import { useOrganization } from '../context/OrganizationContext'

export default function EmployerOrganization() {
  const {
    selectedOrganizationId,
    selectedOrganization,
    organizationLoading,
  } = useOrganization()

  const [organization, setOrganization] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    async function loadOrganization() {
      if (!selectedOrganizationId) {
        if (mounted) {
          setOrganization(null)
          setLoading(false)
        }
        return
      }

      setLoading(true)
      setError('')

      try {
        const response = await authenticatedFetch(
          `/api/organizations/${encodeURIComponent(selectedOrganizationId)}`,
        )

        if (!response.ok) {
          throw new Error(`Organization request failed: ${response.status}`)
        }

        const data = await response.json()

        if (mounted) {
          setOrganization(data?.organization || null)
        }
      } catch (err) {
        console.error('Failed to load organization:', err)

        if (mounted) {
          setOrganization(null)
          setError('Unable to load organization information.')
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    loadOrganization()

    return () => {
      mounted = false
    }
  }, [selectedOrganizationId])

  const displayOrganization =
    organization || selectedOrganization || null

  if (organizationLoading || loading) {
    return (
      <div className="page-container">
        <PageHeader
          title="My Organization"
          description="View your employer organization information."
        />
        <div className="dashboard-card">
          <p>Loading organization information...</p>
        </div>
      </div>
    )
  }

  if (!selectedOrganizationId) {
    return (
      <div className="page-container">
        <PageHeader
          title="My Organization"
          description="View your employer organization information."
        />
        <div className="dashboard-card">
          <h3>No organization selected</h3>
          <p>
            No organization is currently available for your employer account.
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <PageHeader
          title="My Organization"
          description="View your employer organization information."
        />
        <div className="dashboard-card">
          <h3>Unable to load organization</h3>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <PageHeader
        title="My Organization"
        description="View your employer organization information."
      />

      <div className="dashboard-card">
        <div className="section-header">
          <div>
            <h2>{displayOrganization?.name || 'Organization'}</h2>
            <p>Employer organization profile</p>
          </div>

          <span className="status-badge">
            {displayOrganization?.status || 'Active'}
          </span>
        </div>

        <div className="profile-grid">
          <div className="profile-field">
            <span className="profile-field-label">Organization Name</span>
            <strong>
              {displayOrganization?.name || '—'}
            </strong>
          </div>

          <div className="profile-field">
            <span className="profile-field-label">Status</span>
            <strong>
              {displayOrganization?.status || '—'}
            </strong>
          </div>

          <div className="profile-field">
            <span className="profile-field-label">Organization ID</span>
            <strong>
              {displayOrganization?.id || selectedOrganizationId}
            </strong>
          </div>

          <div className="profile-field">
            <span className="profile-field-label">Access Role</span>
            <strong>Employer Manager</strong>
          </div>
        </div>
      </div>
    </div>
  )
}
