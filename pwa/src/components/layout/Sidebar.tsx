import { NavLink } from 'react-router-dom'
import {
  HeartPulse,
  PlusCircle,
  History,
  ShieldAlert,
  BookOpen,
  Settings,
  Stethoscope,
  X,
} from 'lucide-react'
import { useStore } from '../../store/useStore'

const navItems = [
  { to: '/app/nuevo-caso', label: 'Nuevo Caso', icon: PlusCircle },
  { to: '/app/historial', label: 'Historial', icon: History },
  { to: '/app/seguridad-farmacologica', label: 'Seguridad Farmacologica', icon: ShieldAlert },
  { to: '/app/literatura', label: 'Literatura', icon: BookOpen },
  { to: '/app/configuracion', label: 'Configuracion', icon: Settings },
] as const

export default function Sidebar() {
  const sidebarOpen = useStore((s) => s.sidebarOpen)
  const toggleSidebar = useStore((s) => s.toggleSidebar)

  return (
    <>
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-40 flex w-64 flex-col
          border-r border-white/10
          bg-white/70 backdrop-blur-xl
          shadow-lg shadow-brand-500/5
          transition-transform duration-300 ease-in-out
          dark:bg-slate-800/90 dark:border-slate-700/50
          lg:translate-x-0 lg:static lg:z-auto
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between px-5">
          <NavLink to="/app" className="flex items-center gap-2.5 group">
            <div className="relative flex items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 p-2 shadow-md shadow-brand-500/30 transition-shadow group-hover:shadow-brand-500/50">
              <HeartPulse className="h-5 w-5 text-white" />
              <Stethoscope className="absolute -bottom-1 -right-1 h-3.5 w-3.5 text-brand-300" />
            </div>
            <span className="text-lg font-bold tracking-tight text-slate-800 dark:text-white">
              Vetriage
            </span>
          </NavLink>

          {/* Close button (mobile only) */}
          <button
            onClick={toggleSidebar}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700 dark:hover:text-slate-300 lg:hidden"
            aria-label="Cerrar menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="mt-4 flex-1 space-y-1 px-3 overflow-y-auto">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => {
                // Close sidebar on mobile after navigating
                if (window.innerWidth < 1024) toggleSidebar()
              }}
              className={({ isActive }) =>
                `group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200
                ${
                  isActive
                    ? 'bg-brand-50 text-brand-600 shadow-sm shadow-brand-500/10 dark:bg-brand-500/15 dark:text-brand-400'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-700/50 dark:hover:text-slate-200'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={`h-5 w-5 flex-shrink-0 transition-colors ${
                      isActive
                        ? 'text-brand-600 dark:text-brand-400'
                        : 'text-slate-400 group-hover:text-slate-600 dark:text-slate-500 dark:group-hover:text-slate-300'
                    }`}
                  />
                  <span>{label}</span>
                  {isActive && (
                    <span className="ml-auto h-1.5 w-1.5 rounded-full bg-brand-500" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-slate-200/60 px-4 py-3 dark:border-slate-700/50">
          <p className="text-xs text-slate-400 dark:text-slate-500">
            Vetriage v1.0 &mdash; Copiloto Veterinario
          </p>
        </div>
      </aside>
    </>
  )
}
