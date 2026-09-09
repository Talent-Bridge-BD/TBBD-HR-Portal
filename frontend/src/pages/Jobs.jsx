import { useEffect, useState } from "react";

const API_BASE = "";

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [organizationId, setOrganizationId] = useState("");
  const [organizationLoading, setOrganizationLoading] = useState(true);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
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
  });

  async function loadJobs() {
    if (!organizationId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE}/api/jobs?organization_id=${encodeURIComponent(organizationId)}`,
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

  async function createJob(event) {
    event.preventDefault();

    if (!organizationId) {
      setMessage("No active organization is available.");
      return;
    }

    setSaving(true);
    setMessage("");

    try {
      const response = await fetch(`${API_BASE}/api/jobs`, {
        method: "POST",
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
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to create job");
      }

      setShowCreateForm(false);
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
      });

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
          onClick={() => setShowCreateForm(true)}
          disabled={organizationLoading || !organizationId}
        >
          + Create Job
        </button>
      </div>

      {showCreateForm && (
        <div className="card">
          <div className="card-header">
            <h2>Create Job</h2>
          </div>

          <form onSubmit={createJob}>
            <div className="form-grid">
              <label>
                Job Title
                <input
                  required
                  value={form.title}
                  onChange={(event) => updateForm("title", event.target.value)}
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
                  onChange={(event) => updateForm("status", event.target.value)}
                >
                  <option value="draft">Draft</option>
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
                onClick={() => setShowCreateForm(false)}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="primary-button"
                disabled={saving}
              >
                {saving ? "Creating..." : "Create Job"}
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
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
