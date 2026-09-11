import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊', roles: null },
  { to: '/employees', label: 'Employees', icon: '👥', roles: null },
  { to: '/attrition', label: 'Attrition Risk', icon: '🧠', roles: ['Admin', 'HR', 'Manager'] },
  { to: '/leaves', label: 'Leave', icon: '🗓️', roles: null },
  { to: '/attendance', label: 'Attendance', icon: '⏱️', roles: null },
  { to: '/payroll', label: 'Payroll', icon: '💰', roles: ['Admin', 'HR'] },
]

export default function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const items = NAV_ITEMS.filter((i) => !i.roles || i.roles.includes(user?.role))

  return (
    <div className="min-h-screen flex bg-slate-50">
      <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col">
        <div className="px-5 py-5 border-b border-slate-800">
          <h1 className="text-lg font-bold text-white">WorkForce AI Pro</h1>
          <p className="text-xs text-slate-400">HR Intelligence Platform</p>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                  isActive ? 'bg-indigo-600 text-white' : 'hover:bg-slate-800 text-slate-300'
                }`
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-5 py-4 border-t border-slate-800">
          <p className="text-sm font-medium text-white">{user?.full_name}</p>
          <p className="text-xs text-slate-400 mb-3">{user?.role}</p>
          <button
            onClick={() => {
              logout()
              navigate('/login')
            }}
            className="text-xs text-slate-400 hover:text-white"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
