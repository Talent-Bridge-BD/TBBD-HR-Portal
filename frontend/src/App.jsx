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
import PlatformPlaceholder from './pages/PlatformPlaceholder'
import EmployerDashboard from './pages/EmployerDashboard'
import EmployerJobRequests from './pages/EmployerJobRequests'
import EmployerJobOpenings from './pages/EmployerJobOpenings'
import EmployerApplications from './pages/EmployerApplications'
import Hiring from './pages/Hiring'
import CandidateDashboard from './pages/CandidateDashboard'
import CandidateMyProfile from './pages/CandidateMyProfile'
import CandidateMyApplications from './pages/CandidateMyApplications'
import CandidateAvailableJobs from './pages/CandidateAvailableJobs'
import Jobs from './pages/Jobs'
import CandidateInterviews from './pages/CandidateInterviews'
import CandidateDocuments from './pages/CandidateDocuments'
import CandidateNotifications from './pages/CandidateNotifications'
import { getCurrentUser } from './utils/auth'

const placeholderPages = {
  'Recruitment Jobs': {
    area: 'RECRUITMENT',
    title: 'Jobs',
    description: 'Manage recruitment job openings and workforce requirements.',
  },
  'Recruitment Candidates': {
    area: 'RECRUITMENT',
    title: 'Candidates',
    description: 'Manage and review candidates across the recruitment pipeline.',
  },
  'Recruitment Applications': {
    area: 'RECRUITMENT',
    title: 'Applications',
    description: 'Review candidate applications and application activity.',
  },
  'Recruitment Screening': {
    area: 'RECRUITMENT',
    title: 'Screening',
    description: 'Support structured candidate screening and evaluation.',
  },
  'Recruitment Interviews': {
    area: 'RECRUITMENT',
    title: 'Interviews',
    description: 'Coordinate interviews and hiring-stage activities.',
  },
  'Recruitment Offers': {
    area: 'RECRUITMENT',
    title: 'Offers',
    description: 'Manage offers and offer-stage recruitment workflows.',
  },
  'Recruitment Onboarding': {
    area: 'RECRUITMENT',
    title: 'Onboarding',
    description: 'Prepare successful candidates for onboarding and deployment.',
  },

  'Employer Job Requests': {
    area: 'EMPLOYER PORTAL',
    title: 'Job Requests',
    description: 'Create and manage employer workforce and recruitment requests.',
  },
  'Employer Job Openings': {
    area: 'EMPLOYER PORTAL',
    title: 'Job Openings',
    description: 'View and manage employer job openings.',
  },
  'Employer Applications': {
    area: 'EMPLOYER PORTAL',
    title: 'Candidate Applications',
    description: 'Review candidates submitted against employer openings.',
  },
  'Employer Hiring': {
    area: 'EMPLOYER PORTAL',
    title: 'Hiring',
    description: 'Manage employer hiring decisions and recruitment progress.',
  },
}

export default function App() {
  const [activePage, setActivePage] = useState('Dashboard')
  const [auth, setAuth] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    getCurrentUser()
      .then((data) => {
        if (mounted) {
          setAuth(data)
        }
      })
      .catch((error) => {
        console.error('Failed to load current user:', error)
      })
      .finally(() => {
        if (mounted) {
          setAuthLoading(false)
        }
      })

    return () => {
      mounted = false
    }
  }, [])

  if (authLoading) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <p>Loading Workplace Hub...</p>
        </main>
      </div>
    )
  }

  const pages = {
    Dashboard: <Dashboard onNavigate={setActivePage} />,
    'My Profile': <MyProfile auth={auth} />,
    Leave: <Leave />,
    Attendance: <Attendance />,
    Applications: <Applications />,
    Schedule: <Schedule />,
    'Workplace Assistant': <WorkplaceAssistantPage />,
    'Employer Dashboard': (
      <EmployerDashboard
        auth={auth}
        onNavigate={setActivePage}
      />
    ),
    'Employer Job Requests': <EmployerJobRequests auth={auth} />,
    'Employer Job Openings': <EmployerJobOpenings auth={auth} />,
    'Candidate Dashboard': <CandidateDashboard onNavigate={setActivePage} />,
    'Candidate My Profile': <CandidateMyProfile />,
    'Candidate My Applications': <CandidateMyApplications />,
    'Recruitment Jobs': <Jobs />,
    'Candidate Available Jobs': <CandidateAvailableJobs />,
  'Candidate Interviews': <CandidateInterviews />,
  'Candidate Documents': <CandidateDocuments />,
  'Candidate Notifications': <CandidateNotifications />,
  }

  Object.entries(placeholderPages).forEach(([page, config]) => {
    pages[page] = <PlatformPlaceholder {...config} />
  })
  pages['Employer Applications'] = (
    <EmployerApplications auth={auth} />
  )

  pages['Employer Hiring'] = (
    <Hiring auth={auth} />
  )

  return (
    <div className="app-shell">
      <Header />

      <div className="app-body">
        <Sidebar
          activePage={activePage}
          onNavigate={setActivePage}
          auth={auth}
        />

        <main className="main-content">
          {pages[activePage] || (
            <PlatformPlaceholder
              area="TBBD PLATFORM"
              title="Page Not Found"
              description="The requested platform area could not be found."
            />
          )}
        </main>
      </div>
    </div>
  )
}
