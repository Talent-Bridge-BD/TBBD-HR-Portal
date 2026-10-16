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
import AdministrationEmployers from './pages/AdministrationEmployers'
import UserManagement from './pages/UserManagement'
import OrganizationManagement from './pages/OrganizationManagement'
import RolesManagement from './pages/RolesManagement'
import SystemConfiguration from './pages/SystemConfiguration'
import SystemActivity from './pages/SystemActivity'
import NotificationSettings from './pages/NotificationSettings'
import AdministratorNotifications from './pages/AdministratorNotifications'
import EmployerAccessRequests from './pages/EmployerAccessRequests'
import CandidateApprovals from './pages/CandidateApprovals'
import EmployerDashboard from './pages/EmployerDashboard'
import EmployerOrganization from './pages/EmployerOrganization'
import EmployerJobRequests from './pages/EmployerJobRequests'
import EmployerJobOpenings from './pages/EmployerJobOpenings'
import EmployerApplications from './pages/EmployerApplications'
import Hiring from './pages/Hiring'
import CandidateDashboard from './pages/CandidateDashboard'
import CandidateMyProfile from './pages/CandidateMyProfile'
import CandidateMyApplications from './pages/CandidateMyApplications'
import CandidateAvailableJobs from './pages/CandidateAvailableJobs'
import Jobs from './pages/Jobs'
import RecruitmentCandidates from './pages/RecruitmentCandidates'
import RecruitmentApplications from './pages/RecruitmentApplications'
import RecruitmentScreening from './pages/RecruitmentScreening'
import RecruitmentInterviews from './pages/RecruitmentInterviews'
import RecruitmentTradeTests from './pages/RecruitmentTradeTests'
import EmployerInterviewsTests from './pages/EmployerInterviewsTests'
import RecruitmentMedical from './pages/RecruitmentMedical'
import RecruitmentVisaProcessing from './pages/RecruitmentVisaProcessing'
import RecruitmentTicketing from './pages/RecruitmentTicketing'
import RecruitmentDeployment from './pages/RecruitmentDeployment'
import RecruitmentOnboarding from './pages/RecruitmentOnboarding'
import CandidateInterviews from './pages/CandidateInterviews'
import CandidateDocuments from './pages/CandidateDocuments'
import CandidateNotifications from './pages/CandidateNotifications'
import CandidateOffers from './pages/CandidateOffers'
import EmployerNotifications from './pages/EmployerNotifications'
import CandidateHelpSupport from './pages/CandidateHelpSupport'
import { getCurrentUser, signIn } from './utils/auth'
import { OrganizationProvider } from './context/OrganizationContext'
import OrganizationSelector from './components/OrganizationSelector'

const placeholderPages = {}

export default function App() {
  const [activePage, setActivePage] = useState('Dashboard')
  const [auth, setAuth] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)

  const isCandidateMode =
    new URLSearchParams(window.location.search).get('authMode') === 'candidate'

  useEffect(() => {
    let mounted = true

    getCurrentUser()
      .then((data) => {
        if (!mounted) return

        setAuth(data)

        const roles = data?.roles || []

        if (roles.includes('Candidate')) {
          setActivePage('Candidate Dashboard')
        } else if (
          roles.includes('Employer Manager') ||
          roles.includes('Employer.Manager')
        ) {
          setActivePage('Employer Dashboard')
        } else {
          setActivePage('Dashboard')
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

  if (!auth?.authenticated) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <div className="empty-state">
            <strong>Welcome to Talent Bridge BD</strong>


{isCandidateMode ? (
              <>
                <p>
                  Sign in to your candidate account, or register if you are new.
                </p>

                <p>
                  <strong>Are you applying for a job?</strong>
                </p>

                <div
                  style={{
                    display: 'flex',
                    width: '100%',
                    overflow: 'hidden',
                    border: '1px solid #0067B8',
                    borderRadius: '6px',
                  }}
                >
                  <button
                    type="button"
                    className="primary-button"
                    style={{
                      flex: 1,
                      minWidth: 0,
                      border: 0,
                      borderRadius: 0,
                      borderRight: '1px solid #FFFFFF',
                    }}
                    onClick={() => {
                      window.location.assign(
                        '/.auth/login/TBBDCandidateExternalID?post_login_redirect_uri=%2F%3FauthMode%3Dcandidate&prompt=login'
                      )
                    }}
                  >
                    Candidate Sign in
                  </button>

                  <button
                    type="button"
                    className="primary-button"
                    style={{
                      flex: 1,
                      minWidth: 0,
                      border: 0,
                      borderRadius: 0,
                    }}
                    onClick={() => {
                      window.location.assign(
                        '/.auth/login/TBBDCandidateExternalID?post_login_redirect_uri=%2F%3FauthMode%3Dcandidate&prompt=create'
                      )
                    }}
                  >
                    No Account? Register
                  </button>
                </div>
              </>
) : (

              <>
                <p>
                  Staff and administrators can continue with Microsoft.
                </p>

                <button
                  type="button"
                  className="primary-button"
                  onClick={() => signIn()}
                >
                  Sign in with Microsoft
                </button>
              </>
            )}
          </div>
        </main>
      </div>
    )
  }

  const pages = {
Dashboard: auth?.roles?.includes('Candidate') ? (
  <CandidateDashboard onNavigate={setActivePage} />
) : (
  <Dashboard auth={auth} onNavigate={setActivePage} />
),
    'My Profile': auth?.roles?.includes('Candidate')
      ? <CandidateMyProfile />
      : <MyProfile auth={auth} />,
    Leave: <Leave />,
    Attendance: <Attendance />,
    Applications: <Applications />,
    Schedule: <Schedule />,
    'Workplace Assistant': <WorkplaceAssistantPage />,
    'Administration Employers': <AdministrationEmployers auth={auth} />,
    organizations: <OrganizationManagement onNavigate={setActivePage} />,

 users: <UserManagement auth={auth} />,

    roles: <RolesManagement />,

    notifications: <AdministratorNotifications />,

    settings: <SystemConfiguration />,

    activity: <SystemActivity />,
    'employer-access-requests': <EmployerAccessRequests auth={auth} />,
    'candidate-approvals': <CandidateApprovals />,

    'Employer Dashboard': <EmployerDashboard onNavigate={setActivePage} />,
    'Employer My Organization': <EmployerOrganization />,
    'Employer Job Requests': <EmployerJobRequests auth={auth} />,
    'Employer Job Openings': <EmployerJobOpenings auth={auth} />,
    'Employer Applications': <EmployerApplications auth={auth} />,
    'Employer Candidates': <RecruitmentCandidates auth={auth} />,
    'Employer Interviews / Tests': <EmployerInterviewsTests auth={auth} />,
    'Employer Hiring': <Hiring auth={auth} />,
    'Employer Notifications': <EmployerNotifications />,

    'Candidate Dashboard': <CandidateDashboard onNavigate={setActivePage} />,
    'Candidate My Profile': <CandidateMyProfile />,
    'Candidate My Applications': <CandidateMyApplications />,
    'Recruitment Jobs': <Jobs auth={auth} />,
  'Recruitment Candidates': <RecruitmentCandidates auth={auth} />,
    'Recruitment Applications': <RecruitmentApplications auth={auth} />,
    'Recruitment Screening': <RecruitmentScreening auth={auth} />,
    'Recruitment Interviews': <RecruitmentInterviews auth={auth} />,
    'Recruitment Trade Tests': <RecruitmentTradeTests auth={auth} />,
    'Recruitment Medical': <RecruitmentMedical auth={auth} />,
    'Recruitment Visa Processing': <RecruitmentVisaProcessing auth={auth} />,
    'Recruitment Ticketing': <RecruitmentTicketing auth={auth} />,
    'Recruitment Deployment': <RecruitmentDeployment auth={auth} />,
    'Recruitment Onboarding': <RecruitmentOnboarding auth={auth} />,
    'Candidate Available Jobs': <CandidateAvailableJobs />,
  'Candidate Interviews': <CandidateInterviews />,
  'Candidate Documents': <CandidateDocuments />,
  'Candidate My Offers': <CandidateOffers />,
  'Candidate Notifications': <CandidateNotifications />,
  }

  Object.entries(placeholderPages).forEach(([page, config]) => {
    pages[page] = <PlatformPlaceholder {...config} />
  })

  return (
    <OrganizationProvider auth={auth}>
      <div className="app-shell">
        <Header auth={auth} />

        <div className="app-body">
          <Sidebar
            activePage={activePage}
            onNavigate={setActivePage}
            auth={auth}
          />

          <main className="main-content">
            <OrganizationSelector />
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
    </OrganizationProvider>
  )
}

