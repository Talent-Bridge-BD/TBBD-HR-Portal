import { useEffect, useState } from "react";
import { authenticatedFetch } from "../utils/auth";

const API_BASE = "";

export default function Jobs({ auth }) {
  const [jobs, setJobs] = useState([]);

  const roles = auth?.roles || [];
  const organizationId = auth?.organization_ids?.[0] || "";
  const isAdministrator = roles.includes("Administrator");
  const canManageJobs = roles.some((role) =>
    ["Employer Manager", "HR Manager", "Administrator"].includes(role)
  );
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingJobId, setEditingJobId] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    title: "",
    description: "",
    employment_type: "",
    location: "",
    country: "",
    status: "draft",
    number_of_positions: "",
    published_at: "",
    closing_at: "",

    // Overseas recruitment core fields
    requisition_number: "",
    employer_name: "",
    employer_country: "",
    employer_city: "",
    trade_skill_category: "",
    industry_sector: "",
    gender_requirement: "",
    minimum_age: "",
    maximum_age: "",
    contract_duration: "",
    work_location: "",
    project_name: "",

    // Job Requirements
    years_of_experience: "",
    education_requirement: "",
    language_requirement: "",
    required_certifications: "",

    // Visa Requirements
    visa_type: "",
    visa_number: "",
    visa_quota: "",
    visa_expiry: "",

    // Deployment
    deployment_date: "",
    batch_number: "",

    // Compensation & Benefits
    salary_currency: "",
    basic_salary: "",
    overtime_rate: "",
    food_provided: false,
    accommodation_provided: false,
    transportation_provided: false,
    medical_coverage: false,
    air_ticket_provided: false,
    leave_entitlement: "",
    other_benefits: "",
  });

  async function loadJobs() {
    if (!isAdministrator && !organizationId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/jobs?organization_id=${encodeURIComponent(isAdministrator ? "" : organizationId)}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to load jobs");
      }

      setJobs(data.jobs || []);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    loadJobs();
  }, [organizationId, isAdministrator]);
  function updateForm(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function saveJob(event) {
    event.preventDefault();

    if (!organizationId) {
      setMessage("No active organization is available.");
      return;
    }

    setSaving(true);
    setMessage("");

    const editing = Boolean(editingJobId);

    try {
      const response = await fetch(
        editing
          ? `${API_BASE}/api/jobs/${encodeURIComponent(editingJobId)}`
          : `${API_BASE}/api/jobs`,
        {
          method: editing ? "PUT" : "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            organization_id: organizationId,
            title: form.title,
            description: form.description,
            employment_type: form.employment_type,
            location: form.location,
            country: form.country,
            status: form.status,
            number_of_positions: form.number_of_positions
              ? Number(form.number_of_positions)
              : null,
            published_at: form.published_at || null,
            closing_at: form.closing_at || null,

            // Overseas recruitment core fields
            requisition_number: form.requisition_number || null,
            employer_name: form.employer_name || null,
            employer_country: form.employer_country || null,
            employer_city: form.employer_city || null,
            trade_skill_category: form.trade_skill_category || null,
            industry_sector: form.industry_sector || null,
            gender_requirement: form.gender_requirement || null,
            minimum_age: form.minimum_age
              ? Number(form.minimum_age)
              : null,
            maximum_age: form.maximum_age
              ? Number(form.maximum_age)
              : null,
            contract_duration: form.contract_duration || null,
            work_location: form.work_location || null,
            project_name: form.project_name || null,

            years_of_experience: form.years_of_experience || null,
            education_requirement: form.education_requirement || null,
            language_requirement: form.language_requirement || null,
            required_certifications: form.required_certifications || null,

            visa_type: form.visa_type || null,
            visa_number: form.visa_number || null,
            visa_quota: form.visa_quota || null,
            visa_expiry: form.visa_expiry || null,

            deployment_date: form.deployment_date || null,
            batch_number: form.batch_number || null,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || (editing ? "Unable to update job" : "Unable to create job")
        );
      }

      const savedJobId = data.job?.id || editingJobId;

      if (!savedJobId) {
        throw new Error("Job was saved but no job ID was returned.");
      }

      const compensationResponse = await fetch(
        `${API_BASE}/api/jobs/${encodeURIComponent(savedJobId)}/compensation`,
        {
          method: "PUT",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            organization_id: organizationId,
            salary_currency: form.salary_currency || null,
            basic_salary: form.basic_salary
              ? Number(form.basic_salary)
              : null,
            overtime_rate: form.overtime_rate
              ? Number(form.overtime_rate)
              : null,
            food_provided: Boolean(form.food_provided),
            accommodation_provided: Boolean(form.accommodation_provided),
            transportation_provided: Boolean(form.transportation_provided),
            medical_coverage: Boolean(form.medical_coverage),
            air_ticket_provided: Boolean(form.air_ticket_provided),
            leave_entitlement: form.leave_entitlement || null,
            other_benefits: form.other_benefits || null,
          }),
        }
      );

      const compensationData = await compensationResponse.json();

      if (!compensationResponse.ok) {
        throw new Error(
          compensationData.detail || "Unable to save compensation details"
        );
      }

      setShowCreateForm(false);
      setEditingJobId("");

      setForm({
        title: "",
        description: "",
        employment_type: "",
        location: "",
        country: "",
        status: "draft",
        number_of_positions: "",
        published_at: "",
        closing_at: "",

        // Overseas recruitment core fields
        requisition_number: "",
        employer_name: "",
        employer_country: "",
        employer_city: "",
        trade_skill_category: "",
        industry_sector: "",
        gender_requirement: "",
        minimum_age: "",
        maximum_age: "",
        contract_duration: "",
        work_location: "",
        project_name: "",

        // Job Requirements
        years_of_experience: "",
        education_requirement: "",
        language_requirement: "",
        required_certifications: "",

        // Visa Requirements
        visa_type: "",
        visa_number: "",
        visa_quota: "",
        visa_expiry: "",

        // Deployment
        deployment_date: "",
        batch_number: "",

        // Compensation & Benefits
        salary_currency: "",
        basic_salary: "",
        overtime_rate: "",
        food_provided: false,
        accommodation_provided: false,
        transportation_provided: false,
        medical_coverage: false,
        air_ticket_provided: false,
        leave_entitlement: "",
        other_benefits: "",
      });

      await loadJobs();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  function openCreateForm() {
    setEditingJobId("");
    setForm({
      title: "",
      description: "",
      employment_type: "",
      location: "",
      country: "",
      status: "draft",
      number_of_positions: "",
      published_at: "",
      closing_at: "",

      // Overseas recruitment core fields
      requisition_number: "",
      employer_name: "",
      employer_country: "",
      employer_city: "",
      trade_skill_category: "",
      industry_sector: "",
      gender_requirement: "",
      minimum_age: "",
      maximum_age: "",
      contract_duration: "",
      work_location: "",
      project_name: "",

      // Compensation & Benefits
      salary_currency: "",
      basic_salary: "",
      overtime_rate: "",
      food_provided: false,
      accommodation_provided: false,
      transportation_provided: false,
      medical_coverage: false,
      air_ticket_provided: false,
      leave_entitlement: "",
      other_benefits: "",
    });
    setMessage("");
    setShowCreateForm(true);
  }

  async function openEditForm(job) {
    let compensation = null;

    try {
      const response = await fetch(
        `${API_BASE}/api/jobs/${encodeURIComponent(job.id)}/compensation?organization_id=${encodeURIComponent(organizationId)}`,
        {
          credentials: "include",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to load compensation details");
      }

      compensation = data.compensation;
    } catch (error) {
      setMessage(error.message);
      return;
    }

    setEditingJobId(job.id);
    setForm({
      title: job.title || "",
      description: job.description || "",
      employment_type: job.employment_type || "",
      location: job.location || "",
      country: job.country || "",
      status: job.status || "draft",
      number_of_positions:
        job.number_of_positions === null || job.number_of_positions === undefined
          ? ""
          : String(job.number_of_positions),
      published_at: job.published_at
        ? new Date(job.published_at).toISOString().slice(0, 16)
        : "",
      closing_at: job.closing_at
        ? new Date(job.closing_at).toISOString().slice(0, 16)
        : "",

      // Overseas recruitment core fields
      requisition_number: job.requisition_number || "",
      employer_name: job.employer_name || "",
      employer_country: job.employer_country || "",
      employer_city: job.employer_city || "",
      trade_skill_category: job.trade_skill_category || "",
      industry_sector: job.industry_sector || "",
      gender_requirement: job.gender_requirement || "",
      minimum_age: job.minimum_age ?? "",
      maximum_age: job.maximum_age ?? "",
      contract_duration: job.contract_duration || "",
      work_location: job.work_location || "",
      project_name: job.project_name || "",

      // Job Requirements
      years_of_experience: job.years_of_experience || "",
      education_requirement: job.education_requirement || "",
      language_requirement: job.language_requirement || "",
      required_certifications: job.required_certifications || "",

      // Visa Requirements
      visa_type: job.visa_type || "",
      visa_number: job.visa_number || "",
      visa_quota: job.visa_quota || "",
      visa_expiry: job.visa_expiry || "",

      // Deployment
      deployment_date: job.deployment_date || "",
      batch_number: job.batch_number || "",

      // Compensation & Benefits
      salary_currency: compensation?.salary_currency || "",
      basic_salary:
        compensation?.basic_salary === null ||
        compensation?.basic_salary === undefined
          ? ""
          : String(compensation.basic_salary),
      overtime_rate:
        compensation?.overtime_rate === null ||
        compensation?.overtime_rate === undefined
          ? ""
          : String(compensation.overtime_rate),
      food_provided: Boolean(compensation?.food_provided),
      accommodation_provided: Boolean(compensation?.accommodation_provided),
      transportation_provided: Boolean(compensation?.transportation_provided),
      medical_coverage: Boolean(compensation?.medical_coverage),
      air_ticket_provided: Boolean(compensation?.air_ticket_provided),
      leave_entitlement: compensation?.leave_entitlement || "",
      other_benefits: compensation?.other_benefits || "",
    });
    setMessage("");
    setShowCreateForm(true);
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <h1>Jobs</h1>
          <p>Manage recruitment job openings and workforce requirements.</p>
        </div>
      </div>

      {showCreateForm && (
        <div className="card">
          <div className="card-header">
            <h2>{editingJobId ? "Edit Job" : "Create Job"}</h2>
          </div>

          <form onSubmit={saveJob}>
            <div className="form-grid">
              <label className="form-full-width">
                <strong>Employer & Demand Information</strong>
              </label>

              <label>
                Requisition Number
                <input
                  value={form.requisition_number}
                  onChange={(event) =>
                    updateForm("requisition_number", event.target.value)
                  }
                  placeholder="REQ-2026-001"
                />
              </label>

              <label>
                Client / Employer Name
                <input
                  value={form.employer_name}
                  onChange={(event) =>
                    updateForm("employer_name", event.target.value)
                  }
                  placeholder="Employer name"
                />
              </label>

              <label>
                Destination Country
                <input
                  value={form.employer_country}
                  onChange={(event) =>
                    updateForm("employer_country", event.target.value)
                  }
                  placeholder="Saudi Arabia"
                />
              </label>

              <label>
                Destination City
                <input
                  value={form.employer_city}
                  onChange={(event) =>
                    updateForm("employer_city", event.target.value)
                  }
                  placeholder="Riyadh"
                />
              </label>

              <label>
                Project / Worksite Name
                <input
                  value={form.project_name}
                  onChange={(event) =>
                    updateForm("project_name", event.target.value)
                  }
                  placeholder="Project or contract name"
                />
              </label>

              <label className="form-full-width">
                <strong>Job Information</strong>
              </label>

              <label>
                Job Title
                <input
                  required
                  value={form.title}
                  onChange={(event) => updateForm("title", event.target.value)}
                />
              </label>

              <label>
                Trade / Skill Category
                <input
                  value={form.trade_skill_category}
                  onChange={(event) =>
                    updateForm("trade_skill_category", event.target.value)
                  }
                  placeholder="Construction, Welding, Nursing"
                />
              </label>

              <label>
                Industry Sector
                <input
                  value={form.industry_sector}
                  onChange={(event) =>
                    updateForm("industry_sector", event.target.value)
                  }
                  placeholder="Construction, Healthcare, Hospitality"
                />
              </label>

              <label>
                Gender Requirement
                <input
                  value={form.gender_requirement}
                  onChange={(event) =>
                    updateForm("gender_requirement", event.target.value)
                  }
                  placeholder="Any / Male / Female"
                />
              </label>

              <label>
                Minimum Age
                <input
                  type="number"
                  min="0"
                  value={form.minimum_age}
                  onChange={(event) =>
                    updateForm("minimum_age", event.target.value)
                  }
                />
              </label>

              <label>
                Maximum Age
                <input
                  type="number"
                  min="0"
                  value={form.maximum_age}
                  onChange={(event) =>
                    updateForm("maximum_age", event.target.value)
                  }
                />
              </label>

              <label>
                Contract Duration
                <input
                  value={form.contract_duration}
                  onChange={(event) =>
                    updateForm("contract_duration", event.target.value)
                  }
                  placeholder="2 years"
                />
              </label>

              <label>
                Country of Employment / City of Employment
                <input
                  value={form.work_location}
                  onChange={(event) =>
                    updateForm("work_location", event.target.value)
                  }
                  placeholder="Riyadh, Saudi Arabia"
                />
              </label>

              <label>
                Employment Type
                <input
                  value={form.employment_type}
                  onChange={(event) =>
                    updateForm("employment_type", event.target.value)
                  }
                  placeholder="Full-time"
                />
              </label>

              <label>
                Project Location
                <input
                  value={form.location}
                  onChange={(event) =>
                    updateForm("location", event.target.value)
                  }
                  placeholder="Dhaka"
                />
              </label>

              <label>
                Country
                <input
                  value={form.country}
                  onChange={(event) =>
                    updateForm("country", event.target.value)
                  }
                  placeholder="Bangladesh"
                />
              </label>

              <label>
                Status
                <select
                  value={form.status}
                  onChange={(event) => updateForm("status", event.target.value)}
                >
                  <option value="draft">Draft</option>
                  <option value="open">Open</option>
                  <option value="paused">Paused</option>
                </select>
              </label>

              <label>
                Years of Experience
                <input
                  value={form.years_of_experience}
                  onChange={(event) =>
                    updateForm("years_of_experience", event.target.value)
                  }
                />
              </label>

              <label>
                Education Requirement
                <input
                  value={form.education_requirement}
                  onChange={(event) =>
                    updateForm("education_requirement", event.target.value)
                  }
                />
              </label>

              <label>
                Language Requirement
                <input
                  value={form.language_requirement}
                  onChange={(event) =>
                    updateForm("language_requirement", event.target.value)
                  }
                />
              </label>

              <label>
                Required Certifications
                <input
                  value={form.required_certifications}
                  onChange={(event) =>
                    updateForm("required_certifications", event.target.value)
                  }
                />
              </label>

              <label>
                Number of Vacancies
                <input
                  type="number"
                  min="1"
                  value={form.number_of_positions}
                  onChange={(event) =>
                    updateForm("number_of_positions", event.target.value)
                  }
                />
              </label>

              <label>
                Published At
                <input
                  type="datetime-local"
                  value={form.published_at}
                  onChange={(event) =>
                    updateForm("published_at", event.target.value)
                  }
                />
              </label>

              <label>
                Closing At
                <input
                  type="datetime-local"
                  value={form.closing_at}
                  onChange={(event) =>
                    updateForm("closing_at", event.target.value)
                  }
                />
              </label>

              <label className="form-full-width">
                Description
                <textarea
                  rows="6"
                  value={form.description}
                  onChange={(event) =>
                    updateForm("description", event.target.value)
                  }
                />
              </label>

              <div className="form-full-width">
                <strong>Visa Requirements & Deployment</strong>
              </div>

              <label>
                Visa Type
                <input
                  value={form.visa_type}
                  onChange={(event) =>
                    updateForm("visa_type", event.target.value)
                  }
                />
              </label>

              <label>
                Visa Number
                <input
                  value={form.visa_number}
                  onChange={(event) =>
                    updateForm("visa_number", event.target.value)
                  }
                />
              </label>

              <label>
                Visa Quota
                <input
                  value={form.visa_quota}
                  onChange={(event) =>
                    updateForm("visa_quota", event.target.value)
                  }
                />
              </label>

              <label>
                Visa Expiry
                <input
                  type="date"
                  value={form.visa_expiry}
                  onChange={(event) =>
                    updateForm("visa_expiry", event.target.value)
                  }
                />
              </label>

              <label>
                Expected Deployment Date
                <input
                  type="date"
                  value={form.deployment_date}
                  onChange={(event) =>
                    updateForm("deployment_date", event.target.value)
                  }
                />
              </label>

              <label>
                Batch Number
                <input
                  value={form.batch_number}
                  onChange={(event) =>
                    updateForm("batch_number", event.target.value)
                  }
                />
              </label>

              <div className="form-full-width">
                <strong>Compensation & Benefits</strong>
              </div>

              <label>
                Salary Currency
                <input
                  type="text"
                  value={form.salary_currency}
                  onChange={(event) =>
                    updateForm("salary_currency", event.target.value)
                  }
                  placeholder="e.g. SAR, AED, USD"
                />
              </label>

              <label>
                Basic Salary
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.basic_salary}
                  onChange={(event) =>
                    updateForm("basic_salary", event.target.value)
                  }
                />
              </label>

              <label>
                Overtime Rate
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.overtime_rate}
                  onChange={(event) =>
                    updateForm("overtime_rate", event.target.value)
                  }
                />
              </label>

              <label>
                Food Provided
                <input
                  type="checkbox"
                  checked={form.food_provided}
                  onChange={(event) =>
                    updateForm("food_provided", event.target.checked)
                  }
                />
              </label>

              <label>
                Accommodation Provided
                <input
                  type="checkbox"
                  checked={form.accommodation_provided}
                  onChange={(event) =>
                    updateForm(
                      "accommodation_provided",
                      event.target.checked
                    )
                  }
                />
              </label>

              <label>
                Transportation Provided
                <input
                  type="checkbox"
                  checked={form.transportation_provided}
                  onChange={(event) =>
                    updateForm(
                      "transportation_provided",
                      event.target.checked
                    )
                  }
                />
              </label>

              <label>
                Medical Insurance
                <input
                  type="checkbox"
                  checked={form.medical_coverage}
                  onChange={(event) =>
                    updateForm("medical_coverage", event.target.checked)
                  }
                />
              </label>

              <label>
                Air Ticket Provided
                <input
                  type="checkbox"
                  checked={form.air_ticket_provided}
                  onChange={(event) =>
                    updateForm(
                      "air_ticket_provided",
                      event.target.checked
                    )
                  }
                />
              </label>

              <label>
                Annual Leave
                <input
                  type="text"
                  value={form.leave_entitlement}
                  onChange={(event) =>
                    updateForm("leave_entitlement", event.target.value)
                  }
                  placeholder="e.g. 30 days per year"
                />
              </label>

              <label className="form-full-width">
                Other Benefits
                <textarea
                  rows="4"
                  value={form.other_benefits}
                  onChange={(event) =>
                    updateForm("other_benefits", event.target.value)
                  }
                  placeholder="Additional benefits or allowances"
                />
              </label>
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingJobId("");
                }}
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
                  ? editingJobId
                    ? "Saving..."
                    : "Creating..."
                  : editingJobId
                    ? "Save Changes"
                    : "Create Job"}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <div>
            <h2>Job Openings</h2>
            <span>{jobs.length} jobs</span>
          </div>
          {canManageJobs && organizationId && (
            <button
              type="button"
              className="primary-button"
              onClick={openCreateForm}
            >
              + Create Job
            </button>
          )}
        </div>

        {!isAdministrator && !organizationId ? (
          <div className="empty-state">
            <h3>Organization access required</h3>
            <p>
              No active organization is currently assigned to your account.
              Jobs will appear here once organization access is configured.
            </p>
          </div>
        ) : loading ? (
          <div className="empty-state">
            <p>Loading jobs...</p>
          </div>
        ) : message ? (
          <div className="empty-state">
            <h3>Unable to load jobs</h3>
            <p>{message}</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="empty-state">
            <h3>No jobs yet</h3>
            <p>Create your first recruitment job opening to begin building the candidate pipeline.</p>
          </div>
        ) : (
          <div className="jobs-list">
            {jobs.map((job) => (
              <article className="job-row" key={job.id}>
                <div>
                  <h3>{job.title}</h3>
                  <p>
                    {job.location || "Location not specified"}
                    {job.country ? ` · ${job.country}` : ""}
                  </p>
                </div>

                <div className="job-meta">
                  <span className={`job-status job-status-${job.status}`}>
                    {job.status}
                  </span>
                  {job.employment_type && (
                    <span>{job.employment_type}</span>
                  )}
                  {canManageJobs && organizationId && (
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => openEditForm(job)}
                    >
                      Edit
                    </button>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
