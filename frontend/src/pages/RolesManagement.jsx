import "./RolesManagement.css";

export default function RolesManagement() {

  const roles = [
    {
      name: "Administrator",
      permissions: [
        "Manage organizations",
        "Manage users",
        "Manage roles",
        "System configuration",
      ],
    },
    {
      name: "HR Manager",
      permissions: [
        "Manage candidates",
        "Recruitment workflow",
        "Hiring operations",
      ],
    },
    {
      name: "Employer Manager",
      permissions: [
        "Manage job requests",
        "Manage openings",
        "View candidates",
      ],
    },
    {
      name: "Candidate",
      permissions: [
        "Apply jobs",
        "Manage profile",
        "Track applications",
      ],
    },
  ];


  return (
    <div className="roles-management-page">

      <div className="roles-header">
        <h1>
          Roles & Permissions
        </h1>

        <p>
          Manage application roles and access permissions.
        </p>
      </div>


      <div className="roles-grid">

        {roles.map((role) => (

          <div
            className="role-card"
            key={role.name}
          >

            <h2>
              {role.name}
            </h2>

            <ul>
              {role.permissions.map((permission) => (
                <li key={permission}>
                  {permission}
                </li>
              ))}
            </ul>

          </div>

        ))}

      </div>

    </div>
  );
}
