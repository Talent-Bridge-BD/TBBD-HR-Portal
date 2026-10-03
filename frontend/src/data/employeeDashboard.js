export const employeeDashboard = {
  employee: {
    name: 'Employee',
    role: 'Employee',
  },

  attendance: {
    percentage: 95,
    status: 'On track',
    checkedIn: true,
    checkInTime: '09:02 AM',
  },

  leave: {
    balance: 12,
    unit: 'days',
    detail: 'Annual leave remaining',
    scheduled: false,
  },

  schedule: {
    start: '09:00',
    end: '17:30',
    location: 'Office · Dhaka',
  },

  tasks: {
    pending: 2,
  },

  notifications: [
    {
      id: 'leave-approved',
      title: 'Leave approved',
      message: 'Your recent leave request has been approved.',
    },
    {
      id: 'new-hr-policy',
      title: 'New HR policy',
      message: 'A new workplace policy is available to review.',
    },
    {
      id: 'team-announcement',
      title: 'Team announcement',
      message: 'There is a new announcement from your team.',
    },
  ],

  applications: {
    pending: 2,
    approved: 5,
    completed: 12,
  },

  announcements: [
    {
      id: 'workplace-updates',
      title: 'Important workplace updates',
      message:
        'Stay informed about the latest workplace updates and HR information.',
    },
    {
      id: 'upcoming-events',
      title: 'Upcoming events',
      message:
        'Check upcoming company events, meetings, and important dates.',
    },
    {
      id: 'hr-announcements',
      title: 'HR announcements',
      message:
        'Review the latest HR announcements and employee information.',
    },
  ],
}
