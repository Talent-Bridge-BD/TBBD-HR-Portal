import { useEffect, useState } from 'react'
import "./OrganizationManagement.css";

import { authenticatedFetch } from '../utils/auth'


export default function OrganizationManagement({ onNavigate }) {

  const [organizations, setOrganizations] = useState([])
  const [memberCounts, setMemberCounts] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')


  async function loadOrganizations() {

    setLoading(true)
    setError('')

    try {

      const response = await authenticatedFetch('/api/organizations')

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load organizations.'
        )
      }

      const loadedOrganizations = data.organizations || []

      setOrganizations(loadedOrganizations)


      const counts = {}

      await Promise.all(
        loadedOrganizations.map(async (organization) => {

          try {

            const memberResponse = await authenticatedFetch(
              `/api/organizations/${encodeURIComponent(organization.id)}/members`
            )

            const memberData = await memberResponse.json()

            counts[organization.id] =
              memberData.members?.length || 0

          } catch {

            counts[organization.id] = 0

          }

        })
      )


      setMemberCounts(counts)


    } catch (err) {

      console.error(err)

      setError(
        err.message || 'Unable to load organizations.'
      )

    } finally {

      setLoading(false)

    }
  }


  useEffect(() => {

    loadOrganizations()

  }, [])



  return (

    <div className="organization-management-page">

      <div className="organization-header">

        <h1>
          Organization Management
        </h1>

        <p>
          Manage organizations, tenant structure, and organization status.
        </p>

      </div>


      {loading && (

        <div className="organization-card">
          Loading organizations...
        </div>

      )}


      {error && (

        <div className="organization-card">
          {error}
        </div>

      )}



      <div className="organization-card-grid">

        {organizations.map((organization) => (

          <div
            key={organization.id}
            className="organization-card"
          >

            <h2>
              {organization.name}
            </h2>


            <div className="organization-details">


              <div>

                <span>
                  Status
                </span>

                <strong>
                  {organization.status || 'Active'}
                </strong>

              </div>


              <div>

                <span>
                  Members
                </span>

                <strong>
                  {memberCounts[organization.id] ?? '...'}
                </strong>

              </div>


              <div>

                <span>
                  Organization ID
                </span>

                <strong>
                  {organization.id}
                </strong>

              </div>


            </div>



            <button
              onClick={() =>
                onNavigate?.('Administration Employers')
              }
            >
              View Details →
            </button>


          </div>

        ))}

      </div>


    </div>

  )
}
