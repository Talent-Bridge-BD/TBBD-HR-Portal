import PageHeader from '../components/PageHeader'

const profile = {
  name: 'Moazzem Hossain',
  title: 'Founder & CEO',
  department: 'Management',
  role: 'Administrator',
  employeeId: 'TBBD-EMP-001',
  status: 'Active',
  employmentType: 'Full-time',
  location: 'Dhaka, Bangladesh',
  workEmail: 'admin@talentbridgebd.com',
  secondaryEmail: 'admin_tbbd@loyaltrademanagement.com',
  phone: '+8801713007477',
}

function InfoRow({ label, value, controlled = false, privateField = false }) {
  return (
    <div className="profile-info-row">
      <div className="profile-info-label">{label}</div>
      <div className="profile-info-value">
        <span>{value}</span>
        {controlled && <small>HR controlled</small>}
        {privateField && <small>Private</small>}
      </div>
    </div>
  )
}

export default function MyProfile({ employee }) {
  const displayName = employee?.displayName || profile.name
  const displayEmail = employee?.email || profile.workEmail
  const initials = employee?.initials || 'MH'
  return (
    <>
      <PageHeader
        title="My Profile"
        subtitle="View and manage your employee profile."
      />

      <section className="profile-hero">
        <div className="profile-avatar-large">{initials}</div>

        <div className="profile-hero-content">
          <span className="profile-eyebrow">EMPLOYEE PROFILE</span>
          <h2>{displayName}</h2>
          <p>{profile.title}</p>

          <div className="profile-hero-meta">
            <span>{profile.department}</span>
            <span>{profile.role}</span>
            <span className="profile-status">{profile.status}</span>
          </div>
        </div>
      </section>

      <div className="profile-grid">
        <section className="profile-card">
          <div className="profile-section-heading">
            <span className="section-eyebrow">EMPLOYMENT</span>
            <h2>Work Information</h2>
          </div>

          <div className="profile-info-list">
            <InfoRow label="Employee ID" value={profile.employeeId} controlled />
            <InfoRow label="Job Title" value={profile.title} controlled />
            <InfoRow label="Department" value={profile.department} controlled />
            <InfoRow label="System Role" value={profile.role} controlled />
            <InfoRow label="Work Location" value={profile.location} controlled />
            <InfoRow label="Employment Status" value={profile.status} controlled />
            <InfoRow label="Employment Type" value={profile.employmentType} controlled />
          </div>
        </section>

        <section className="profile-card">
          <div className="profile-section-heading">
            <span className="section-eyebrow">CONTACT</span>
            <h2>Contact Information</h2>
          </div>

          <div className="profile-info-list">
            <div className="profile-info-row">
              <div className="profile-info-label">Work Email</div>
              <div className="profile-info-value">
                <a href={`mailto:${displayEmail}`}>{displayEmail}</a>
                <small>Directory visibility applies</small>
              </div>
            </div>

            <InfoRow
              label="Secondary Email"
              value={profile.secondaryEmail}
            />

            <div className="profile-info-row">
              <div className="profile-info-label">Phone</div>
              <div className="profile-info-value">
                <a href={`tel:${profile.phone.replace(/\s/g, '')}`}>
                  {profile.phone}
                </a>
                <small>Employee editable</small>
              </div>
            </div>
          </div>
        </section>

        <section className="profile-card">
          <div className="profile-section-heading">
            <span className="section-eyebrow">PERSONAL</span>
            <h2>Personal Information</h2>
          </div>

          <div className="profile-private-notice">
            <span className="profile-private-icon">🔒</span>
            <div>
              <strong>Private information</strong>
              <p>
                Personal information is protected and is not displayed in the
                workplace directory.
              </p>
            </div>
          </div>

          <div className="profile-info-list">
            <InfoRow
              label="Emergency Contact"
              value="Private"
              privateField
            />
            <InfoRow
              label="Address"
              value="Private"
              privateField
            />
          </div>
        </section>

        <section className="profile-card">
          <div className="profile-section-heading">
            <span className="section-eyebrow">PROFILE ACTIONS</span>
            <h2>Manage Your Profile</h2>
          </div>

          <div className="profile-actions">
            <button type="button" className="profile-action">
              <span>✎</span>
              <div>
                <strong>Edit Profile</strong>
                <small>Update employee-editable information</small>
              </div>
            </button>

            <button type="button" className="profile-action">
              <span>🔑</span>
              <div>
                <strong>Change Password</strong>
                <small>Update your account password</small>
              </div>
            </button>

            <button type="button" className="profile-action">
              <span>🛡</span>
              <div>
                <strong>Security Settings</strong>
                <small>Review account security</small>
              </div>
            </button>

            <button type="button" className="profile-action">
              <span>▣</span>
              <div>
                <strong>My Documents</strong>
                <small>View your employee documents</small>
              </div>
            </button>
          </div>
        </section>
      </div>

      <section className="profile-directory-card">
        <div>
          <span className="section-eyebrow">DIRECTORY</span>
          <h2>Workplace Directory</h2>
          <p>Information visible to authorized workplace users.</p>
        </div>

        <div className="directory-profile">
          <strong>{displayName}</strong>
          <span>{profile.title} · {profile.department}</span>
          <a href={`mailto:${displayEmail}`}>{displayEmail}</a>
          <span className="profile-status">{profile.status}</span>
        </div>
      </section>
    </>
  )
}
