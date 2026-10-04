import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

export default function AdministratorDashboard({ onNavigate }) {
  return (
    <>
      <PageHeader
        className="administrator-dashboard-header"
        title="Welcome back, Administrator 👋"
        subtitle="Manage organization, users, permissions, notifications, and system settings."
      />

      <section className="workplace-dashboard-card-grid">

        <DashboardCard title="Organization Management">
          <p>
            Manage organizations, company settings, and business structure.
          </p>

          <button
            className="card-link"
            type="button"
            onClick={() => onNavigate('Organization Management')}
          >
            Manage organizations →
          </button>
        </DashboardCard>


        <DashboardCard title="User Management">
          <p>
            Manage users, invitations, and account access.
          </p>

          <button
            className="card-link"
            type="button"
            onClick={() => onNavigate('User Management')}
          >
            Manage users →
          </button>
        </DashboardCard>


        <DashboardCard title="Roles & Permissions">
          <p>
            Configure security roles and application permissions.
          </p>

          <button
            className="card-link"
            type="button"
            onClick={() => onNavigate('Roles & Permissions')}
          >
            Manage permissions →
          </button>
        </DashboardCard>


        <DashboardCard title="Notification Settings">
          <p>
            Configure email providers, templates, and delivery tracking.
          </p>

          <button
            className="card-link"
            type="button"
            onClick={() => onNavigate('Notification Settings')}
          >
            Configure notifications →
          </button>
        </DashboardCard>


        <DashboardCard title="System Settings">
          <p>
            Manage system configuration, security, integrations, and audit logs.
          </p>

          <button
            className="card-link"
            type="button"
            onClick={() => onNavigate('System Settings')}
          >
            Open settings →
          </button>
        </DashboardCard>

      </section>
    </>
  )
}