import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'


const INTERVIEW_STATUSES = [
  'scheduled',
  'completed',
  'cancelled',
  'rescheduled',
  'no_show',
]


export default function RecruitmentInterviews({ auth }) {

  const organizationId = auth?.organization_ids?.[0] || ''

  const [interviews, setInterviews] = useState([])
  const [applications, setApplications] = useState([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showForm, setShowForm] = useState(false)
  const [saving, setSaving] = useState(false)

  const [form, setForm] = useState({
    application_id: '',
    scheduled_start: '',
    scheduled_end: '',
    interview_type: 'Video',
    location_or_link: '',
    interviewer_name: '',
    notes: '',
  })


  const loadInterviews = async () => {

    if (!organizationId) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {

      const response = await fetch(
        `/api/interviews?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          credentials: 'include',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load interviews.'
        )
      }

      setInterviews(data.interviews || [])

    } catch (err) {

      setError(err.message)

    } finally {

      setLoading(false)

    }
  }


  const loadApplications = async () => {

    if (!organizationId) {
      return
    }

    try {

      const response = await fetch(
        `/api/applications?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          credentials: 'include',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load applications.'
        )
      }

      setApplications(data.applications || [])

    } catch (err) {

      setError(err.message)

    }
  }


  useEffect(() => {

    loadInterviews()
    loadApplications()

  }, [organizationId])


  const resetForm = () => {

    setForm({
      application_id: '',
      scheduled_start: '',
      scheduled_end: '',
      interview_type: 'Video',
      location_or_link: '',
      interviewer_name: '',
      notes: '',
    })

  }


  const openForm = () => {

    resetForm()
    setShowForm(true)

  }


  const closeForm = () => {

    if (!saving) {
      setShowForm(false)
      resetForm()
    }

  }


  const handleChange = (event) => {

    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))

  }


  const handleSubmit = async (event) => {

    event.preventDefault()

    if (!form.application_id) {
      setError('Please select an application.')
      return
    }

    if (!form.scheduled_start) {
      setError('Please select an interview date and time.')
      return
    }

    setSaving(true)
    setError('')

    try {

      const payload = {
        application_id: form.application_id,
        scheduled_start: new Date(
          form.scheduled_start
        ).toISOString(),
        scheduled_end: form.scheduled_end
          ? new Date(form.scheduled_end).toISOString()
          : null,
        interview_type: form.interview_type,
        location_or_link: form.location_or_link,
        interviewer_name: form.interviewer_name,
        notes: form.notes,
      }

      const response = await fetch(
        `/api/interviews?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to schedule interview.'
        )
      }

      setShowForm(false)
      resetForm()

      await loadInterviews()

    } catch (err) {

      setError(err.message)

    } finally {

      setSaving(false)

    }
  }


  const updateStatus = async (interview, status) => {

    try {

      const response = await fetch(
        `/api/interviews/${encodeURIComponent(
          interview.id
        )}?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            scheduled_start: interview.scheduled_start,
            scheduled_end: interview.scheduled_end,
            interview_type: interview.interview_type || '',
            location_or_link: interview.location_or_link || '',
            interviewer_name: interview.interviewer_name || '',
            notes: interview.notes || '',
            status,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to update interview status.'
        )
      }

      setInterviews((current) =>
        current.map((item) =>
          item.id === interview.id
            ? data.interview
            : item
        )
      )

    } catch (err) {

      setError(err.message)

    }
  }


  const formatDateTime = (value) => {

    if (!value) {
      return '—'
    }

    return new Date(value).toLocaleString()

  }


  if (!organizationId) {

    return (

      <>

        <PageHeader
          title="Interviews"
          subtitle="Schedule and manage candidate interviews."
        />

        <section className="placeholder-card">

          <h2>Organization access required</h2>

          <p>
            Your account is not currently assigned to an organization.
          </p>

        </section>

      </>

    )

  }


  return (

    <>

      <PageHeader
        title="Interviews"
        subtitle="Schedule and manage candidate interviews through the recruitment process."
      />

      {error && (

        <section className="placeholder-card">

          <h2>Interview action needs attention</h2>

          <p>{error}</p>

        </section>

      )}


      <section className="dashboard-card">

        <div className="card-heading">

          <div>

            <h2>Interview Schedule</h2>

            <p>
              Coordinate interviews linked to candidate applications.
            </p>

          </div>

          <button
            type="button"
            className="primary-button"
            onClick={openForm}
          >
            Schedule Interview
          </button>

        </div>


        {loading ? (

          <div className="empty-state">

            <strong>Loading interviews...</strong>

          </div>

        ) : interviews.length === 0 ? (

          <div className="empty-state">

            <strong>No interviews scheduled</strong>

            <span>
              Schedule an interview for a candidate application to begin the interview stage.
            </span>

          </div>

        ) : (

          <div className="table-wrap">

            <table>

              <thead>

                <tr>

                  <th>Candidate</th>
                  <th>Job</th>
                  <th>Date & Time</th>
                  <th>Type</th>
                  <th>Interviewer</th>
                  <th>Status</th>
                  <th>Action</th>

                </tr>

              </thead>

              <tbody>

                {interviews.map((interview) => (

                  <tr key={interview.id}>

                    <td>

                      <strong>
                        {interview.candidate_first_name}{' '}
                        {interview.candidate_last_name}
                      </strong>

                      <br />

                      <small>
                        {interview.candidate_email}
                      </small>

                    </td>

                    <td>
                      {interview.job_title}
                    </td>

                    <td>
                      {formatDateTime(
                        interview.scheduled_start
                      )}
                    </td>

                    <td>
                      {interview.interview_type || '—'}
                    </td>

                    <td>
                      {interview.interviewer_name || '—'}
                    </td>

                    <td>

                      <select
                        value={interview.status}
                        onChange={(event) =>
                          updateStatus(
                            interview,
                            event.target.value
                          )
                        }
                      >

                        {INTERVIEW_STATUSES.map((status) => (

                          <option
                            key={status}
                            value={status}
                          >
                            {status.replace('_', ' ')}
                          </option>

                        ))}

                      </select>

                    </td>

                    <td>

                      {interview.location_or_link ? (

                        <a
                          href={interview.location_or_link}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Open link
                        </a>

                      ) : (

                        '—'

                      )}

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </section>


      {showForm && (

        <section className="dashboard-card">

          <div className="card-heading">

            <div>

              <h2>Schedule Interview</h2>

              <p>
                Create an interview linked to an existing candidate application.
              </p>

            </div>

          </div>


          <form
            className="job-opening-form"
            onSubmit={handleSubmit}
          >

            <div className="job-opening-grid">


              <div className="job-form-card">

                <h3>Candidate & Application</h3>

                <div className="job-form-fields">

                  <label>

                    <span>Candidate Application *</span>

                    <select
                      name="application_id"
                      value={form.application_id}
                      onChange={handleChange}
                      required
                    >

                      <option value="">
                        Select an application
                      </option>

                      {applications.map((application) => (

                        <option
                          key={application.id}
                          value={application.id}
                        >

                          {application.candidate_first_name}{' '}
                          {application.candidate_last_name}
                          {' — '}
                          {application.job_title}

                        </option>

                      ))}

                    </select>

                  </label>

                </div>

              </div>


              <div className="job-form-card">

                <h3>Interview Details</h3>

                <div className="job-form-fields">

                  <label>

                    <span>Start Date & Time *</span>

                    <input
                      type="datetime-local"
                      name="scheduled_start"
                      value={form.scheduled_start}
                      onChange={handleChange}
                      required
                    />

                  </label>


                  <label>

                    <span>End Date & Time</span>

                    <input
                      type="datetime-local"
                      name="scheduled_end"
                      value={form.scheduled_end}
                      onChange={handleChange}
                    />

                  </label>


                  <label>

                    <span>Interview Type</span>

                    <input
                      type="text"
                      name="interview_type"
                      value={form.interview_type}
                      onChange={handleChange}
                      placeholder="Video, Phone, In-person"
                    />

                  </label>

                </div>

              </div>


              <div className="job-form-card">

                <h3>Interview Location</h3>

                <div className="job-form-fields">

                  <label>

                    <span>Location / Meeting Link</span>

                    <input
                      type="text"
                      name="location_or_link"
                      value={form.location_or_link}
                      onChange={handleChange}
                      placeholder="Meeting link or interview location"
                    />

                  </label>


                  <label>

                    <span>Interviewer</span>

                    <input
                      type="text"
                      name="interviewer_name"
                      value={form.interviewer_name}
                      onChange={handleChange}
                      placeholder="Interviewer name"
                    />

                  </label>

                </div>

              </div>


              <div className="job-form-card">

                <h3>Notes</h3>

                <div className="job-form-fields">

                  <label>

                    <span>Interview Notes</span>

                    <textarea
                      name="notes"
                      value={form.notes}
                      onChange={handleChange}
                      rows="5"
                      placeholder="Interview instructions or internal notes"
                    />

                  </label>

                </div>

              </div>


            </div>


            <div className="job-form-actions">

              <button
                type="button"
                className="secondary-button"
                onClick={closeForm}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="primary-button"
                disabled={saving}
              >
                {saving
                  ? 'Scheduling...'
                  : 'Schedule Interview'}
              </button>

            </div>

          </form>

        </section>

      )}

    </>

  )
}
