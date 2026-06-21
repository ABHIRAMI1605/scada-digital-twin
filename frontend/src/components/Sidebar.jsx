import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/alarms', label: 'Alarms' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 bg-[#161922] border-r border-[#2a2e3a] h-screen p-4 flex flex-col gap-2">
      <h1 className="text-lg font-bold text-gray-100 mb-4">Plant SCADA</h1>
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) =>
            `px-3 py-2 rounded-md text-sm ${
              isActive ? 'bg-green-500/10 text-green-400' : 'text-gray-300 hover:bg-[#1f2330]'
            }`
          }
        >
          {link.label}
        </NavLink>
      ))}
    </aside>
  )
}