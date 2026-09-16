import React, { useEffect, useMemo, useState } from "react";

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString();
}

function getInitials(firstName, lastName) {
  return `${firstName?.[0] || ""}${lastName?.[0] || ""}`.toUpperCase() || "?";
}

function statusClass(status) {
  const value = String(status || "").toLowerCase();

  if (value === "approved") return "status-badge status-approved";
  if (value === "rejected") return "status-badge status-rejected";
  if (value === "submitted") return "status-badge status-submitted";
  if (value === "in progress") return "status-badge status-in-progress";
  return "status-badge status-pending";
}

export default function RecruitmentVisaProcessing() {
  const [records, setRecords] = useState([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadVisaRecords() {
      try {
        setLoading(true);
        setError("");

        const meResponse = await fetch("/api/me");
        if (!meResponse.ok) {
          throw new Error("Unable to load current user.");
        }

        const me = await meResponse.json();
        const organizationId =
          me?.user?.organization_id ||
          me?.user?.organization_ids?.[0] ||
          me?.organization_id ||
          me?.organization_ids?.[0];

        if (!organizationId) {
          throw new Error("No organization was found for the current user.");
        }

        const applicationsResponse = await fetch(
          `/api/applications?organization_id=${encodeURIComponent(organizationId)}`
        );

        if (!applicationsResponse.ok) {
          throw new Error("Unable to load applications.");
        }

        const applicationsData = await applicationsResponse.json();
        const applications = Array.isArray(applicationsData)
          ? applicationsData
          : applicationsData?.items || applicationsData?.applications || [];

        const loaded = [];

        for (const application of applications) {
          try {
            const response = await fetch(
              `/api/visa-processing/application/${application.id}?organization_id=${encodeURIComponent(
                organizationId
              )}`
            );

            if (!response.ok) continue;

            const data = await response.json();
            const visaRecords = Array.isArray(data)
              ? data
              : data?.items || data?.visa_processings || [];

            visaRecords.forEach((visa) => {
              loaded.push({
                ...visa,
                application,
              });
            });
          } catch {
            // Continue loading other applications if one visa request fails.
          }
        }

        if (!cancelled) {
          setRecords(loaded);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load Visa Processing records.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadVisaRecords();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredRecords = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) return records;

    return records.filter((record) => {
      const application = record.application || {};
      const candidateName = [
        application.first_name,
        application.last_name,
        application.candidate_name,
      ]
        .filter(Boolean)
        .join(" ");

      return [
        candidateName,
        application.email,
        application.job_title,
        record.visa_type,
        record.visa_number,
        record.country,
        record.status,
        record.result,
      ]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query));
    });
  }, [records, search]);

  const counts = useMemo(
    () => ({
      pending: records.filter(
        (record) => String(record.status).toLowerCase() === "pending"
      ).length,
      submitted: records.filter(
        (record) => String(record.status).toLowerCase() === "submitted"
      ).length,
      approved: records.filter(
        (record) => String(record.status).toLowerCase() === "approved"
      ).length,
      rejected: records.filter(
        (record) => String(record.status).toLowerCase() === "rejected"
      ).length,
    }),
    [records]
  );

  return (
    <div className="medical-workspace visa-processing-workspace">
      <div className="medical-workspace-header">
        <div>
          <h1>Visa Processing</h1>
          <p>Manage candidate visa applications and approvals.</p>
        </div>
      </div>

      <div className="medical-kpi-grid">
        <div className="medical-kpi-card">
          <span>Pending</span>
          <strong>{counts.pending}</strong>
          <small>Applications awaiting action</small>
        </div>

        <div className="medical-kpi-card">
          <span>Submitted</span>
          <strong>{counts.submitted}</strong>
          <small>Applications submitted</small>
        </div>

        <div className="medical-kpi-card">
          <span>Approved</span>
          <strong>{counts.approved}</strong>
          <small>Approved visa applications</small>
        </div>

        <div className="medical-kpi-card">
          <span>Rejected</span>
          <strong>{counts.rejected}</strong>
          <small>Rejected applications</small>
        </div>
      </div>

      <section className="dashboard-card recruitment-table-card">
        <div className="card-heading">
          <div>
            <h2>Visa Processing Records</h2>
            <p>
              Review candidate visa applications, submission status, and
              approval details.
            </p>
          </div>

          <span className="medical-count">
            {filteredRecords.length}{" "}
            {filteredRecords.length === 1 ? "record" : "records"}
          </span>
        </div>

        <div className="medical-toolbar">
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search candidates, visa type, country or status"
            aria-label="Search visa processing records" className="medical-search-input"
          />
        </div>

        {loading && (
          <div className="medical-empty-state">
            <strong>Loading Visa Processing records…</strong>
            <p>Please wait while the records are loaded.</p>
          </div>
        )}

        {!loading && error && (
          <div className="medical-empty-state">
            <strong>Unable to load Visa Processing records</strong>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && filteredRecords.length === 0 && (
          <div className="medical-empty-state">
            <strong>No visa processing records have been recorded yet.</strong>
            <p>
              Visa records will appear here when candidates enter the visa
              processing stage.
            </p>
          </div>
        )}

        {!loading && !error && filteredRecords.length > 0 && (
          <div className="medical-table-wrap">
            <table className="medical-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Job</th>
                  <th>Visa Type</th>
                  <th>Country</th>
                  <th>Status</th>
                  <th>Submitted</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredRecords.map((record) => {
                  const application = record.application || {};
                  const firstName =
                    application.first_name ||
                    application.candidate_first_name ||
                    "";
                  const lastName =
                    application.last_name ||
                    application.candidate_last_name ||
                    "";
                  const candidateName =
                    application.candidate_name ||
                    `${firstName} ${lastName}`.trim() ||
                    application.email ||
                    "Candidate";

                  return (
                    <tr key={record.id}>
                      <td>
                        <div className="medical-candidate">
                          <span className="medical-avatar">
                            {getInitials(firstName, lastName)}
                          </span>
                          <div>
                            <strong>{candidateName}</strong>
                            <small>
                              Visa ID: {record.id || "—"}
                            </small>
                          </div>
                        </div>
                      </td>

                      <td>{application.job_title || "—"}</td>
                      <td>{record.visa_type || "—"}</td>
                      <td>{record.country || "—"}</td>

                      <td>
                        <span className={statusClass(record.status)}>
                          {record.status || "Pending"}
                        </span>
                      </td>

                      <td>{formatDate(record.submitted_at)}</td>

                      <td>
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() => setSelected(record)}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selected && (
        <div
          className="medical-overlay"
          role="presentation"
          onClick={() => setSelected(null)}
        >
          <aside
            className="medical-detail-panel"
            role="dialog"
            aria-modal="true"
            aria-label="Visa processing details"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="medical-detail-header">
              <div>
                <span>VISA PROCESSING DETAILS</span>
                <h2>
                  {selected.application?.candidate_name ||
                    `${selected.application?.first_name || ""} ${
                      selected.application?.last_name || ""
                    }`.trim() ||
                    selected.application?.email ||
                    "Candidate"}
                </h2>
              </div>

              <button
                type="button"
                className="medical-close-button"
                onClick={() => setSelected(null)}
                aria-label="Close details"
              >
                ×
              </button>
            </div>

            <div className="medical-detail-status">
              <span className={statusClass(selected.status)}>
                {selected.status || "Pending"}
              </span>
              {selected.visa_type && <span>{selected.visa_type}</span>}
            </div>

            <div className="medical-detail-grid">
              <div>
                <span>Email</span>
                <strong>{selected.application?.email || "—"}</strong>
              </div>

              <div>
                <span>Job</span>
                <strong>{selected.application?.job_title || "—"}</strong>
              </div>

              <div>
                <span>Visa Type</span>
                <strong>{selected.visa_type || "—"}</strong>
              </div>

              <div>
                <span>Country</span>
                <strong>{selected.country || "—"}</strong>
              </div>

              <div>
                <span>Visa Number</span>
                <strong>{selected.visa_number || "—"}</strong>
              </div>

              <div>
                <span>Submitted</span>
                <strong>{formatDate(selected.submitted_at)}</strong>
              </div>

              <div>
                <span>Approved</span>
                <strong>{formatDate(selected.approved_at)}</strong>
              </div>

              <div>
                <span>Rejected</span>
                <strong>{formatDate(selected.rejected_at)}</strong>
              </div>
            </div>

            <div className="medical-notes">
              <span>Notes</span>
              <p>{selected.notes || "No additional notes provided."}</p>
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}
