import { useEffect, useState } from 'react'

import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import MyProfile from './pages/MyProfile'
import Leave from './pages/Leave'
import Attendance from './pages/Attendance'
import Applications from './pages/Applications'
import Schedule from './pages/Schedule'
import WorkplaceAssistantPage from './pages/WorkplaceAssistantPage'
import { getAuthenticatedEmployee } from './utils/employee'

export default function App() {
  const [activePage, setActivePage] = useState('Dashboard')
  const [employee, setEmployee] = useState({
    displayName: 'Employee',
    initials: 'E',
    email: '',
    authenticated: false,
  })

  useEffect(() => {
    let mounted = true

    getAuthenticatedEmployee().then((user) => {
      if (mounted) {
        setEmployee(user)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  const pages = {
    Dashboard: (
      <Dashboard
        onNavigate={setActivePage}
        employee={employee}
      />
    ),
    'My Profile': <MyProfile employee={employee} />,
    Leave: <Leave />,
    Attendance: <Attendance />,
    Applications: <Applications />,
    Schedule: <Schedule />,
    'Workplace Assistant': <WorkplaceAssistantPage />,
  }

  return (
    <div className="app-shell">
      <Header employee={employee} />

      <div className="app-body">
        <Sidebar
          activePage={activePage}
          onNavigate={setActivePage}
        />

        <main className="main-content">
          {pages[activePage]}
        </main>
      </div>
    </div>
  )
}
