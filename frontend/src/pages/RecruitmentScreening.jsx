import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'

export default function RecruitmentScreening({ auth }) {
  const organizationId = auth?.organization_ids?.[0] || ''

  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!organizationId) {
      setLoading(false)
      return
    }

    fetch(
      `/api/applications?organization_id=${encodeURIComponent(
        organizationId
      )}`,
      {
        credentials: 'include',
      }
    )
      .then(async (response) => {
        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            data.detail || 'Unable to load screening candidates.'
          )
        }

        return data
      })
      .then((data) => {
        setApplications(data.applications || [])
      })
      .catch((err) => {
        setError(err.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [organizationId])

  return (
    <>
      <PageHeader
        title="Screening"
        subtitle="Review and evaluate candidates before moving them to the next recruitment stage."
      />

      {!organizationId ? (
        <section className="placeholder-card">
          <h2>Organization access required</h2>
          <p>
            Your account is not currently assigned to an organization.
          </p>
        </section>
      ) : loading ? (
        <section className="placeholder-card">
          <p>Loading screening candidates...</p>
        </section>
      ) : error ? (
        <section className="placeholder-card">
          <h2>Unable to load screening candidates</h2>
          <p>{error}</p>
        </section>
      ) : applications.length === 0 ? (
        <section className="placeholder-card">
          <h2>No candidates to screen</h2>
          <p>
            Candidates will appear here when applications are submitted
            for your organization's jobs.
          </p>
        </section>
      ) : (
        <section className="dashboard-card">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Email</th>
                  <th>Job</th>
                  <th>Status</th>
                  <th>Cover Letter</th>
                  <th>Applied</th>
                </tr>
              </thead>

              <tbody>
                {applications.map((application) => (
                  <tr key={application.id}>
                    <td>
                      {application.candidate_first_name}{' '}
                      {application.candidate_last_name}
                    </td>

                    <td>{application.candidate_email}</td>

                    <td>{application.job_title}</td>

                    <td>{application.status}</td>

                    <td>
                      {application.cover_letter ? 'Available' : '—'}
                    </td>

                    <td>
                      {application.applied_at
                        ? new Date(
                            application.applied_at
                          ).toLocaleDateString()
                        : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </>
  )
}
