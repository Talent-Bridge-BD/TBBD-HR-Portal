import { useOrganization } from '../context/OrganizationContext'

export default function OrganizationSelector() {
  const {
    availableOrganizations,
    selectedOrganizationId,
    organizationLoading,
    requiresOrganizationSelection,
    setSelectedOrganizationId,
  } = useOrganization()

  if (organizationLoading || availableOrganizations.length === 0) {
    return null
  }

  return (
    <div className="organization-selector">
      <label htmlFor="organization-context">
        Operating organization
      </label>

      <select
        id="organization-context"
        value={selectedOrganizationId}
        onChange={(event) =>
          setSelectedOrganizationId(event.target.value)
        }
        aria-required={requiresOrganizationSelection}
      >
        {requiresOrganizationSelection && (
          <option value="">Select an organization</option>
        )}

        {availableOrganizations.map((organization) => (
          <option key={organization.id} value={organization.id}>
            {organization.name}
          </option>
        ))}
      </select>
    </div>
  )
}
