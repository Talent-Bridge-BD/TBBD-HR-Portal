import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import { authenticatedFetch } from "../utils/auth";

const STATUS_OPTIONS = [
  "Pending",
  "In Progress",
  "Completed",
  "Cancelled",
];

const CHECKLIST_FIELDS = [
  ["contract_signed", "Contract Signed"],
  ["documents_verified", "Documents Verified"],
  ["orientation_completed", "Orientation Completed"],
  ["accommodation_arranged", "Accommodation Arranged"],
  ["transport_arranged", "Transport Arranged"],
];

const getStatusClasses = (status) => {
  switch (status) {
    case "Completed":
      return "bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20";
    case "In Progress":
      return "bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-600/20";
    case "Cancelled":
      return "bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20";
    case "Pending":
    default:
      return "bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-600/20";
  }
};

const getChecklistProgress = (record) => {
  if (!record) {
    return 0;
  }

  const completed = CHECKLIST_FIELDS.filter(([field]) =>
    Boolean(record[field])
  ).length;

  return Math.round((completed / CHECKLIST_FIELDS.length) * 100);
};

const getCandidateInitials = (firstName, lastName) => {
  const first = firstName?.trim()?.charAt(0) || "";
  const last = lastName?.trim()?.charAt(0) || "";

  return `${first}${last}`.toUpperCase() || "C";
};

export default function RecruitmentOnboarding({ auth }) {
  const [organizationId, setOrganizationId] = useState("");
  const [isAdministrator, setIsAdministrator] = useState(false);

  const [applications, setApplications] = useState([]);
  const [onboardingRecords, setOnboardingRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const loadOnboarding = async (resolvedOrganizationId = organizationId, administrator = isAdministrator) => {
    if (!administrator && !resolvedOrganizationId) {
      setApplications([]);
      setOnboardingRecords([]);
      setError("No organization is available for this account.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const applicationsUrl = administrator
        ? "/api/applications"
        : `/api/applications?organization_id=${encodeURIComponent(
            resolvedOrganizationId
          )}`;

      const applicationsResponse = await authenticatedFetch(
        applicationsUrl
      );

      const applicationsData = await applicationsResponse.json();

      if (!applicationsResponse.ok) {
        throw new Error(
          applicationsData.detail || "Unable to load applications."
        );
      }

      const loadedApplications = applicationsData.applications || [];

      const recordsByApplication = await Promise.all(
        loadedApplications.map(async (application) => {
          const applicationOrganizationId =
            application?.organization_id || resolvedOrganizationId;

          if (!applicationOrganizationId) {
            return [];
          }

          const response = await authenticatedFetch(
            `/api/onboarding/application/${encodeURIComponent(
              application.id
            )}?organization_id=${encodeURIComponent(
              applicationOrganizationId
            )}`
          );

          if (response.status === 404) {
            return [];
          }

          const data = await response.json();

          if (!response.ok) {
            throw new Error(
              data.detail ||
                `Unable to load onboarding for application ${application.id}.`
            );
          }

          return data.onboarding || [];
        })
      );

      setApplications(loadedApplications);
      setOnboardingRecords(recordsByApplication.flat());
    } catch (loadError) {
      setApplications([]);
      setOnboardingRecords([]);
      setError(
        loadError.message || "Unable to load onboarding records."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const meResponse = await authenticatedFetch("/api/me");

        if (!meResponse.ok) {
          throw new Error("Unable to load the signed-in user.");
        }

        const meData = await meResponse.json();

        const roles = meData?.roles || [];
        const administrator = roles.includes("Administrator");

        const resolvedOrganizationId =
          meData?.user?.organization_id ||
          meData?.user?.organization_ids?.[0] ||
          meData?.organization_id ||
          meData?.organization_ids?.[0] ||
          "";

        if (cancelled) {
          return;
        }

        setIsAdministrator(administrator);
        setOrganizationId(resolvedOrganizationId);

        if (!administrator && !resolvedOrganizationId) {
          setError("No organization is available for this account.");
          setLoading(false);
          return;
        }

        await loadOnboarding(
          resolvedOrganizationId,
          administrator
        );
      } catch (loadError) {
        if (!cancelled) {
          setApplications([]);
          setOnboardingRecords([]);
          setError(
            loadError.message || "Unable to load onboarding records."
          );
          setLoading(false);
        }
      }
    };

    load();

    return () => {
      cancelled = true;
    };
  }, []);

  const applicationMap = useMemo(
    () =>
      new Map(
        applications.map((application) => [application.id, application])
      ),
    [applications]
  );

  const recordsByApplication = useMemo(
    () =>
      new Map(
        onboardingRecords.map((record) => [
          record.application_id,
          record,
        ])
      ),
    [onboardingRecords]
  );

  const filteredApplications = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    return applications.filter((application) => {
      const record = recordsByApplication.get(application.id);

      const candidateName = [
        application.candidate_first_name,
        application.candidate_last_name,
      ]
        .filter(Boolean)
        .join(" ");

      const searchableText = [
        candidateName,
        application.candidate_email,
        application.job_title,
        record?.job_title,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      const matchesSearch =
        !normalizedSearch ||
        searchableText.includes(normalizedSearch);

      const recordStatus = record?.status || "Not Started";

      const matchesStatus =
        statusFilter === "All" ||
        (statusFilter === "Pending" &&
          (recordStatus === "Pending" ||
            recordStatus === "Not Started")) ||
        recordStatus === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [applications, recordsByApplication, searchTerm, statusFilter]);

  const counters = useMemo(
    () => ({
      pending: applications.filter((application) => {
        const record = recordsByApplication.get(application.id);
        return !record || record.status === "Pending";
      }).length,

      inProgress: onboardingRecords.filter(
        (record) => record.status === "In Progress"
      ).length,

      completed: onboardingRecords.filter(
        (record) => record.status === "Completed"
      ).length,

      readyForDeployment: onboardingRecords.filter(
        (record) =>
          record.status === "Completed" &&
          record.contract_signed &&
          record.documents_verified &&
          record.orientation_completed
      ).length,
    }),
    [applications, onboardingRecords, recordsByApplication]
  );

  const openCreate = (application) => {
    setSelectedApplication(application);
    setSelectedRecord({
      application_id: application.id,
      employer_name: "",
      job_title: application.job_title || "",
      joining_date: "",
      status: "Pending",
      contract_signed: false,
      documents_verified: false,
      orientation_completed: false,
      accommodation_arranged: false,
      transport_arranged: false,
      notes: "",
    });
  };

  const openEdit = (record) => {
    setSelectedApplication(
      applicationMap.get(record.application_id) || null
    );
    setSelectedRecord({
      ...record,
      joining_date: record.joining_date || "",
      notes: record.notes || "",
    });
  };

  const closeEditor = () => {
    setSelectedRecord(null);
    setSelectedApplication(null);
  };

  const saveRecord = async (event) => {
    event.preventDefault();

    if (!selectedRecord) {
      return;
    }

    const isNew = !selectedRecord.id;

    const payload = {
      employer_name: selectedRecord.employer_name || null,
      job_title: selectedRecord.job_title || null,
      joining_date: selectedRecord.joining_date || null,
      status: selectedRecord.status,
      contract_signed: Boolean(selectedRecord.contract_signed),
      documents_verified: Boolean(selectedRecord.documents_verified),
      orientation_completed: Boolean(
        selectedRecord.orientation_completed
      ),
      accommodation_arranged: Boolean(
        selectedRecord.accommodation_arranged
      ),
      transport_arranged: Boolean(
        selectedRecord.transport_arranged
      ),
      notes: selectedRecord.notes || null,
    };

    if (isNew) {
      payload.application_id = selectedRecord.application_id;
    }

    try {
      const response = await fetch(
        isNew
          ? `/api/onboarding?organization_id=${encodeURIComponent(
              organizationId
            )}`
          : `/api/onboarding/${encodeURIComponent(
              selectedRecord.id
            )}?organization_id=${encodeURIComponent(organizationId)}`,
        {
          method: isNew ? "POST" : "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to save onboarding record."
        );
      }

      closeEditor();
      await loadOnboarding();
    } catch (saveError) {
      setError(
        saveError.message || "Unable to save onboarding record."
      );
    }
  };

  return (
    <>
      <PageHeader
        title="🚀 Onboarding Management"
        subtitle="Manage employee onboarding and deployment readiness."
      />

      <div className="onboarding-kpi-grid">
        <section className="dashboard-card w-full overflow-hidden border border-amber-100 bg-white p-4 shadow-sm">
          <div className="flex min-h-[112px] items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-500">Pending</p>
              <p className="mt-1 text-3xl font-bold tracking-tight text-gray-900">
                {counters.pending}
              </p>
              <p className="mt-1 text-xs text-amber-700">
                Awaiting onboarding action
              </p>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-lg">
              ⏳
            </div>
          </div>
          <div className="mt-3 h-1 rounded-full bg-amber-100">
            <div className="h-1 w-1/3 rounded-full bg-amber-500" />
          </div>
        </section>

        <section className="dashboard-card w-full overflow-hidden border border-blue-100 bg-white p-4 shadow-sm">
          <div className="flex min-h-[112px] items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-500">In Progress</p>
              <p className="mt-1 text-3xl font-bold tracking-tight text-gray-900">
                {counters.inProgress}
              </p>
              <p className="mt-1 text-xs text-blue-700">
                Currently being processed
              </p>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-lg">
              🔄
            </div>
          </div>
          <div className="mt-3 h-1 rounded-full bg-blue-100">
            <div className="h-1 w-1/2 rounded-full bg-[#0067B8]" />
          </div>
        </section>

        <section className="dashboard-card w-full overflow-hidden border border-green-100 bg-white p-4 shadow-sm">
          <div className="flex min-h-[112px] items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-500">Completed</p>
              <p className="mt-1 text-3xl font-bold tracking-tight text-gray-900">
                {counters.completed}
              </p>
              <p className="mt-1 text-xs text-green-700">
                Onboarding completed
              </p>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-green-50 text-lg">
              ✅
            </div>
          </div>
          <div className="mt-3 h-1 rounded-full bg-green-100">
            <div className="h-1 w-full rounded-full bg-green-500" />
          </div>
        </section>

        <section className="dashboard-card w-full overflow-hidden border border-[#0067B8]/15 bg-white p-4 shadow-sm">
          <div className="flex min-h-[112px] items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-500">
                Ready for Deployment
              </p>
              <p className="mt-1 text-3xl font-bold tracking-tight text-gray-900">
                {counters.readyForDeployment}
              </p>
              <p className="mt-1 text-xs text-[#0067B8]">
                Ready for next stage
              </p>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#0067B8]/10 text-lg">
              🚀
            </div>
          </div>
          <div className="mt-3 h-1 rounded-full bg-[#0067B8]/10">
            <div className="h-1 w-2/3 rounded-full bg-[#0067B8]" />
          </div>
        </section>
      </div>

      <section className="mb-6 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="onboarding-toolbar-layout">
          <div className="relative min-w-0 flex-1">
            <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-gray-400">
              🔍
            </span>
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search Candidate"
              aria-label="Search candidate"
              className="h-11 w-full rounded-lg border border-gray-300 bg-white py-2.5 pl-10 pr-4 text-sm text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-[#0067B8] focus:ring-2 focus:ring-[#0067B8]/20"
            />
          </div>

          <div className="onboarding-toolbar-actions">
            <div className="relative w-full sm:w-[160px]">
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
                aria-label="Filter onboarding records"
                className="h-11 w-full appearance-none rounded-lg border border-gray-300 bg-white py-2.5 pl-4 pr-10 text-sm font-medium text-gray-700 outline-none transition focus:border-[#0067B8] focus:ring-2 focus:ring-[#0067B8]/20"
              >
                <option value="All">Filter</option>
                {STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
              <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-gray-400">
                ▾
              </span>
            </div>

            <button
              type="button"
              className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-5 text-sm font-medium text-gray-700 transition hover:border-[#0067B8] hover:text-[#0067B8] disabled:cursor-not-allowed disabled:opacity-60 sm:w-[120px]"
              disabled
              title="Export will be added after the onboarding workflow is finalized."
            >
              <span>↓</span>
              <span>Export</span>
            </button>
          </div>
        </div>
      </section>
      <section className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-200 px-5 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#0067B8]/10 text-lg">
              📋
            </div>

            <div>
              <h2 className="text-base font-semibold text-gray-900">
                Onboarding Records
              </h2>
              <p className="mt-0.5 text-sm text-gray-500">
                Manage onboarding steps for recruitment applications.
              </p>
            </div>
          </div>
        </div>

        {loading && (
          <div className="px-6 py-12 text-center text-sm text-gray-500">
            Loading onboarding records...
          </div>
        )}

        {!loading && error && (
          <div className="m-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && applications.length === 0 && (
          <div className="px-6 py-12 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-xl">
              📋
            </div>
            <p className="mt-3 text-sm font-medium text-gray-900">
              No onboarding records found
            </p>
            <p className="mt-1 text-sm text-gray-500">
              Onboarding records will appear here when recruitment
              applications are available.
            </p>
          </div>
        )}

        {!loading && !error && applications.length > 0 && (
          <div className="onboarding-table-wrap">
            <table className="onboarding-table">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50/70 text-left">
                  <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500 sm:px-6">
                    Candidate
                  </th>
                  <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Job Title
                  </th>
                  <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Status
                  </th>
                  <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Progress
                  </th>
                  <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-gray-500 sm:px-6">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-100">
                {filteredApplications.length === 0 ? (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-6 py-12 text-center text-sm text-gray-500"
                    >
                      No matching onboarding records.
                    </td>
                  </tr>
                ) : (
                  filteredApplications.map((application) => {
                    const record = recordsByApplication.get(application.id);

                    const candidateName = [
                      application.candidate_first_name,
                      application.candidate_last_name,
                    ]
                      .filter(Boolean)
                      .join(" ") || "Unknown Candidate";

                    const initials = getCandidateInitials(
                      application.candidate_first_name,
                      application.candidate_last_name
                    );

                    const status = record?.status || "Pending";
                    const progress = getChecklistProgress(record);

                    const actionLabel = !record
                      ? "Start"
                      : status === "Completed"
                        ? "Deploy"
                        : status === "Cancelled"
                          ? "View"
                          : status === "Pending"
                            ? "View"
                            : "Edit";

                    const handleAction = () => {
                      if (!record) {
                        openCreate(application);
                        return;
                      }
                      openEdit(record);
                    };

                    return (
                      <tr
                        key={application.id}
                        className="transition hover:bg-gray-50"
                      >
                        <td className="px-5 py-4 sm:px-6">
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#0067B8]/10 text-sm font-semibold text-[#0067B8]">
                              {initials}
                            </div>

                            <div className="min-w-0">
                              <p className="truncate text-sm font-semibold text-gray-900">
                                {candidateName}
                              </p>
                              <p className="mt-0.5 truncate text-xs text-gray-500">
                                {application.candidate_email ||
                                  "No email available"}
                              </p>
                            </div>
                          </div>
                        </td>

                        <td className="px-5 py-4">
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {record?.job_title ||
                                application.job_title ||
                                "—"}
                            </p>

                            {record?.employer_name && (
                              <p className="mt-0.5 text-xs text-gray-500">
                                {record.employer_name}
                              </p>
                            )}
                          </div>
                        </td>

                        <td className="px-5 py-4">
                          <span
                            className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${getStatusClasses(
                              status
                            )}`}
                          >
                            <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-current" />
                            {status}
                          </span>
                        </td>

                        <td className="px-5 py-4">
                          <div className="w-40">
                            <div className="mb-1.5 flex items-center justify-between gap-3">
                              
                              <div className="flex items-center justify-between gap-3">
                                <span className="text-xs font-medium text-gray-500">
                                  Progress
                                </span>
                                <span className="text-xs font-bold text-gray-900">
                                  {progress}%
                                </span>
                              </div>
                            </div>

                            <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                              <div
                                className={`h-full rounded-full transition-all ${
                                  progress === 100
                                    ? "bg-green-500"
                                    : progress > 0
                                      ? "bg-[#0067B8]"
                                      : "bg-gray-300"
                                }`}
                                style={{ width: `${progress}%` }}
                              />
                            </div>
                          </div>
                        </td>

                        <td className="px-5 py-4 text-right sm:px-6">
                          <button
                            type="button"
                            onClick={handleAction}
                            className={`inline-flex items-center justify-center rounded-lg px-3.5 py-2 text-sm font-semibold transition ${
                              actionLabel === "Deploy"
                                ? "bg-green-600 text-white hover:bg-green-700"
                                : "bg-[#0067B8] text-white hover:bg-[#005a9f]"
                            }`}
                          >
                            {actionLabel}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedRecord && (
        <div className="deployment-editor-backdrop">
          <section
            className="deployment-editor"
            role="dialog"
            aria-modal="true"
            aria-labelledby="onboarding-editor-title"
          >
            <div className="deployment-editor-header">
              <div className="deployment-editor-hero">
                <div className="deployment-editor-avatar">
                  {getCandidateInitials(
                    selectedApplication?.candidate_first_name,
                    selectedApplication?.candidate_last_name
                  )}
                </div>

                <div className="deployment-editor-hero-info">
                  <div className="deployment-editor-name-line">
                    <div>
                      <p className="deployment-editor-kicker">
                        {selectedRecord.id
                          ? "Edit Onboarding"
                          : "Start Onboarding"}
                      </p>

                      <h2 id="onboarding-editor-title">
                        {[
                          selectedApplication?.candidate_first_name,
                          selectedApplication?.candidate_last_name,
                        ]
                          .filter(Boolean)
                          .join(" ") || "Candidate Profile"}
                      </h2>
                    </div>

                    <span className="deployment-editor-status">
                      ● {selectedRecord.status || "Pending"}
                    </span>
                  </div>

                  <p className="deployment-editor-job-title">
                    {selectedRecord.job_title ||
                      selectedApplication?.job_title ||
                      "Job title not added"}
                  </p>

                  <p className="deployment-editor-organization">
                    {selectedRecord.employer_name || "Employer not added"}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={closeEditor}
                aria-label="Close onboarding editor"
                className="deployment-editor-close"
              >
                ×
              </button>
            </div>

            <form onSubmit={saveRecord} className="deployment-editor-form">
              <section className="deployment-editor-completion">
                <div className="deployment-editor-completion-heading">
                  <div>
                    <strong>Onboarding Readiness</strong>
                    <span>
                      {
                        CHECKLIST_FIELDS.filter(([field]) =>
                          Boolean(selectedRecord[field])
                        ).length
                      }{" "}
                      of {CHECKLIST_FIELDS.length} onboarding steps completed
                    </span>
                  </div>

                  <strong>
                    {getChecklistProgress(selectedRecord)}%
                  </strong>
                </div>

                <div className="deployment-editor-completion-track">
                  <div
                    className="deployment-editor-completion-bar"
                    style={{
                      width: `${getChecklistProgress(
                        selectedRecord
                      )}%`,
                    }}
                  />
                </div>
              </section>

              <section className="deployment-editor-section">
                <div className="deployment-editor-section-heading">
                  <h3>Candidate & Employment Information</h3>
                  <p>
                    Candidate and employment details for this onboarding
                    record.
                  </p>
                </div>

                {selectedApplication?.candidate_email && (
                  <div className="deployment-editor-information-item deployment-editor-information-full">
                    <span>Candidate Email</span>
                    <strong>
                      {selectedApplication.candidate_email}
                    </strong>
                  </div>
                )}

                <div className="deployment-editor-information-grid">
                  <label className="deployment-editor-information-item">
                    <span>Employer</span>
                    <input
                      value={selectedRecord.employer_name || ""}
                      onChange={(event) =>
                        setSelectedRecord((current) => ({
                          ...current,
                          employer_name: event.target.value,
                        }))
                      }
                      placeholder="Employer name"
                    />
                  </label>

                  <label className="deployment-editor-information-item">
                    <span>Job Title</span>
                    <input
                      value={selectedRecord.job_title || ""}
                      onChange={(event) =>
                        setSelectedRecord((current) => ({
                          ...current,
                          job_title: event.target.value,
                        }))
                      }
                      placeholder="Job title"
                    />
                  </label>

                  <label className="deployment-editor-information-item">
                    <span>Joining Date</span>
                    <input
                      type="date"
                      value={selectedRecord.joining_date || ""}
                      onChange={(event) =>
                        setSelectedRecord((current) => ({
                          ...current,
                          joining_date: event.target.value,
                        }))
                      }
                    />
                  </label>

                  <label className="deployment-editor-information-item">
                    <span>Status</span>
                    <select
                      value={selectedRecord.status || "Pending"}
                      onChange={(event) =>
                        setSelectedRecord((current) => ({
                          ...current,
                          status: event.target.value,
                        }))
                      }
                    >
                      {STATUS_OPTIONS.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              </section>

              <section className="deployment-editor-section">
                <div className="deployment-editor-section-heading">
                  <h3>Onboarding Checklist</h3>
                  <p>
                    Track onboarding completion and deployment readiness.
                  </p>
                </div>

                <div className="deployment-editor-checklist">
                  {CHECKLIST_FIELDS.map(([field, label]) => (
                    <label
                      key={field}
                      className={`deployment-editor-checklist-item ${
                        selectedRecord[field] ? "is-complete" : ""
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={Boolean(selectedRecord[field])}
                        onChange={(event) =>
                          setSelectedRecord((current) => ({
                            ...current,
                            [field]: event.target.checked,
                          }))
                        }
                      />

                      <span className="deployment-editor-checklist-label">
                        {label}
                      </span>

                      {selectedRecord[field] && (
                        <span className="deployment-editor-checklist-status">
                          Complete
                        </span>
                      )}
                    </label>
                  ))}
                </div>
              </section>

              <section className="deployment-editor-section">
                <div className="deployment-editor-section-heading">
                  <h3>Notes & Activity</h3>
                  <p>
                    Add onboarding remarks, deployment instructions, or
                    important information.
                  </p>
                </div>

                <div className="deployment-editor-journey">
                  <div className="deployment-editor-journey-heading">
                    <strong>Onboarding Journey</strong>
                    <span>Current session</span>
                  </div>

                  <div className="deployment-editor-journey-item">
                    <span className="deployment-editor-journey-dot is-active" />
                    <p>Onboarding record opened for review</p>
                  </div>

                  <div className="deployment-editor-journey-item">
                    <span className="deployment-editor-journey-dot" />
                    <p>Checklist status can be updated below</p>
                  </div>
                </div>

                <label className="deployment-editor-notes">
                  <span>Notes</span>

                  <textarea
                    rows="5"
                    value={selectedRecord.notes || ""}
                    onChange={(event) =>
                      setSelectedRecord((current) => ({
                        ...current,
                        notes: event.target.value,
                      }))
                    }
                    placeholder="Add onboarding notes, deployment instructions, or remarks..."
                  />
                </label>
              </section>

              <div className="deployment-editor-actions">
                <button
                  type="button"
                  className="deployment-editor-button deployment-editor-button-secondary"
                  onClick={closeEditor}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="deployment-editor-button deployment-editor-button-primary"
                >
                  Save Onboarding
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </>
  );
}
