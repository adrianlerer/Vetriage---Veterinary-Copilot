import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

/** Map route paths to human-readable Spanish page titles. */
const pageTitles: Record<string, string> = {
  '/app': 'Inicio',
  '/app/nuevo-caso': 'Nuevo Caso',
  '/app/historial': 'Historial de Casos',
  '/app/seguridad-farmacologica': 'Seguridad Farmacologica',
  '/app/literatura': 'Busqueda de Literatura',
  '/app/configuracion': 'Configuracion',
}

export default function Layout() {
  const { pathname } = useLocation()
  const title = pageTitles[pathname] ?? 'Vetriage'

  return (
    <div className="flex h-screen overflow-hidden bg-gradient-to-br from-slate-50 via-white to-brand-50/30 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800">
      {/* Sidebar */}
      <Sidebar />

      {/* Main area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header title={title} />

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-5xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
