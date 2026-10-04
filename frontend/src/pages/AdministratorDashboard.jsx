import React from "react";
import "./AdministratorDashboard.css";

export default function AdministratorDashboard({ onNavigate }) {

  const adminModules = [
    {
      title: "Organization Management",
      description: "Manage organizations and tenant structure.",
      metrics: [
        ["Organizations", "0"],
        ["Active Organizations", "0"],
      ],
      action: "organizations",
      button: "Manage Organizations →",
    },
    {
      title: "User Management",
      description: "Manage users, access, and memberships.",
      metrics: [
        ["Total Users", "0"],
        ["Active Users", "0"],
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
        ["Recent Actions", "0"],
        ["Failed Events", "0"],
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