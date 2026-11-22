export default function PlatformPlaceholder({
  area,
  title,
  description,
}) {
  return (
    <section className="platform-placeholder">
      <div className="platform-placeholder-badge">{area}</div>

      <h1>{title}</h1>

      <p>{description}</p>

      <div className="platform-placeholder-card">
        <span className="platform-placeholder-icon">✦</span>

        <div>
          <strong>This platform area is being prepared.</strong>
          <span>
            The navigation is now part of the TBBD Platform shell.
            Functionality will be introduced in the next implementation phase.
          </span>
        </div>
      </div>
    </section>
  )
}
