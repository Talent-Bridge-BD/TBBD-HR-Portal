import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'

export default function RecruitmentCandidates({ auth }) {
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
            data.detail || 'Unable to load candidates.'
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

  const candidates = Array.from(
    new Map(
      applications.map((application) => [
        application.candidate_id,
        application,
      ])
    ).values()
  )

  return (
    <>
      <PageHeader
        title="Candidates"
        subtitle="Manage and review candidates across the recruitment pipeline."
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
          <p>Loading candidates...</p>
        </section>
      ) : error ? (
        <section className="placeholder-card">
          <h2>Unable to load candidates</h2>
          <p>{error}</p>
        </section>
      ) : candidates.length === 0 ? (
        <section className="placeholder-card">
          <h2>No candidates yet</h2>
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
                  <th>Applied Job</th>
                  <th>Status</th>
                  <th>Applied</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((candidate) => (
                  <tr key={candidate.candidate_id}>
                    <td>
                      {candidate.candidate_first_name}{' '}
                      {candidate.candidate_last_name}
                    </td>
                    <td>{candidate.candidate_email}</td>
                    <td>{candidate.job_title}</td>
                    <td>{candidate.status}</td>
                    <td>
                      {candidate.applied_at
                        ? new Date(
                            candidate.applied_at
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
