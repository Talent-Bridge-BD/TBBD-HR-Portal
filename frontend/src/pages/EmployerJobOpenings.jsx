import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'
import { authenticatedFetch } from '../utils/auth'
import { useOrganization } from '../context/OrganizationContext'

const emptyOpeningForm = {
  title: '',
  description: '',
  employment_type: '',
  location: '',
  country: '',
  number_of_positions: 1,
  working_hours: '',
  benefits: '',
  requisition_number: '',
  employer_name: '',
  employer_country: '',
  employer_city: '',
  trade_skill_category: '',
  industry_sector: '',
  gender_requirement: '',
  minimum_age: '',
  maximum_age: '',
  contract_duration: '',
  work_location: '',
  project_name: '',
  closing_at: '',
}

function isJobReadyToPublish(job) {
  const requiredFields = [
    job?.title,
    job?.description,
    job?.employment_type,
    job?.location,
    job?.country,
    job?.number_of_positions,
    job?.working_hours,
    job?.benefits,
    job?.employer_name,
    job?.employer_country,
    job?.employer_city,
    job?.trade_skill_category,
    job?.industry_sector,
    job?.contract_duration,
    job?.work_location,
    job?.closing_at,
  ]

  return requiredFields.every(
    (value) => value !== null && value !== undefined && String(value).trim() !== '',
  )
}

function jobToForm(job) {
  return {
    title: job.title || '',
    description: job.description || '',
    employment_type: job.employment_type || '',
    location: job.location || '',
    country: job.country || '',
    number_of_positions: job.number_of_positions || 1,
    working_hours: job.working_hours || '',
    benefits: job.benefits || '',
    requisition_number: job.requisition_number || '',
    employer_name: job.employer_name || '',
    employer_country: job.employer_country || '',
    employer_city: job.employer_city || '',
    trade_skill_category: job.trade_skill_category || '',
    industry_sector: job.industry_sector || '',
    gender_requirement: job.gender_requirement || '',
    minimum_age: job.minimum_age ?? '',
    maximum_age: job.maximum_age ?? '',
    contract_duration: job.contract_duration || '',
    work_location: job.work_location || '',
    project_name: job.project_name || '',
    closing_at: job.closing_at
      ? String(job.closing_at).slice(0, 10)
      : '',
  }
}

export default function EmployerJobOpenings({ auth }) {
  const { selectedOrganizationId, organizationLoading } = useOrganization()

  const organizationId = selectedOrganizationId || ''

  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [actionJobId, setActionJobId] = useState('')
  const [editingJobId, setEditingJobId] = useState('')
  const [openingForm, setOpeningForm] = useState(emptyOpeningForm)

  const roles = auth?.roles || []
  const canManageOpenings = roles.some((role) =>
    ['Administrator', 'HR Manager'].includes(role),
  )

  const statusOptions = ['All', 'Open', 'Paused', 'Closed', 'Draft']

  const filteredJobs =
    statusFilter === 'All'
      ? jobs
      : jobs.filter(
          (job) =>
            String(job.status || '').toLowerCase() ===
            statusFilter.toLowerCase(),
        )

  async function loadJobs(showLoading = true) {
    if (organizationLoading || !organizationId) {
      setJobs([])
      setLoading(false)
      return
    }

    if (showLoading) {
      setLoading(true)
    }

    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/jobs?organization_id=${encodeURIComponent(organizationId)}`,
      )

      if (!response.ok) {
        throw new Error(`Failed to load job openings: ${response.status}`)
      }

      const data = await response.json()
      setJobs(data.jobs || [])
    } catch (err) {
      console.error(err)
      setError('Unable to load job openings.')
    } finally {
      if (showLoading) {
        setLoading(false)
      }
    }
  }

  useEffect(() => {
    loadJobs()
  }, [organizationId, organizationLoading])

  function startEditing(job) {
    setEditingJobId(job.id)
    setOpeningForm(jobToForm(job))
    setError('')
  }

  function cancelEditing() {
    setEditingJobId('')
    setOpeningForm(emptyOpeningForm)
  }

  function handleFormChange(event) {
    const { name, value } = event.target

    setOpeningForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function saveOpening(job) {
    if (!organizationId || !job?.id) return

    setActionJobId(job.id)
    setError('')

    try {
      const response = await authenticatedFetch(`/api/jobs/${job.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          organization_id: organizationId,
          title: openingForm.title.trim(),
          description: openingForm.description.trim(),
          employment_type: openingForm.employment_type.trim(),
          location: openingForm.location.trim(),
          country: openingForm.country.trim(),
          status: 'draft',
          number_of_positions:
            Number(openingForm.number_of_positions) || 1,
          working_hours: openingForm.working_hours.trim(),
          benefits: openingForm.benefits.trim(),
          published_at: job.published_at,
          closing_at: openingForm.closing_at
            ? `${openingForm.closing_at}T23:59:59`
            : null,
          requisition_number: openingForm.requisition_number.trim(),
          employer_name: openingForm.employer_name.trim(),
          employer_country: openingForm.employer_country.trim(),
          employer_city: openingForm.employer_city.trim(),
          trade_skill_category:
            openingForm.trade_skill_category.trim(),
          industry_sector: openingForm.industry_sector.trim(),
          gender_requirement: openingForm.gender_requirement.trim(),
          minimum_age:
            openingForm.minimum_age === ''
              ? null
              : Number(openingForm.minimum_age),
          maximum_age:
            openingForm.maximum_age === ''
              ? null
              : Number(openingForm.maximum_age),
          contract_duration: openingForm.contract_duration.trim(),
          work_location: openingForm.work_location.trim(),
          project_name: openingForm.project_name.trim(),
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to save job opening.')
      }

      await loadJobs(false)
      cancelEditing()
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to save job opening.')
    } finally {
      setActionJobId('')
    }
  }

  async function updateJobStatus(job, status) {
    if (!organizationId || !job?.id) return

    setActionJobId(job.id)
    setError('')

    try {
      const response = await authenticatedFetch(`/api/jobs/${job.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          organization_id: organizationId,
          title: job.title,
          description: job.description,
          employment_type: job.employment_type,
          location: job.location,
          country: job.country,
          status,
          number_of_positions: job.number_of_positions,
          working_hours: job.working_hours || '',
          benefits: job.benefits || '',
          published_at:
            status === 'open'
              ? job.published_at || new Date().toISOString()
              : job.published_at,
          closing_at: job.closing_at,
          requisition_number: job.requisition_number || '',
          employer_name: job.employer_name || '',
          employer_country: job.employer_country || '',
          employer_city: job.employer_city || '',
          trade_skill_category: job.trade_skill_category || '',
          industry_sector: job.industry_sector || '',
          gender_requirement: job.gender_requirement || '',
          minimum_age: job.minimum_age,
          maximum_age: job.maximum_age,
          contract_duration: job.contract_duration || '',
          work_location: job.work_location || '',
          project_name: job.project_name || '',
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to change job status.')
      }

      await loadJobs(false)
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to change job status.')
    } finally {
      setActionJobId('')
    }
  }

  return (
    <>
      <PageHeader
        title="Job Openings"
        subtitle="View your organization's recruitment job openings."
      />

      <section className="dashboard-card">
        <div className="card-heading">
          <div>
            <h2>Employer Job Openings</h2>
            <p>
              Review open, paused, closed, and draft positions for your
              organization.
            </p>
          </div>
        </div>

        {error && (
          <div className="empty-state">
            <strong>{error}</strong>
          </div>
        )}

        {!organizationId && !loading ? (
          <div className="empty-state">
            <strong>Organization access required</strong>
            <span>
              Your account must be connected to an employer organization.
            </span>
          </div>
        ) : loading ? (
          <div className="empty-state">
            <strong>Loading job openings...</strong>
          </div>
        ) : (
          <>
            <div
              className="job-opening-filters"
              aria-label="Job opening status filter"
            >
              {statusOptions.map((status) => {
                const count =
                  status === 'All'
                    ? jobs.length
                    : jobs.filter(
                        (job) =>
                          String(job.status || '').toLowerCase() ===
                          status.toLowerCase(),
                      ).length

                return (
                  <button
                    key={status}
                    type="button"
                    className={`job-opening-filter ${
                      statusFilter === status ? 'active' : ''
                    }`}
                    onClick={() => setStatusFilter(status)}
                  >
                    {status} <span>{count}</span>
                  </button>
                )
              })}
            </div>

            {filteredJobs.length === 0 ? (
              <div className="empty-state">
                <strong>
                  No {statusFilter.toLowerCase()} job openings
                </strong>
                <span>
                  There are no job openings with this status for your
                  organization.
                </span>
              </div>
            ) : (
              <div className="job-opening-list">
                {filteredJobs.map((job) => {
                  const isDraft =
                    String(job.status || '').toLowerCase() === 'draft'
                  const isEditing = editingJobId === job.id

                  return (
                    <article className="job-opening-card" key={job.id}>
                      <div className="job-opening-main">
                        <div className="job-opening-title-row">
                          <h3>{job.title}</h3>
                          <span
                            className={`job-opening-status status-${String(
                              job.status || '',
                            ).toLowerCase()}`}
                          >
                            {job.status}
                          </span>
                        </div>

                        <div className="job-opening-meta">
                          {job.location && (
                            <span>📍 {job.location}</span>
                          )}
                          {job.country && (
                            <span>🌐 {job.country}</span>
                          )}
                          {job.employment_type && (
                            <span>💼 {job.employment_type}</span>
                          )}
                          {job.number_of_positions && (
                            <span>
                              👥 {job.number_of_positions} position(s)
                            </span>
                          )}
                          {job.closing_at && (
                            <span>
                              📅 Closing{' '}
                              {new Date(
                                job.closing_at,
                              ).toLocaleDateString()}
                            </span>
                          )}
                        </div>

                        {isEditing && isDraft && canManageOpenings && (
                          <div className="job-opening-editor">
                            <div className="job-opening-editor-heading">
                              <div>
                                <h3>Complete Job Opening</h3>
                                <p>
                                  Confirm the approved request information
                                  and complete the opening details before
                                  publication.
                                </p>
                              </div>
                            </div>

                            <div className="job-opening-form-section">
                              <h4>Approved Request Information</h4>

                              <div className="job-opening-form-grid">
                                <label>
                                  <span>Job Title *</span>
                                  <input
                                    name="title"
                                    value={openingForm.title}
                                    onChange={handleFormChange}
                                    required
                                  />
                                </label>

                                <label>
                                  <span>Employment Type</span>
                                  <input
                                    name="employment_type"
                                    value={openingForm.employment_type}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Location</span>
                                  <input
                                    name="location"
                                    value={openingForm.location}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Country</span>
                                  <input
                                    name="country"
                                    value={openingForm.country}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Number of Positions *</span>
                                  <input
                                    name="number_of_positions"
                                    type="number"
                                    min="1"
                                    value={openingForm.number_of_positions}
                                    onChange={handleFormChange}
                                    required
                                  />
                                </label>

                                <label>
                                  <span>Working Hours</span>
                                  <input
                                    name="working_hours"
                                    value={openingForm.working_hours}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label className="job-opening-form-full">
                                  <span>Description</span>
                                  <textarea
                                    name="description"
                                    value={openingForm.description}
                                    onChange={handleFormChange}
                                    rows="4"
                                  />
                                </label>

                                <label className="job-opening-form-full">
                                  <span>Benefits</span>
                                  <textarea
                                    name="benefits"
                                    value={openingForm.benefits}
                                    onChange={handleFormChange}
                                    rows="4"
                                  />
                                </label>
                              </div>
                            </div>

                            <div className="job-opening-form-section">
                              <h4>Job Opening Details</h4>

                              <div className="job-opening-form-grid">
                                <label>
                                  <span>Requisition Number</span>
                                  <input
                                    name="requisition_number"
                                    value={openingForm.requisition_number}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Employer Name</span>
                                  <input
                                    name="employer_name"
                                    value={openingForm.employer_name}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Employer Country</span>
                                  <input
                                    name="employer_country"
                                    value={openingForm.employer_country}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Employer City</span>
                                  <input
                                    name="employer_city"
                                    value={openingForm.employer_city}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Trade / Skill Category</span>
                                  <input
                                    name="trade_skill_category"
                                    value={openingForm.trade_skill_category}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Industry Sector</span>
                                  <input
                                    name="industry_sector"
                                    value={openingForm.industry_sector}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Gender Requirement</span>
                                  <input
                                    name="gender_requirement"
                                    value={openingForm.gender_requirement}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Minimum Age</span>
                                  <input
                                    name="minimum_age"
                                    type="number"
                                    min="0"
                                    value={openingForm.minimum_age}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Maximum Age</span>
                                  <input
                                    name="maximum_age"
                                    type="number"
                                    min="0"
                                    value={openingForm.maximum_age}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Contract Duration</span>
                                  <input
                                    name="contract_duration"
                                    value={openingForm.contract_duration}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Work Location</span>
                                  <input
                                    name="work_location"
                                    value={openingForm.work_location}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Project Name</span>
                                  <input
                                    name="project_name"
                                    value={openingForm.project_name}
                                    onChange={handleFormChange}
                                  />
                                </label>

                                <label>
                                  <span>Closing Date</span>
                                  <input
                                    name="closing_at"
                                    type="date"
                                    value={openingForm.closing_at}
                                    onChange={handleFormChange}
                                  />
                                </label>
                              </div>
                            </div>

                            <div className="job-opening-editor-actions">
                              <button
                                className="primary-action"
                                type="button"
                                onClick={() => saveOpening(job)}
                                disabled={actionJobId === job.id}
                              >
                                {actionJobId === job.id
                                  ? 'Saving...'
                                  : 'Save Draft'}
                              </button>

                              <button
                                className="secondary-action"
                                type="button"
                                onClick={cancelEditing}
                                disabled={actionJobId === job.id}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        )}

                        <div className="job-opening-actions">
                          {isDraft && canManageOpenings && (
                            isJobReadyToPublish(job) ? (
                              <button
                                className="primary-action"
                                type="button"
                                onClick={() => updateJobStatus(job, 'open')}
                                disabled={actionJobId === job.id}
                              >
                                {actionJobId === job.id
                                  ? 'Publishing...'
                                  : 'Publish Job'}
                              </button>
                            ) : (
                              <button
                                className="primary-action"
                                type="button"
                                onClick={() => startEditing(job)}
                                disabled={
                                  actionJobId === job.id || isEditing
                                }
                              >
                                Complete Opening
                              </button>
                            )
                          )}

                          {isDraft && !canManageOpenings && (
                            <span className="job-opening-review-note">
                              Awaiting HR/Admin completion
                            </span>
                          )}

                          {String(job.status || '').toLowerCase() ===
                            'open' && (
                            <>
                              <button
                                className="secondary-action"
                                type="button"
                                onClick={() =>
                                  updateJobStatus(job, 'paused')
                                }
                                disabled={actionJobId === job.id}
                              >
                                {actionJobId === job.id
                                  ? 'Updating...'
                                  : 'Pause'}
                              </button>

                              <button
                                className="secondary-action"
                                type="button"
                                onClick={() =>
                                  updateJobStatus(job, 'closed')
                                }
                                disabled={actionJobId === job.id}
                              >
                                {actionJobId === job.id
                                  ? 'Updating...'
                                  : 'Close'}
                              </button>
                            </>
                          )}

                          {String(job.status || '').toLowerCase() ===
                            'paused' && (
                            <>
                              <button
                                className="primary-action"
                                type="button"
                                onClick={() =>
                                  updateJobStatus(job, 'open')
                                }
                                disabled={actionJobId === job.id}
                              >
                                {actionJobId === job.id
                                  ? 'Updating...'
                                  : 'Open'}
                              </button>

                              <button
                                className="secondary-action"
                                type="button"
                                onClick={() =>
                                  updateJobStatus(job, 'closed')
                                }
                                disabled={actionJobId === job.id}
                              >
                                {actionJobId === job.id
                                  ? 'Updating...'
                                  : 'Close'}
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    </article>
                  )
                })}
              </div>
            )}
          </>
        )}
      </section>
    </>
  )
}
