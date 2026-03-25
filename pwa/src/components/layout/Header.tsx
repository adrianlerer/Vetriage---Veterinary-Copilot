import { Menu, Moon, Sun, Wifi, WifiOff } from 'lucide-react'
import { useStore } from '../../store/useStore'

interface HeaderProps {
  title?: string
}

export default function Header({ title = 'Vetriage' }: HeaderProps) {
  const toggleSidebar = useStore((s) => s.toggleSidebar)
  const toggleDarkMode = useStore((s) => s.toggleDarkMode)
  const darkMode = useStore((s) => s.settings.darkMode)
  const apiUrl = useStore((s) => s.settings.apiUrl)
  const error = useStore((s) => s.error)

  // Simple heuristic: if there's an active error we treat it as disconnected
  const connected = !error

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-white/10 bg-white/60 px-4 backdrop-blur-xl dark:bg-slate-900/60 dark:border-slate-700/50 sm:px-6">
      {/* Hamburger (mobile) */}
      <button
        onClick={toggleSidebar}
        className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200 lg:hidden"
        aria-label="Abrir menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Page title */}
      <h1 className="text-lg font-semibold tracking-tight text-slate-800 dark:text-white truncate">
        {title}
      </h1>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Connection indicator */}
      <div
        className="flex items-center gap-1.5 rounded-full bg-slate-100/80 px-3 py-1.5 text-xs font-medium dark:bg-slate-700/60"
        title={connected ? `Conectado a ${apiUrl}` : 'Sin conexion al servidor'}
      >
        {connected ? (
          <>
            <Wifi className="h-3.5 w-3.5 text-emerald-500" />
            <span className="hidden text-emerald-600 dark:text-emerald-400 sm:inline">
              Conectado
            </span>
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
          </>
        ) : (
          <>
            <WifiOff className="h-3.5 w-3.5 text-red-500" />
            <span className="hidden text-red-600 dark:text-red-400 sm:inline">
              Desconectado
            </span>
            <span className="h-2 w-2 rounded-full bg-red-500" />
          </>
        )}
      </div>

      {/* Dark mode toggle */}
      <button
        onClick={toggleDarkMode}
        className="rounded-xl p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-amber-400"
        aria-label={darkMode ? 'Modo claro' : 'Modo oscuro'}
      >
        {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
      </button>
    </header>
  )
}
