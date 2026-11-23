import { useEffect, useState } from "react";
import { authenticatedFetch } from "../utils/auth";
import "./AdministratorOrganizations.css";

export default function AdministratorOrganizations() {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOrganizations() {
      try {
        const response = await authenticatedFetch(
          "/api/administrator/organizations"
        );

        const data = await response.json();
        setOrganizations(data);
      } catch (error) {
        console.error("Failed to load organizations", error);
      } finally {
        setLoading(false);
      }
    }

    loadOrganizations();
  }, []);

  if (loading) {
    return (
      <div className="administrator-page">
        Loading organizations...
      </div>
    );
  }

  return (
    <div className="administrator-page">

      <div className="administrator-header">
        <h1>Organization Management</h1>
        <p>
          Manage organizations, memberships, and access control.
        </p>
      </div>

      <div className="organization-table-card">

        <table>
          <thead>
            <tr>
              <th>Organization</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>

          {organizations.map((organization) => (
            <tr key={organization.id}>
              <td>{organization.name}</td>

              <td>
                <span className="status">
                  {organization.status}
                </span>
              </td>

              <td>
                <button>
                  Manage
                </button>
              </td>

            </tr>
          ))}

          </tbody>
        </table>

      </div>

    </div>
  );
}
