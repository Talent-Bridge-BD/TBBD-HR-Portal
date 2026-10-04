import React from "react";
import "./OrganizationManagement.css";

export default function OrganizationManagement() {
  const organizations = [
    {
      name: "Talent Bridge BD",
      status: "Active",
      members: "—",
      created: "—",
    },
  ];

  return (
    <div className="organization-management-page">

      <div className="organization-header">
        <h1>Organization Management</h1>
        <p>
          Manage organizations, tenant structure, and organization status.
        </p>
      </div>

      <div className="organization-card-grid">

        {organizations.map((organization) => (

          <div
            key={organization.name}
            className="organization-card"
          >

            <h2>
              {organization.name}
            </h2>

            <div className="organization-details">

              <div>
                <span>Status</span>
                <strong>{organization.status}</strong>
              </div>

              <div>
                <span>Members</span>
                <strong>{organization.members}</strong>
              </div>

              <div>
                <span>Created</span>
                <strong>{organization.created}</strong>
              </div>

            </div>

            <button>
              View Details →
            </button>

          </div>

        ))}

      </div>

    </div>
  );
}
