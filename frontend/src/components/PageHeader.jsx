export default function PageHeader({ title, subtitle, className = '' }) {
  return (
    <div className={`page-header ${className}`.trim()}>
      <h1>{title}</h1>
      {subtitle && <p>{subtitle}</p>}
    </div>
  )
}
