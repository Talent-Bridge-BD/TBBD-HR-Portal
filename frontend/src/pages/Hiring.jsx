import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'


export default function Hiring({ auth }) {
  const organizationId = auth?.organization_ids?.[0] || ""

  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!organizationId) {
      setApplications([])
      return
    }

    let cancelled = false

    async function loadHiringApplications() {
      setLoading(true)
      setError("")

      try {
        const response = await fetch(
          `/api/hiring?organization_id=${encodeURIComponent(organizationId)}`,
          {
            credentials: "include",
          },
        )

        if (!response.ok) {
          throw new Error(
            `Unable to load hiring applications (${response.status})`,
          )
        }

        const data = await response.json()

        if (!cancelled) {
          setApplications(data.applications || [])
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load hiring applications.")
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadHiringApplications()

    return () => {
      cancelled = true
    }
  }, [organizationId])

  return (
    <>
      <PageHeader
        title="Hiring"
        subtitle="Manage candidates progressing through the hiring pipeline."
      />

      {!organizationId ? (
        <section className="placeholder-card">
          <h2>Organization access required</h2>
          <p>
            Your account does not currently have access to an employer
            organization.
          </p>
        </section>
      ) : (
        <section className="placeholder-card">
          <div className="page-section-header">
            <div>
              <h2>Hiring Pipeline</h2>
              <p>
                Applications currently progressing toward an offer or hire.
              </p>
            </div>
          </div>

          {loading && <p>Loading hiring pipeline...</p>}

          {error && (
            <p role="alert">
              {error}
            </p>
          )}

          {!loading && !error && applications.length === 0 && (
            <p>
              No candidates are currently in the hiring pipeline.
            </p>
          )}

          {!loading && !error && applications.length > 0 && (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Email</th>
                    <th>Job</th>
                    <th>Status</th>
                    <th>Applied</th>
                  </tr>
                </thead>

                <tbody>
                  {applications.map((application) => (
                    <tr key={application.id}>
                      <td>
                        {application.candidate_first_name}{" "}
                        {application.candidate_last_name}
                      </td>

                      <td>{application.candidate_email}</td>

                      <td>{application.job_title}</td>

                      <td>{application.status}</td>

                      <td>
                        {application.applied_at
                          ? new Date(
                              application.applied_at,
                            ).toLocaleDateString()
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </>
  )
}
