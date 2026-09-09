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
      status: statusOverride || form.status,
      number_of_positions: form.number_of_positions
        ? Number(form.number_of_positions)
        : null,
      published_at: form.published_at || null,
      closing_at: form.closing_at || null,
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
            status: "published",
            number_of_positions: job.number_of_positions ?? null,
            published_at: new Date().toISOString(),
            closing_at: job.closing_at || null,
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
        <div className="card">
          <div className="card-header">
            <h2>{editingJobId ? "Edit Job" : "Create Job"}</h2>
          </div>

          <form onSubmit={saveJob}>
            <div className="form-grid">
              <label>
                Job Title
                <input
                  required
                  value={form.title}
                  onChange={(event) =>
                    updateForm("title", event.target.value)
                  }
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
                Location
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
                  onChange={(event) =>
                    updateForm("status", event.target.value)
                  }
                >
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="open">Open</option>
                  <option value="paused">Paused</option>
                </select>
              </label>

              <label>
                Number of Positions
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
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={resetForm}
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

                    {job.status === "published" ? (
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
