import { useEffect, useMemo, useState } from "react"
import PageHeader from "../components/PageHeader"
import { authenticatedFetch } from "../utils/auth"

const PIPELINE_STAGES = [
  {
    key: "Applied",
    label: "Applied",
    color: "#0067B8",
  },
  {
    key: "Screening",
    label: "Screening",
    color: "#D97706",
  },
  {
    key: "Interview",
    label: "Interview",
    color: "#7C3AED",
  },
  {
    key: "Trade Test",
    label: "Trade Test",
    color: "#7C3AED",
  },
  {
    key: "Medical",
    label: "Medical",
    color: "#D97706",
  },
  {
    key: "Visa Processing",
    label: "Visa Processing",
    color: "#D97706",
  },
  {
    key: "Ticketing",
    label: "Ticketing",
    color: "#0067B8",
  },
  {
    key: "Onboarding",
    label: "Onboarding",
    color: "#16A34A",
  },
  {
    key: "Deployment",
    label: "Deployment",
    color: "#16A34A",
  },
  {
    key: "Completed",
    label: "Completed",
    color: "#16A34A",
  },
]

function formatDate(value) {
  if (!value) return "—"

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return "—"
  }

  return date.toLocaleDateString()
}

function getCandidateName(application) {
  const name = [
    application.candidate_first_name,
    application.candidate_last_name,
  ]
    .filter(Boolean)
    .join(" ")

  return name || "Unnamed Candidate"
}

function getStage(application) {
  const workflowStatus = application.workflow_status || "Applied"

  return (
    PIPELINE_STAGES.find((stage) => stage.key === workflowStatus) ||
    PIPELINE_STAGES[0]
  )
}

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
        const response = await authenticatedFetch(
          `/api/hiring?organization_id=${encodeURIComponent(organizationId)}`,
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

  const groupedApplications = useMemo(() => {
    return PIPELINE_STAGES.reduce((groups, stage) => {
      groups[stage.key] = applications.filter(
        (application) => getStage(application).key === stage.key,
      )
      return groups
    }, {})
  }, [applications])

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
                Track candidates from application through onboarding and
                deployment.
              </p>
            </div>
            <div className="page-section-meta">
              <strong>{applications.length}</strong>
              <span>applications</span>
            </div>
          </div>

          {loading && <p>Loading hiring pipeline...</p>}

          {error && <p role="alert">{error}</p>}

          {!loading && !error && (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: `repeat(${PIPELINE_STAGES.length}, minmax(250px, 1fr))`,
                gap: "16px",
                overflowX: "auto",
                paddingBottom: "12px",
              }}
            >
              {PIPELINE_STAGES.map((stage) => {
                const stageApplications = groupedApplications[stage.key] || []

                return (
                  <div
                    key={stage.key}
                    style={{
                      minHeight: "360px",
                      background: "#f8fafc",
                      border: "1px solid #e2e8f0",
                      borderRadius: "12px",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        padding: "14px 16px",
                        borderTop: `4px solid ${stage.color}`,
                        background: "#ffffff",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          gap: "12px",
                        }}
                      >
                        <h3
                          style={{
                            margin: 0,
                            fontSize: "15px",
                            fontWeight: 700,
                          }}
                        >
                          {stage.label}
                        </h3>

                        <span
                          style={{
                            minWidth: "28px",
                            height: "28px",
                            padding: "0 8px",
                            borderRadius: "999px",
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: stage.color,
                            color: "#ffffff",
                            fontSize: "13px",
                            fontWeight: 700,
                          }}
                        >
                          {stageApplications.length}
                        </span>
                      </div>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "12px",
                        padding: "12px",
                      }}
                    >
                      {stageApplications.length === 0 ? (
                        <div
                          style={{
                            padding: "24px 12px",
                            textAlign: "center",
                            color: "#64748b",
                            fontSize: "13px",
                          }}
                        >
                          No candidates
                        </div>
                      ) : (
                        stageApplications.map((application) => (
                          <article
                            key={application.id}
                            style={{
                              background: "#ffffff",
                              border: "1px solid #e2e8f0",
                              borderRadius: "14px",
                              padding: "15px",
                              boxShadow: "0 2px 6px rgba(15, 23, 42, 0.06)",
                            }}
                          >
                            <div
                              style={{
                                display: "flex",
                                alignItems: "flex-start",
                                justifyContent: "space-between",
                                gap: "10px",
                              }}
                            >
                              <div>
                                <h4
                                  style={{
                                    margin: 0,
                                    fontSize: "15px",
                                    fontWeight: 700,
                                    color: "#0f172a",
                                  }}
                                >
                                  {getCandidateName(application)}
                                </h4>

                                <p
                                  style={{
                                    margin: "5px 0 0",
                                    fontSize: "13px",
                                    color: "#64748b",
                                    wordBreak: "break-word",
                                  }}
                                >
                                  {application.candidate_email || "No email"}
                                </p>
                              </div>

                              <span
                                style={{
                                  flexShrink: 0,
                                  padding: "4px 8px",
                                  borderRadius: "999px",
                                  background: `${stage.color}15`,
                                  color: stage.color,
                                  fontSize: "11px",
                                  fontWeight: 700,
                                }}
                              >
                                {stage.label}
                              </span>
                            </div>

                            <div
                              style={{
                                marginTop: "14px",
                                paddingTop: "12px",
                                borderTop: "1px solid #e2e8f0",
                              }}
                            >
                              <p
                                style={{
                                  margin: 0,
                                  fontSize: "13px",
                                  fontWeight: 600,
                                  color: "#334155",
                                }}
                              >
                                {application.job_title || "Untitled position"}
                              </p>

                              <p
                                style={{
                                  margin: "5px 0 0",
                                  fontSize: "12px",
                                  color: "#64748b",
                                }}
                              >
                                Applied {formatDate(application.applied_at)}
                              </p>
                            </div>
                          </article>
                        ))
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </section>
      )}
    </>
  )
}
