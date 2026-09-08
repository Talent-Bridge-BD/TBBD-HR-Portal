import { useEffect, useState } from 'react'
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

  const [profile, setProfile] = useState({
    full_name: name,
    phone: '+8801713007477',
    organization_email: 'admin_tbbd@loyaltrademanagement.com',
  })

  const [isEditing, setIsEditing] = useState(false)
  const [draft, setDraft] = useState(profile)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadProfile() {
      try {
        const response = await fetch('/api/profile', {
          credentials: 'include',
        })

        if (!response.ok) {
          throw new Error('Unable to load profile')
        }

        const data = await response.json()
        const loadedProfile = {
          full_name: data.profile?.full_name || name,
          phone: data.profile?.phone || '+8801713007477',
          organization_email:
            data.profile?.organization_email ||
            'admin_tbbd@loyaltrademanagement.com',
        }

        if (!cancelled) {
          setProfile(loadedProfile)
          setDraft(loadedProfile)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Unable to load profile')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadProfile()

    return () => {
      cancelled = true
    }
  }, [name])

  function openEditor() {
    setDraft(profile)
    setMessage('')
    setError('')
    setIsEditing(true)
  }

  function closeEditor() {
    if (saving) return

    setDraft(profile)
    setMessage('')
    setError('')
    setIsEditing(false)
  }

  function updateDraft(field, value) {
    setDraft((current) => ({
      ...current,
      [field]: value,
    }))
  }

  async function saveProfile(event) {
    event.preventDefault()
    setSaving(true)
    setMessage('')
    setError('')

    try {
      const response = await fetch('/api/profile', {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(draft),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to save profile')
      }

      const savedProfile = {
        full_name: data.profile?.full_name || draft.full_name,
        phone: data.profile?.phone || draft.phone,
        organization_email:
          data.profile?.organization_email || draft.organization_email,
      }

      setProfile(savedProfile)
      setDraft(savedProfile)
      setMessage('Profile updated successfully.')
      setIsEditing(false)
    } catch (err) {
      setError(err.message || 'Unable to save profile')
    } finally {
      setSaving(false)
    }
  }

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

        <button
          className="profile-edit-button"
          type="button"
          onClick={openEditor}
        >
          ✎ Edit Profile
        </button>
      </section>

      {message && (
        <div className="profile-success-message" role="status">
          {message}
        </div>
      )}

      {error && (
        <div className="profile-error-message" role="alert">
          {error}
        </div>
      )}

      <section className="profile-section">
        <div className="profile-section-heading">
          <h2>Personal Information</h2>
          <p>Your contact information</p>
        </div>

        <div className="profile-information-grid">
          <div className="profile-information-item">
            <span>Full Name</span>
            <strong>{loading ? 'Loading...' : profile.full_name}</strong>
          </div>

          <div className="profile-information-item">
            <span>Phone</span>
            <strong>{loading ? 'Loading...' : profile.phone}</strong>
          </div>

          <div className="profile-information-item">
            <span>Primary Email</span>
            <strong>{email}</strong>
          </div>

          <div className="profile-information-item">
            <span>Organization Email</span>
            <strong>
              {loading ? 'Loading...' : profile.organization_email}
            </strong>
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
          <button
            type="button"
            className="profile-action-primary"
            onClick={openEditor}
          >
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

      {isEditing && (
        <div
          className="profile-modal-backdrop"
          role="presentation"
          onMouseDown={closeEditor}
        >
          <div
            className="profile-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="profile-edit-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="profile-modal-header">
              <div>
                <h2 id="profile-edit-title">Edit Profile</h2>
                <p>Update your personal information.</p>
              </div>

              <button
                type="button"
                className="profile-modal-close"
                onClick={closeEditor}
                disabled={saving}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <form onSubmit={saveProfile}>
              <div className="profile-form-field">
                <label htmlFor="profile-full-name">Full Name</label>
                <input
                  id="profile-full-name"
                  type="text"
                  value={draft.full_name}
                  onChange={(event) =>
                    updateDraft('full_name', event.target.value)
                  }
                  required
                />
              </div>

              <div className="profile-form-field">
                <label htmlFor="profile-phone">Phone</label>
                <input
                  id="profile-phone"
                  type="tel"
                  value={draft.phone}
                  onChange={(event) =>
                    updateDraft('phone', event.target.value)
                  }
                />
              </div>

              <div className="profile-form-field">
                <label htmlFor="profile-primary-email">Primary Email</label>
                <input
                  id="profile-primary-email"
                  type="email"
                  value={email}
                  readOnly
                  disabled
                />
                <small>
                  Your primary sign-in email is managed by Microsoft Entra ID.
                </small>
              </div>

              <div className="profile-form-field">
                <label htmlFor="profile-organization-email">
                  Organization Email
                </label>
                <input
                  id="profile-organization-email"
                  type="email"
                  value={draft.organization_email}
                  onChange={(event) =>
                    updateDraft('organization_email', event.target.value)
                  }
                />
              </div>

              {error && (
                <div className="profile-error-message" role="alert">
                  {error}
                </div>
              )}

              <div className="profile-modal-actions">
                <button
                  type="button"
                  className="profile-action-secondary"
                  onClick={closeEditor}
                  disabled={saving}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="profile-action-primary"
                  disabled={saving}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
