import React, { useEffect, useState } from "react";
import { authenticatedFetch } from "../utils/auth";
import "./SystemActivity.css";

function formatActivityDetails(details, action, status) {
  if (details === null || details === undefined || details === "") {
    return `${action || "Activity"} — ${status || "Recorded"}`;
  }

  if (typeof details === "string") {
    try {
      return JSON.stringify(JSON.parse(details), null, 2);
    } catch {
      return details;
    }
  }

  try {
    return JSON.stringify(details, null, 2);
  } catch {
    return String(details);
  }
}

export default function SystemActivity() {
  const [activities, setActivities] = useState([]);
  const [failedEvents, setFailedEvents] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadActivity() {
      try {
        const response = await authenticatedFetch(
          "/api/administrator/activity"
        );

        if (response.ok) {
          const data = await response.json();

          setActivities(data.activities || []);
          setFailedEvents(data.failedEvents || 0);
        } else {
          setError("Unable to load system activity.");
        }
      } catch (err) {
        setError("Unable to load system activity.");
      } finally {
        setLoading(false);
      }
    }

    loadActivity();
  }, []);

  return (
    <section className="system-activity-page">

      <div className="page-header">
        <h1>System Activity</h1>
        <p>
          Monitor audit logs and platform events.
        </p>
      </div>

      <div className="activity-card">

        {loading && (
          <div className="activity-row">
            <p>Loading system activity...</p>
          </div>
        )}

        {!loading && error && (
          <div className="activity-row">
            <h3>Unable to load activity</h3>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && activities.length === 0 && (
          <div className="activity-row">
            <h3>No activity recorded</h3>
            <p>
              System audit events will appear here as activity occurs.
            </p>
          </div>
        )}

        {!loading &&
          !error &&
          activities.map((activity) => (
            <div className="activity-row" key={activity.id}>
              <h3>
                {activity.event_type || activity.action}
              </h3>

              <pre className="activity-details">
                {formatActivityDetails(
                  activity.details,
                  activity.action,
                  activity.status
                )}
              </pre>
            </div>
          ))}

        {!loading && !error && (
          <div className="activity-row">
            <h3>Failed Events</h3>
            <p>
              {failedEvents} failed audit events recorded.
            </p>
          </div>
        )}

      </div>

    </section>
  );
}
