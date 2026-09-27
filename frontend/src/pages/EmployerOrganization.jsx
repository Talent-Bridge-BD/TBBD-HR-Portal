import PageHeader from '../components/PageHeader'
import { useOrganization } from '../context/OrganizationContext'

export default function EmployerOrganization() {
  const {
    selectedOrganization,
    availableOrganizations,
    organizationLoading,
  } = useOrganization()

  if (organizationLoading) {
    return (
      <section className="page-section">
        <PageHeader
          title="My Organization"
          subtitle="View your organization details."
        />
        <div className="empty-state">
          Loading organization details...
        </div>
      </section>
    )
  }

  if (!selectedOrganization) {
    return (
      <section className="page-section">
        <PageHeader
          title="My Organization"
          subtitle="View your organization details."
        />
        <div className="empty-state">
          <strong>No organization selected</strong>
          <p>
            {availableOrganizations.length
              ? 'Select an organization above to continue.'
              : 'Your account is not currently connected to an active organization.'}
          </p>
        </div>
      </section>
    )
  }

  return (
    <section className="page-section">
      <PageHeader
        title="My Organization"
        subtitle="Organization information and access."
      />

      <div className="dashboard-grid">
        <article className="dashboard-card">
          <div className="dashboard-card-header">
            <div>
              <span className="eyebrow">ORGANIZATION</span>
              <h2>{selectedOrganization.name}</h2>
            </div>
          </div>

          <div className="dashboard-card-body">
            <div className="stat-row">
              <span>Organization ID</span>
              <strong>{selectedOrganization.id}</strong>
            </div>

            <div className="stat-row">
              <span>Status</span>
              <strong>{selectedOrganization.status}</strong>
            </div>
          </div>
        </article>
      </div>
    </section>
  )
}
