import { useEffect, useMemo, useState } from "react";

import { authenticatedFetch } from "../utils/auth";

import "./UserManagement.css";

export default function UserManagement({ auth }) {
  const [organizations, setOrganizations] = useState([]);
  const [users, setUsers] = useState([]);
  const [roleFilter, setRoleFilter] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadUsers() {
    setLoading(true);
    setError("");

    try {
      const orgResponse = await authenticatedFetch(
        "/api/administrator/organizations"
      );

      const orgData = await orgResponse.json();

      if (!orgResponse.ok) {
        throw new Error(
          orgData.detail || "Unable to load organizations."
        );
      }

      const organizationList =
        orgData.organizations || [];

      setOrganizations(organizationList);

      const allUsers = [];

      await Promise.all(
        organizationList.map(async (organization) => {
          const response = await authenticatedFetch(
            `/api/organizations/${encodeURIComponent(
              organization.id
            )}/members`
          );

          const data = await response.json();

          if (response.ok) {
            (data.members || []).forEach((member) => {
              allUsers.push({
                ...member,
                organization: organization.name,
              });
            });
          }
        })
      );

      setUsers(allUsers);
    } catch (err) {
      console.error(err);

      setError(
        err.message || "Unable to load users."
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    if (auth?.roles?.includes("Administrator")) {
      loadUsers();
    } else {
      setError(
        "Administrator access is required."
      );
      setLoading(false);
    }
  }, [auth]);


  const roles = useMemo(() => {
    return [
      "All",
      ...new Set(
        users.map((user) => user.role)
      ),
    ];
  }, [users]);


  const filteredUsers =
    roleFilter === "All"
      ? users
      : users.filter(
          (user) =>
            user.role === roleFilter
        );


  return (
    <section className="page-section user-management-page">

      <div className="page-header">
        <div>
          <h1>
            User Management
          </h1>

          <p>
            Manage users, organization access,
            roles, and memberships.
          </p>
        </div>
      </div>


      {loading && (
        <div className="card">
          Loading users...
        </div>
      )}


      {error && (
        <div className="card">
          {error}
        </div>
      )}


      {!loading && !error && (
        <section className="card">

          <div className="card-header">

            <div>
              <h2>
                Users
              </h2>

              <p>
                {filteredUsers.length} users across{" "}
                {organizations.length}
                {" "}organizations
              </p>
            </div>


            <div>
              <select
                value={roleFilter}
                onChange={(event) =>
                  setRoleFilter(
                    event.target.value
                  )
                }
              >
                {roles.map((role) => (
                  <option
                    key={role}
                    value={role}
                  >
                    {role}
                  </option>
                ))}
              </select>
            </div>

          </div>


          <div className="onboarding-table-wrap">

            <table className="onboarding-table">

              <thead>
                <tr>
                  <th>
                    User ID
                  </th>

                  <th>
                    Organization
                  </th>

                  <th>
                    Role
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                    Action
                  </th>
                </tr>
              </thead>


              <tbody>

                {filteredUsers.map((user) => (

                  <tr
                    key={`${user.organization}-${user.user_id}`}
                  >

                    <td>
                      {user.user_id}
                    </td>


                    <td>
                      {user.organization}
                    </td>


                    <td>
                      {user.role}
                    </td>


                    <td>
                      {user.status}
                    </td>


                    <td>
                      <button
                        type="button"
                        disabled
                      >
                        Manage
                      </button>
                    </td>

                  </tr>

                ))}


                {filteredUsers.length === 0 && (

                  <tr>
                    <td colSpan="5">
                      No users found.
                    </td>
                  </tr>

                )}

              </tbody>

            </table>

          </div>

        </section>
      )}

    </section>
  );
}