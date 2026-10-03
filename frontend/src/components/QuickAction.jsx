export default function QuickAction({ icon, label, onClick }) {
  return (
    <button className="quick-action" onClick={onClick}>
      <span>{icon}</span>
      {label}
    </button>
  )
}
