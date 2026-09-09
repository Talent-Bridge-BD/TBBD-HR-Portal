import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'

const EMPTY_PROFILE = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  professional_title: '',
  summary: '',
  location: '',
  resume_document_id: null,
}

export default function CandidateMyProfile() {
  const [profile, setProfile] = useState(EMPTY_PROFILE)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    let active = true

    async function loadProfile() {
      try {
        setLoading(true)
        setError('')

        const response = await fetch('/api/candidate/profile')

        if (!response.ok) {
          const body = await response.text()
          throw new Error(body || `Unable to load profile (${response.status})`)
        }

        const data = await response.json()

        if (!active) return

        setProfile({
          ...EMPTY_PROFILE,
          ...(data.profile || {}),
        })
      } catch (err) {
        if (active) {
          setError(err.message || 'Unable to load candidate profile.')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadProfile()

    return () => {
      active = false
    }
  }, [])

  function handleChange(event) {
    const { name, value } = event.target

    setProfile((current) => ({
      ...current,
      [name]: value,
    }))

    setMessage('')
    setError('')
  }

  async function handleSubmit(event) {
    event.preventDefault()

    try {
      setSaving(true)
      setError('')
      setMessage('')

      const response = await fetch('/api/candidate/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: profile.first_name.trim(),
          last_name: profile.last_name.trim(),
          email: profile.email.trim(),
          phone: profile.phone.trim(),
          professional_title: profile.professional_title.trim(),
          summary: profile.summary.trim(),
          location: profile.location.trim(),
          resume_document_id: profile.resume_document_id || null,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || data.message || `Unable to save profile (${response.status})`,
        )
      }

      if (data.profile) {
        setProfile({
          ...EMPTY_PROFILE,
          ...data.profile,
        })
      }

      setMessage(data.message || 'Candidate profile saved successfully.')
    } catch (err) {
      setError(err.message || 'Unable to save candidate profile.')
    } finally {
      setSaving(false)
    }
  }

  const initials =
    `${profile.first_name} ${profile.last_name}`
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0])
      .join('')
      .toUpperCase() || 'C'

  if (loading) {
    return (
      <>
        <PageHeader
          title="My Profile"
          subtitle="Manage your candidate profile and recruitment information."
        />

        <section className="dashboard-card">
          <div className="empty-state">
            <strong>Loading candidate profile...</strong>
            <span>Please wait while your profile information is retrieved.</span>
          </div>
        </section>
      </>
    )
  }

  return (
    <>
      <PageHeader
        title="My Profile"
        subtitle="Manage your candidate profile and recruitment information."
      />

      <section className="profile-hero-card">
        <div className="profile-avatar">{initials}</div>

        <div className="profile-hero-info">
          <div className="profile-name-line">
            <h2>
              {`${profile.first_name} ${profile.last_name}`.trim() ||
                'Candidate Profile'}
            </h2>

            <span className="profile-active-badge">
              ● {profile.first_name || profile.last_name ? 'Profile' : 'Setup'}
            </span>
          </div>

          <p className="profile-job-title">
            {profile.professional_title || 'Professional title not added'}
          </p>

          <p className="profile-organization">
            {profile.location || 'Location not added'}
          </p>
        </div>
      </section>

      {error && (
        <section className="dashboard-card">
          <div className="empty-state">
            <strong>Unable to complete the request</strong>
            <span>{error}</span>
          </div>
        </section>
      )}

      {message && !error && (
        <section className="dashboard-card">
          <div className="empty-state">
            <strong>Profile saved</strong>
            <span>{message}</span>
          </div>
        </section>
      )}

      <form onSubmit={handleSubmit}>
        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Personal Information</h2>
            <p>Your contact and personal details.</p>
          </div>

          <div className="profile-information-grid">
            <label className="profile-information-item">
              <span>First Name</span>
              <input
                name="first_name"
                value={profile.first_name}
                onChange={handleChange}
                required
              />
            </label>

            <label className="profile-information-item">
              <span>Last Name</span>
              <input
                name="last_name"
                value={profile.last_name}
                onChange={handleChange}
                required
              />
            </label>

            <label className="profile-information-item">
              <span>Email</span>
              <input
                type="email"
                name="email"
                value={profile.email}
                onChange={handleChange}
                required
              />
            </label>

            <label className="profile-information-item">
              <span>Phone</span>
              <input
                type="tel"
                name="phone"
                value={profile.phone}
                onChange={handleChange}
              />
            </label>

            <label className="profile-information-item">
              <span>Location</span>
              <input
                name="location"
                value={profile.location}
                onChange={handleChange}
                placeholder="City, Country"
              />
            </label>
          </div>
        </section>

        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Professional Profile</h2>
            <p>Your experience, skills, and qualifications.</p>
          </div>

          <div className="profile-information-grid">
            <label className="profile-information-item">
              <span>Professional Title</span>
              <input
                name="professional_title"
                value={profile.professional_title}
                onChange={handleChange}
                placeholder="e.g. Software Engineer"
              />
            </label>
          </div>

          <div className="profile-form-full-width">
            <label className="profile-information-item">
              <span>Professional Summary</span>
              <textarea
                name="summary"
                value={profile.summary}
                onChange={handleChange}
                rows="6"
                placeholder="Briefly describe your professional experience, skills, and qualifications."
              />
            </label>
          </div>
        </section>

        <section className="profile-actions-section">
          <div>
            <h2>Profile Actions</h2>
            <p>
              {profile.first_name || profile.last_name
                ? 'Update your candidate profile information.'
                : 'Complete your candidate profile to continue.'}
            </p>
          </div>

          <div className="profile-actions">
            <button
              type="submit"
              className="profile-action-primary"
              disabled={saving}
            >
              {saving ? 'Saving...' : '✓ Save Profile'}
            </button>
          </div>
        </section>
      </form>
    </>
  )
}
