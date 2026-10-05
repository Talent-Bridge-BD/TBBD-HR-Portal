import "./SystemActivity.css";

export default function SystemActivity() {

  const activities = [
    {
      event: "User authentication",
      description: "Microsoft Entra ID sign-in events",
    },
    {
      event: "Organization changes",
      description: "Organization and membership updates",
    },
    {
      event: "Role changes",
      description: "Role and permission updates",
    },
    {
      event: "System events",
      description: "Portal configuration activities",
    },
  ];

  return (
    <section className="system-activity-page">

      <div className="page-header">
        <h1>System Activity</h1>
        <p>
          Monitor audit logs and platform events.
        </p>
      </div>

      <div className="activity-card">
        {activities.map((activity) => (
          <div className="activity-row" key={activity.event}>
            <h3>{activity.event}</h3>
            <p>{activity.description}</p>
          </div>
        ))}
      </div>

    </section>
  );
}
