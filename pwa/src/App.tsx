import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import NewCase from './pages/NewCase'
import DiagnosisView from './pages/DiagnosisView'
import CaseHistory from './pages/CaseHistory'
import DrugSafety from './pages/DrugSafety'
import Literature from './pages/Literature'
import Settings from './pages/Settings'
import LandingPage from './pages/LandingPage'
import { useStore } from './store/useStore'

export default function App() {
  const { settings } = useStore()

  // Apply dark mode on mount
  useEffect(() => {
    if (settings.darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [settings.darkMode])

  return (
    <BrowserRouter>
      <Routes>
        {/* Landing page */}
        <Route path="/" element={<LandingPage />} />

        {/* App routes */}
        <Route path="/app" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="nuevo-caso" element={<NewCase />} />
          <Route path="diagnostico" element={<DiagnosisView />} />
          <Route path="historial" element={<CaseHistory />} />
          <Route path="seguridad-farmacologica" element={<DrugSafety />} />
          <Route path="literatura" element={<Literature />} />
          <Route path="configuracion" element={<Settings />} />
        </Route>

        {/* Redirect old routes to /app */}
        <Route path="/nuevo-caso" element={<Navigate to="/app/nuevo-caso" replace />} />
        <Route path="/diagnostico" element={<Navigate to="/app/diagnostico" replace />} />
        <Route path="/historial" element={<Navigate to="/app/historial" replace />} />
        <Route path="/seguridad-farmacologica" element={<Navigate to="/app/seguridad-farmacologica" replace />} />
        <Route path="/literatura" element={<Navigate to="/app/literatura" replace />} />
        <Route path="/configuracion" element={<Navigate to="/app/configuracion" replace />} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
