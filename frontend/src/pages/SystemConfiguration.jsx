import "./SystemConfiguration.css";

export default function SystemConfiguration() {
  const settings = [
    {
      title: "Tenant Configuration",
      items: [
        "Microsoft Entra ID integration",
        "Organization structure",
        "Access policies",
      ],
    },
    {
      title: "Portal Configuration",
      items: [
        "HR workflow settings",
        "Recruitment lifecycle",
        "Notification templates",
      ],
    },
    {
      title: "Integration Settings",
      items: [
        "AI Workplace Assistant",
        "Azure services",
        "External integrations",
      ],
    },
  ];

  return (
    <section className="system-configuration-page">

      <div className="page-header">
        <h1>System Configuration</h1>
        <p>
          Manage portal settings, integrations, and platform configuration.
        </p>
      </div>

      <div className="configuration-grid">
        {settings.map((section) => (
          <div className="configuration-card" key={section.title}>
            <h2>{section.title}</h2>

            <ul>
              {section.items.map((item) => (
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
