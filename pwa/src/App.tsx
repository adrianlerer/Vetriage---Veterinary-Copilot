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
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/nuevo-caso" element={<NewCase />} />
          <Route path="/diagnostico" element={<DiagnosisView />} />
          <Route path="/historial" element={<CaseHistory />} />
          <Route path="/seguridad-farmacologica" element={<DrugSafety />} />
          <Route path="/literatura" element={<Literature />} />
          <Route path="/configuracion" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
