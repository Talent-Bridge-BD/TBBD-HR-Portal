import { useEffect, useState } from "react";

const API_BASE = "";

const emptyForm = {
  title: "",
  description: "",
  employment_type: "",
  location: "",
  country: "",
  status: "draft",
  number_of_positions: "",
  published_at: "",
  closing_at: "",
  department: "",
  job_category: "",
  workplace_type: "",
  experience: "",
  education: "",
  skills: "",
  salary_compensation: "",
  application_instructions: "",
  responsibilities: "",
  requirements: "",
};

function toDateTimeLocal(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  const pad = (number) => String(number).padStart(2, "0");

  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
    date.getDate()
  )}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [organizationId, setOrganizationId] = useState("");
  const [organizationLoading, setOrganizationLoading] = useState(true);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingJobId, setEditingJobId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(emptyForm);

  async function loadJobs() {
    if (!organizationId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE}/api/jobs?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        { credentials: "include" }
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
    async function loadOrganization() {
      try {
        const response = await fetch("/api/me", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error("Unable to load account information");
        }

        const data = await response.json();
        const ids = data.organization_ids || [];
        setOrganizationId(ids[0] || "");
      } catch (error) {
        setMessage(error.message);
      } finally {
        setOrganizationLoading(false);
      }
    }

    loadOrganization();
  }, []);

  useEffect(() => {
    if (!organizationLoading) {
      loadJobs();
    }
  }, [organizationId, organizationLoading]);

  function updateForm(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function resetForm() {
    setForm({ ...emptyForm });
    setEditingJobId(null);
    setShowForm(false);
  }

  function openCreateForm() {
    setForm({ ...emptyForm });
    setEditingJobId(null);
    setMessage("");
    setShowForm(true);
  }

  function openEditForm(job) {
    setEditingJobId(job.id);
    setMessage("");

    setForm({
      title: job.title || "",
      description: job.description || "",
      employment_type: job.employment_type || "",
      location: job.location || "",
      country: job.country || "",
      status: job.status || "draft",
      number_of_positions:
        job.number_of_positions != null
          ? String(job.number_of_positions)
          : "",
      published_at: toDateTimeLocal(job.published_at),
      closing_at: toDateTimeLocal(job.closing_at),
      department: job.department || "",
      job_category: job.job_category || "",
      workplace_type: job.workplace_type || "",
      experience: job.experience || "",
      education: job.education || "",
      skills: job.skills || "",
      salary_compensation: job.salary_compensation || "",
      application_instructions: job.application_instructions || "",
      responsibilities: job.responsibilities || "",
      requirements: job.requirements || "",
    });

    setShowForm(true);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  function buildPayload(statusOverride = null) {
    return {
      organization_id: organizationId,
      title: form.title,
      description: form.description,
      employment_type: form.employment_type,
      location: form.location,
      country: form.country,
      status: statusOverride || form.status || "draft",
      number_of_positions: form.number_of_positions
        ? Number(form.number_of_positions)
        : null,
      published_at: form.published_at || null,
      closing_at: form.closing_at || null,
      department: form.department,
      job_category: form.job_category,
      workplace_type: form.workplace_type,
      experience: form.experience,
      education: form.education,
      skills: form.skills,
      salary_compensation: form.salary_compensation,
      application_instructions: form.application_instructions,
      responsibilities: form.responsibilities,
      requirements: form.requirements,
    };
  }

  async function saveJob(event) {
    event.preventDefault();

    if (!organizationId) {
      setMessage("No active organization is available.");
      return;
    }

    setSaving(true);
    setMessage("");

    try {
      const isEditing = Boolean(editingJobId);

      const response = await fetch(
        isEditing
          ? `${API_BASE}/api/jobs/${encodeURIComponent(editingJobId)}`
          : `${API_BASE}/api/jobs`,
        {
          method: isEditing ? "PUT" : "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(buildPayload()),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            (isEditing ? "Unable to update job" : "Unable to create job")
        );
      }

      resetForm();
      await loadJobs();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  async function publishJob(job) {
    if (!organizationId) {
      setMessage("No active organization is available.");
      return;
    }

    const confirmed = window.confirm(
      `Publish "${job.title}"?\n\nThis will make the job available through the candidate jobs endpoint.`
    );

    if (!confirmed) return;

    setSaving(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE}/api/jobs/${encodeURIComponent(job.id)}`,
        {
          method: "PUT",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            organization_id: organizationId,
            title: job.title,
            description: job.description || "",
            employment_type: job.employment_type || "",
            location: job.location || "",
            country: job.country || "",
            status: "open",
            number_of_positions: job.number_of_positions ?? null,
            published_at: new Date().toISOString(),
            closing_at: job.closing_at || null,
            department: job.department || "",
            job_category: job.job_category || "",
            workplace_type: job.workplace_type || "",
            experience: job.experience || "",
            education: job.education || "",
            skills: job.skills || "",
            salary_compensation: job.salary_compensation || "",
            application_instructions: job.application_instructions || "",
            responsibilities: job.responsibilities || "",
            requirements: job.requirements || "",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to publish job");
      }

      setMessage(`"${job.title}" has been published.`);
      await loadJobs();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  async function unpublishJob(job) {
    if (!organizationId) {
      setMessage("No active organization is available.");
      return;
    }

    const confirmed = window.confirm(
      `Unpublish "${job.title}"?\n\nThe job will no longer appear in the candidate jobs endpoint.`
    );

    if (!confirmed) return;

    setSaving(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE}/api/jobs/${encodeURIComponent(job.id)}`,
        {
          method: "PUT",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            organization_id: organizationId,
            title: job.title,
            description: job.description || "",
            employment_type: job.employment_type || "",
            location: job.location || "",
            country: job.country || "",
            status: "draft",
            number_of_positions: job.number_of_positions ?? null,
            published_at: null,
            closing_at: job.closing_at || null,
            department: job.department || "",
            job_category: job.job_category || "",
            workplace_type: job.workplace_type || "",
            experience: job.experience || "",
            education: job.education || "",
            skills: job.skills || "",
            salary_compensation: job.salary_compensation || "",
            application_instructions: job.application_instructions || "",
            responsibilities: job.responsibilities || "",
            requirements: job.requirements || "",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to unpublish job");
      }

      setMessage(`"${job.title}" has been moved back to draft.`);
      await loadJobs();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <h1>Jobs</h1>
          <p>Manage recruitment job openings and workforce requirements.</p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={openCreateForm}
          disabled={organizationLoading || !organizationId || saving}
        >
          + Create Job
        </button>
      </div>

      {showForm && (
        <div className="job-opening-form">
          <div className="page-header">
            <div>
              <h1>{editingJobId ? "EDIT JOB OPENING" : "CREATE JOB OPENING"}</h1>
              <p>
                {editingJobId
                  ? "Update the job opening details before reviewing or publishing."
                  : "Create and publish a new job opening to attract qualified candidates."}
              </p>
            </div>
          </div>

          <form onSubmit={saveJob}>
            <div className="job-opening-grid">
              <section className="job-form-card">
                <div className="job-form-card-header">
                  <h2>Job Information</h2>
                  <p>Define the role and where it fits within your organization.</p>
                </div>

                <div className="job-form-fields">
                  <div className="job-form-field full-width">
                    <label>
                      Job Title <span className="required">*</span>
                    </label>
                    <input
                      required
                      value={form.title}
                      onChange={(event) =>
                        updateForm("title", event.target.value)
                      }
                      placeholder="e.g. Senior Recruitment Consultant"
                    />
                  </div>

                  <div className="job-form-field">
                    <label>Department</label>
                    <input
                      value={form.department}
                      onChange={(event) =>
                        updateForm("department", event.target.value)
                      }
                      placeholder="e.g. Recruitment"
                    />
                  </div>

                  <div className="job-form-field">
                    <label>Job Category</label>
                    <input
                      value={form.job_category}
                      onChange={(event) =>
                        updateForm("job_category", event.target.value)
                      }
                      placeholder="e.g. Recruitment & HR"
                    />
                  </div>
                </div>
              </section>

              <section className="job-form-card">
                <div className="job-form-card-header">
                  <h2>Workplace &amp; Vacancy</h2>
                  <p>Set the employment arrangement and available positions.</p>
                </div>

                <div className="job-form-fields">
                  <div className="job-form-field">
                    <label>
                      Employment Type <span className="required">*</span>
                    </label>
                    <select
                      required
                      value={form.employment_type}
                      onChange={(event) =>
                        updateForm("employment_type", event.target.value)
                      }
                    >
                      <option value="">Select employment type</option>
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                      <option value="Temporary">Temporary</option>
                      <option value="Internship">Internship</option>
                    </select>
                  </div>

                  <div className="job-form-field">
                    <label>
                      Work Arrangement <span className="required">*</span>
                    </label>
                    <select
                      required
                      value={form.workplace_type}
                      onChange={(event) =>
                        updateForm("workplace_type", event.target.value)
                      }
                    >
                      <option value="">Select arrangement</option>
                      <option value="On-site">On-site</option>
                      <option value="Hybrid">Hybrid</option>
                      <option value="Remote">Remote</option>
                    </select>
                  </div>

                  <div className="job-form-field">
                    <label>Location</label>
                    <input
                      value={form.location}
                      onChange={(event) =>
                        updateForm("location", event.target.value)
                      }
                      placeholder="e.g. Dhaka"
                    />
                  </div>

                  <div className="job-form-field">
                    <label>
                      Number of Vacancies <span className="required">*</span>
                    </label>
                    <input
                      type="number"
                      min="1"
                      required
                      value={form.number_of_positions}
                      onChange={(event) =>
                        updateForm("number_of_positions", event.target.value)
                      }
                      placeholder="1"
                    />
                  </div>
                </div>
              </section>

              <section className="job-form-card">
                <div className="job-form-card-header">
                  <h2>Candidate Requirements</h2>
                  <p>Describe the experience, education and skills expected.</p>
                </div>

                <div className="job-form-fields">
                  <div className="job-form-field">
                    <label>Experience</label>
                    <input
                      value={form.experience}
                      onChange={(event) =>
                        updateForm("experience", event.target.value)
                      }
                      placeholder="e.g. 3–5 years"
                    />
                  </div>

                  <div className="job-form-field">
                    <label>Education</label>
                    <input
                      value={form.education}
                      onChange={(event) =>
                        updateForm("education", event.target.value)
                      }
                      placeholder="e.g. Bachelor's degree"
                    />
                  </div>

                  <div className="job-form-field full-width">
                    <label>Skills</label>
                    <textarea
                      rows="4"
                      value={form.skills}
                      onChange={(event) =>
                        updateForm("skills", event.target.value)
                      }
                      placeholder="List the key skills, qualifications or certifications."
                    />
                  </div>
                </div>
              </section>

              <section className="job-form-card">
                <div className="job-form-card-header">
                  <h2>Compensation &amp; Application</h2>
                  <p>Provide compensation information and application guidance.</p>
                </div>

                <div className="job-form-fields">
                  <div className="job-form-field full-width">
                    <label>Salary / Compensation</label>
                    <input
                      value={form.salary_compensation}
                      onChange={(event) =>
                        updateForm("salary_compensation", event.target.value)
                      }
                      placeholder="e.g. BDT 50,000–70,000 per month"
                    />
                  </div>

                  <div className="job-form-field">
                    <label>
                      Application Deadline <span className="required">*</span>
                    </label>
                    <input
                      type="datetime-local"
                      required
                      value={form.closing_at}
                      onChange={(event) =>
                        updateForm("closing_at", event.target.value)
                      }
                    />
                  </div>

                  <div className="job-form-field">
                    <label>Application Instructions</label>
                    <textarea
                      rows="4"
                      value={form.application_instructions}
                      onChange={(event) =>
                        updateForm(
                          "application_instructions",
                          event.target.value
                        )
                      }
                      placeholder="Tell candidates how to apply."
                    />
                  </div>
                </div>
              </section>

              <section className="job-form-card full-width">
                <div className="job-form-card-header">
                  <h2>Job Description</h2>
                  <p>
                    Give candidates a clear understanding of the role,
                    responsibilities and requirements.
                  </p>
                </div>

                <div className="job-form-fields">
                  <div className="job-form-field full-width">
                    <label>
                      Description <span className="required">*</span>
                    </label>
                    <textarea
                      rows="6"
                      required
                      value={form.description}
                      onChange={(event) =>
                        updateForm("description", event.target.value)
                      }
                      placeholder="Provide an overview of the position and its purpose."
                    />
                  </div>

                  <div className="job-form-field">
                    <label>
                      Responsibilities <span className="required">*</span>
                    </label>
                    <textarea
                      rows="7"
                      required
                      value={form.responsibilities}
                      onChange={(event) =>
                        updateForm("responsibilities", event.target.value)
                      }
                      placeholder="List the main responsibilities of the role."
                    />
                  </div>

                  <div className="job-form-field">
                    <label>
                      Requirements <span className="required">*</span>
                    </label>
                    <textarea
                      rows="7"
                      required
                      value={form.requirements}
                      onChange={(event) =>
                        updateForm("requirements", event.target.value)
                      }
                      placeholder="List the essential candidate requirements."
                    />
                  </div>
                </div>
              </section>
            </div>

            <div className="job-form-status">
              <div className="job-form-status-label">
                <span className="job-form-status-dot"></span>
                Draft
              </div>
              <span className="job-form-help">
                New job openings are saved as Draft and can be published after review.
              </span>
            </div>

            <div className="job-form-actions">
              <button
                type="button"
                className="job-form-secondary"
                onClick={resetForm}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="job-form-secondary"
                disabled={saving}
              >
                {saving
                  ? editingJobId
                    ? "Saving..."
                    : "Saving..."
                  : "Save as Draft"}
              </button>

              <button
                type="submit"
                className="job-form-primary"
                disabled={saving}
              >
                {saving
                  ? editingJobId
                    ? "Saving..."
                    : "Saving..."
                  : editingJobId
                    ? "Save Changes"
                    : "Create Job Opening"}
              </button>
            </div>
          </form>
        </div>
      )}


      <div className="card">
        <div className="card-header">
          <h2>Job Openings</h2>
          <span>{jobs.length} jobs</span>
        </div>

        {organizationLoading ? (
          <div className="empty-state">
            <p>Loading organization access...</p>
          </div>
        ) : !organizationId ? (
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
        ) : message && jobs.length === 0 ? (
          <div className="empty-state">
            <h3>Unable to load jobs</h3>
            <p>{message}</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="empty-state">
            <h3>No jobs yet</h3>
            <p>
              Create your first recruitment job opening to begin building the
              candidate pipeline.
            </p>
          </div>
        ) : (
          <>
            {message && (
              <div className="empty-state">
                <p>{message}</p>
              </div>
            )}

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
                    <span
                      className={`job-status job-status-${job.status}`}
                    >
                      {job.status}
                    </span>

                    {job.employment_type && (
                      <span>{job.employment_type}</span>
                    )}

                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => openEditForm(job)}
                      disabled={saving}
                    >
                      Edit
                    </button>

                    {job.status === "open" ? (
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() => unpublishJob(job)}
                        disabled={saving}
                      >
                        Unpublish
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="primary-button"
                        onClick={() => publishJob(job)}
                        disabled={saving}
                      >
                        Publish
                      </button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  );
}
