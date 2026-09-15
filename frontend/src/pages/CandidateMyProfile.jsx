import { useEffect, useMemo, useState } from 'react'

import PageHeader from '../components/PageHeader'

const EMPTY_PROFILE = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  location: '',
  professional_title: '',
  summary: '',
  career_level: '',
  years_experience: '',
  passport_number: '',
  passport_country: '',
  passport_expiry_date: '',
  passport_status: '',
  international_travel_readiness: '',
  resume_document_id: null,
}

const EMPTY_DOCUMENTS = []

const CAREER_LEVELS = [
  'Entry Level',
  'Junior',
  'Mid-Level',
  'Senior',
  'Lead',
  'Manager',
  'Director',
  'Executive',
]

const PASSPORT_STATUSES = [
  'Valid',
  'Expired',
  'Renewal in Progress',
  'Not Available',
]

const TRAVEL_READINESS = [
  'Ready to Travel',
  'Available with Notice',
  'Requires Preparation',
]

const EMPLOYMENT_TYPES = [
  'Full-Time',
  'Part-Time',
  'Contract',
  'Temporary',
]

const WORK_ARRANGEMENTS = [
  'On-site',
  'Hybrid',
  'Remote',
  'Flexible',
]

const CONTACT_METHODS = [
  'Email',
  'Phone',
  'WhatsApp',
]

const PREFERENCE_WORK_ARRANGEMENTS = [
  { value: 'on_site', label: 'On-site' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'remote', label: 'Remote' },
]

const PREFERENCE_CONTACT_METHODS = [
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Phone' },
]

function formatFileSize(bytes) {
  if (!bytes) return 'Size unavailable'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) {
    return `${Math.round(bytes / 1024)} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function maskPassportNumber(value) {
  if (!value) return 'Not added'
  if (value.length <= 4) return '••••'
  return `${'•'.repeat(Math.max(0, value.length - 4))}${value.slice(-4)}`
}

export default function CandidateMyProfile() {
  const [profile, setProfile] = useState(EMPTY_PROFILE)
  const [cityOfResidence, setCityOfResidence] = useState('')
  const [countryOfResidence, setCountryOfResidence] = useState('')
  const [documents, setDocuments] = useState(EMPTY_DOCUMENTS)
  const [experience, setExperience] = useState([])
  const [skills, setSkills] = useState([])
  const [languages, setLanguages] = useState([])
  const [preferences, setPreferences] = useState(null)
  const [preferenceForm, setPreferenceForm] = useState({
    preferred_job_title: '',
    preferred_location: '',
    preferred_employment_type: '',
    work_arrangement: '',
    expected_salary: '',
    currency: '',
    availability_notice_period: '',
    open_to_relocation: false,
    available_for_recruitment: true,
    preferred_contact_method: '',
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [experienceSaving, setExperienceSaving] = useState(false)
  const [editingExperienceId, setEditingExperienceId] = useState(null)
  const [skillsSaving, setSkillsSaving] = useState(false)
  const [editingSkillId, setEditingSkillId] = useState(null)
  const [languagesSaving, setLanguagesSaving] = useState(false)
  const [editingLanguageId, setEditingLanguageId] = useState(null)
  const [preferencesSaving, setPreferencesSaving] = useState(false)
  const [uploadingType, setUploadingType] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    let active = true

    async function loadProfile() {
      try {
        setLoading(true)
        setError('')

        const [
          profileResponse,
          documentsResponse,
          experienceResponse,
          skillsResponse,
          languagesResponse,
          preferencesResponse,
        ] = await Promise.all([
          fetch('/api/candidate/profile'),
          fetch('/api/candidate/documents'),
          fetch('/api/candidate/experience'),
          fetch('/api/candidate/skills'),
          fetch('/api/candidate/languages'),
          fetch('/api/candidate/preferences'),
        ])

        if (!profileResponse.ok) {
          const body = await profileResponse.text()
          throw new Error(
            body || `Unable to load profile (${profileResponse.status})`,
          )
        }

        if (!documentsResponse.ok) {
          const body = await documentsResponse.text()
          throw new Error(
            body || `Unable to load documents (${documentsResponse.status})`,
          )
        }
        if (!experienceResponse.ok) {
          const body = await experienceResponse.text()
          throw new Error(
            body ||
              `Unable to load experience (${experienceResponse.status})`,
          )
        }
        if (!skillsResponse.ok) {
          const body = await skillsResponse.text()
          throw new Error(
            body ||
              `Unable to load skills (${skillsResponse.status})`,
          )
        }

        if (!languagesResponse.ok) {
          const body = await languagesResponse.text()
          throw new Error(
            body ||
              `Unable to load languages (${languagesResponse.status})`,
          )
        }
        if (!preferencesResponse.ok) {
          const body = await preferencesResponse.text()
          throw new Error(
            body ||
              `Unable to load preferences (${preferencesResponse.status})`,
          )
        }
        const profileData = await profileResponse.json()
        const documentsData = await documentsResponse.json()
        const experienceData = await experienceResponse.json()
        const skillsData = await skillsResponse.json()
        const languagesData = await languagesResponse.json()
        const preferencesData = await preferencesResponse.json()

        if (!active) return

        const loadedProfile = {
          ...EMPTY_PROFILE,
          ...(profileData.profile || {}),
        }
        setProfile(loadedProfile)

        const locationParts = (loadedProfile.location || '')
          .split(',')
          .map((part) => part.trim())
          .filter(Boolean)

        setCityOfResidence(locationParts[0] || '')
        setCountryOfResidence(
          locationParts.length > 1
            ? locationParts.slice(1).join(', ')
            : '',
        )

        setDocuments(documentsData.documents || [])
        setExperience(experienceData.experience || [])
        setSkills(Array.isArray(skillsData) ? skillsData : [])
        setLanguages(Array.isArray(languagesData) ? languagesData : [])

        const loadedPreferences = preferencesData.preferences || null
        setPreferences(loadedPreferences)

        if (loadedPreferences) {
          setPreferenceForm({
            preferred_job_title: loadedPreferences.preferred_job_title || '',
            preferred_location: loadedPreferences.preferred_location || '',
            preferred_employment_type:
              loadedPreferences.preferred_employment_type || '',
            work_arrangement: loadedPreferences.work_arrangement || '',
            expected_salary:
              loadedPreferences.expected_salary != null
                ? String(loadedPreferences.expected_salary)
                : '',
            currency: loadedPreferences.currency || '',
            availability_notice_period:
              loadedPreferences.availability_notice_period || '',
            open_to_relocation:
              loadedPreferences.open_to_relocation ?? false,
            available_for_recruitment:
              loadedPreferences.available_for_recruitment ?? true,
            preferred_contact_method:
              loadedPreferences.preferred_contact_method || '',
          })
        }
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
          location: profile.location.trim(),
          professional_title: profile.professional_title.trim(),
          summary: profile.summary.trim(),
          career_level: profile.career_level.trim(),
          years_experience:
            profile.years_experience === ''
              ? null
              : Number(profile.years_experience),
          passport_number: profile.passport_number.trim().toUpperCase(),
          passport_country: profile.passport_country.trim(),
          passport_expiry_date: profile.passport_expiry_date || null,
          passport_status: profile.passport_status.trim(),
          international_travel_readiness:
            profile.international_travel_readiness.trim(),
          resume_document_id: profile.resume_document_id || null,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            `Unable to save profile (${response.status})`,
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

  async function refreshLanguages() {
    const response = await fetch('/api/candidate/languages')

    if (!response.ok) {
      const body = await response.text()
      throw new Error(
        body || `Unable to load languages (${response.status})`,
      )
    }

    const data = await response.json()
    const nextLanguages = Array.isArray(data) ? data : []

    setLanguages(nextLanguages)
    return nextLanguages
  }

  async function saveLanguage() {
    const languageName =
      document.getElementById('language-name')?.value.trim() || ''
    const speakingProficiency =
      document.getElementById('language-speaking')?.value || ''
    const readingProficiency =
      document.getElementById('language-reading')?.value || ''
    const writingProficiency =
      document.getElementById('language-writing')?.value || ''

    if (!languageName) {
      setError('Language name is required.')
      setMessage('')
      return
    }

    setLanguagesSaving(true)
    setError('')
    setMessage('')

    try {
      const url = editingLanguageId
        ? `/api/candidate/languages/${encodeURIComponent(editingLanguageId)}`
        : '/api/candidate/languages'

      const response = await fetch(url, {
        method: editingLanguageId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          language_name: languageName,
          speaking_proficiency: speakingProficiency || null,
          reading_proficiency: readingProficiency || null,
          writing_proficiency: writingProficiency || null,
        }),
      })

      if (!response.ok) {
        const body = await response.text()
        throw new Error(
          body || `Unable to save language (${response.status})`,
        )
      }

      await refreshLanguages()

      document.getElementById('language-name').value = ''
      document.getElementById('language-speaking').value = ''
      document.getElementById('language-reading').value = ''
      document.getElementById('language-writing').value = ''

      setEditingLanguageId(null)
      setMessage(
        editingLanguageId
          ? 'Language updated successfully.'
          : 'Language added successfully.',
      )
    } catch (err) {
      setError(err.message || 'Unable to save language.')
      setMessage('')
    } finally {
      setLanguagesSaving(false)
    }
  }

  async function deleteLanguage(languageId) {
    setLanguagesSaving(true)
    setError('')
    setMessage('')

    try {
      const response = await fetch(
        `/api/candidate/languages/${encodeURIComponent(languageId)}`,
        {
          method: 'DELETE',
        },
      )

      if (!response.ok) {
        const body = await response.text()
        throw new Error(
          body || `Unable to delete language (${response.status})`,
        )
      }

      await refreshLanguages()

      setEditingLanguageId(null)
      setMessage('Language removed successfully.')
    } catch (err) {
      setError(err.message || 'Unable to delete language.')
      setMessage('')
    } finally {
      setLanguagesSaving(false)
    }
  }

  async function refreshSkills() {
    const response = await fetch('/api/candidate/skills')

    if (!response.ok) {
      const body = await response.text()
      throw new Error(
        body || `Unable to load skills (${response.status})`,
      )
    }

    const data = await response.json()
    const nextSkills = Array.isArray(data) ? data : []
    setSkills(nextSkills)
    return nextSkills
  }

  async function saveSkill(skillData) {
    setSkillsSaving(true)
    setError('')
    setMessage('')

    try {
      const url = editingSkillId
        ? `/api/candidate/skills/${encodeURIComponent(editingSkillId)}`
        : '/api/candidate/skills'

      const response = await fetch(url, {
        method: editingSkillId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(skillData),
      })

      if (!response.ok) {
        const body = await response.text()
        throw new Error(
          body || `Unable to save skill (${response.status})`,
        )
      }

      await refreshSkills()
      setEditingSkillId(null)

      setMessage(
        editingSkillId
          ? 'Skill updated successfully.'
          : 'Skill added successfully.',
      )
    } catch (err) {
      setError(err.message || 'Unable to save skill.')
      throw err
    } finally {
      setSkillsSaving(false)
    }
  }

  async function deleteSkill(skillId) {
    if (!window.confirm('Delete this skill?')) {
      return
    }

    setError('')
    setMessage('')

    try {
      const response = await fetch(
        `/api/candidate/skills/${encodeURIComponent(skillId)}`,
        {
          method: 'DELETE',
        },
      )

      if (!response.ok) {
        const body = await response.text()
        throw new Error(
          body || `Unable to delete skill (${response.status})`,
        )
      }

      await refreshSkills()

      if (editingSkillId === skillId) {
        setEditingSkillId(null)
      }

      setMessage('Skill deleted successfully.')
    } catch (err) {
      setError(err.message || 'Unable to delete skill.')
    }
  }

  async function refreshExperience() {
    const response = await fetch('/api/candidate/experience')
    if (!response.ok) {
      const body = await response.text()
      throw new Error(
        body || `Unable to load experience (${response.status})`,
      )
    }
    const data = await response.json()
    setExperience(data.experience || [])
    return data.experience || []
  }

  async function saveExperience(experienceData) {
    try {
      setExperienceSaving(true)
      setError('')
      setMessage('')

      const isEditing = Boolean(editingExperienceId)
      const url = isEditing
        ? `/api/candidate/experience/${encodeURIComponent(
            editingExperienceId,
          )}`
        : '/api/candidate/experience'

      const response = await fetch(url, {
        method: isEditing ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(experienceData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            `Unable to save experience (${response.status})`,
        )
      }

      await refreshExperience()
      setEditingExperienceId(null)
      setMessage(
        data.message ||
          (isEditing
            ? 'Employment experience updated successfully.'
            : 'Employment experience added successfully.'),
      )
      return true
    } catch (err) {
      setError(err.message || 'Unable to save employment experience.')
      return false
    } finally {
      setExperienceSaving(false)
    }
  }

  async function deleteExperience(experienceId) {
    if (!window.confirm('Delete this employment experience?')) {
      return
    }

    try {
      setError('')
      setMessage('')

      const response = await fetch(
        `/api/candidate/experience/${encodeURIComponent(experienceId)}`,
        {
          method: 'DELETE',
        },
      )

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(
          data.detail ||
            data.message ||
            `Unable to delete experience (${response.status})`,
        )
      }

      await refreshExperience()

      if (editingExperienceId === experienceId) {
        setEditingExperienceId(null)
      }

      setMessage('Employment experience deleted successfully.')
    } catch (err) {
      setError(err.message || 'Unable to delete employment experience.')
    }
  }

  async function refreshPreferences() {
    const response = await fetch('/api/candidate/preferences')

    if (!response.ok) {
      const body = await response.text()
      throw new Error(
        body || `Unable to load preferences (${response.status})`,
      )
    }

    const data = await response.json()
    setPreferences(data.preferences || null)
    return data.preferences || null
  }

  async function savePreferences() {
    try {
      setPreferencesSaving(true)
      setError('')
      setMessage('')

      const expectedSalary =
        preferenceForm.expected_salary.trim() === ''
          ? null
          : Number(preferenceForm.expected_salary)

      if (expectedSalary !== null && Number.isNaN(expectedSalary)) {
        throw new Error('Expected salary must be a valid number')
      }

      const response = await fetch('/api/candidate/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          preferred_job_title:
            preferenceForm.preferred_job_title.trim() || null,
          preferred_location:
            preferenceForm.preferred_location.trim() || null,
          preferred_employment_type:
            preferenceForm.preferred_employment_type || null,
          work_arrangement:
            preferenceForm.work_arrangement || null,
          expected_salary: expectedSalary,
          currency:
            preferenceForm.currency.trim() || null,
          availability_notice_period:
            preferenceForm.availability_notice_period.trim() || null,
          open_to_relocation:
            preferenceForm.open_to_relocation,
          available_for_recruitment:
            preferenceForm.available_for_recruitment,
          preferred_contact_method:
            preferenceForm.preferred_contact_method || null,
        }),
      })

      if (!response.ok) {
        const body = await response.text()
        throw new Error(
          body || `Unable to save preferences (${response.status})`,
        )
      }

      const data = await response.json()
      const savedPreferences = data.preferences || null

      setPreferences(savedPreferences)

      if (savedPreferences) {
        setPreferenceForm({
          preferred_job_title:
            savedPreferences.preferred_job_title || '',
          preferred_location:
            savedPreferences.preferred_location || '',
          preferred_employment_type:
            savedPreferences.preferred_employment_type || '',
          work_arrangement:
            savedPreferences.work_arrangement || '',
          expected_salary:
            savedPreferences.expected_salary != null
              ? String(savedPreferences.expected_salary)
              : '',
          currency:
            savedPreferences.currency || '',
          availability_notice_period:
            savedPreferences.availability_notice_period || '',
          open_to_relocation:
            savedPreferences.open_to_relocation ?? false,
          available_for_recruitment:
            savedPreferences.available_for_recruitment ?? true,
          preferred_contact_method:
            savedPreferences.preferred_contact_method || '',
        })
      }

      setMessage('Overseas employment preferences saved successfully.')
    } catch (err) {
      setError(err.message || 'Unable to save overseas employment preferences.')
    } finally {
      setPreferencesSaving(false)
    }
  }

  async function refreshDocuments() {
    const response = await fetch('/api/candidate/documents')

    if (!response.ok) {
      const body = await response.text()
      throw new Error(
        body || `Unable to load documents (${response.status})`,
      )
    }

    const data = await response.json()
    setDocuments(data.documents || [])
    return data.documents || []
  }

  async function handleDocumentUpload(documentType, event) {
    const file = event.target.files?.[0]

    event.target.value = ''

    if (!file) return

    try {
      setUploadingType(documentType)
      setError('')
      setMessage('')

      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(
        `/api/candidate/documents?document_type=${encodeURIComponent(
          documentType,
        )}`,
        {
          method: 'POST',
          body: formData,
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            `Unable to upload ${documentType}.`,
        )
      }

      const updatedDocuments = await refreshDocuments()

      if (documentType === 'resume') {
        setProfile((current) => ({
          ...current,
          resume_document_id: data.document?.id || null,
        }))

        if (!data.document?.id) {
          const resume = updatedDocuments.find(
            (document) => document.document_type === 'resume',
          )

          if (resume) {
            setProfile((current) => ({
              ...current,
              resume_document_id: resume.id,
            }))
          }
        }
      }

      setMessage(
        documentType === 'profile_photo'
          ? 'Profile photo uploaded successfully.'
          : documentType === 'passport'
            ? 'Passport copy uploaded successfully.'
            : 'CV / Resume uploaded successfully.',
      )
    } catch (err) {
      setError(err.message || `Unable to upload ${documentType}.`)
    } finally {
      setUploadingType('')
    }
  }

  async function handleDocumentDelete(document) {
    const label =
      document.document_type === 'profile_photo'
        ? 'profile photo'
        : document.document_type === 'passport'
          ? 'passport copy'
          : 'CV / Resume'

    if (!window.confirm(`Remove your ${label}?`)) {
      return
    }

    try {
      setError('')
      setMessage('')

      const response = await fetch(
        `/api/candidate/documents/${encodeURIComponent(document.id)}`,
        {
          method: 'DELETE',
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            `Unable to remove ${label}.`,
        )
      }

      await refreshDocuments()

      if (document.document_type === 'resume') {
        setProfile((current) => ({
          ...current,
          resume_document_id: null,
        }))
      }

      setMessage(
        document.document_type === 'profile_photo'
          ? 'Profile photo removed successfully.'
          : document.document_type === 'passport'
            ? 'Passport copy removed successfully.'
            : 'CV / Resume removed successfully.',
      )
    } catch (err) {
      setError(err.message || `Unable to remove ${label}.`)
    }
  }

  const profilePhotoDocument = documents.find(
    (document) => document.document_type === 'profile_photo',
  )

  const passportDocument = documents.find(
    (document) => document.document_type === 'passport',
  )

  const resumeDocument = documents.find(
    (document) => document.document_type === 'resume',
  )

  const completionItems = useMemo(
    () => [
      Boolean(profile.first_name.trim()),
      Boolean(profile.last_name.trim()),
      Boolean(profile.email.trim()),
      Boolean(profile.phone.trim()),
      Boolean(profile.location.trim()),
      Boolean(profile.professional_title.trim()),
      Boolean(profile.career_level.trim()),
      profile.years_experience !== '' &&
        profile.years_experience !== null &&
        profile.years_experience !== undefined,
      Boolean(profile.passport_country.trim()),
      Boolean(profile.passport_expiry_date),
      Boolean(profile.passport_status.trim()),
      Boolean(profile.international_travel_readiness.trim()),
      Boolean(resumeDocument),
      Boolean(passportDocument),
      Boolean(profilePhotoDocument),
    ],
    [
      profile,
      resumeDocument,
      passportDocument,
      profilePhotoDocument,
    ],
  )

  const completedItems = completionItems.filter(Boolean).length
  const completionPercent = Math.round(
    (completedItems / completionItems.length) * 100,
  )

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
          subtitle="Manage your candidate profile and overseas recruitment information."
        />
        <section className="dashboard-card">
          <div className="empty-state">
            <strong>Loading candidate profile...</strong>
            <span>
              Please wait while your profile information is retrieved.
            </span>
          </div>
        </section>
      </>
    )
  }

  return (
    <>
      <PageHeader
        title="My Profile"
        subtitle="Manage your candidate profile and overseas recruitment information."
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
              ● {completionPercent === 100 ? 'Complete' : 'In Progress'}
            </span>
          </div>

          <p className="profile-job-title">
            {profile.professional_title || 'Professional title not added'}
          </p>

          <p className="profile-organization">
            {profile.location || 'Country and city not added'}
          </p>
        </div>
      </section>

      <section className="profile-completion-card">
        <div className="profile-completion-heading">
          <div>
            <strong>Profile Completion</strong>
            <span>
              {completedItems} of {completionItems.length} key items completed
            </span>
          </div>
          <strong>{completionPercent}%</strong>
        </div>

        <div className="profile-completion-track">
          <div
            className="profile-completion-bar"
            style={{ width: `${completionPercent}%` }}
          />
        </div>
      </section>

      {error && (
        <div className="profile-error-message" role="alert">
          {error}
        </div>
      )}

      {message && !error && (
        <div className="profile-success-message" role="status">
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Personal Information</h2>
            <p>Your personal contact and current residence information.</p>
          </div>

          <div className="profile-information-grid">
            <label className="profile-form-field">
              <span>First Name</span>
              <input
                name="first_name"
                value={profile.first_name}
                onChange={handleChange}
                required
              />
            </label>

            <label className="profile-form-field">
              <span>Last Name</span>
              <input
                name="last_name"
                value={profile.last_name}
                onChange={handleChange}
                required
              />
            </label>

            <label className="profile-form-field">
              <span>Email</span>
              <input
                type="email"
                name="email"
                value={profile.email}
                onChange={handleChange}
                required
              />
            </label>

            <label className="profile-form-field">
              <span>Phone</span>
              <input
                type="tel"
                name="phone"
                value={profile.phone}
                onChange={handleChange}
                placeholder="+880..."
              />
            </label>

            <label className="profile-form-field">
              <span>City</span>
              <input
                name="city"
                value={cityOfResidence}
                onChange={(event) => {
                  const city = event.target.value
                  setCityOfResidence(city)
                  setProfile((current) => ({
                    ...current,
                    location: countryOfResidence.trim()
                      ? `${city.trim()}, ${countryOfResidence.trim()}`
                      : city.trim(),
                  }))
                  setMessage('')
                  setError('')
                }}
                placeholder="e.g. Dhaka"
              />
            </label>

            <label className="profile-form-field">
              <span>Country of Residence</span>
              <input
                name="country_of_residence"
                value={countryOfResidence}
                onChange={(event) => {
                  const country = event.target.value
                  setCountryOfResidence(country)
                  setProfile((current) => ({
                    ...current,
                    location: cityOfResidence.trim()
                      ? `${cityOfResidence.trim()}, ${country.trim()}`
                      : country.trim(),
                  }))
                  setMessage('')
                  setError('')
                }}
                placeholder="e.g. Bangladesh"
              />
            </label>
          </div>
        </section>

        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Passport & International Travel</h2>
            <p>
              Maintain the passport and international mobility information
              required for overseas recruitment.
            </p>
          </div>

          <div className="profile-information-grid">
            <label className="profile-form-field">
              <span>Passport Number</span>
              <input
                name="passport_number"
                value={profile.passport_number}
                onChange={handleChange}
                placeholder="e.g. A12345678"
                autoComplete="off"
              />
              <small>
                Your passport number is visible only within your own candidate
                profile.
              </small>
            </label>

            <label className="profile-form-field">
              <span>Passport Country</span>
              <input
                name="passport_country"
                value={profile.passport_country}
                onChange={handleChange}
                placeholder="Country that issued your passport"
              />
            </label>

            <label className="profile-form-field">
              <span>Passport Expiry Date</span>
              <input
                type="date"
                name="passport_expiry_date"
                value={profile.passport_expiry_date || ''}
                onChange={handleChange}
              />
            </label>

            <label className="profile-form-field">
              <span>Passport Status</span>
              <select
                name="passport_status"
                value={profile.passport_status}
                onChange={handleChange}
              >
                <option value="">Select status</option>
                {PASSPORT_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>

            <label className="profile-form-field">
              <span>International Travel Readiness</span>
              <select
                name="international_travel_readiness"
                value={profile.international_travel_readiness}
                onChange={handleChange}
              >
                <option value="">Select readiness</option>
                {TRAVEL_READINESS.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>

            <div className="profile-readonly-field">
              <span>Passport Number Preview</span>
              <strong>{maskPassportNumber(profile.passport_number)}</strong>
            </div>
          </div>
        </section>

        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Professional Profile</h2>
            <p>
              Present your professional identity and experience to the TBBD
              recruitment team.
            </p>
          </div>

          <div className="profile-information-grid">
            <label className="profile-form-field">
              <span>Professional Headline</span>
              <input
                name="professional_title"
                value={profile.professional_title}
                onChange={handleChange}
                placeholder="e.g. Senior Mechanical Engineer"
              />
            </label>

            <label className="profile-form-field">
              <span>Career Level</span>
              <select
                name="career_level"
                value={profile.career_level}
                onChange={handleChange}
              >
                <option value="">Select career level</option>
                {CAREER_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {level}
                  </option>
                ))}
              </select>
            </label>

            <label className="profile-form-field">
              <span>Years of Experience</span>
              <input
                type="number"
                name="years_experience"
                value={profile.years_experience ?? ''}
                onChange={handleChange}
                min="0"
                max="60"
                step="0.5"
                placeholder="e.g. 7"
              />
            </label>
          </div>

          <div className="profile-form-full-width">
            <label className="profile-form-field">
              <span>Professional Summary</span>
              <textarea
                name="summary"
                value={profile.summary}
                onChange={handleChange}
                rows="6"
                placeholder="Briefly describe your professional experience, key strengths, qualifications, and international employment goals."
              />
            </label>
          </div>
        </section>

        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Education</h2>
            <p>
              Provide your educational background to help TBBD match you with suitable overseas opportunities.
            </p>
          </div>

          <div className="profile-information-grid">
            <label className="profile-form-field">
              <span>Highest Education</span>
              <input
                type="text"
                name="highest_education"
                placeholder="Bachelor Degree"
              />
            </label>

            <label className="profile-form-field">
              <span>Institution Name</span>
              <input
                type="text"
                name="institution_name"
                placeholder="University / College"
              />
            </label>

            <label className="profile-form-field">
              <span>Field of Study</span>
              <input
                type="text"
                name="field_of_study"
                placeholder="Computer Science"
              />
            </label>

            <label className="profile-form-field">
              <span>Passing Year</span>
              <input
                type="number"
                name="passing_year"
                min="1950"
                max="2100"
              />
            </label>

            <label className="profile-form-field">
              <span>Result / GPA</span>
              <input
                type="text"
                name="gpa_result"
                placeholder="3.75"
              />
            </label>
          </div>
        </section>

        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Trade & Technical Qualifications</h2>
            <p>
              Provide your trade, license and technical qualifications for overseas employment opportunities.
            </p>
          </div>

          <div className="profile-information-grid">

            <label className="profile-form-field">
              <span>Primary Trade</span>
              <input
                type="text"
                placeholder="Electrician"
              />
            </label>

            <label className="profile-form-field">
              <span>Secondary Trade</span>
              <input
                type="text"
                placeholder="HVAC Technician"
              />
            </label>

            <label className="profile-form-field">
              <span>Driving License Available</span>
              <select>
                <option>No</option>
                <option>Yes</option>
              </select>
            </label>

            <label className="profile-form-field">
              <span>License Type</span>
              <input
                type="text"
                placeholder="Heavy Vehicle"
              />
            </label>

            <label className="profile-form-field">
              <span>Trade Certificate</span>
              <input
                type="text"
                placeholder="Electrical Installation Level 2"
              />
            </label>

            <label className="profile-form-field">
              <span>Issuing Authority</span>
              <input
                type="text"
                placeholder="Technical Education Board"
              />
            </label>

            <label className="profile-form-field">
              <span>Training Institute</span>
              <input
                type="text"
                placeholder="Technical Training Centre"
              />
            </label>

            <label className="profile-form-field">
              <span>Completion Year</span>
              <input
                type="number"
                min="1950"
                max="2100"
              />
            </label>

          </div>
        </section>

        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Employment Experience</h2>
            <p>
              Add your professional work history to help TBBD match you with
              suitable overseas opportunities.
            </p>
          </div>

          {experience.length > 0 && (
            <div className="profile-information-grid">
              {experience.map((item) => (
                <div className="profile-document-card" key={item.id}>
                  <div className="profile-document-heading">
                    <div>
                      <h3>{item.job_title}</h3>
                      <p>{item.company}</p>
                    </div>
                    <span className="profile-document-status profile-document-status-ready">
                      {item.currently_working ? 'Current' : 'Previous'}
                    </span>
                  </div>

                  <div className="profile-document-file">
                    <strong>
                      {item.start_date || 'Start date'}
                      {' — '}
                      {item.currently_working
                        ? 'Present'
                        : item.end_date || 'End date not provided'}
                    </strong>
                    {item.location && <span>{item.location}</span>}
                    {item.employment_type && (
                      <span>{item.employment_type}</span>
                    )}
                    {item.description && <span>{item.description}</span>}
                  </div>

                  <div className="profile-document-actions">
                    <button
                      type="button"
                      className="profile-document-upload-button"
                      onClick={() => {
                        setEditingExperienceId(item.id)
                      }}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="profile-document-remove-button"
                      onClick={() => deleteExperience(item.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {experience.length === 0 && (
            <div className="profile-document-empty">
              No employment experience has been added yet.
            </div>
          )}

          <div className="profile-form-full-width">
            <div className="profile-section-heading">
              <h3>
                {editingExperienceId
                  ? 'Edit Employment Experience'
                  : 'Add Employment Experience'}
              </h3>
            </div>

            <div className="profile-information-grid">
              <label className="profile-form-field">
                <span>Job Title</span>
                <input
                  id="experience-job-title"
                  placeholder="e.g. Recruitment Specialist"
                  defaultValue={
                    experience.find(
                      (item) => item.id === editingExperienceId,
                    )?.job_title || ''
                  }
                />
              </label>

              <label className="profile-form-field">
                <span>Company</span>
                <input
                  id="experience-company"
                  placeholder="e.g. Talent Bridge BD"
                  defaultValue={
                    experience.find(
                      (item) => item.id === editingExperienceId,
                    )?.company || ''
                  }
                />
              </label>

              <label className="profile-form-field">
                <span>Location</span>
                <input
                  id="experience-location"
                  placeholder="e.g. Dhaka, Bangladesh"
                  defaultValue={
                    experience.find(
                      (item) => item.id === editingExperienceId,
                    )?.location || ''
                  }
                />
              </label>

              <label className="profile-form-field">
                <span>Employment Type</span>
                <select
                  id="experience-employment-type"
                  defaultValue={
                    experience.find(
                      (item) => item.id === editingExperienceId,
                    )?.employment_type || ''
                  }
                >
                  <option value="">Select employment type</option>
                  {EMPLOYMENT_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </label>

              <label className="profile-form-field">
                <span>Start Date</span>
                <input
                  id="experience-start-date"
                  type="date"
                  defaultValue={
                    experience.find(
                      (item) => item.id === editingExperienceId,
                    )?.start_date || ''
                  }
                />
              </label>

              <label className="profile-form-field">
                <span>End Date</span>
                <input
                  id="experience-end-date"
                  type="date"
                  defaultValue={
                    experience.find(
                      (item) => item.id === editingExperienceId,
                    )?.end_date || ''
                  }
                  disabled={
                    experience.find(
                      (item) => item.id === editingExperienceId,
                    )?.currently_working || false
                  }
                />
              </label>
            </div>

            <div className="profile-form-full-width">
              <label className="profile-form-field">
                <span>Description</span>
                <textarea
                  id="experience-description"
                  rows="5"
                  placeholder="Describe your responsibilities, achievements, and key duties."
                  defaultValue={
                    experience.find(
                      (item) => item.id === editingExperienceId,
                    )?.description || ''
                  }
                />
              </label>
            </div>

            <div className="profile-document-actions">
              <label className="profile-form-field" style={{ flexDirection: 'row', alignItems: 'center', gap: '8px' }}>
                <input
                  id="experience-currently-working"
                  type="checkbox"
                  defaultChecked={
                    experience.find(
                      (item) => item.id === editingExperienceId,
                    )?.currently_working || false
                  }
                />
                <span>Currently working here</span>
              </label>

              <button
                type="button"
                className="profile-action-primary"
                disabled={experienceSaving}
                onClick={() => {
                  const jobTitle = document
                    .getElementById('experience-job-title')
                    .value.trim()
                  const company = document
                    .getElementById('experience-company')
                    .value.trim()
                  const location = document
                    .getElementById('experience-location')
                    .value.trim()
                  const employmentType = document.getElementById(
                    'experience-employment-type',
                  ).value
                  const startDate = document.getElementById(
                    'experience-start-date',
                  ).value
                  const endDate = document.getElementById(
                    'experience-end-date',
                  ).value
                  const currentlyWorking = document.getElementById(
                    'experience-currently-working',
                  ).checked
                  const description = document
                    .getElementById('experience-description')
                    .value.trim()

                  if (!jobTitle || !company || !startDate) {
                    setError(
                      'Job Title, Company, and Start Date are required.',
                    )
                    setMessage('')
                    return
                  }

                  saveExperience({
                    job_title: jobTitle,
                    company,
                    location: location || null,
                    employment_type: employmentType || null,
                    start_date: startDate,
                    end_date: currentlyWorking ? null : endDate || null,
                    currently_working: currentlyWorking,
                    description: description || null,
                  })
                }}
              >
                {experienceSaving
                  ? 'Saving...'
                  : editingExperienceId
                    ? 'Update Experience'
                    : 'Add Experience'}
              </button>

              {editingExperienceId && (
                <button
                  type="button"
                  className="profile-document-remove-button"
                  disabled={experienceSaving}
                  onClick={() => setEditingExperienceId(null)}
                >
                  Cancel
                </button>
              )}
            </div>
          </div>
        </section>
        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Skills &amp; Professional Competencies</h2>
            <p>
              Add your key professional skills and competencies to help TBBD
              match you with suitable employment opportunities.
            </p>
          </div>

          {skills.length > 0 && (
            <div className="profile-information-grid">
              {skills.map((skill) => (
                <div
                  key={skill.id}
                  className="profile-document-card"
                >
                  <div className="profile-document-content">
                    <div className="profile-document-heading">
                      <strong>{skill.skill_name}</strong>
                    </div>

                    {skill.skill_category && (
                      <div className="profile-document-file">
                        Category: {skill.skill_category}
                      </div>
                    )}

                    {skill.proficiency && (
                      <div className="profile-document-help">
                        Proficiency:{' '}
                        <span style={{ textTransform: 'capitalize' }}>
                          {skill.proficiency}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="profile-document-actions">
                    <button
                      type="button"
                      className="profile-action-primary"
                      onClick={() => {
                        setEditingSkillId(skill.id)
                        setError('')
                        setMessage('')
                      }}
                      disabled={skillsSaving}
                    >
                      Edit
                    </button>

                    <button
                      type="button"
                      className="profile-document-remove-button"
                      onClick={() => deleteSkill(skill.id)}
                      disabled={skillsSaving}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {skills.length === 0 && (
            <div className="profile-document-empty">
              No professional skills have been added yet.
            </div>
          )}

          <div className="profile-information-grid">
            <label className="profile-form-field">
              <span>Skill Name</span>
              <input
                id="skill-name"
                placeholder="e.g. Microsoft Azure"
                defaultValue={
                  editingSkillId
                    ? skills.find(
                        (item) => item.id === editingSkillId,
                      )?.skill_name || ''
                    : ''
                }
                disabled={skillsSaving}
              />
            </label>

            <label className="profile-form-field">
              <span>Skill Category</span>
              <input
                id="skill-category"
                placeholder="e.g. Cloud Computing"
                defaultValue={
                  editingSkillId
                    ? skills.find(
                        (item) => item.id === editingSkillId,
                      )?.skill_category || ''
                    : ''
                }
                disabled={skillsSaving}
              />
            </label>

            <label className="profile-form-field">
              <span>Proficiency</span>
              <select
                id="skill-proficiency"
                defaultValue={
                  editingSkillId
                    ? skills.find(
                        (item) => item.id === editingSkillId,
                      )?.proficiency || ''
                    : ''
                }
                disabled={skillsSaving}
              >
                <option value="">Select proficiency</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="expert">Expert</option>
              </select>
            </label>
          </div>

          <div className="profile-document-actions">
            <button
              type="button"
              className="profile-action-primary"
              disabled={skillsSaving}
              onClick={async () => {
                const skillName =
                  document
                    .getElementById('skill-name')
                    ?.value.trim() || ''

                const skillCategory =
                  document
                    .getElementById('skill-category')
                    ?.value.trim() || ''

                const proficiency =
                  document.getElementById(
                    'skill-proficiency',
                  )?.value || ''

                if (!skillName) {
                  setError('Skill Name is required.')
                  setMessage('')
                  return
                }

                try {
                  await saveSkill({
                    skill_name: skillName,
                    skill_category: skillCategory || null,
                    proficiency: proficiency || null,
                  })

                  document.getElementById('skill-name').value = ''
                  document.getElementById('skill-category').value = ''
                  document.getElementById('skill-proficiency').value = ''
                } catch {
                  // saveSkill handles the error message.
                }
              }}
            >
              {skillsSaving
                ? 'Saving...'
                : editingSkillId
                  ? 'Update Skill'
                  : 'Add Skill'}
            </button>

            {editingSkillId && (
              <button
                type="button"
                className="profile-document-remove-button"
                disabled={skillsSaving}
                onClick={() => {
                  setEditingSkillId(null)
                  setError('')
                  setMessage('')
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </section>

        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Languages</h2>
            <p>
              Add the languages you can use professionally to help TBBD match
              you with suitable overseas employment opportunities.
            </p>
          </div>

          {languages.length > 0 && (
            <div className="profile-information-grid">
              {languages.map((language) => (
                <div
                  key={language.id}
                  className="profile-document-card"
                >
                  <div className="profile-document-content">
                    <div className="profile-document-heading">
                      <strong>{language.language_name}</strong>
                    </div>

                    {language.speaking_proficiency && (
                      <div className="profile-document-file">
                        Speaking:{' '}
                        <span style={{ textTransform: 'capitalize' }}>
                          {language.speaking_proficiency}
                        </span>
                      </div>
                    )}

                    {language.reading_proficiency && (
                      <div className="profile-document-file">
                        Reading:{' '}
                        <span style={{ textTransform: 'capitalize' }}>
                          {language.reading_proficiency}
                        </span>
                      </div>
                    )}

                    {language.writing_proficiency && (
                      <div className="profile-document-help">
                        Writing:{' '}
                        <span style={{ textTransform: 'capitalize' }}>
                          {language.writing_proficiency}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="profile-document-actions">
                    <button
                      type="button"
                      className="profile-action-primary"
                      onClick={() => {
                        setEditingLanguageId(language.id)
                        setError('')
                        setMessage('')
                      }}
                      disabled={languagesSaving}
                    >
                      Edit
                    </button>

                    <button
                      type="button"
                      className="profile-document-remove-button"
                      onClick={() => deleteLanguage(language.id)}
                      disabled={languagesSaving}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {languages.length === 0 && (
            <div className="profile-document-empty">
              No languages have been added yet.
            </div>
          )}

          <div className="profile-information-grid">
            <label className="profile-form-field">
              <span>Language</span>
              <input
                id="language-name"
                placeholder="e.g. English"
                defaultValue={
                  editingLanguageId
                    ? languages.find(
                        (item) => item.id === editingLanguageId,
                      )?.language_name || ''
                    : ''
                }
                disabled={languagesSaving}
              />
            </label>

            <label className="profile-form-field">
              <span>Speaking Proficiency</span>
              <select
                id="language-speaking"
                defaultValue={
                  editingLanguageId
                    ? languages.find(
                        (item) => item.id === editingLanguageId,
                      )?.speaking_proficiency || ''
                    : ''
                }
                disabled={languagesSaving}
              >
                <option value="">Select proficiency</option>
                <option value="basic">Basic</option>
                <option value="beginner">Beginner</option>
                <option value="elementary">Elementary</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="fluent">Fluent</option>
                <option value="native">Native</option>
                <option value="expert">Expert</option>
              </select>
            </label>

            <label className="profile-form-field">
              <span>Reading Proficiency</span>
              <select
                id="language-reading"
                defaultValue={
                  editingLanguageId
                    ? languages.find(
                        (item) => item.id === editingLanguageId,
                      )?.reading_proficiency || ''
                    : ''
                }
                disabled={languagesSaving}
              >
                <option value="">Select proficiency</option>
                <option value="basic">Basic</option>
                <option value="beginner">Beginner</option>
                <option value="elementary">Elementary</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="fluent">Fluent</option>
                <option value="native">Native</option>
                <option value="expert">Expert</option>
              </select>
            </label>

            <label className="profile-form-field">
              <span>Writing Proficiency</span>
              <select
                id="language-writing"
                defaultValue={
                  editingLanguageId
                    ? languages.find(
                        (item) => item.id === editingLanguageId,
                      )?.writing_proficiency || ''
                    : ''
                }
                disabled={languagesSaving}
              >
                <option value="">Select proficiency</option>
                <option value="basic">Basic</option>
                <option value="beginner">Beginner</option>
                <option value="elementary">Elementary</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="fluent">Fluent</option>
                <option value="native">Native</option>
                <option value="expert">Expert</option>
              </select>
            </label>
          </div>

          <div className="profile-document-actions">
            <button
              type="button"
              className="profile-action-primary"
              disabled={languagesSaving}
              onClick={saveLanguage}
            >
              {languagesSaving
                ? 'Saving...'
                : editingLanguageId
                  ? 'Update Language'
                  : 'Add Language'}
            </button>

            {editingLanguageId && (
              <button
                type="button"
                className="profile-document-remove-button"
                disabled={languagesSaving}
                onClick={() => {
                  setEditingLanguageId(null)
                  setError('')
                  setMessage('')
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </section>
        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Documents</h2>
            <p>
              Keep your professional photo, latest CV, and passport copy ready
              for overseas recruitment.
            </p>
          </div>

          <div className="profile-document-grid">
            <DocumentCard
              title="Profile Photo"
              description="A recent passport-size professional photo."
              document={profilePhotoDocument}
              documentType="profile_photo"
              uploading={uploadingType === 'profile_photo'}
              onUpload={handleDocumentUpload}
              onDelete={handleDocumentDelete}
            />

            <DocumentCard
              title="CV / Resume"
              description="Your current professional CV or resume."
              document={resumeDocument}
              documentType="resume"
              uploading={uploadingType === 'resume'}
              onUpload={handleDocumentUpload}
              onDelete={handleDocumentDelete}
            />

            <DocumentCard
              title="Passport Copy"
              description="A clear copy of your current passport."
              document={passportDocument}
              documentType="passport"
              uploading={uploadingType === 'passport'}
              onUpload={handleDocumentUpload}
              onDelete={handleDocumentDelete}
            />
          </div>
        </section>

        <section className="profile-section">
          <div className="profile-section-heading">
            <h2>Overseas Employment Preferences</h2>
            <p>
              Tell TBBD what types of international opportunities you are
              looking for.
            </p>
          </div>

          <div className="profile-information-grid">
            <label className="profile-form-field">
              <span>Preferred Job Title</span>
              <input
                name="preferred_job_title"
                value={preferenceForm.preferred_job_title}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    preferred_job_title: event.target.value,
                  }))
                }
                placeholder="e.g. Electrical Engineer"
              />
            </label>

            <label className="profile-form-field">
              <span>Preferred Location / Country</span>
              <input
                name="preferred_location"
                value={preferenceForm.preferred_location}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    preferred_location: event.target.value,
                  }))
                }
                placeholder="e.g. Saudi Arabia, UAE"
              />
            </label>

            <label className="profile-form-field">
              <span>Employment Type</span>
              <select
                value={preferenceForm.preferred_employment_type}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    preferred_employment_type: event.target.value,
                  }))
                }
              >
                <option value="">Select employment type</option>
                {EMPLOYMENT_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </label>

            <label className="profile-form-field">
              <span>Work Arrangement</span>
              <select
                value={preferenceForm.work_arrangement}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    work_arrangement: event.target.value,
                  }))
                }
              >
                <option value="">Select arrangement</option>
                {PREFERENCE_WORK_ARRANGEMENTS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="profile-form-field">
              <span>Expected Salary</span>
              <input
                type="number"
                min="0"
                value={preferenceForm.expected_salary}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    expected_salary: event.target.value,
                  }))
                }
                placeholder="Expected monthly or annual salary"
              />
            </label>

            <label className="profile-form-field">
              <span>Currency</span>
              <input
                value={preferenceForm.currency}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    currency: event.target.value,
                  }))
                }
                placeholder="e.g. USD, SAR, AED"
              />
            </label>

            <label className="profile-form-field">
              <span>Notice Period</span>
              <input
                value={preferenceForm.availability_notice_period}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    availability_notice_period: event.target.value,
                  }))
                }
                placeholder="e.g. 30 days"
              />
            </label>

            <label className="profile-form-field">
              <span>Preferred Contact Method</span>
              <select
                value={preferenceForm.preferred_contact_method}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    preferred_contact_method: event.target.value,
                  }))
                }
              >
                <option value="">Select contact method</option>
                {PREFERENCE_CONTACT_METHODS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="profile-readiness-grid">
            <label className="profile-readiness-item">
              <span>Willing to Relocate</span>
              <input
                type="checkbox"
                checked={preferenceForm.open_to_relocation}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    open_to_relocation: event.target.checked,
                  }))
                }
              />
            </label>

            <label className="profile-readiness-item">
              <span>Available for Overseas Employment</span>
              <input
                type="checkbox"
                checked={preferenceForm.available_for_recruitment}
                onChange={(event) =>
                  setPreferenceForm((current) => ({
                    ...current,
                    available_for_recruitment: event.target.checked,
                  }))
                }
              />
            </label>
          </div>

          <div className="profile-actions">
            <button
              type="button"
              className="profile-action-primary"
              onClick={savePreferences}
              disabled={preferencesSaving}
            >
              {preferencesSaving
                ? 'Saving Preferences...'
                : 'Save Employment Preferences'}
            </button>
          </div>
        </section>
        <section className="profile-actions-section">
          <div>
            <h2>Save Candidate Profile</h2>
            <p>
              Keep your personal, professional, passport, and recruitment
              information up to date.
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

function DocumentCard({
  title,
  description,
  document,
  documentType,
  uploading,
  onUpload,
  onDelete,
}) {
  const [previewUrl, setPreviewUrl] = useState('')
  const [previewError, setPreviewError] = useState('')

  useEffect(() => {
    let active = true
    let objectUrl = ''

    async function loadPreview() {
      if (
        documentType !== 'profile_photo' ||
        !document ||
        !document.id
      ) {
        return
      }

      try {
        setPreviewError('')

        const response = await fetch(
          `/api/candidate/documents/${encodeURIComponent(document.id)}`,
        )

        if (!response.ok) {
          throw new Error('Unable to load photo preview.')
        }

        const blob = await response.blob()

        if (!active) return

        objectUrl = URL.createObjectURL(blob)
        setPreviewUrl(objectUrl)
      } catch (err) {
        if (active) {
          setPreviewUrl('')
          setPreviewError(
            err.message || 'Unable to load photo preview.',
          )
        }
      }
    }

    loadPreview()

    return () => {
      active = false

      if (objectUrl) {
        URL.revokeObjectURL(objectUrl)
      }
    }
  }, [documentType, document?.id])

  const accept =
    documentType === 'profile_photo'
      ? '.jpg,.jpeg,.png'
      : documentType === 'passport'
        ? '.pdf,.jpg,.jpeg,.png'
        : '.pdf,.doc,.docx'

  const maxFileSize =
    documentType === 'profile_photo'
      ? 'Maximum 5 MB.'
      : 'Maximum 10 MB.'

  const helpText =
    documentType === 'profile_photo'
      ? 'JPG, JPEG or PNG.'
      : documentType === 'passport'
        ? 'PDF, JPG, JPEG or PNG.'
        : 'PDF, DOC or DOCX.'

  const icon =
    documentType === 'profile_photo'
      ? '◉'
      : documentType === 'passport'
        ? '▣'
        : '▤'

  return (
    <div
      className={
        documentType === 'profile_photo'
          ? 'profile-document-card profile-document-card-photo'
          : 'profile-document-card'
      }
    >
      <div className="profile-document-icon">{icon}</div>

      <div className="profile-document-content">
        <div className="profile-document-heading">
          <div>
            <h3>{title}</h3>
            <p>{description}</p>
          </div>

          <span
            className={
              document
                ? 'profile-document-status profile-document-status-ready'
                : 'profile-document-status'
            }
          >
            {document ? 'Uploaded' : 'Required'}
          </span>
        </div>

        {document ? (
          <>
            {documentType === 'profile_photo' && (
              <div className="profile-photo-preview">
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Candidate profile"
                    className="profile-photo-preview-image"
                  />
                ) : (
                  <div className="profile-photo-preview-placeholder">
                    {previewError || 'Loading photo...'}
                  </div>
                )}
              </div>
            )}

            <div className="profile-document-file">
              <strong>{document.file_name}</strong>
              <span>
                {formatFileSize(document.file_size)} ·{' '}
                {document.content_type || 'Document'}
              </span>
            </div>
          </>
        ) : (
          <div className="profile-document-empty">
            No document uploaded yet.
          </div>
        )}

        <div className="profile-document-actions">
          <label className="profile-document-upload-button">
            {uploading
              ? 'Uploading...'
              : document
                ? 'Replace'
                : 'Upload'}
            <input
              type="file"
              accept={accept}
              onChange={(event) => onUpload(documentType, event)}
              disabled={uploading}
            />
          </label>

          {document && (
            <button
              type="button"
              className="profile-document-remove-button"
              onClick={() => onDelete(document)}
              disabled={uploading}
            >
              Remove
            </button>
          )}
        </div>

        <small className="profile-document-help">
          {maxFileSize} {helpText}
        </small>
      </div>
    </div>
  )
}
