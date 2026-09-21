import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import { authenticatedFetch } from '../utils/auth'

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function getInitials(firstName, lastName) {
  const first = String(firstName || "").trim().charAt(0);
  const last = String(lastName || "").trim().charAt(0);

  return `${first}${last}`.toUpperCase() || "—";
}

function statusClass(status) {
  const value = String(status || "").toLowerCase();

  if (value === "completed") {
    return "medical-status medical-status-completed";
  }

  if (value === "in progress") {
    return "medical-status medical-status-progress";
  }

  if (value === "cancelled") {
    return "medical-status medical-status-cancelled";
  }

  return "medical-status medical-status-scheduled";
}

function resultClass(result) {
  const value = String(result || "").toLowerCase();

  if (value === "fit") {
    return "medical-result medical-result-fit";
  }

  if (value === "unfit") {
    return "medical-result medical-result-unfit";
  }

  if (value === "further review") {
    return "medical-result medical-result-review";
  }

  return "medical-result medical-result-pending";
}

export default function RecruitmentMedical() {
  const [applications, setApplications] = useState([]);
  const [medicalRecords, setMedicalRecords] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadMedicalRecords() {
      setLoading(true);
      setError("");

      try {
        const meResponse = await authenticatedFetch("/api/me");

        if (!meResponse.ok) {
          throw new Error("Unable to load the signed-in user.");
        }

        const meData = await meResponse.json();
        const roles = meData?.roles || [];
        const isAdministrator = roles.includes("Administrator");
        const organizationId =
          meData?.user?.organization_id ||
          meData?.organization_ids?.[0] ||
          null;

        let applicationsUrl = "/api/applications";

        if (!isAdministrator) {
          if (!organizationId) {
            throw new Error("No organization is available for the signed-in user.");
          }

          applicationsUrl =
            `/api/applications?organization_id=${encodeURIComponent(organizationId)}`;
        }

        const applicationsResponse = await authenticatedFetch(applicationsUrl);

        if (!applicationsResponse.ok) {
          throw new Error("Unable to load recruitment applications.");
        }

        const applicationsData = await applicationsResponse.json();
        const applicationItems = applicationsData?.applications || [];

        const records = [];

        for (const application of applicationItems) {
          const response = await authenticatedFetch(
            `/api/medical-examinations/application/${encodeURIComponent(
              application.id
            )}?organization_id=${encodeURIComponent(
              application?.organization_id || organizationId
            )}`
          );

          if (!response.ok) {
            continue;
          }

          const data = await response.json();

          for (const medical of data?.medical_examinations || []) {
            records.push({
              ...medical,
              candidate_first_name: application.candidate_first_name,
              candidate_last_name: application.candidate_last_name,
              candidate_email: application.candidate_email,
              candidate_phone: application.candidate_phone,
              job_title: application.job_title,
              application_status: application.status,
            });
          }
        }

        if (!cancelled) {
          setApplications(applicationItems);
          setMedicalRecords(records);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load medical examinations.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadMedicalRecords();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredRecords = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return medicalRecords;
    }

    return medicalRecords.filter((record) =>
      [
        record.candidate_first_name,
        record.candidate_last_name,
        record.candidate_email,
        record.job_title,
        record.medical_center,
        record.doctor_name,
        record.medical_type,
        record.status,
        record.result,
      ]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query))
    );
  }, [medicalRecords, search]);

  const scheduledCount = medicalRecords.filter(
    (record) => record.status === "Scheduled"
  ).length;

  const inProgressCount = medicalRecords.filter(
    (record) => record.status === "In Progress"
  ).length;

  const fitCount = medicalRecords.filter(
    (record) => record.result === "Fit"
  ).length;

  const unfitCount = medicalRecords.filter(
    (record) => record.result === "Unfit"
  ).length;

  return (
    <>
      <PageHeader
        title="Medical Examinations"
        subtitle="Manage candidate medical examinations and fitness results."
      />

      <div className="medical-kpi-grid">
        <section className="medical-kpi-card">
          <span>Scheduled</span>
          <strong>{scheduledCount}</strong>
          <small>Upcoming examinations</small>
        </section>

        <section className="medical-kpi-card medical-kpi-progress">
          <span>In Progress</span>
          <strong>{inProgressCount}</strong>
          <small>Currently being assessed</small>
        </section>

        <section className="medical-kpi-card medical-kpi-fit">
          <span>Fit</span>
          <strong>{fitCount}</strong>
          <small>Cleared for recruitment</small>
        </section>

        <section className="medical-kpi-card medical-kpi-unfit">
          <span>Unfit</span>
          <strong>{unfitCount}</strong>
          <small>Not medically cleared</small>
        </section>
      </div>

      <section className="medical-workspace">
        <div className="medical-workspace-header">
          <div>
            <h2>Medical Examination Records</h2>
            <p>
              Review candidate medical examinations, fitness results, and
              assessment details.
            </p>
          </div>

          <span className="medical-count">
            {filteredRecords.length}{" "}
            {filteredRecords.length === 1 ? "examination" : "examinations"}
          </span>
        </div>

        <div className="medical-toolbar">
          <div className="medical-search">
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search candidate, job, medical center, doctor..."
              aria-label="Search medical examinations"
            />
          </div>
        </div>

        {loading && (
          <div className="medical-empty-state">
            Loading medical examinations...
          </div>
        )}

        {!loading && error && (
          <div className="medical-error">
            {error}
          </div>
        )}

        {!loading && !error && filteredRecords.length === 0 && (
          <div className="medical-empty-state">
            {medicalRecords.length === 0
              ? "No medical examinations have been recorded yet."
              : "No medical examinations match your search."}
          </div>
        )}

        {!loading && !error && filteredRecords.length > 0 && (
          <div className="medical-table-wrap">
            <table className="medical-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Job</th>
                  <th>Medical Center</th>
                  <th>Examination Date</th>
                  <th>Doctor</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Result</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredRecords.map((record) => (
                  <tr key={record.id}>
                    <td>
                      <div className="medical-candidate">
                        <span className="medical-avatar">
                          {getInitials(
                            record.candidate_first_name,
                            record.candidate_last_name
                          )}
                        </span>

                        <div>
                          <strong>
                            {record.candidate_first_name}{" "}
                            {record.candidate_last_name}
                          </strong>
                          <small>{record.candidate_email || "—"}</small>
                        </div>
                      </div>
                    </td>

                    <td>
                      <strong>{record.job_title || "—"}</strong>
                    </td>

                    <td>{record.medical_center || "—"}</td>

                    <td className="medical-date">
                      {formatDate(record.examination_date)}
                    </td>

                    <td>{record.doctor_name || "—"}</td>

                    <td>{record.medical_type || "—"}</td>

                    <td>
                      <span className={statusClass(record.status)}>
                        {record.status || "Scheduled"}
                      </span>
                    </td>

                    <td>
                      <span className={resultClass(record.result)}>
                        {record.result || "Pending"}
                      </span>
                    </td>

                    <td>
                      <button
                        type="button"
                        className="secondary-button medical-view-button"
                        onClick={() => setSelectedRecord(record)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedRecord && (
        <div
          className="medical-overlay"
          role="presentation"
          onClick={() => setSelectedRecord(null)}
        >
          <aside
            className="medical-detail-panel"
            role="dialog"
            aria-modal="true"
            aria-label="Medical examination details"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="medical-detail-header">
              <div>
                <span className="medical-detail-eyebrow">
                  MEDICAL EXAMINATION
                </span>
                <h2>
                  {selectedRecord.candidate_first_name}{" "}
                  {selectedRecord.candidate_last_name}
                </h2>
                <p>{selectedRecord.candidate_email || "—"}</p>
              </div>

              <button
                type="button"
                className="medical-close-button"
                onClick={() => setSelectedRecord(null)}
                aria-label="Close medical examination details"
              >
                ×
              </button>
            </div>

            <div className="medical-detail-status">
              <span className={statusClass(selectedRecord.status)}>
                {selectedRecord.status || "Scheduled"}
              </span>
              <span className={resultClass(selectedRecord.result)}>
                {selectedRecord.result || "Pending"}
              </span>
            </div>

            <div className="medical-detail-grid">
              <div>
                <span>Job</span>
                <strong>{selectedRecord.job_title || "—"}</strong>
              </div>

              <div>
                <span>Medical Center</span>
                <strong>{selectedRecord.medical_center || "—"}</strong>
              </div>

              <div>
                <span>Examination Date</span>
                <strong>{formatDate(selectedRecord.examination_date)}</strong>
              </div>

              <div>
                <span>Doctor</span>
                <strong>{selectedRecord.doctor_name || "—"}</strong>
              </div>

              <div>
                <span>Medical Type</span>
                <strong>{selectedRecord.medical_type || "—"}</strong>
              </div>

              <div>
                <span>Candidate Phone</span>
                <strong>{selectedRecord.candidate_phone || "—"}</strong>
              </div>
            </div>

            <div className="medical-notes">
              <span>Report Notes</span>
              <p>{selectedRecord.report_notes || "No report notes provided."}</p>
            </div>

            {selectedRecord.completed_at && (
              <div className="medical-completed">
                <span>Completed</span>
                <strong>{formatDate(selectedRecord.completed_at)}</strong>
              </div>
            )}
          </aside>
        </div>
      )}
    </>
  );
}
