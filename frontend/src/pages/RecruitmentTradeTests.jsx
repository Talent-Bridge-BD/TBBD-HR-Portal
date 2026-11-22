import { Fragment, useEffect, useMemo, useState } from "react";

import PageHeader from "../components/PageHeader";

import { authenticatedFetch } from '../utils/auth'
import { useOrganization } from '../context/OrganizationContext'
export default function RecruitmentTradeTests({ auth }) {
  const {
    selectedOrganizationId,
    organizationLoading,
  } = useOrganization();

  const organizationId = selectedOrganizationId || "";
  const [applications, setApplications] = useState([]);
  const [tradeTests, setTradeTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [search, setSearch] = useState("");
  const [selectedApplicationId, setSelectedApplicationId] = useState("");
  const [testType, setTestType] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [selectedTradeTests, setSelectedTradeTests] = useState([]);
  const [selectedTradeTestId, setSelectedTradeTestId] = useState("");
  const [assessmentScores, setAssessmentScores] = useState({
    technical_knowledge_score: "",
    trade_skills_score: "",
    safety_awareness_score: "",
    tool_handling_score: "",
    communication_score: "",
    problem_solving_score: "",
    teamwork_score: "",
  });
  const [assessmentNotes, setAssessmentNotes] = useState("");

  useEffect(() => {
    if (organizationLoading || !organizationId) {
      setLoading(false);
      return;
    }

    authenticatedFetch(
      `/api/applications?organization_id=${encodeURIComponent(
        organizationId
      )}`,
      {
        credentials: "include",
      }
    )
      .then(async (response) => {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Unable to load applications."
          );
        }

        return data;
      })
      .then((data) => {
  const eligibleApplications = (data.applications || []).filter(
    (application) =>
      String(application.status || '').toLowerCase() === 'shortlisted'
  );

  setApplications(eligibleApplications);
})
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [organizationId, organizationLoading]);

  useEffect(() => {
    if (organizationLoading || !organizationId) {
      setTradeTests([]);
      return;
    }

    authenticatedFetch(
      `/api/trade-tests?organization_id=${encodeURIComponent(
        organizationId
      )}`,
      {
        credentials: "include",
      }
    )
      .then(async (response) => {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Unable to load trade tests."
          );
        }

        return data;
      })
      .then((data) => {
        setTradeTests(data.trade_tests || []);
      })
      .catch((err) => {
        setError(err.message);
        setTradeTests([]);
      });
  }, [organizationId, organizationLoading]);

  useEffect(() => {
    if (
      organizationLoading ||
      !organizationId ||
      !selectedApplicationId
    ) {
      setSelectedTradeTests([]);
      return;
    }

    authenticatedFetch(
      `/api/trade-tests/application/${encodeURIComponent(
        selectedApplicationId
      )}?organization_id=${encodeURIComponent(organizationId)}`,
      {
        credentials: "include",
      }
    )
      .then(async (response) => {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Unable to load trade tests."
          );
        }

        return data;
      })
      .then((data) => {
        setSelectedTradeTests(data.trade_tests || []);
      })
      .catch((err) => {
        setError(err.message);
      });
  }, [organizationId, organizationLoading, selectedApplicationId]);

  const filteredTradeTests = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return tradeTests;
    }

    return tradeTests.filter((tradeTest) =>
      [
        tradeTest.test_type,
        tradeTest.location,
        tradeTest.assessor_name,
        tradeTest.status,
        tradeTest.result,
        tradeTest.scheduled_at,
      ]
        .filter(Boolean)
        .some((value) =>
          String(value).toLowerCase().includes(query)
        )
    );
  }, [tradeTests, search]);

  const formatDate = (value) => {
    if (!value) {
      return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString();
  };

  const getStatusClass = (status) => {
    const normalized = String(status || "").toLowerCase();

    if (normalized === "completed") {
      return "trade-test-status trade-test-status-completed";
    }

    if (normalized === "scheduled") {
      return "trade-test-status trade-test-status-scheduled";
    }

    return "trade-test-status";
  };

  const getResultClass = (result) => {
    const normalized = String(result || "").toLowerCase();

    if (normalized === "pass" || normalized === "passed") {
      return "trade-test-result trade-test-result-pass";
    }

    if (normalized === "fail" || normalized === "failed") {
      return "trade-test-result trade-test-result-fail";
    }

    return "trade-test-result";
  };

  const handleSaveAssessment = async (tradeTestId) => {
    setError("");

    if (!organizationId) {
      setError("Organization access is required.");
      return;
    }

    const scores = Object.values(assessmentScores);

    if (scores.some((score) => score === "")) {
      setError("Please enter all seven assessment scores.");
      return;
    }

    const numericScores = Object.fromEntries(
      Object.entries(assessmentScores).map(([field, score]) => [
        field,
        Number(score),
      ])
    );

    if (
      Object.values(numericScores).some(
        (score) => !Number.isInteger(score) || score < 0 || score > 100
      )
    ) {
      setError("Each assessment score must be an integer from 0 to 100.");
      return;
    }

    try {
      const response = await authenticatedFetch(
        `/api/trade-tests/${encodeURIComponent(
          tradeTestId
        )}/assessment?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          method: "PUT",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ...numericScores,
            assessment_notes: assessmentNotes || null,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to save trade test assessment."
        );
      }

      setSelectedTradeTests((current) =>
        current.map((tradeTest) =>
          tradeTest.id === tradeTestId
            ? data.trade_test
            : tradeTest
        )
      );

      setTradeTests((current) =>
        current.map((tradeTest) =>
          tradeTest.id === tradeTestId
            ? data.trade_test
            : tradeTest
        )
      );

      setAssessmentScores({
        technical_knowledge_score: "",
        trade_skills_score: "",
        safety_awareness_score: "",
        tool_handling_score: "",
        communication_score: "",
        problem_solving_score: "",
        teamwork_score: "",
      });
      setAssessmentNotes("");
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSaveSchedule = async () => {
    setError("");

    if (!organizationId) {
      setError("Organization access is required.");
      return;
    }

    if (!selectedApplicationId) {
      setError("Please select a candidate.");
      return;
    }

    try {
      const response = await authenticatedFetch(
        `/api/trade-tests?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            application_id: selectedApplicationId,
            test_type: testType || null,
            scheduled_at: scheduledAt
              ? new Date(scheduledAt).toISOString()
              : null,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to schedule trade test."
        );
      }

      setShowScheduleForm(false);
      setTestType("");
      setScheduledAt("");

      const refreshResponse = await authenticatedFetch(
        `/api/trade-tests/application/${encodeURIComponent(
          selectedApplicationId
        )}?organization_id=${encodeURIComponent(organizationId)}`,
        {
          credentials: "include",
        }
      );

      const refreshData = await refreshResponse.json();

      if (!refreshResponse.ok) {
        throw new Error(
          refreshData.detail || "Unable to refresh trade tests."
        );
      }

      setSelectedTradeTests(refreshData.trade_tests || []);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <PageHeader
        title="Trade Tests"
        subtitle="Manage practical skill assessments from scheduling through final results."
      />

      <div className="trade-test-page">
        <div className="trade-test-kpi-grid">
          <section className="trade-test-kpi-card">
            <div className="trade-test-kpi-icon" aria-hidden="true">◷</div>
            <div>
              <span className="trade-test-kpi-label">Scheduled Tests</span>
              <strong>
                {
                  tradeTests.filter(
                    (tradeTest) =>
                      String(tradeTest.status || "").toLowerCase() ===
                      "scheduled"
                  ).length
                }
              </strong>
              <small>Upcoming assessments</small>
            </div>
          </section>

          <section className="trade-test-kpi-card">
            <div className="trade-test-kpi-icon" aria-hidden="true">✓</div>
            <div>
              <span className="trade-test-kpi-label">Completed Tests</span>
              <strong>
                {
                  tradeTests.filter(
                    (tradeTest) =>
                      String(tradeTest.status || "").toLowerCase() ===
                      "completed"
                  ).length
                }
              </strong>
              <small>Assessments completed</small>
            </div>
          </section>

          <section className="trade-test-kpi-card trade-test-kpi-success">
            <div className="trade-test-kpi-icon" aria-hidden="true">✓</div>
            <div>
              <span className="trade-test-kpi-label">Passed</span>
              <strong>
                {
                  tradeTests.filter(
                    (tradeTest) =>
                      String(tradeTest.result || "").toLowerCase() === "pass"
                  ).length
                }
              </strong>
              <small>Successful assessments</small>
            </div>
          </section>

          <section className="trade-test-kpi-card trade-test-kpi-danger">
            <div className="trade-test-kpi-icon" aria-hidden="true">×</div>
            <div>
              <span className="trade-test-kpi-label">Failed</span>
              <strong>
                {
                  tradeTests.filter(
                    (tradeTest) =>
                      String(tradeTest.result || "").toLowerCase() === "fail"
                  ).length
                }
              </strong>
              <small>Unsuccessful assessments</small>
            </div>
          </section>
        </div>

        <section className="trade-test-workspace">
          <div className="trade-test-workspace-header">
            <div>
              <span className="trade-test-eyebrow">PRACTICAL ASSESSMENT</span>
              <h2>Candidate Trade Tests</h2>
              <p>
                Schedule, assess and review practical skill tests for shortlisted
                candidates.
              </p>
            </div>

            <div className="trade-test-header-actions">
              <span className="trade-test-count">
                {filteredTradeTests.length}{" "}
                {filteredTradeTests.length === 1 ? "test" : "tests"}
              </span>

              {applications.length > 0 && (
                <button
                  type="button"
                  className="trade-test-primary-button"
                  onClick={() => setShowScheduleForm(true)}
                >
                  <span>+</span>
                  Schedule Test
                </button>
              )}
            </div>
          </div>

          <div className="trade-test-toolbar">
            <label className="trade-test-search">
              <span className="trade-test-search-icon">⌕</span>
              <span className="sr-only">Search trade tests</span>
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search by test type, location, assessor or status..."
              />
            </label>
          </div>

          {error && (
            <div className="trade-test-error" role="alert">
              {error}
            </div>
          )}

          {!organizationId ? (
            <div className="trade-test-state">
              <div className="trade-test-state-icon">!</div>
              <strong>Organization access required</strong>
              <span>
                Your account is not currently assigned to an organization.
              </span>
            </div>
          ) : loading ? (
            <div className="trade-test-state">
              <div className="trade-test-state-icon">…</div>
              <strong>Loading trade tests</strong>
              <span>Retrieving candidates and assessment records.</span>
            </div>
          ) : applications.length === 0 ? (
            <div className="trade-test-state">
              <div className="trade-test-state-icon">✓</div>
              <strong>No candidates ready for trade testing</strong>
              <span>
                Shortlisted candidate applications will appear here when they
                become eligible for a practical assessment.
              </span>
            </div>
          ) : (
            <>
              <section className="trade-test-ready-panel">
                <div className="trade-test-ready-copy">
                  <div className="trade-test-ready-icon" aria-hidden="true">✓</div>

                  <div>
                    <span className="trade-test-eyebrow">READY FOR TESTING</span>

                    <h3>
                      {applications.length}{" "}
                      {applications.length === 1 ? "candidate" : "candidates"}{" "}
                      ready for trade testing
                    </h3>

                    <p>
                      These candidates have reached the shortlisted stage and
                      can now be scheduled for a practical assessment.
                    </p>
                  </div>
                </div>

                <div className="trade-test-ready-candidates">
                  {applications.map((application) => (
                    <div
                      key={application.id}
                      className="trade-test-ready-candidate"
                    >
                      <div className="trade-test-ready-candidate-avatar">
                        {`${application.candidate_first_name?.[0] || ""}${
                          application.candidate_last_name?.[0] || ""
                        }`}
                      </div>

                      <div className="trade-test-ready-candidate-info">
                        <strong>
                          {application.candidate_first_name}{" "}
                          {application.candidate_last_name}
                        </strong>

                        <span>{application.job_title}</span>

                        {application.candidate_email && (
                          <span>{application.candidate_email}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  type="button"
                  className="trade-test-secondary-button"
                  onClick={() => setShowScheduleForm(true)}
                >
                  Schedule a Test
                </button>
              </section>

              {showScheduleForm && (
                <section className="trade-test-form-card">
                  <div className="trade-test-form-header">
                    <div>
                      <span className="trade-test-eyebrow">NEW ASSESSMENT</span>
                      <h3>Schedule a Trade Test</h3>
                      <p>
                        Select a shortlisted candidate and set the assessment
                        details.
                      </p>
                    </div>

                    <button
                      type="button"
                      className="trade-test-close-button"
                      aria-label="Close schedule form"
                      onClick={() => setShowScheduleForm(false)}
                    >
                      ×
                    </button>
                  </div>

                  <div className="trade-test-form-grid">
                    <label className="trade-test-field trade-test-field-wide">
                      <span>Candidate</span>
                      <select
                        value={selectedApplicationId}
                        onChange={(event) =>
                          setSelectedApplicationId(event.target.value)
                        }
                      >
                        <option value="">Select candidate</option>
                        {applications.map((application) => (
                          <option key={application.id} value={application.id}>
                            {application.candidate_first_name}{" "}
                            {application.candidate_last_name} —{" "}
                            {application.job_title}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label className="trade-test-field">
                      <span>Trade Test Type</span>
                      <input
                        type="text"
                        value={testType}
                        onChange={(event) => setTestType(event.target.value)}
                        placeholder="e.g. Welding"
                      />
                    </label>

                    <label className="trade-test-field">
                      <span>Scheduled Date &amp; Time</span>
                      <input
                        type="datetime-local"
                        value={scheduledAt}
                        onChange={(event) => setScheduledAt(event.target.value)}
                      />
                    </label>
                  </div>

                  <div className="trade-test-form-footer">
                    <button
                      type="button"
                      className="trade-test-secondary-button"
                      onClick={() => setShowScheduleForm(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      className="trade-test-primary-button"
                      onClick={handleSaveSchedule}
                    >
                      Save Schedule
                    </button>
                  </div>
                </section>
              )}

              {selectedTradeTests.length > 0 && (
                <section className="trade-test-assessment-card">
                  <div className="trade-test-section-heading">
                    <div>
                      <span className="trade-test-eyebrow">SELECTED CANDIDATE</span>
                      <h3>Scheduled Trade Tests</h3>
                    </div>
                  </div>

                  {selectedTradeTests.map((tradeTest) => (
                    <Fragment key={tradeTest.id}>
                      <div className="trade-test-summary">
                        <div className="trade-test-summary-main">
                          <div className="trade-test-test-icon" aria-hidden="true">▣</div>
                          <div>
                            <strong>
                              {tradeTest.test_type || "Practical Assessment"}
                            </strong>
                            <span>
                              {tradeTest.scheduled_at
                                ? new Date(
                                    tradeTest.scheduled_at
                                  ).toLocaleString()
                                : "No schedule set"}
                            </span>
                          </div>
                        </div>

                        <div className="trade-test-summary-item">
                          <span>Status</span>
                          <span
                            className={getStatusClass(tradeTest.status)}
                          >
                            {tradeTest.status || "—"}
                          </span>
                        </div>

                        <div className="trade-test-summary-item">
                          <span>Result</span>
                          <span className={getResultClass(tradeTest.result)}>
                            {tradeTest.result || "Pending"}
                          </span>
                        </div>

                        <div className="trade-test-score-box">
                          <span>Total Score</span>
                          <strong>
                            {tradeTest.total_score !== null &&
                            tradeTest.total_score !== undefined
                              ? tradeTest.total_score
                              : "—"}
                          </strong>
                          <small>/ 100</small>
                        </div>

                        {String(tradeTest.status || "").toLowerCase() !==
                          "completed" && (
                          <button
                            type="button"
                            className="trade-test-assess-button"
                            onClick={() => {
                              setSelectedTradeTestId(tradeTest.id);
                              setAssessmentScores({
                                technical_knowledge_score:
                                  tradeTest.technical_knowledge_score ?? "",
                                trade_skills_score:
                                  tradeTest.trade_skills_score ?? "",
                                safety_awareness_score:
                                  tradeTest.safety_awareness_score ?? "",
                                tool_handling_score:
                                  tradeTest.tool_handling_score ?? "",
                                communication_score:
                                  tradeTest.communication_score ?? "",
                                problem_solving_score:
                                  tradeTest.problem_solving_score ?? "",
                                teamwork_score:
                                  tradeTest.teamwork_score ?? "",
                              });
                              setAssessmentNotes(
                                tradeTest.assessment_notes ?? ""
                              );
                            }}
                          >
                            Assess
                          </button>
                        )}
                      </div>

                      {selectedTradeTestId === tradeTest.id &&
                        String(tradeTest.status || "").toLowerCase() !==
                          "completed" && (
                          <div className="trade-test-assessment-form">
                            <div className="trade-test-assessment-heading">
                              <div>
                                <span className="trade-test-eyebrow">
                                  ASSESSMENT
                                </span>
                                <h4>Record Practical Skills</h4>
                              </div>
                              <span>Each category is scored 0–100</span>
                            </div>

                            <div className="trade-test-score-grid">
                              {[
                                [
                                  "technical_knowledge_score",
                                  "Technical Knowledge",
                                ],
                                ["trade_skills_score", "Trade Skills"],
                                ["safety_awareness_score", "Safety Awareness"],
                                ["tool_handling_score", "Tool Handling"],
                                ["communication_score", "Communication"],
                                ["problem_solving_score", "Problem Solving"],
                                ["teamwork_score", "Teamwork"],
                              ].map(([field, label]) => (
                                <label
                                  className="trade-test-score-field"
                                  key={field}
                                >
                                  <span>{label}</span>
                                  <input
                                    type="number"
                                    min="0"
                                    max="100"
                                    value={assessmentScores[field]}
                                    onChange={(event) =>
                                      setAssessmentScores((current) => ({
                                        ...current,
                                        [field]: event.target.value,
                                      }))
                                    }
                                  />
                                </label>
                              ))}
                            </div>

                            <label className="trade-test-field trade-test-notes-field">
                              <span>Assessment Notes</span>
                              <textarea
                                value={assessmentNotes}
                                onChange={(event) =>
                                  setAssessmentNotes(event.target.value)
                                }
                                rows="4"
                                placeholder="Add practical observations, strengths or areas requiring attention..."
                              />
                            </label>

                            <div className="trade-test-form-footer">
                              <button
                                type="button"
                                className="trade-test-secondary-button"
                                onClick={() => {
                                  setSelectedTradeTestId("");
                                  setAssessmentScores({
                                    technical_knowledge_score: "",
                                    trade_skills_score: "",
                                    safety_awareness_score: "",
                                    tool_handling_score: "",
                                    communication_score: "",
                                    problem_solving_score: "",
                                    teamwork_score: "",
                                  });
                                  setAssessmentNotes("");
                                }}
                              >
                                Cancel
                              </button>
                              <button
                                type="button"
                                className="trade-test-primary-button"
                                onClick={() => handleSaveAssessment(tradeTest.id)}
                              >
                                Save Assessment
                              </button>
                            </div>
                          </div>
                        )}
                    </Fragment>
                  ))}
                </section>
              )}

              {!loading &&
                !error &&
                tradeTests.length === 0 && (
                  <div className="trade-test-state trade-test-empty-state">
                    <div className="trade-test-state-icon">TT</div>
                    <strong>No trade tests scheduled yet</strong>
                    <span>
                      Schedule a trade test above to begin the practical
                      assessment stage.
                    </span>
                  </div>
                )}

              {!loading &&
                !error &&
                tradeTests.length > 0 &&
                filteredTradeTests.length === 0 && (
                  <div className="trade-test-state trade-test-empty-state">
                    <div className="trade-test-state-icon">⌕</div>
                    <strong>No matching trade tests</strong>
                    <span>Try a different search term.</span>
                  </div>
                )}

              {!loading &&
                !error &&
                filteredTradeTests.length > 0 && (
                  <div className="trade-test-table-wrap">
                    <table className="trade-test-table">
                      <thead>
                        <tr>
                          <th>Test Type</th>
                          <th>Scheduled</th>
                          <th>Location</th>
                          <th>Assessor</th>
                          <th>Status</th>
                          <th>Result</th>
                          <th>Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredTradeTests.map((tradeTest) => (
                          <tr key={tradeTest.id}>
                            <td>
                              <div className="trade-test-table-primary">
                                <strong>
                                  {tradeTest.test_type ||
                                    "Practical Assessment"}
                                </strong>
                                <span>Trade assessment</span>
                              </div>
                            </td>
                            <td className="trade-test-date">
                              {formatDate(tradeTest.scheduled_at)}
                            </td>
                            <td>{tradeTest.location || "—"}</td>
                            <td>{tradeTest.assessor_name || "—"}</td>
                            <td>
                              <span
                                className={getStatusClass(tradeTest.status)}
                              >
                                {tradeTest.status || "—"}
                              </span>
                            </td>
                            <td>
                              <span
                                className={getResultClass(tradeTest.result)}
                              >
                                {tradeTest.result || "Pending"}
                              </span>
                            </td>
                            <td className="trade-test-score">
                              {tradeTest.total_score ?? "—"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
            </>
          )}
        </section>
      </div>
    </>
  );

}
