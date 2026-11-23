import { useEffect, useMemo, useState } from "react";

import PageHeader from "../components/PageHeader";
import { authenticatedFetch } from "../utils/auth";

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

const emptyAssessment = {
  medical_center: "",
  examination_date: "",
  doctor_name: "",
  medical_type: "",
  status: "Completed",
  result: "Fit",
  report_notes: "",
};

export default function RecruitmentMedical() {
  const [applications, setApplications] = useState([]);
  const [medicalRecords, setMedicalRecords] = useState([]);
  const [eligibleApplications, setEligibleApplications] = useState([]);

  const [organizationId, setOrganizationId] = useState(null);
  const [organizationLoading, setOrganizationLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [selectedApplicationId, setSelectedApplicationId] = useState("");

  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [selectedAssessmentId, setSelectedAssessmentId] = useState(null);

  const [scheduleForm, setScheduleForm] = useState({
    medical_center: "",
    examination_date: "",
    doctor_name: "",
    medical_type: "",
  });

  const [assessmentForm, setAssessmentForm] = useState(emptyAssessment);

  const [loading, setLoading] = useState(true);
  const [savingSchedule, setSavingSchedule] = useState(false);
  const [savingAssessment, setSavingAssessment] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadOrganization() {
      try {
        setOrganizationLoading(true);

        const response = await authenticatedFetch("/api/me");

        if (!response.ok) {
          throw new Error("Unable to load the signed-in user.");
        }

        const data = await response.json();

        const roles = data?.roles || [];
        const isAdministrator = roles.includes("Administrator");

        const id =
          data?.user?.organization_id ||
          data?.organization_ids?.[0] ||
          null;

        if (!isAdministrator && !id) {
          throw new Error(
            "No organization is available for the signed-in user."
          );
        }

        if (!cancelled) {
          setOrganizationId(id);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load organization access.");
        }
      } finally {
        if (!cancelled) {
          setOrganizationLoading(false);
        }
      }
    }

    loadOrganization();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (organizationLoading) {
      return;
    }

    let cancelled = false;

    async function loadMedicalWorkflow() {
      setLoading(true);
      setError("");

      try {
        let applicationsUrl = "/api/applications";

        if (organizationId) {
          applicationsUrl = `/api/applications?organization_id=${encodeURIComponent(
            organizationId
          )}`;
        }

        const applicationsResponse =
          await authenticatedFetch(applicationsUrl);

        if (!applicationsResponse.ok) {
          const data = await applicationsResponse.json().catch(() => ({}));

          throw new Error(
            data.detail || "Unable to load recruitment applications."
          );
        }

        const applicationsData = await applicationsResponse.json();

        const applicationItems = applicationsData?.applications || [];

        setApplications(applicationItems);

        /*
         * Medical eligibility:
         *
         * Application must have a completed Trade Test
         * with a Pass result.
         */
        const passedTradeTestApplications = [];

        await Promise.all(
          applicationItems.map(async (application) => {
            try {
              const tradeResponse = await authenticatedFetch(
                `/api/trade-tests/application/${encodeURIComponent(
                  application.id
                )}?organization_id=${encodeURIComponent(
                  application?.organization_id || organizationId
                )}`
              );

              if (!tradeResponse.ok) {
                return;
              }

              const tradeData = await tradeResponse.json();

              const tradeTests = tradeData?.trade_tests || [];

              const passed = tradeTests.some(
                (tradeTest) =>
                  String(tradeTest.status || "").toLowerCase() ===
                    "completed" &&
                  ["pass", "passed"].includes(
                    String(tradeTest.result || "").toLowerCase()
                  )
              );

              if (passed) {
                passedTradeTestApplications.push(application);
              }
            } catch {
              // Ignore individual application lookup failures.
            }
          })
        );

        if (!cancelled) {
          setEligibleApplications(passedTradeTestApplications);
        }

        const records = [];

        await Promise.all(
          applicationItems.map(async (application) => {
            try {
              const response = await authenticatedFetch(
                `/api/medical-examinations/application/${encodeURIComponent(
                  application.id
                )}?organization_id=${encodeURIComponent(
                  application?.organization_id || organizationId
                )}`
              );

              if (!response.ok) {
                return;
              }

              const data = await response.json();

              for (const medical of data?.medical_examinations || []) {
                records.push({
                  ...medical,
                  candidate_first_name:
                    application.candidate_first_name,
                  candidate_last_name:
                    application.candidate_last_name,
                  candidate_email:
                    application.candidate_email,
                  candidate_phone:
                    application.candidate_phone,
                  job_title: application.job_title,
                  application_status: application.status,
                  application_id: application.id,
                });
              }
            } catch {
              // Ignore individual medical lookup failures.
            }
          })
        );

        if (!cancelled) {
          setMedicalRecords(records);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message || "Unable to load medical examinations."
          );
          setMedicalRecords([]);
          setEligibleApplications([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadMedicalWorkflow();

    return () => {
      cancelled = true;
    };
  }, [organizationId, organizationLoading]);

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
        .some((value) =>
          String(value).toLowerCase().includes(query)
        )
    );
  }, [medicalRecords, search]);

  const scheduledCount = medicalRecords.filter(
    (record) =>
      String(record.status || "").toLowerCase() === "scheduled"
  ).length;

  const inProgressCount = medicalRecords.filter(
    (record) =>
      String(record.status || "").toLowerCase() === "in progress"
  ).length;

  const fitCount = medicalRecords.filter(
    (record) =>
      String(record.result || "").toLowerCase() === "fit"
  ).length;

  const unfitCount = medicalRecords.filter(
    (record) =>
      String(record.result || "").toLowerCase() === "unfit"
  ).length;

  function updateScheduleField(field, value) {
    setScheduleForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function updateAssessmentField(field, value) {
    setAssessmentForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSaveSchedule() {
    setError("");

    if (!organizationId) {
      setError("Organization access is required.");
      return;
    }

    if (!selectedApplicationId) {
      setError("Please select a candidate.");
      return;
    }

    if (!scheduleForm.medical_center.trim()) {
      setError("Please enter the medical center.");
      return;
    }

    if (!scheduleForm.examination_date) {
      setError("Please select the examination date and time.");
      return;
    }

    setSavingSchedule(true);

    try {
      const response = await authenticatedFetch(
        `/api/medical-examinations?organization_id=${encodeURIComponent(
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
            medical_center:
              scheduleForm.medical_center.trim() || null,
            examination_date: scheduleForm.examination_date
              ? new Date(
                  scheduleForm.examination_date
                ).toISOString()
              : null,
            doctor_name:
              scheduleForm.doctor_name.trim() || null,
            medical_type:
              scheduleForm.medical_type.trim() || null,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to schedule medical examination."
        );
      }

      const application = applications.find(
        (item) => String(item.id) === String(selectedApplicationId)
      );

      const createdRecord = {
        ...(data.medical_examination || data.medical || {}),
        candidate_first_name:
          application?.candidate_first_name,
        candidate_last_name:
          application?.candidate_last_name,
        candidate_email:
          application?.candidate_email,
        candidate_phone:
          application?.candidate_phone,
        job_title: application?.job_title,
        application_status: application?.status,
        application_id: selectedApplicationId,
      };

      setMedicalRecords((current) => [
        createdRecord,
        ...current,
      ]);

      setShowScheduleForm(false);
      setSelectedApplicationId("");

      setScheduleForm({
        medical_center: "",
        examination_date: "",
        doctor_name: "",
        medical_type: "",
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingSchedule(false);
    }
  }

  function openAssessment(record) {
    setSelectedAssessmentId(record.id);

    setAssessmentForm({
      medical_center: record.medical_center || "",
      examination_date: record.examination_date
        ? new Date(record.examination_date)
            .toISOString()
            .slice(0, 16)
        : "",
      doctor_name: record.doctor_name || "",
      medical_type: record.medical_type || "",
      status:
        record.status &&
        ["Scheduled", "In Progress", "Completed", "Cancelled"].includes(
          record.status
        )
          ? record.status
          : "Completed",
      result:
        record.result &&
        ["Fit", "Unfit", "Further Review"].includes(record.result)
          ? record.result
          : "Fit",
      report_notes: record.report_notes || "",
    });
  }

  async function handleSaveAssessment(record) {
    setError("");

    if (!organizationId) {
      setError("Organization access is required.");
      return;
    }

    if (!assessmentForm.status) {
      setError("Please select a medical status.");
      return;
    }

    if (!assessmentForm.result) {
      setError("Please select a medical result.");
      return;
    }

    setSavingAssessment(true);

    try {
      const response = await authenticatedFetch(
        `/api/medical-examinations/${encodeURIComponent(
          record.id
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
            medical_center:
              assessmentForm.medical_center.trim() || null,
            examination_date: assessmentForm.examination_date
              ? new Date(
                  assessmentForm.examination_date
                ).toISOString()
              : null,
            doctor_name:
              assessmentForm.doctor_name.trim() || null,
            medical_type:
              assessmentForm.medical_type.trim() || null,
            status: assessmentForm.status,
            result: assessmentForm.result,
            report_notes:
              assessmentForm.report_notes.trim() || null,
            completed_at:
              assessmentForm.status === "Completed"
                ? new Date().toISOString()
                : null,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to save medical assessment."
        );
      }

      const updatedRecord =
        data.medical_examination || data.medical || data.record;

      if (updatedRecord) {
        setMedicalRecords((current) =>
          current.map((item) =>
            item.id === record.id
              ? {
                  ...item,
                  ...updatedRecord,
                }
              : item
          )
        );

        setSelectedRecord((current) =>
          current && current.id === record.id
            ? {
                ...current,
                ...updatedRecord,
              }
            : current
        );
      }

      setSelectedAssessmentId(null);
      setAssessmentForm(emptyAssessment);
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingAssessment(false);
    }
  }

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

      <section className="medical-ready-panel">
        <div className="medical-ready-copy">
          <div className="medical-ready-icon" aria-hidden="true">
            ✓
          </div>

          <div>
            <span className="medical-eyebrow">
              READY FOR MEDICAL
            </span>

            <h2>
              {eligibleApplications.length}{" "}
              {eligibleApplications.length === 1
                ? "candidate"
                : "candidates"}{" "}
              ready for medical examination
            </h2>

            <p>
              Candidates become eligible after completing their Trade Test
              with a passing result.
            </p>
          </div>
        </div>

        <div className="medical-ready-action">
          <button
            type="button"
            className="secondary-button medical-schedule-button"
            onClick={() => {
              setError("");
              setShowScheduleForm(true);
            }}
            disabled={eligibleApplications.length === 0}
          >
            Schedule Medical
          </button>
        </div>
      </section>

      {eligibleApplications.length > 0 && (
        <section className="medical-ready-candidates">
          {eligibleApplications.map((application) => (
            <div
              key={application.id}
              className="medical-ready-candidate"
            >
              <span className="medical-avatar">
                {getInitials(
                  application.candidate_first_name,
                  application.candidate_last_name
                )}
              </span>

              <div>
                <strong>
                  {application.candidate_first_name}{" "}
                  {application.candidate_last_name}
                </strong>

                <span>{application.job_title || "—"}</span>

                {application.candidate_email && (
                  <small>{application.candidate_email}</small>
                )}
              </div>

              <span className="medical-eligibility-badge">
                Trade Test Passed
              </span>
            </div>
          ))}
        </section>
      )}

      {showScheduleForm && (
        <section className="medical-form-card">
          <div className="medical-form-header">
            <div>
              <span className="medical-eyebrow">
                NEW MEDICAL EXAMINATION
              </span>

              <h2>Schedule a Medical Examination</h2>

              <p>
                Schedule a medical examination for a candidate who has
                successfully completed the Trade Test.
              </p>
            </div>

            <button
              type="button"
              className="medical-close-button"
              aria-label="Close schedule form"
              onClick={() => setShowScheduleForm(false)}
            >
              ×
            </button>
          </div>

          <div className="medical-form-grid">
            <label className="medical-field medical-field-wide">
              <span>Candidate</span>

              <select
                value={selectedApplicationId}
                onChange={(event) =>
                  setSelectedApplicationId(event.target.value)
                }
              >
                <option value="">Select candidate</option>

                {eligibleApplications.map((application) => (
                  <option
                    key={application.id}
                    value={application.id}
                  >
                    {application.candidate_first_name}{" "}
                    {application.candidate_last_name} —{" "}
                    {application.job_title || "Job"}
                  </option>
                ))}
              </select>
            </label>

            <label className="medical-field">
              <span>Passport Number</span>
              <input
                type="text"
                value={
                  eligibleApplications.find(
                    (application) =>
                      String(application.id) ===
                      String(selectedApplicationId)
                  )?.candidate_passport_number || ""
                }
                readOnly
                placeholder="Passport number"
              />
            </label>
            <label className="medical-field">
              <span>Destination Country</span>
              <input
                type="text"
                value={
                  eligibleApplications.find(
                    (application) =>
                      String(application.id) ===
                      String(selectedApplicationId)
                  )?.destination_country || ""
                }
                readOnly
                placeholder="Destination country"
              />
            </label>
            <label className="medical-field">
              <span>Medical Center</span>

              <input
                type="text"
                value={scheduleForm.medical_center}
                onChange={(event) =>
                  updateScheduleField(
                    "medical_center",
                    event.target.value
                  )
                }
                placeholder="e.g. International Medical Centre"
              />
            </label>

            <label className="medical-field">
              <span>Examination Date &amp; Time</span>

              <input
                type="datetime-local"
                value={scheduleForm.examination_date}
                onChange={(event) =>
                  updateScheduleField(
                    "examination_date",
                    event.target.value
                  )
                }
              />
            </label>

            <label className="medical-field">
              <span>Doctor</span>

              <input
                type="text"
                value={scheduleForm.doctor_name}
                onChange={(event) =>
                  updateScheduleField(
                    "doctor_name",
                    event.target.value
                  )
                }
                placeholder="Doctor name"
              />
            </label>

            <label className="medical-field">
              <span>Medical Type</span>

              <input
                type="text"
                value={scheduleForm.medical_type}
                onChange={(event) =>
                  updateScheduleField(
                    "medical_type",
                    event.target.value
                  )
                }
                placeholder="e.g. Pre-employment Medical"
              />
            </label>
          </div>

          <div className="medical-form-footer">
            <button
              type="button"
              className="secondary-button"
              onClick={() => setShowScheduleForm(false)}
              disabled={savingSchedule}
            >
              Cancel
            </button>

            <button
              type="button"
              className="primary-button"
              onClick={handleSaveSchedule}
              disabled={savingSchedule}
            >
              {savingSchedule
                ? "Saving..."
                : "Save Medical Schedule"}
            </button>
          </div>
        </section>
      )}

      <section className="medical-workspace">
        <div className="medical-workspace-header">
          <div>
            <h2>Medical Examination Records</h2>

            <p>
              Review candidate medical examinations, fitness results,
              and assessment details.
            </p>
          </div>

          <span className="medical-count">
            {filteredRecords.length}{" "}
            {filteredRecords.length === 1
              ? "examination"
              : "examinations"}
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

        {error && <div className="medical-error">{error}</div>}

        {loading && (
          <div className="medical-empty-state">
            Loading medical examinations...
          </div>
        )}

        {!loading &&
          !error &&
          filteredRecords.length === 0 && (
            <div className="medical-empty-state">
              {medicalRecords.length === 0
                ? "No medical examinations have been recorded yet."
                : "No medical examinations match your search."}
            </div>
          )}

        {!loading &&
          !error &&
          filteredRecords.length > 0 && (
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

                            <small>
                              {record.candidate_email || "—"}
                            </small>
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
                        <div className="medical-actions">
                          <button
                            type="button"
                            className="secondary-button medical-view-button"
                            onClick={() => setSelectedRecord(record)}
                          >
                            View
                          </button>

                          {String(record.status || "").toLowerCase() !==
                            "completed" && (
                            <button
                              type="button"
                              className="secondary-button medical-assess-button"
                              onClick={() => openAssessment(record)}
                            >
                              Assess
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </section>

      {selectedAssessmentId && (
        <div className="medical-overlay">
          <aside
            className="medical-assessment-panel"
            role="dialog"
            aria-modal="true"
            aria-label="Medical assessment"
          >
            <div className="medical-detail-header">
              <div>
                <span className="medical-detail-eyebrow">
                  MEDICAL ASSESSMENT
                </span>

                <h2>Record Medical Result</h2>

                <p>
                  Complete the examination record and medical clearance
                  result.
                </p>
              </div>

              <button
                type="button"
                className="medical-close-button"
                onClick={() => setSelectedAssessmentId(null)}
                aria-label="Close assessment"
              >
                ×
              </button>
            </div>

            <div className="medical-form-grid">
              <label className="medical-field">
                <span>Medical Center</span>

                <input
                  type="text"
                  value={assessmentForm.medical_center}
                  onChange={(event) =>
                    updateAssessmentField(
                      "medical_center",
                      event.target.value
                    )
                  }
                />
              </label>

              <label className="medical-field">
                <span>Examination Date &amp; Time</span>

                <input
                  type="datetime-local"
                  value={assessmentForm.examination_date}
                  onChange={(event) =>
                    updateAssessmentField(
                      "examination_date",
                      event.target.value
                    )
                  }
                />
              </label>

              <label className="medical-field">
                <span>Doctor</span>

                <input
                  type="text"
                  value={assessmentForm.doctor_name}
                  onChange={(event) =>
                    updateAssessmentField(
                      "doctor_name",
                      event.target.value
                    )
                  }
                />
              </label>

              <label className="medical-field">
                <span>Medical Type</span>

                <input
                  type="text"
                  value={assessmentForm.medical_type}
                  onChange={(event) =>
                    updateAssessmentField(
                      "medical_type",
                      event.target.value
                    )
                  }
                />
              </label>

              <label className="medical-field">
                <span>Status</span>

                <select
                  value={assessmentForm.status}
                  onChange={(event) =>
                    updateAssessmentField(
                      "status",
                      event.target.value
                    )
                  }
                >
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </label>

              <label className="medical-field">
                <span>Medical Result</span>

                <select
                  value={assessmentForm.result}
                  onChange={(event) =>
                    updateAssessmentField(
                      "result",
                      event.target.value
                    )
                  }
                >
                  <option value="Fit">Fit</option>
                  <option value="Unfit">Unfit</option>
                  <option value="Further Review">
                    Further Review
                  </option>
                </select>
              </label>

              <label className="medical-field medical-field-wide">
                <span>Report Notes</span>

                <textarea
                  rows="5"
                  value={assessmentForm.report_notes}
                  onChange={(event) =>
                    updateAssessmentField(
                      "report_notes",
                      event.target.value
                    )
                  }
                  placeholder="Enter medical assessment notes..."
                />
              </label>
            </div>

            <div className="medical-form-footer">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setSelectedAssessmentId(null)}
                disabled={savingAssessment}
              >
                Cancel
              </button>

              <button
                type="button"
                className="primary-button"
                disabled={savingAssessment}
                onClick={() => {
                  const record = medicalRecords.find(
                    (item) => item.id === selectedAssessmentId
                  );

                  if (record) {
                    handleSaveAssessment(record);
                  }
                }}
              >
                {savingAssessment
                  ? "Saving..."
                  : "Save Medical Assessment"}
              </button>
            </div>
          </aside>
        </div>
      )}

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

                <p>
                  {selectedRecord.candidate_email || "—"}
                </p>
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
                <strong>
                  {selectedRecord.medical_center || "—"}
                </strong>
              </div>

              <div>
                <span>Examination Date</span>
                <strong>
                  {formatDate(selectedRecord.examination_date)}
                </strong>
              </div>

              <div>
                <span>Doctor</span>
                <strong>
                  {selectedRecord.doctor_name || "—"}
                </strong>
              </div>

              <div>
                <span>Medical Type</span>
                <strong>
                  {selectedRecord.medical_type || "—"}
                </strong>
              </div>

              <div>
                <span>Candidate Phone</span>
                <strong>
                  {selectedRecord.candidate_phone || "—"}
                </strong>
              </div>
            </div>

            <div className="medical-notes">
              <span>Report Notes</span>
              <p>
                {selectedRecord.report_notes ||
                  "No report notes provided."}
              </p>
            </div>

            {selectedRecord.completed_at && (
              <div className="medical-completed">
                <span>Completed</span>
                <strong>
                  {formatDate(selectedRecord.completed_at)}
                </strong>
              </div>
            )}

            {String(selectedRecord.status || "").toLowerCase() !==
              "completed" && (
              <div className="medical-detail-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    openAssessment(selectedRecord);
                    setSelectedRecord(null);
                  }}
                >
                  Assess Examination
                </button>
              </div>
            )}
          </aside>
        </div>
      )}
    </>
  );
}
