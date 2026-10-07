import React, { useEffect, useState } from "react";
import { authenticatedFetch } from "../utils/auth";
import "./AdministratorDashboard.css";

export default function AdministratorDashboard({ onNavigate }) {
 const [dashboard, setDashboard] = useState(null);
const [organizationStats, setOrganizationStats] = useState({
  total: 0,
  active: 0,
});

const [activityStats, setActivityStats] = useState({
  total: 0,
  failed: 0,
});

useEffect(() => {
  async function loadDashboard() {
    const response = await authenticatedFetch(
      "/api/administrator/dashboard"
    );

    if (response.ok) {
      const data = await response.json();
      setDashboard(data);
    }
  }

  async function loadOrganizations() {
    const response = await authenticatedFetch(
      "/api/organizations"
    );

    if (response.ok) {
      const data = await response.json();

      const organizations = data.organizations || [];

      setOrganizationStats({
        total: organizations.length,
        active: organizations.filter(
          (organization) =>
            organization.status === "active"
        ).length,
      });
    }
  }

  async function loadActivity() {
    const response = await authenticatedFetch(
      "/api/administrator/activity"
    );

    if (response.ok) {
      const data = await response.json();

      setActivityStats({
        total: (data.activities || []).length,
        failed: data.failedEvents || 0,
      });
    }
  }

  loadDashboard();
  loadOrganizations();
  loadActivity();
}, []);
  const adminModules = [
    {
      title: "Organization Management",
      description: "Manage organizations and tenant structure.",
metrics: [
  ["Organizations", organizationStats.total],
  [
    "Active Organizations",
    organizationStats.active,
  ],
],
      action: "organizations",
      button: "Manage Organizations →",
    },
    {
      title: "User Management",
      description: "Manage users, access, and memberships.",
      metrics: [
        ["Total Users", dashboard?.users?.total ?? 0],
        ["Active Users", dashboard?.users?.active ?? 0],
      ],
      action: "users",
      button: "Manage Users →",
    },
    {
      title: "Roles & Permissions",
      description: "Control roles and access permissions.",
      metrics: [
        ["Roles", "4"],
        ["Permission Sets", "0"],
      ],
      action: "roles",
      button: "Manage Access →",
    },
    {
      title: "Notification System",
      description: "Configure email and notification delivery.",
      metrics: [
        ["Templates", "0"],
        ["Delivery Status", "0"],
      ],
      action: "notifications",
      button: "Configure →",
    },
    {
      title: "System Configuration",
      description: "Manage portal settings and integrations.",
      metrics: [
        ["Settings", "—"],
        ["Integrations", "—"],
      ],
      action: "settings",
      button: "Manage Settings →",
    },
    {
      title: "System Activity",
      description: "Monitor system events and audit history.",
      metrics: [
        ["Recent Actions", activityStats.total],
        ["Failed Events", activityStats.failed],
      ],
      action: "activity",
      button: "View Audit Logs →",
    },
  ];


  return (
    <div className="administrator-dashboard">

      <div className="administrator-header">

        <h1>
          Administration Dashboard
        </h1>

        <p>
          Manage organizations, users, access, notifications, and system configuration.
        </p>

      </div>


      <div className="administrator-card-grid">

        {adminModules.map((module) => (

          <div
            key={module.title}
            className="administrator-card"
          >

            <h2>
              {module.title}
            </h2>

            <p>
              {module.description}
            </p>


            <div className="administrator-metrics">

              {module.metrics.map(([label, value]) => (

                <div
                  key={label}
                  className="administrator-metric"
                >

                  <span>
                    {label}
                  </span>

                  <strong>
                    {value}
                  </strong>

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
