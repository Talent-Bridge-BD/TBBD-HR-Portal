import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";

const STATUS_OPTIONS = [
  "Ready",
  "Scheduled",
  "In Transit",
  "Cancelled",
];

const CHECKLIST_FIELDS = [
  ["passport_verified", "Passport Verified"],
  ["medical_cleared", "Medical Cleared"],
  ["visa_approved", "Visa Approved"],
  ["ticket_issued", "Ticket Issued"],
  ["orientation_completed", "Orientation Completed"],
  ["departure_confirmed", "Departure Confirmed"],
  ["arrival_confirmed", "Arrival Confirmed"],
  ["employer_confirmed", "Employer Joined Confirmation"],
];

const getStatusClasses = (status) => {
  switch (status) {
    case "In Transit":
      return "bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20";
    case "Scheduled":
      return "bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-600/20";
    case "Cancelled":
      return "bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20";
    case "Ready":
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

export default function RecruitmentDeployment({ auth }) {
  const [organizationId, setOrganizationId] = useState("");

  const [applications, setApplications] = useState([]);
  const [onboardingRecords, setOnboardingRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const loadOnboarding = async () => {
    if (!organizationId) {
      setApplications([]);
      setOnboardingRecords([]);
      setError("No organization is available for this account.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const applicationsResponse = await fetch(
        `/api/applications?organization_id=${encodeURIComponent(
          organizationId
        )}`
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
          const response = await fetch(
            `/api/onboarding/application/${encodeURIComponent(
              application.id
            )}?organization_id=${encodeURIComponent(organizationId)}`
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
        const meResponse = await fetch("/api/me", {
          credentials: "include",
        });

        if (!meResponse.ok) {
          throw new Error("Unable to load the signed-in user.");
        }

        const meData = await meResponse.json();

        const resolvedOrganizationId =
          meData?.user?.organization_id ||
          meData?.user?.organization_ids?.[0] ||
          meData?.organization_id ||
          meData?.organization_ids?.[0] ||
          "";

        if (cancelled) {
          return;
        }

        console.log("ORG DEBUG", meData, resolvedOrganizationId);
        setOrganizationId(resolvedOrganizationId);

        if (!resolvedOrganizationId) {
          setError("No organization is available for this account.");
          setLoading(false);
          return;
        }

        const applicationsResponse = await fetch(
          `/api/applications?organization_id=${encodeURIComponent(
            resolvedOrganizationId
          )}`
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
            const response = await fetch(
              `/api/onboarding/application/${encodeURIComponent(
                application.id
              )}?organization_id=${encodeURIComponent(
                resolvedOrganizationId
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

        if (!cancelled) {
          
setApplications(loadedApplications);

          setOnboardingRecords(recordsByApplication.flat());
        }
      } catch (loadError) {
        if (!cancelled) {
          setApplications([]);
          setOnboardingRecords([]);
          setError(
            loadError.message || "Unable to load onboarding records."
          );
        }
      } finally {
        if (!cancelled) {
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
        (statusFilter === "Ready" &&
          (recordStatus === "Ready" ||
            recordStatus === "Not Started")) ||
        recordStatus === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [applications, recordsByApplication, searchTerm, statusFilter]);

  const counters = useMemo(
    () => ({
      pending: applications.filter((application) => {
        const record = recordsByApplication.get(application.id);
        return !record || record.status === "Ready";
      }).length,

      inProgress: onboardingRecords.filter(
        (record) => record.status === "Scheduled"
      ).length,

      completed: onboardingRecords.filter(
        (record) => record.status === "In Transit"
      ).length,

      readyForDeployment: onboardingRecords.filter(
        (record) =>
          record.status === "In Transit" &&
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
      status: "Ready",
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
        title="🚀 Deployment Management"
        subtitle="Manage overseas deployment, travel readiness and employer confirmation."
      />

      <div className="onboarding-kpi-grid">
        <section className="dashboard-card w-full overflow-hidden border border-amber-100 bg-white p-4 shadow-sm">
          <div className="flex min-h-[112px] items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-500">Ready</p>
              <p className="mt-1 text-3xl font-bold tracking-tight text-gray-900">
                {counters.pending}
              </p>
              <p className="mt-1 text-xs text-amber-700">
                Ready for travel
              </p>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-lg">
              ✈️
            </div>
          </div>
          <div className="mt-3 h-1 rounded-full bg-amber-100">
            <div className="h-1 w-1/3 rounded-full bg-amber-500" />
          </div>
        </section>

        <section className="dashboard-card w-full overflow-hidden border border-blue-100 bg-white p-4 shadow-sm">
          <div className="flex min-h-[112px] items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-500">Scheduled</p>
              <p className="mt-1 text-3xl font-bold tracking-tight text-gray-900">
                {counters.inProgress}
              </p>
              <p className="mt-1 text-xs text-blue-700">
                Flight scheduled
              </p>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-lg">
              📅
            </div>
          </div>
          <div className="mt-3 h-1 rounded-full bg-blue-100">
            <div className="h-1 w-1/2 rounded-full bg-[#0067B8]" />
          </div>
        </section>

        <section className="dashboard-card w-full overflow-hidden border border-green-100 bg-white p-4 shadow-sm">
          <div className="flex min-h-[112px] items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-500">In Transit</p>
              <p className="mt-1 text-3xl font-bold tracking-tight text-gray-900">
                {counters.completed}
              </p>
              <p className="mt-1 text-xs text-green-700">
                Travelling overseas
              </p>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-green-50 text-lg">
              🌍
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
                Deployed
              </p>
              <p className="mt-1 text-3xl font-bold tracking-tight text-gray-900">
                {counters.readyForDeployment}
              </p>
              <p className="mt-1 text-xs text-[#0067B8]">
                Employer confirmed
              </p>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#0067B8] text-white text-lg">
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
                Deployment Records
              </h2>
              <p className="mt-0.5 text-sm text-gray-500">
                Manage overseas worker deployment and travel activities.
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

                    const status = record?.status || "Ready";
                    const progress = getChecklistProgress(record);

                    const actionLabel = !record
                      ? "Start"
                      : status === "In Transit"
                        ? "Deploy"
                        : status === "Cancelled"
                          ? "View"
                          : status === "Ready"
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
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <section className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
            <div className="mb-6 flex items-start justify-between gap-4 border-b border-gray-200 pb-5">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#0067B8]/10 text-xl text-[#0067B8]">
                  👤
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {selectedRecord.id
                      ? "Edit Onboarding"
                      : "Start Deployment"}
                  </h2>

                  {selectedApplication && (
                    <p className="mt-1 text-sm text-gray-500">
                      {[
                        selectedApplication.candidate_first_name,
                        selectedApplication.candidate_last_name,
                      ]
                        .filter(Boolean)
                        .join(" ") || "Candidate"}

                      {selectedApplication.job_title
                        ? ` · ${selectedApplication.job_title}`
                        : ""}
                    </p>
                  )}
                </div>
              </div>

              <button
                type="button"
                onClick={closeEditor}
                aria-label="Close onboarding editor"
                className="flex h-9 w-9 items-center justify-center rounded-lg text-xl text-gray-400 transition hover:bg-gray-100 hover:text-gray-700"
              >
                ×
              </button>
            </div>

            <form onSubmit={saveRecord} className="space-y-6">
              <div className="onboarding-detail-grid">
                <section className="overflow-hidden rounded-xl border border-gray-200 bg-white">
                  <div className="border-b border-gray-200 bg-gray-50/70 px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#0067B8]/10 text-base text-[#0067B8]">
                        👤
                      </div>

                      <div className="min-w-0">
                        <h3 className="text-sm font-semibold text-gray-900">
                          👤 Candidate Profile
                        </h3>
                        <p className="mt-0.5 text-xs text-gray-500">
                          Candidate and employment details
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4 p-5">
                    {selectedApplication && (
                      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                        <div className="flex items-center gap-3">
                          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[#0067B8]/10 text-sm font-bold text-[#0067B8]">
                            {getCandidateInitials(
                              selectedApplication.candidate_first_name,
                              selectedApplication.candidate_last_name
                            )}
                          </div>

                          <div className="min-w-0">
                            <p className="truncate text-sm font-semibold text-gray-900">
                              {[
                                selectedApplication.candidate_first_name,
                                selectedApplication.candidate_last_name,
                              ]
                                .filter(Boolean)
                                .join(" ") || "Candidate"}
                            </p>

                            <p className="mt-0.5 truncate text-xs text-gray-500">
                              {selectedApplication.candidate_email || "—"}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    <label className="block">
                      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Employer
                      </span>
                      <input
                        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-[#0067B8] focus:ring-2 focus:ring-[#0067B8]/20"
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

                    <label className="block">
                      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Job Title
                      </span>
                      <input
                        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-[#0067B8] focus:ring-2 focus:ring-[#0067B8]/20"
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

                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <label className="block">
                        <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-gray-500">
                          Joining Date
                        </span>
                        <input
                          type="date"
                          className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-[#0067B8] focus:ring-2 focus:ring-[#0067B8]/20"
                          value={selectedRecord.joining_date || ""}
                          onChange={(event) =>
                            setSelectedRecord((current) => ({
                              ...current,
                              joining_date: event.target.value,
                            }))
                          }
                        />
                      </label>

                      <label className="block">
                        <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-gray-500">
                          Status
                        </span>
                        <select
                          className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-[#0067B8] focus:ring-2 focus:ring-[#0067B8]/20"
                          value={selectedRecord.status || "Ready"}
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
                  </div>
                </section>

                <section className="overflow-hidden rounded-xl border border-gray-200 bg-white">
                  <div className="border-b border-gray-200 bg-gray-50/70 px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-50 text-base text-green-600">
                        ✓
                      </div>

                      <div className="min-w-0">
                        <h3 className="text-sm font-semibold text-gray-900">
                          Deployment Checklist
                        </h3>
                        <p className="mt-0.5 text-xs text-gray-500">
                          Track deployment readiness
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-5">
                    <div className="space-y-2.5">
                      {CHECKLIST_FIELDS.map(([field, label]) => (
                        <label
                          key={field}
                          className={`flex cursor-pointer items-center gap-3 rounded-lg border px-4 py-3 transition ${
                            selectedRecord[field]
                              ? "border-green-200 bg-green-50"
                              : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
                          }`}
                        >
                          <input
                            type="checkbox"
                            className="h-4 w-4 rounded border-gray-300 text-[#0067B8] focus:ring-[#0067B8]"
                            checked={Boolean(selectedRecord[field])}
                            onChange={(event) =>
                              setSelectedRecord((current) => ({
                                ...current,
                                [field]: event.target.checked,
                              }))
                            }
                          />

                          <span
                            className={`text-sm font-medium ${
                              selectedRecord[field]
                                ? "text-green-800"
                                : "text-gray-700"
                            }`}
                          >
                            {label}
                          </span>

                          {selectedRecord[field] && (
                            <span className="ml-auto rounded-full bg-green-100 px-2 py-0.5 text-[11px] font-semibold text-green-700">
                              Complete
                            </span>
                          )}
                        </label>
                      ))}
                    </div>

                    <div className="mt-6 rounded-xl border border-[#0067B8]/20 bg-gradient-to-r from-blue-50 to-cyan-50 p-5 shadow-sm">
                      <div className="mb-2 flex items-center justify-between">
                        <span className="text-sm font-semibold text-gray-700">
                          Progress
                        </span>

                        <span className="text-sm font-bold text-[#0067B8]">
                          {getChecklistProgress(selectedRecord)}%
                        </span>
                      </div>

                      <div className="h-2.5 overflow-hidden rounded-full bg-gray-100">
                        <div
                          className="h-full rounded-full bg-[#0067B8] transition-all duration-300"
                          style={{
                            width: `${getChecklistProgress(
                              selectedRecord
                            )}%`,
                          }}
                        />
                      </div>

                      <p className="mt-2 text-xs text-gray-500">
                        {
                          CHECKLIST_FIELDS.filter(([field]) =>
                            Boolean(selectedRecord[field])
                          ).length
                        }{" "}
                        of {CHECKLIST_FIELDS.length} deployment steps completed
                      </p>
                    </div>
                  </div>
                </section>
              </div>

              <section className="overflow-hidden rounded-xl border border-gray-200 bg-white">
                <div className="border-b border-gray-200 bg-gray-50/70 px-5 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 text-base">
                      📝
                    </div>

                    <div>
                      <h3 className="font-semibold text-gray-900">
                        Notes & Activity
                      </h3>
                      <p className="mt-0.5 text-xs text-gray-500">
                        Add onboarding remarks, deployment instructions, or
                        important information.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-5">
                  <div className="mb-5 rounded-xl border border-gray-200 bg-gray-50/70 px-4 py-4">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-gray-900">
                        📋 Deployment Journey
                      </p>
                      <span className="text-xs font-medium text-gray-400">
                        Current session
                      </span>
                    </div>

                    <div className="mt-4 space-y-3">
                      <div className="flex gap-3">
                        <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[#0067B8]" />
                        <p className="text-sm leading-5 text-gray-600">
                          Onboarding record opened for review
                        </p>
                      </div>

                      <div className="flex gap-3">
                        <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-gray-300" />
                        <p className="text-sm leading-5 text-gray-600">
                          Checklist status can be updated below
                        </p>
                      </div>
                    </div>
                  </div>

                  <label className="block">
                    <span className="mb-1.5 block text-sm font-semibold text-gray-700">
                      Notes
                    </span>

                    <textarea
                      className="min-h-[120px] w-full rounded-lg border border-gray-300 bg-white px-3 py-3 text-sm text-gray-900 outline-none transition focus:border-[#0067B8] focus:ring-2 focus:ring-[#0067B8]/20"
                      rows="5"
                      placeholder="Add onboarding notes, deployment instructions, or remarks..."
                      value={selectedRecord.notes || ""}
                      onChange={(event) =>
                        setSelectedRecord((current) => ({
                          ...current,
                          notes: event.target.value,
                        }))
                      }
                    />
                  </label>
                </div>
              </section>

              <div className="flex flex-col-reverse gap-3 border-t border-gray-200 pt-5 sm:flex-row sm:items-center sm:justify-end">
                <button
                  type="button"
                  className="inline-flex h-10 items-center justify-center rounded-lg border border-gray-300 bg-white px-5 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300/40"
                  onClick={closeEditor}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="inline-flex h-10 items-center justify-center rounded-lg bg-[#0067B8] px-5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#005A9E] focus:outline-none focus:ring-2 focus:ring-[#0067B8]/30"
                >
                  Save Deployment 🚀
                </button>
              </div>
            </form>
          </section>

        </div>
      )}
    </>
  );
}
