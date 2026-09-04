export function getEmployeeDisplayName() {
  return import.meta.env.VITE_EMPLOYEE_NAME || 'Employee'
}
