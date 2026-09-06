import PageHeader from '../components/PageHeader'

export default function MyProfile({ auth }) {
  const name = auth?.user?.name || 'Employee'
  const email = auth?.user?.email || 'Not available'
  const role =
    auth?.roles?.find((item) => item === 'Administrator') ||
    auth?.roles?.find((item) => item === 'HR Manager') ||
    auth?.roles?.find((item) => item === 'Employer Manager') ||
    auth?.roles?.find((item) => item === 'Candidate') ||
    'Employee'
  const initials = name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()

  return (
    <>
      <PageHeader
        title="My Profile"
        subtitle="Your personal and workplace information."
      />

      <section className="profile-hero-card">
        <div className="profile-avatar">{initials}</div>

        <div className="profile-hero-info">
          <div className="profile-name-line">
            <h2>{name}</h2>
            <span className="profile-active-badge">● Active</span>
          </div>
          <p className="profile-job-title">{role}</p>
          <p className="profile-organization">Talent Bridge BD</p>
        </div>

        <button className="profile-edit-button" type="button">
          ✎ Edit Profile
        </button>
      </section>

      <section className="profile-section">
        <div className="profile-section-heading">
          <h2>Personal Information</h2>
          <p>Your contact information</p>
        </div>

        <div className="profile-information-grid">
          <div className="profile-information-item">
            <span>Full Name</span>
            <strong>{name}</strong>
          </div>

          <div className="profile-information-item">
            <span>Phone</span>
            <strong>+8801713007477</strong>
          </div>

          <div className="profile-information-item">
            <span>Primary Email</span>
            <strong>{email}</strong>
          </div>

          <div className="profile-information-item">
            <span>Organization Email</span>
            <strong>admin_tbbd@loyaltrademanagement.com</strong>
          </div>
        </div>
      </section>

      <section className="profile-section">
        <div className="profile-section-heading">
          <h2>Work Information</h2>
          <p>Your workplace details</p>
        </div>

        <div className="profile-information-grid">
          <div className="profile-information-item">
            <span>Role</span>
            <strong>{role}</strong>
          </div>

          <div className="profile-information-item">
            <span>Department</span>
            <strong>Administration / Management</strong>
          </div>

          <div className="profile-information-item">
            <span>Organization</span>
            <strong>Talent Bridge BD</strong>
          </div>

          <div className="profile-information-item">
            <span>Employee Status</span>
            <strong className="profile-status-value">● Active</strong>
          </div>
        </div>
      </section>

      <section className="profile-section">
        <div className="profile-section-heading">
          <h2>Account & Security</h2>
          <p>Your workplace account status</p>
        </div>

        <div className="profile-security-list">
          <div className="profile-security-item">
            <div>
              <span>Microsoft Entra ID</span>
              <small>Identity provider</small>
            </div>
            <strong className="profile-connected-value">● Connected</strong>
          </div>

          <div className="profile-security-item">
            <div>
              <span>Authentication</span>
              <small>Workplace sign-in method</small>
            </div>
            <strong>Microsoft Entra ID</strong>
          </div>

          <div className="profile-security-item">
            <div>
              <span>Account Status</span>
              <small>Current account state</small>
            </div>
            <strong className="profile-status-value">● Active</strong>
          </div>
        </div>
      </section>

      <section className="profile-actions-section">
        <div>
          <h2>Profile Actions</h2>
          <p>Manage your profile and account settings.</p>
        </div>

        <div className="profile-actions">
          <button type="button" className="profile-action-primary">
            ✎ Edit Profile
          </button>
          <button type="button" className="profile-action-secondary">
            ◉ Change Photo
          </button>
          <button type="button" className="profile-action-secondary">
            ⚙ Account & Security
          </button>
        </div>
      </section>
    </>
  )
}
