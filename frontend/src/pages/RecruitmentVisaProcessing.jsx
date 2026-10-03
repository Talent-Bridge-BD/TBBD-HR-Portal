import React, { useCallback, useEffect, useMemo, useState } from "react";

import { authenticatedFetch } from "../utils/auth";

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString();
}

function toDateInput(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toISOString().slice(0, 10);
}

function getInitials(firstName, lastName) {
  return `${firstName?.[0] || ""}${lastName?.[0] || ""}`.toUpperCase() || "?";
}

function statusClass(status) {
  const value = String(status || "").toLowerCase();

  if (value === "approved") return "status-badge status-approved";
  if (value === "rejected") return "status-badge status-rejected";
  if (value === "submitted") return "status-badge status-submitted";
  if (value === "processing" || value === "in progress") {
    return "status-badge status-in-progress";
  }

  return "status-badge status-pending";
}

function getCandidateName(application) {
  const firstName =
    application?.first_name ||
    application?.candidate_first_name ||
    "";
  const lastName =
    application?.last_name ||
    application?.candidate_last_name ||
    "";

  return (
    application?.candidate_name ||
    `${firstName} ${lastName}`.trim() ||
    application?.email ||
    "Candidate"
  );
}

export default function RecruitmentVisaProcessing() {
  const [records, setRecords] = useState([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(null);
  const [organizationId, setOrganizationId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saveError, setSaveError] = useState("");

  const loadVisaRecords = useCallback(async (cancelledRef = null) => {
    try {
      setLoading(true);
      setError("");

      const meResponse = await authenticatedFetch("/api/me");

      if (!meResponse.ok) {
        throw new Error("Unable to load current user.");
      }

      const me = await meResponse.json();
      const roles = me?.roles || [];
      const isAdministrator = roles.includes("Administrator");

      const currentOrganizationId =
        me?.user?.organization_id ||
        me?.organization_id ||
        me?.organization_ids?.[0] ||
        me?.user?.organization_ids?.[0] ||
        null;

      if (!isAdministrator && !currentOrganizationId) {
        throw new Error("No organization was found for the current user.");
      }

      if (!cancelledRef) {
        setOrganizationId(currentOrganizationId);
      }

      let applicationsUrl = "/api/applications";

      if (!isAdministrator) {
        applicationsUrl =
          `/api/applications?organization_id=${encodeURIComponent(
            currentOrganizationId
          )}`;
      }

      const applicationsResponse =
        await authenticatedFetch(applicationsUrl);

      if (!applicationsResponse.ok) {
        throw new Error("Unable to load applications.");
      }

      const applicationsData = await applicationsResponse.json();

      const applications = Array.isArray(applicationsData)
        ? applicationsData
        : applicationsData?.items ||
          applicationsData?.applications ||
          [];

      const loaded = [];

      for (const application of applications) {
        try {
          const applicationOrganizationId =
            application?.organization_id || currentOrganizationId;

          if (!applicationOrganizationId) continue;

          const response = await authenticatedFetch(
            `/api/visa-processing/application/${encodeURIComponent(
              application.id
            )}?organization_id=${encodeURIComponent(
              applicationOrganizationId
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
          // Continue loading other applications if one request fails.
        }
      }

      if (!cancelledRef) {
        setRecords(loaded);
      }
    } catch (err) {
      if (!cancelledRef) {
        setError(
          err.message || "Unable to load Visa Processing records."
        );
      }
    } finally {
      if (!cancelledRef) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    loadVisaRecords(cancelled);

    return () => {
      cancelled = true;
    };
  }, [loadVisaRecords]);

  const filteredRecords = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) return records;

    return records.filter((record) => {
      const application = record.application || {};
      const candidateName = getCandidateName(application);

      const destinationCountry =
        application.destination_country ||
        application.employer_country ||
        "";

      return [
        candidateName,
        application.email,
        application.job_title,
        record.visa_type,
        record.visa_number,
        record.application_number,
        destinationCountry,
        record.sponsor_name,
        record.sponsor_reference,
        record.status,
      ]
        .filter(Boolean)
        .some((value) =>
          String(value).toLowerCase().includes(query)
        );
    });
  }, [records, search]);

  const counts = useMemo(
    () => ({
      pending: records.filter(
        (record) =>
          String(record.status || "").toLowerCase() === "pending"
      ).length,
      submitted: records.filter(
        (record) =>
          String(record.status || "").toLowerCase() === "submitted"
      ).length,
      approved: records.filter(
        (record) =>
          String(record.status || "").toLowerCase() === "approved"
      ).length,
      rejected: records.filter(
        (record) =>
          String(record.status || "").toLowerCase() === "rejected"
      ).length,
    }),
    [records]
  );

  function openRecord(record) {
    setSelected(record);
    setSaveError("");

    setForm({
      visa_type: record.visa_type || "",
      visa_number: record.visa_number || "",
      application_number: record.application_number || "",
      submission_date: toDateInput(record.submission_date),
      approval_date: toDateInput(record.approval_date),
      expiry_date: toDateInput(record.expiry_date),
      status: record.status || "Pending",
      sponsor_name: record.sponsor_name || "",
      sponsor_reference: record.sponsor_reference || "",
      notes: record.notes || "",
    });
  }

  function closeRecord() {
    if (saving) return;
    setSelected(null);
    setForm(null);
    setSaveError("");
  }

  function updateField(name, value) {
    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function saveRecord(event) {
    event.preventDefault();

    if (!selected || !form || !organizationId) {
      setSaveError("Organization context is unavailable.");
      return;
    }

    setSaving(true);
    setSaveError("");

    try {
      const response = await authenticatedFetch(
        `/api/visa-processing/${encodeURIComponent(
          selected.id
        )}?organization_id=${encodeURIComponent(organizationId)}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            visa_type: form.visa_type || null,
            visa_number: form.visa_number || null,
            application_number: form.application_number || null,
            submission_date: form.submission_date || null,
            approval_date: form.approval_date || null,
            expiry_date: form.expiry_date || null,
            status: form.status || "Pending",
            sponsor_name: form.sponsor_name || null,
            sponsor_reference: form.sponsor_reference || null,
            notes: form.notes || null,
          }),
        }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data?.detail || "Unable to save Visa Processing record."
        );
      }

      const updatedRecord =
        data?.visa_processing || data?.item || data;

      setRecords((current) =>
        current.map((record) =>
          record.id === selected.id
            ? {
                ...record,
                ...updatedRecord,
                application: selected.application,
              }
            : record
        )
      );

      setSelected((current) =>
        current
          ? {
              ...current,
              ...updatedRecord,
              application: current.application,
            }
          : current
      );

      setForm({
        visa_type: updatedRecord.visa_type || "",
        visa_number: updatedRecord.visa_number || "",
        application_number:
          updatedRecord.application_number || "",
        submission_date: toDateInput(
          updatedRecord.submission_date
        ),
        approval_date: toDateInput(
          updatedRecord.approval_date
        ),
        expiry_date: toDateInput(updatedRecord.expiry_date),
        status: updatedRecord.status || "Pending",
        sponsor_name: updatedRecord.sponsor_name || "",
        sponsor_reference:
          updatedRecord.sponsor_reference || "",
        notes: updatedRecord.notes || "",
      });
    } catch (err) {
      setSaveError(
        err.message || "Unable to save Visa Processing record."
      );
    } finally {
      setSaving(false);
    }
  }

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
              Review candidate visa applications, submission status,
              and approval details.
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
            aria-label="Search visa processing records"
            className="medical-search-input"
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
            <strong>
              No visa processing records have been recorded yet.
            </strong>
            <p>
              Visa records will appear here when candidates enter the
              visa processing stage.
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
                  <th>Destination Country</th>
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
                    getCandidateName(application);

                  const destinationCountry =
                    application.destination_country ||
                    application.employer_country ||
                    "—";

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

                      <td>{destinationCountry}</td>

                      <td>
                        <span className={statusClass(record.status)}>
                          {record.status || "Pending"}
                        </span>
                      </td>

                      <td>
                        {formatDate(record.submission_date)}
                      </td>

                      <td>
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() => openRecord(record)}
                        >
                          {String(record.status || "").toLowerCase() ===
                          "pending"
                            ? "Process"
                            : "View / Update"}
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

      {selected && form && (
        <div
          className="medical-overlay"
          role="presentation"
          onClick={closeRecord}
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
                <span>VISA PROCESSING</span>
                <h2>{getCandidateName(selected.application)}</h2>
              </div>

              <button
                type="button"
                className="medical-close-button"
                onClick={closeRecord}
                aria-label="Close Visa Processing"
              >
                ×
              </button>
            </div>

            <div className="medical-detail-status">
              <span className={statusClass(form.status)}>
                {form.status || "Pending"}
              </span>

              {form.visa_type && <span>{form.visa_type}</span>}
            </div>

            <form onSubmit={saveRecord}>
              <div className="medical-detail-grid">
                <div>
                  <span>Email</span>
                  <strong>
                    {selected.application?.email || "—"}
                  </strong>
                </div>

                <div>
                  <span>Job</span>
                  <strong>
                    {selected.application?.job_title || "—"}
                  </strong>
                </div>

                <div>
                  <span>Destination Country</span>
                  <strong>
                    {selected.application?.destination_country ||
                      selected.application?.employer_country ||
                      "—"}
                  </strong>
                </div>

                <div>
                  <span>Candidate Passport</span>
                  <strong>
                    {selected.application
                      ?.candidate_passport_number || "—"}
                  </strong>
                </div>
              </div>

              <div className="medical-assessment-panel">
                <div className="medical-form-grid">
                  <label className="medical-field">
                    <span>Visa Type</span>
                    <input
                      type="text"
                      value={form.visa_type}
                      onChange={(event) =>
                        updateField(
                          "visa_type",
                          event.target.value
                        )
                      }
                      placeholder="e.g. Employment Visa"
                    />
                  </label>

                  <label className="medical-field">
                    <span>Visa Number</span>
                    <input
                      type="text"
                      value={form.visa_number}
                      onChange={(event) =>
                        updateField(
                          "visa_number",
                          event.target.value
                        )
                      }
                      placeholder="Enter visa number"
                    />
                  </label>

                  <label className="medical-field">
                    <span>Application Number</span>
                    <input
                      type="text"
                      value={form.application_number}
                      onChange={(event) =>
                        updateField(
                          "application_number",
                          event.target.value
                        )
                      }
                      placeholder="Enter application number"
                    />
                  </label>

                  <label className="medical-field">
                    <span>Status</span>
                    <select
                      value={form.status}
                      onChange={(event) =>
                        updateField("status", event.target.value)
                      }
                    >
                      <option value="Pending">Pending</option>
                      <option value="Submitted">Submitted</option>
                      <option value="Processing">Processing</option>
                      <option value="Approved">Approved</option>
                      <option value="Rejected">Rejected</option>
                      <option value="Expired">Expired</option>
                    </select>
                  </label>

                  <label className="medical-field">
                    <span>Submission Date</span>
                    <input
                      type="date"
                      value={form.submission_date}
                      onChange={(event) =>
                        updateField(
                          "submission_date",
                          event.target.value
                        )
                      }
                    />
                  </label>

                  <label className="medical-field">
                    <span>Approval Date</span>
                    <input
                      type="date"
                      value={form.approval_date}
                      onChange={(event) =>
                        updateField(
                          "approval_date",
                          event.target.value
                        )
                      }
                    />
                  </label>

                  <label className="medical-field">
                    <span>Expiry Date</span>
                    <input
                      type="date"
                      value={form.expiry_date}
                      onChange={(event) =>
                        updateField(
                          "expiry_date",
                          event.target.value
                        )
                      }
                    />
                  </label>

                  <label className="medical-field">
                    <span>Sponsor Name</span>
                    <input
                      type="text"
                      value={form.sponsor_name}
                      onChange={(event) =>
                        updateField(
                          "sponsor_name",
                          event.target.value
                        )
                      }
                      placeholder="Enter sponsor name"
                    />
                  </label>

                  <label className="medical-field">
                    <span>Sponsor Reference</span>
                    <input
                      type="text"
                      value={form.sponsor_reference}
                      onChange={(event) =>
                        updateField(
                          "sponsor_reference",
                          event.target.value
                        )
                      }
                      placeholder="Enter sponsor reference"
                    />
                  </label>

                  <label className="medical-field medical-field-wide">
                    <span>Notes</span>
                    <textarea
                      rows="5"
                      value={form.notes}
                      onChange={(event) =>
                        updateField("notes", event.target.value)
                      }
                      placeholder="Add visa processing notes"
                    />
                  </label>
                </div>

                {saveError && (
                  <div className="medical-empty-state">
                    <strong>Unable to save Visa Processing</strong>
                    <p>{saveError}</p>
                  </div>
                )}

                <div className="medical-form-footer">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={closeRecord}
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
                      ? "Saving..."
                      : "Save Visa Processing"}
                  </button>
                </div>
              </div>
            </form>
          </aside>
        </div>
      )}
    </div>
  );
}
