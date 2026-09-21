import { Fragment, useEffect, useMemo, useState } from "react";

import PageHeader from "../components/PageHeader";

import { authenticatedFetch } from '../utils/auth'
export default function RecruitmentTradeTests({ auth }) {
  const organizationId = auth?.organization_ids?.[0] || "";
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
    if (!organizationId) {
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
  }, [organizationId]);

  useEffect(() => {
    if (!organizationId) {
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
  }, [organizationId]);

  useEffect(() => {
    if (!organizationId || !selectedApplicationId) {
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
  }, [organizationId, selectedApplicationId]);

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
        subtitle="Manage trade testing and practical skill assessments."
      />

      <div className="trade-test-kpi-grid">
        <section className="dashboard-card trade-test-kpi-card">
          <span className="trade-test-kpi-label">Scheduled Tests</span>
          <strong>{tradeTests.filter((tradeTest) => tradeTest.status === "Scheduled").length}</strong>
          <small>Upcoming assessments</small>
        </section>

        <section className="dashboard-card trade-test-kpi-card">
          <span className="trade-test-kpi-label">Completed Tests</span>
          <strong>{tradeTests.filter((tradeTest) => tradeTest.status === "Completed").length}</strong>
          <small>Assessments completed</small>
        </section>

        <section className="dashboard-card trade-test-kpi-card trade-test-kpi-success">
          <span className="trade-test-kpi-label">Passed</span>
          <strong>{tradeTests.filter((tradeTest) => tradeTest.result === "Pass").length}</strong>
          <small>Successful assessments</small>
        </section>

        <section className="dashboard-card trade-test-kpi-card trade-test-kpi-danger">
          <span className="trade-test-kpi-label">Failed</span>
          <strong>{tradeTests.filter((tradeTest) => tradeTest.result === "Fail").length}</strong>
          <small>Unsuccessful assessments</small>
        </section>
      </div>

      <section className="dashboard-card trade-test-workspace">
        <div className="trade-test-workspace-header">
          <div>
            <h2>Candidate Trade Tests</h2>
            <p>Review scheduled practical assessments and their results.</p>
          </div>

          <div className="trade-test-count">
            {filteredTradeTests.length} test(s)
          </div>
        </div>

        <div className="trade-test-toolbar">
          <label className="trade-test-search">
            <span className="sr-only">Search trade tests</span>
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search test type, location, assessor or status..."
            />
          </label>
        </div>
      </section>

      {!organizationId ? (
        <section className="placeholder-card">
          <h2>Organization access required</h2>
          <p>
            Your account is not currently assigned to an organization.
          </p>
        </section>
      ) : loading ? (
        <section className="placeholder-card">
          <p>Loading applications...</p>
        </section>
      ) : error ? (
        <section className="placeholder-card">
          <h2>Unable to load applications</h2>
          <p>{error}</p>
        </section>
      ) : applications.length === 0 ? (
        <section className="placeholder-card">
          <h2>No applications available</h2>
          <p>
            Candidate applications will appear here when they are available
            for trade testing.
          </p>
        </section>
      ) : (
        <section className="dashboard-card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2>Trade Test Schedule</h2>
              <p>
                {applications.length} application
                {applications.length === 1 ? "" : "s"} available for trade testing.
              </p>
            </div>

            <button
              type="button"
              className="btn-primary"
              onClick={() => setShowScheduleForm(true)}
            >
              Schedule Trade Test
            </button>
          </div>

          {showScheduleForm && (
            <div className="dashboard-card mb-6">
              <h3 className="mb-4">Schedule a Trade Test</h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <label>
                  <span className="block mb-1">Candidate</span>
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

                <label>
                  <span className="block mb-1">Trade Test Type</span>
                  <input
                    type="text"
                    value={testType}
                    onChange={(event) => setTestType(event.target.value)}
                    placeholder="e.g. Welding"
                  />
                </label>

                <label>
                  <span className="block mb-1">Scheduled Date & Time</span>
                  <input
                    type="datetime-local"
                    value={scheduledAt}
                    onChange={(event) => setScheduledAt(event.target.value)}
                  />
                </label>
              </div>

              <div className="flex gap-2 mt-4">
                <button
                  type="button"
                  className="btn-primary"
                  onClick={handleSaveSchedule}
                >
                  Save Schedule
                </button>

                <button
                  type="button"
                  onClick={() => setShowScheduleForm(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {selectedTradeTests.length > 0 && (
            <section className="dashboard-card mb-6">
              <h3 className="mb-4">Scheduled Trade Test</h3>

              {selectedTradeTests.map((tradeTest) => (
                <Fragment key={tradeTest.id}>
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div>
                    <strong>Test Type</strong>
                    <p>{tradeTest.test_type || "Practical Assessment"}</p>
                  </div>

                  <div>
                    <strong>Scheduled</strong>
                    <p>
                      {tradeTest.scheduled_at
                        ? new Date(
                            tradeTest.scheduled_at
                          ).toLocaleString()
                        : "—"}
                    </p>
                  </div>

                  <div>
                    <strong>Status</strong>
                    <p>{tradeTest.status || "—"}</p>
                  </div>

                  <div>
                    <strong>Result</strong>
                    <p>{tradeTest.result || "Pending"}</p>
                  </div>

                  <div>
                    <strong>Total Score</strong>
                    <p>
                      {tradeTest.total_score !== null &&
                      tradeTest.total_score !== undefined
                        ? tradeTest.total_score
                        : "—"}
                    </p>
                  </div>

                  <div>
                    <strong>Action</strong>
                    <button
                      type="button"
                      className="btn-primary mt-2"
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
                  </div>
                </div>

                {selectedTradeTestId === tradeTest.id && (
                <div className="mt-6">
                  <h4 className="mb-4">Trade Test Assessment</h4>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {[
                      ["technical_knowledge_score", "Technical Knowledge"],
                      ["trade_skills_score", "Trade Skills"],
                      ["safety_awareness_score", "Safety Awareness"],
                      ["tool_handling_score", "Tool Handling"],
                      ["communication_score", "Communication"],
                      ["problem_solving_score", "Problem Solving"],
                      ["teamwork_score", "Teamwork"],
                    ].map(([field, label]) => (
                      <label key={field}>
                        <span className="block mb-1">{label}</span>
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

                  <label className="block mt-4">
                    <span className="block mb-1">Assessment Notes</span>
                    <textarea
                      value={assessmentNotes}
                      onChange={(event) =>
                        setAssessmentNotes(event.target.value)
                      }
                      rows="4"
                    />
                  </label>

                  <div className="flex gap-2 mt-4">
                    <button
                      type="button"
                      className="btn-primary"
                      onClick={() => handleSaveAssessment(tradeTest.id)}
                    >
                      Save Assessment
                    </button>

                    <button
                      type="button"
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
              <div className="trade-test-empty-state">
                <strong>No trade tests found</strong>
                <span>
                  Schedule a trade test for a candidate application to begin
                  the practical assessment stage.
                </span>
              </div>
            )}

          {!loading &&
            !error &&
            tradeTests.length > 0 &&
            filteredTradeTests.length === 0 && (
              <div className="trade-test-empty-state">
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
                          <strong>
                            {tradeTest.test_type || "Practical Assessment"}
                          </strong>
                        </td>
                        <td className="trade-test-date">
                          {formatDate(tradeTest.scheduled_at)}
                        </td>
                        <td>{tradeTest.location || "—"}</td>
                        <td>{tradeTest.assessor_name || "—"}</td>
                        <td>
                          <span className={getStatusClass(tradeTest.status)}>
                            {tradeTest.status || "—"}
                          </span>
                        </td>
                        <td>
                          <span className={getResultClass(tradeTest.result)}>
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

        </section>
      )}
    </>
  );
}
