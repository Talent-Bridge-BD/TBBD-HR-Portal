import { useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import MyProfile from './pages/MyProfile'
import Leave from './pages/Leave'
import Attendance from './pages/Attendance'
import Applications from './pages/Applications'
import Schedule from './pages/Schedule'

export default function App() {
  const [activePage, setActivePage] = useState('Dashboard')

  const pages = {
    Dashboard: <Dashboard onNavigate={setActivePage} />,
    'My Profile': <MyProfile />,
    Leave: <Leave />,
    Attendance: <Attendance />,
    Applications: <Applications />,
    Schedule: <Schedule />
  }

  return (
    <div className="app-shell">
      <Header />
      <div className="app-body">
        <Sidebar activePage={activePage} onNavigate={setActivePage} />
        <main className="main-content">
          {pages[activePage]}
        </main>
      </div>
    </div>
  )
}
