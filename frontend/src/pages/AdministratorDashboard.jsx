
import React, { useEffect, useState } from "react";
import { authenticatedFetch } from "../utils/auth";
import "./AdministratorDashboard.css";

function displayMetric(value) {
  return value === null || value === undefined ? "—" : value;
}

export default function AdministratorDashboard({ onNavigate }) {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadDashboard() {
      try {
        const response = await authenticatedFetch(
          "/api/administrator/dashboard"
        );

        if (!response.ok) {
          return;
        }

        const data = await response.json();

        if (isMounted) {
          setDashboard(data);
        }
      } catch (error) {
        console.error(
          "Unable to load administrator dashboard:",
          error
        );
      }
    }

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, []);

  const adminModules = [
    {
      title: "Organization Management",
      description: "Manage organizations and tenant structure.",
      metrics: [
        [
          "All Organizations",
          displayMetric(dashboard?.organizations?.total),
        ],
        [
          "Active Organizations",
          displayMetric(dashboard?.organizations?.active),
        ],
      ],
      action: "organizations",
      button: "Manage Organizations →",
    },
    {
      title: "User Management",
      description: "Manage users, access, and memberships.",
      metrics: [
        ["Total Users", displayMetric(dashboard?.users?.total)],
        ["Active Users", displayMetric(dashboard?.users?.active)],
      ],
      action: "users",
      button: "Manage Users →",
    },
    {
      title: "Roles & Permissions",
      description: "Control roles and access permissions.",
      metrics: [
        ["Configured Roles", displayMetric(dashboard?.roles?.total)],
        [
          "Permission Sets",
          displayMetric(dashboard?.roles?.permissionSets),
        ],
      ],
      action: "roles",
      button: "Manage Access →",
    },
    {
      title: "Notification System",
      description: "Configure email and notification delivery.",
      metrics: [
        [
          "Templates",
          displayMetric(dashboard?.notifications?.templates),
        ],
        [
          "Delivery Status",
          displayMetric(dashboard?.notifications?.deliveryStatus),
        ],
      ],
      action: "notifications",
      button: "Configure →",
    },
    {
      title: "System Configuration",
      description: "Manage portal settings and integrations.",
      metrics: [
        ["Settings", displayMetric(dashboard?.system?.settings)],
        ["Integrations", displayMetric(dashboard?.system?.integrations)],
      ],
      action: "settings",
      button: "Manage Settings →",
    },
    {
      title: "System Activity",
      description: "Monitor system events and audit history.",
      metrics: [
        [
          "Recent Actions",
          displayMetric(dashboard?.system?.recentActions),
        ],
        [
          "Failed Events",
          displayMetric(dashboard?.system?.failedEvents),
        ],
      ],
      action: "activity",
      button: "View Audit Logs →",
    },
  ];

  return (
    <div className="administrator-dashboard">
      <div className="administrator-header">
        <h1>Administration Dashboard</h1>

        <p>
          Manage organizations, users, access, notifications, and system
          configuration.
        </p>
      </div>

      <div className="administrator-card-grid">
        {adminModules.map((module) => (
          <div
            key={module.title}
            className="administrator-card"
          >
            <h2>{module.title}</h2>

            <p>{module.description}</p>

            <div className="administrator-metrics">
              {module.metrics.map(([label, value]) => (
                <div
                  key={label}
                  className="administrator-metric"
                >
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>

            <button
              onClick={() => onNavigate(module.action)}
            >
              {module.button}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
