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
import EmployerDashboard from './pages/EmployerDashboard'
import EmployerOrganization from './pages/EmployerOrganization'
import EmployerJobRequests from './pages/EmployerJobRequests'
import EmployerJobOpenings from './pages/EmployerJobOpenings'
import EmployerApplications from './pages/EmployerApplications'
import Hiring from './pages/Hiring'
import CandidateDashboard from './pages/CandidateDashboard'
import CandidateMyProfile from './pages/CandidateMyProfile'
import EmployerAccessRequests from './pages/EmployerAccessRequests'
import CandidateApprovals from './pages/CandidateApprovals'
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
  const isCandidateMode = new URLSearchParams(window.location.search).get('authMode') === 'candidate'
  const [activePage, setActivePage] = useState('Dashboard')
  const [workplaceHubOpened, setWorkplaceHubOpened] = useState(false)
  const [auth, setAuth] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [authError, setAuthError] = useState(null)

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
        if (mounted) {
          setAuthError(
            error instanceof Error ? error.message : String(error),
          )
        }
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

  useEffect(() => {
    if (
      !authLoading &&
      isCandidateMode &&
      auth?.authenticated === false &&
      !authError
    ) {
      window.location.replace('/candidate-access.html')
    }
  }, [authLoading, auth, authError, isCandidateMode])
  if (authLoading) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <p>Loading Workplace Hub...</p>
        </main>
      </div>
    )
  }

  if (isCandidateMode && authError) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <div className="empty-state">
            <strong>We couldn't verify your sign-in session.</strong>
            <p>
              Your access has not been changed. Please return to candidate
              sign-in and try again. If the problem continues, contact
              Talent Bridge BD support.
            </p>
            <button
              type="button"
              className="primary-button"
              onClick={() =>
                window.location.replace('/candidate-access.html')
              }
            >
              Return to candidate sign-in
            </button>
          </div>
        </main>
      </div>
    )
  }
  if (!auth?.authenticated) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <div className={`empty-state${isCandidateMode ? "" : " staff-signin-state"}`}>
            <>
              <strong>Sign in required</strong>
              <p>
                Staff and administrators can sign in with their Microsoft work account.
              </p>
              <button
                type="button"
                className="primary-button"
                onClick={() => {
                  signIn().catch((error) => {
                    console.error(
                      'Microsoft Entra sign-in failed:',
                      error,
                    )
                  })
                }}
              >
                Staff and administrator sign in
              </button>

            </>
          </div>
        </main>
      </div>
    )
  }

  if (isCandidateMode && auth?.authenticated && !auth?.roles?.includes('Candidate')) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <div className="empty-state">
            <strong>Candidate access is not assigned to this account.</strong>
            <p>Please contact Talent Bridge BD support if you believe this is an error.</p>
          </div>
        </main>
      </div>
    )
  }
  if (!isCandidateMode && !auth?.roles?.includes('Candidate') && !workplaceHubOpened) {
    return (
      <div className="app-shell" style={{ minHeight: '100vh', background: '#F8FAFC' }}>
        <main className="main-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '24px' }}>
          <section style={{ width: '100%', maxWidth: '680px', background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '16px', overflow: 'hidden', boxShadow: '0 12px 36px rgba(15, 23, 42, 0.08)' }}>
            <div style={{ height: '8px', background: '#0067B8' }} />
            <div style={{ padding: '40px 32px', textAlign: 'center' }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '58px', height: '58px', borderRadius: '14px', background: '#EAF4FC', color: '#0067B8', fontSize: '20px', fontWeight: 800, marginBottom: '22px' }}>
                TB
              </div>
              <p style={{ color: '#0067B8', fontSize: '13px', fontWeight: 700, letterSpacing: '1.8px', margin: '0 0 12px' }}>
                WORKPLACE HUB
              </p>
              <h1 style={{ color: '#0F172A', fontSize: '28px', lineHeight: 1.3, margin: '0 0 16px' }}>
                Administrator &amp; HR Manager Operations
              </h1>
              <p style={{ color: '#475569', fontSize: '16px', lineHeight: 1.7, margin: '0 auto 28px', maxWidth: '510px' }}>
                Access TBBD workplace tools and HR operations with role-based access and permission controls.
              </p>
              <button
                type="button"
                className="primary-button"
                onClick={() => setWorkplaceHubOpened(true)}
                style={{ minHeight: '46px', padding: '12px 26px' }}
              >
                Continue to Dashboard
              </button>
            </div>
          </section>
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
    'employer-access-requests': <EmployerAccessRequests />,
    'Candidate Approvals': <CandidateApprovals />,
    organizations: <OrganizationManagement onNavigate={setActivePage} />,

 users: <UserManagement auth={auth} />,

    roles: <RolesManagement />,

    notifications: <AdministratorNotifications />,

    settings: <SystemConfiguration />,

    activity: <SystemActivity />,

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
