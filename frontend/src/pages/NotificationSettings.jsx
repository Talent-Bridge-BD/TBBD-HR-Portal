import "./NotificationSettings.css";

export default function NotificationSettings() {

  const notifications = [
    {
      title: "Email Notifications",
      items: [
        "Candidate application alerts",
        "Interview reminders",
        "Hiring workflow updates",
      ],
    },
    {
      title: "System Notifications",
      items: [
        "User activity alerts",
        "Organization updates",
        "Security events",
      ],
    },
    {
      title: "Workflow Notifications",
      items: [
        "Job request status",
        "Application status changes",
        "Approval notifications",
      ],
    },
  ];

  return (
    <section className="notification-settings-page">

      <div className="page-header">
        <h1>Notification Settings</h1>
        <p>
          Configure notification templates and delivery settings.
        </p>
      </div>

      <div className="notification-grid">

        {notifications.map((notification) => (
          <div
            className="notification-card"
            key={notification.title}
          >
            <h2>{notification.title}</h2>

            <ul>
              {notification.items.map((item) => (
                <li key={item}>
                  {item}
                </li>
              ))}
            </ul>

          </div>
        ))}

      </div>

    </section>
  );
}
