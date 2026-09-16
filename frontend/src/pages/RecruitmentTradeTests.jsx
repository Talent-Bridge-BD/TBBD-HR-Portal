import { useEffect, useMemo, useState } from "react";

import PageHeader from "../components/PageHeader";

export default function RecruitmentTradeTests({ auth }) {
  const organizationId = auth?.organization_ids?.[0] || "";

  const [tradeTests, setTradeTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!organizationId) {
      setTradeTests([]);
      setLoading(false);
      return;
    }

    const loadTradeTests = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `/api/trade-tests?organization_id=${encodeURIComponent(
            organizationId
          )}`,
          {
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error(
            `Failed to load trade tests (${response.status})`
          );
        }

        const data = await response.json();
        setTradeTests(data.trade_tests || []);
      } catch (err) {
        setError(err.message || "Failed to load trade tests.");
      } finally {
        setLoading(false);
      }
    };

    loadTradeTests();
  }, [organizationId]);

  const scheduledCount = tradeTests.filter(
    (item) => String(item.status || "").toLowerCase() === "scheduled"
  ).length;

  const completedCount = tradeTests.filter(
    (item) => String(item.status || "").toLowerCase() === "completed"
  ).length;

  const passedCount = tradeTests.filter(
    (item) => ["pass", "passed"].includes(
      String(item.result || "").toLowerCase()
    )
  ).length;

  const failedCount = tradeTests.filter(
    (item) => ["fail", "failed"].includes(
      String(item.result || "").toLowerCase()
    )
  ).length;

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

  return (
    <>
      <PageHeader
        title="Trade Tests"
        subtitle="Manage trade testing and practical skill assessments."
      />

      <div className="trade-test-kpi-grid">
        <section className="dashboard-card trade-test-kpi-card">
          <span className="trade-test-kpi-label">Scheduled Tests</span>
          <strong>{scheduledCount}</strong>
          <small>Upcoming assessments</small>
        </section>

        <section className="dashboard-card trade-test-kpi-card">
          <span className="trade-test-kpi-label">Completed Tests</span>
          <strong>{completedCount}</strong>
          <small>Assessments completed</small>
        </section>

        <section className="dashboard-card trade-test-kpi-card trade-test-kpi-success">
          <span className="trade-test-kpi-label">Passed</span>
          <strong>{passedCount}</strong>
          <small>Successful assessments</small>
        </section>

        <section className="dashboard-card trade-test-kpi-card trade-test-kpi-danger">
          <span className="trade-test-kpi-label">Failed</span>
          <strong>{failedCount}</strong>
          <small>Unsuccessful assessments</small>
        </section>
      </div>

      <section className="dashboard-card trade-test-workspace">
        <div className="trade-test-workspace-header">
          <div>
            <h2>Candidate Trade Tests</h2>
            <p>
              Review scheduled practical assessments and their results.
            </p>
          </div>

          <div className="trade-test-count">
            {filteredTradeTests.length}{" "}
            {filteredTradeTests.length === 1 ? "test" : "tests"}
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

        {loading && (
          <div className="trade-test-empty-state">
            <strong>Loading trade tests...</strong>
          </div>
        )}

        {!loading && error && (
          <div className="trade-test-error">
            {error}
          </div>
        )}

        {!loading && !error && tradeTests.length === 0 && (
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
              <span>
                Try a different search term.
              </span>
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

                      <td>
                        {tradeTest.location || "—"}
                      </td>

                      <td>
                        {tradeTest.assessor_name || "—"}
                      </td>

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
    </>
  );
}
