import { useEffect, useMemo, useState } from "react"

import PageHeader from "../components/PageHeader"

import { authenticatedFetch } from "../utils/auth"

import { useOrganization } from "../context/OrganizationContext"

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

function getReadinessLabel(source) {
  if (source === "interview_pass") {
    return "Interview Passed"
  }

  if (source === "trade_test_pass") {
    return "Trade Test Passed"
  }

  if (source === "waived") {
    return "Requirement Waived"
  }

  return "Ready for Hiring"
}

function getOfferStatusLabel(status) {
  if (!status) return "Draft"

  return String(status)
}

export default function Hiring() {
  const {
    selectedOrganizationId,
    organizationLoading,
  } = useOrganization()

  const organizationId = selectedOrganizationId || ""

  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(false)
  const [readinessLoading, setReadinessLoading] = useState(false)
  const [error, setError] = useState("")
  const [actionError, setActionError] = useState("")
  const [actionLoading, setActionLoading] = useState("")
  const [offerApplicationId, setOfferApplicationId] = useState("")
  const [offerForm, setOfferForm] = useState({
    offer_title: "",
    employment_type: "",
    salary_amount: "",
    salary_currency: "",
    start_date: "",
    offer_expiry_date: "",
    terms_and_conditions: "",
  })

  const loadHiring = async () => {
    if (!organizationId) {
      setApplications([])
      setReadyCandidates([])
      return
    }

    setLoading(true)
    setReadinessLoading(true)
    setError("")
    setActionError("")

    try {
      const response = await authenticatedFetch(
        `/api/hiring?organization_id=${encodeURIComponent(
          organizationId,
        )}`,
      )

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))

        throw new Error(
          data.detail ||
            `Unable to load hiring records (${response.status})`,
        )
      }

      const data = await response.json()
      const hiringApplications = data.applications || []
      setApplications(hiringApplications)

      const readyResponse = await authenticatedFetch(
        `/api/hiring/ready?organization_id=${encodeURIComponent(
          organizationId,
        )}`,
      )

      if (!readyResponse.ok) {
        const readyData = await readyResponse.json().catch(
          () => ({}),
        )
        throw new Error(
          readyData.detail ||
            `Unable to load ready candidates (${readyResponse.status})`,
        )
      }

      const readyData = await readyResponse.json()
      const readyApplications = readyData.applications || []

      const candidateApplications = readyApplications.map(
        (application) => ({
          application,
          readiness: {
            application_id: application.id,
            application_status: application.status,
            readiness_source: null,
            hiring_record_id: null,
            hiring_status: null,
          },
        }),
      )

      for (const item of candidateApplications) {
        const readinessResponse = await authenticatedFetch(
          `/api/hiring/${encodeURIComponent(
            item.application.id,
          )}/readiness?organization_id=${encodeURIComponent(
            organizationId,
          )}`,
        )

        if (readinessResponse.ok) {
          const readinessData = await readinessResponse.json()
          item.readiness =
            readinessData.readiness || item.readiness
        }
      }


    } catch (err) {
      setError(err.message || "Unable to load hiring records.")
    } finally {
      setLoading(false)
      setReadinessLoading(false)
    }
  }

  useEffect(() => {
    if (organizationLoading || !organizationId) {
      setApplications([])
      setReadyCandidates([])
      return
    }

    let cancelled = false

    async function load() {
      if (cancelled) return
      await loadHiring()
    }

    load()

    return () => {
      cancelled = true
    }
  }, [organizationId, organizationLoading])

  const readyCandidates = useMemo(
    () =>
      applications
        .filter(
          (application) =>
            application.hiring_status === "ready_for_hiring",
        )
        .map((application) => ({
          application,
          readiness: {
            readiness_source: "waived",
            hiring_record_id: application.id,
          },
        })),
    [applications],
  )

  const offers = useMemo(
    () =>
      applications.filter(
        (application) =>
          application.hiring_status === "offered",
      ),
    [applications],
  )

  const hired = useMemo(
    () =>
      applications.filter(
        (application) => application.hiring_status === "hired",
      ),
    [applications],
  )

  const createReadyRecord = async (applicationId) => {
    setActionLoading(applicationId)
    setActionError("")

    try {
      const readinessResponse = await authenticatedFetch(
        `/api/hiring/${encodeURIComponent(
          applicationId,
        )}/readiness?organization_id=${encodeURIComponent(
          organizationId,
        )}`,
      )

      const readinessData = await readinessResponse.json()

      if (!readinessResponse.ok) {
        throw new Error(
          readinessData.detail ||
            "Unable to verify hiring readiness.",
        )
      }

      const readiness = readinessData.readiness

      if (!readiness?.readiness_source) {
        throw new Error(
          "This candidate is not currently ready for hiring.",
        )
      }

      const response = await authenticatedFetch(
        `/api/hiring/${encodeURIComponent(
          applicationId,
        )}/ready?organization_id=${encodeURIComponent(
          organizationId,
        )}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            readiness_source: readiness.readiness_source,
          }),
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to move candidate to Hiring.",
        )
      }

      await loadHiring()
    } catch (err) {
      setActionError(
        err.message || "Unable to move candidate to Hiring.",
      )
    } finally {
      setActionLoading("")
    }
  }

  const createOffer = async (applicationId) => {
    setActionLoading(applicationId)
    setActionError("")

    try {
      if (!offerForm.offer_title.trim()) {
        throw new Error("Offer Title is required.")
      }

      const payload = {
        offer_title: offerForm.offer_title.trim(),
        employment_type:
          offerForm.employment_type.trim() || null,
        salary_amount:
          offerForm.salary_amount === ""
            ? null
            : Number(offerForm.salary_amount),
        salary_currency:
          offerForm.salary_currency.trim() || null,
        start_date: offerForm.start_date || null,
        offer_expiry_date:
          offerForm.offer_expiry_date || null,
        terms_and_conditions:
          offerForm.terms_and_conditions.trim() || null,
      }

      if (
        payload.salary_amount !== null &&
        Number.isNaN(payload.salary_amount)
      ) {
        throw new Error("Salary Amount must be a valid number.")
      }

      const response = await authenticatedFetch(
        `/api/hiring/${encodeURIComponent(
          applicationId,
        )}/offer?organization_id=${encodeURIComponent(
          organizationId,
        )}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        },
      )

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to create offer.",
        )
      }

      setOfferApplicationId("")
      setOfferForm({
        offer_title: "",
        employment_type: "",
        salary_amount: "",
        salary_currency: "",
        start_date: "",
        offer_expiry_date: "",
        terms_and_conditions: "",
      })

      await loadHiring()
    } catch (err) {
      setActionError(
        err.message || "Unable to create offer.",
      )
    } finally {
      setActionLoading("")
    }
  }

  const sendOffer = async (applicationId, offerId) => {
    setActionLoading(applicationId)
    setActionError("")

    try {
      const response = await authenticatedFetch(
        `/api/hiring/${encodeURIComponent(
          applicationId,
        )}/offer/${encodeURIComponent(
          offerId,
        )}/send?organization_id=${encodeURIComponent(
          organizationId,
        )}`,
        {
          method: "POST",
        },
      )

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to send the offer.",
        )
      }

      await loadHiring()
    } catch (err) {
      setActionError(
        err.message ||
          "Unable to send the offer.",
      )
    } finally {
      setActionLoading("")
    }
  }

  const hireCandidate = async (applicationId, offerId) => {
    setActionLoading(applicationId)
    setActionError("")

    try {
      const response = await authenticatedFetch(
        `/api/hiring/${encodeURIComponent(
          applicationId,
        )}/hire?organization_id=${encodeURIComponent(
          organizationId,
        )}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            offer_id: offerId,
          }),
        },
      )

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to mark candidate as hired.",
        )
      }

      await loadHiring()
    } catch (err) {
      setActionError(
        err.message ||
          "Unable to complete hiring.",
      )
    } finally {
      setActionLoading("")
    }
  }

  const renderCandidateCard = (
    application,
    {
      readinessSource = null,
      statusSource = "offer",
      showReadyAction = false,
      showOfferAction = false,
      showHireAction = false,
    } = {},
  ) => {
    const name = getCandidateName(application)

    return (
      <article
        key={application.id}
        style={{
          background: "#ffffff",
          border: "1px solid #E2E8F0",
          borderRadius: "14px",
          padding: "18px",
          boxShadow: "0 2px 8px rgba(15, 23, 42, 0.05)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: "14px",
          }}
        >
          <div>
            <h3
              style={{
                margin: 0,
                color: "#0F172A",
                fontSize: "17px",
                fontWeight: 700,
              }}
            >
              {name}
            </h3>

            <p
              style={{
                margin: "6px 0 0",
                color: "#475569",
                fontSize: "14px",
              }}
            >
              {application.job_title || "Position not specified"}
            </p>
          </div>

          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              borderRadius: "999px",
              padding: "5px 10px",
              background: "#EFF6FF",
              color: "#0067B8",
              fontSize: "12px",
              fontWeight: 700,
              whiteSpace: "nowrap",
            }}
          >
            {readinessSource
              ? getReadinessLabel(readinessSource)
              : getOfferStatusLabel(
                  statusSource === "hiring"
                    ? application.hiring_status
                    : application.offer_status ||
                        application.hiring_status,
                )}
          </span>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "10px",
            marginTop: "16px",
          }}
        >
          <div>
            <span
              style={{
                display: "block",
                color: "#64748B",
                fontSize: "12px",
                marginBottom: "3px",
              }}
            >
              Email
            </span>

            <strong
              style={{
                color: "#0F172A",
                fontSize: "13px",
                fontWeight: 600,
                wordBreak: "break-word",
              }}
            >
              {application.candidate_email || "—"}
            </strong>
          </div>

          <div>
            <span
              style={{
                display: "block",
                color: "#64748B",
                fontSize: "12px",
                marginBottom: "3px",
              }}
            >
              Applied
            </span>

            <strong
              style={{
                color: "#0F172A",
                fontSize: "13px",
                fontWeight: 600,
              }}
            >
              {formatDate(application.applied_at)}
            </strong>
          </div>
        </div>

        {showReadyAction && (
          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              marginTop: "18px",
              paddingTop: "15px",
              borderTop: "1px solid #E2E8F0",
            }}
          >
            <button
              type="button"
              className="primary-action"
              disabled={actionLoading === application.id}
              onClick={() => createReadyRecord(application.id)}
            >
              {actionLoading === application.id
                ? "Processing..."
                : "Ready for Hiring"}
            </button>
          </div>
        )}

        {showOfferAction && (
          <div
            style={{
              marginTop: "18px",
              paddingTop: "15px",
              borderTop: "1px solid #E2E8F0",
            }}
          >
            {offerApplicationId === application.id ? (
              <div>
                <h4
                  style={{
                    margin: "0 0 14px",
                    color: "#0F172A",
                    fontSize: "15px",
                    fontWeight: 700,
                  }}
                >
                  Create Offer
                </h4>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns:
                      "repeat(auto-fit, minmax(180px, 1fr))",
                    gap: "12px",
                  }}
                >
                  <label
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                    }}
                  >
                    <span
                      style={{
                        color: "#475569",
                        fontSize: "12px",
                        fontWeight: 600,
                      }}
                    >
                      Offer Title *
                    </span>
                    <input
                      type="text"
                      value={offerForm.offer_title}
                      onChange={(event) =>
                        setOfferForm((current) => ({
                          ...current,
                          offer_title: event.target.value,
                        }))
                      }
                      placeholder="e.g. Network Engineer Offer"
                    />
                  </label>

                  <label
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                    }}
                  >
                    <span
                      style={{
                        color: "#475569",
                        fontSize: "12px",
                        fontWeight: 600,
                      }}
                    >
                      Employment Type
                    </span>
                    <select
                      value={offerForm.employment_type}
                      onChange={(event) =>
                        setOfferForm((current) => ({
                          ...current,
                          employment_type: event.target.value,
                        }))
                      }
                    >
                      <option value="">Select type</option>
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                      <option value="Temporary">Temporary</option>
                    </select>
                  </label>

                  <label
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                    }}
                  >
                    <span
                      style={{
                        color: "#475569",
                        fontSize: "12px",
                        fontWeight: 600,
                      }}
                    >
                      Salary Amount
                    </span>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={offerForm.salary_amount}
                      onChange={(event) =>
                        setOfferForm((current) => ({
                          ...current,
                          salary_amount: event.target.value,
                        }))
                      }
                      placeholder="e.g. 50000"
                    />
                  </label>

                  <label
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                    }}
                  >
                    <span
                      style={{
                        color: "#475569",
                        fontSize: "12px",
                        fontWeight: 600,
                      }}
                    >
                      Currency
                    </span>
                    <input
                      type="text"
                      value={offerForm.salary_currency}
                      onChange={(event) =>
                        setOfferForm((current) => ({
                          ...current,
                          salary_currency: event.target.value,
                        }))
                      }
                      placeholder="e.g. BDT"
                    />
                  </label>

                  <label
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                    }}
                  >
                    <span
                      style={{
                        color: "#475569",
                        fontSize: "12px",
                        fontWeight: 600,
                      }}
                    >
                      Start Date
                    </span>
                    <input
                      type="date"
                      value={offerForm.start_date}
                      onChange={(event) =>
                        setOfferForm((current) => ({
                          ...current,
                          start_date: event.target.value,
                        }))
                      }
                    />
                  </label>

                  <label
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                    }}
                  >
                    <span
                      style={{
                        color: "#475569",
                        fontSize: "12px",
                        fontWeight: 600,
                      }}
                    >
                      Offer Expiry Date
                    </span>
                    <input
                      type="date"
                      value={offerForm.offer_expiry_date}
                      onChange={(event) =>
                        setOfferForm((current) => ({
                          ...current,
                          offer_expiry_date: event.target.value,
                        }))
                      }
                    />
                  </label>
                </div>

                <label
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "6px",
                    marginTop: "12px",
                  }}
                >
                  <span
                    style={{
                      color: "#475569",
                      fontSize: "12px",
                      fontWeight: 600,
                    }}
                  >
                    Terms & Conditions
                  </span>
                  <textarea
                    rows="4"
                    value={offerForm.terms_and_conditions}
                    onChange={(event) =>
                      setOfferForm((current) => ({
                        ...current,
                        terms_and_conditions:
                          event.target.value,
                      }))
                    }
                    placeholder="Enter offer terms and conditions"
                  />
                </label>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "flex-end",
                    gap: "10px",
                    marginTop: "14px",
                  }}
                >
                  <button
                    type="button"
                    className="secondary-action"
                    disabled={
                      actionLoading === application.id
                    }
                    onClick={() => {
                      setOfferApplicationId("")
                      setActionError("")
                    }}
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    className="primary-action"
                    disabled={
                      actionLoading === application.id
                    }
                    onClick={() =>
                      createOffer(application.id)
                    }
                  >
                    {actionLoading === application.id
                      ? "Creating..."
                      : "Create Draft Offer"}
                  </button>
                </div>
              </div>
            ) : (
              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                }}
              >
                <button
                  type="button"
                  className="primary-action"
                  onClick={() => {
                    setOfferApplicationId(application.id)
                    setActionError("")
                  }}
                >
                  Create Offer
                </button>
              </div>
            )}
          </div>
        )}
        {showHireAction &&
          application.offer_status === "Draft" &&
          application.offer_id && (
            <div
              style={{
                marginTop: "18px",
                paddingTop: "15px",
                borderTop: "1px solid #E2E8F0",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "12px",
              }}
            >
              <div>
                <div
                  style={{
                    color: "#0F172A",
                    fontSize: "14px",
                    fontWeight: 700,
                  }}
                >
                  Draft offer
                </div>
                <div
                  style={{
                    marginTop: "3px",
                    color: "#64748B",
                    fontSize: "12px",
                  }}
                >
                  Review the offer details before sending it to the candidate.
                </div>
              </div>
              <button
                type="button"
                className="primary-action"
                disabled={
                  actionLoading === application.id
                }
                onClick={() =>
                  sendOffer(
                    application.id,
                    application.offer_id,
                  )
                }
              >
                {actionLoading === application.id
                  ? "Sending..."
                  : "Send Offer"}
              </button>
            </div>
          )}

        {showHireAction &&
          application.offer_status === "Accepted" &&
          application.offer_id && (
            <div
              style={{
                marginTop: "18px",
                paddingTop: "15px",
                borderTop: "1px solid #E2E8F0",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "12px",
              }}
            >
              <div>
                <div
                  style={{
                    color: "#0F172A",
                    fontSize: "14px",
                    fontWeight: 700,
                  }}
                >
                  Offer accepted
                </div>
                <div
                  style={{
                    marginTop: "3px",
                    color: "#64748B",
                    fontSize: "12px",
                  }}
                >
                  This candidate is ready to be marked as hired.
                </div>
              </div>

              <button
                type="button"
                className="primary-action"
                disabled={
                  actionLoading === application.id
                }
                onClick={() =>
                  hireCandidate(
                    application.id,
                    application.offer_id,
                  )
                }
              >
                {actionLoading === application.id
                  ? "Processing..."
                  : "Mark as Hired"}
              </button>
            </div>
          )}

      </article>
    )
  }

  return (
    <>
      <PageHeader
        title="Hiring"
        subtitle="Manage candidates who are ready for offers and final hiring."
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
              <h2>Hiring Workflow</h2>

              <p>
                Move qualified candidates from hiring readiness to
                offers and completed hires.
              </p>
            </div>
          </div>

          {loading && (
            <p>Loading hiring workflow...</p>
          )}

          {error && (
            <p role="alert">
              {error}
            </p>
          )}

          {actionError && (
            <p
              role="alert"
              style={{
                marginTop: "12px",
                color: "#B91C1C",
              }}
            >
              {actionError}
            </p>
          )}

          {!loading && !error && (
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(3, minmax(0, 1fr))",
                gap: "18px",
                marginTop: "20px",
              }}
            >
              <section
                style={{
                  minWidth: 0,
                  background: "#F8FAFC",
                  border: "1px solid #E2E8F0",
                  borderRadius: "14px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    padding: "16px 18px",
                    background: "#ffffff",
                    borderTop: "4px solid #0067B8",
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
                    <div>
                      <h3
                        style={{
                          margin: 0,
                          color: "#0F172A",
                        }}
                      >
                        Ready for Hiring
                      </h3>

                      <p
                        style={{
                          margin: "5px 0 0",
                          color: "#64748B",
                          fontSize: "13px",
                        }}
                      >
                        Candidates who completed the required
                        selection step.
                      </p>
                    </div>

                    <strong
                      style={{
                        color: "#0067B8",
                        fontSize: "20px",
                      }}
                    >
                      {readinessLoading
                        ? "—"
                        : readyCandidates.length}
                    </strong>
                  </div>
                </div>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                    padding: "14px",
                  }}
                >
                  {readyCandidates.length === 0 ? (
                    <div
                      style={{
                        padding: "30px 16px",
                        textAlign: "center",
                        color: "#64748B",
                        fontSize: "14px",
                      }}
                    >
                      No candidates ready for hiring.
                    </div>
                  ) : (
                    readyCandidates.map(
                      ({ application, readiness }) =>
                        renderCandidateCard(application, {
                          readinessSource:
                            readiness.readiness_source,
                          showReadyAction:
                            !readiness.hiring_record_id &&
                            Boolean(
                              readiness.readiness_source,
                            ),
                          showOfferAction: true,
                        }),
                    )
                  )}
                </div>
              </section>

              <section
                style={{
                  minWidth: 0,
                  background: "#F8FAFC",
                  border: "1px solid #E2E8F0",
                  borderRadius: "14px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    padding: "16px 18px",
                    background: "#ffffff",
                    borderTop: "4px solid #D97706",
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
                    <div>
                      <h3
                        style={{
                          margin: 0,
                          color: "#0F172A",
                        }}
                      >
                        Offers
                      </h3>

                      <p
                        style={{
                          margin: "5px 0 0",
                          color: "#64748B",
                          fontSize: "13px",
                        }}
                      >
                        Candidates with an active hiring offer.
                      </p>
                    </div>

                    <strong
                      style={{
                        color: "#D97706",
                        fontSize: "20px",
                      }}
                    >
                      {offers.length}
                    </strong>
                  </div>
                </div>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                    padding: "14px",
                  }}
                >
                  {offers.length === 0 ? (
                    <div
                      style={{
                        padding: "30px 16px",
                        textAlign: "center",
                        color: "#64748B",
                        fontSize: "14px",
                      }}
                    >
                      No active offers.
                    </div>
                  ) : (
                    offers.map((application) =>
                      renderCandidateCard(application, {
                        showHireAction: true,
                      })
                    )
                  )}
                </div>
              </section>

              <section
                style={{
                  minWidth: 0,
                  background: "#F8FAFC",
                  border: "1px solid #E2E8F0",
                  borderRadius: "14px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    padding: "16px 18px",
                    background: "#ffffff",
                    borderTop: "4px solid #16A34A",
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
                    <div>
                      <h3
                        style={{
                          margin: 0,
                          color: "#0F172A",
                        }}
                      >
                        Hired
                      </h3>

                      <p
                        style={{
                          margin: "5px 0 0",
                          color: "#64748B",
                          fontSize: "13px",
                        }}
                      >
                        Candidates whose hiring process is complete.
                      </p>
                    </div>

                    <strong
                      style={{
                        color: "#16A34A",
                        fontSize: "20px",
                      }}
                    >
                      {hired.length}
                    </strong>
                  </div>
                </div>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                    padding: "14px",
                  }}
                >
                  {hired.length === 0 ? (
                    <div
                      style={{
                        padding: "30px 16px",
                        textAlign: "center",
                        color: "#64748B",
                        fontSize: "14px",
                      }}
                    >
                      No completed hires.
                    </div>
                  ) : (
                    hired.map((application) =>
                      renderCandidateCard(application, {
                        statusSource: "hiring",
                      }),
                    )
                  )}
                </div>
              </section>
            </div>
          )}
        </section>
      )}
    </>
  )
}
