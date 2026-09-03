const navigation = [
  ['Dashboard', '⌂'],
  ['My Profile', '◉'],
  ['Leave', '▣'],
  ['Attendance', '◷'],
  ['Applications', '▤'],
  ['Schedule', '□']
]

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <nav>
        {navigation.map(([label, icon]) => (
          <button
            key={label}
            className={`nav-item ${activePage === label ? 'active' : ''}`}
            onClick={() => onNavigate(label)}
          >
            <span className="nav-icon">{icon}</span>
            <span>{label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
