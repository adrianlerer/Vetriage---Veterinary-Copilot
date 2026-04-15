import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import CaseForm from '../components/case/CaseForm'
import { useStore } from '../store/useStore'
import { api } from '../api/client'
import type { ClinicalCase } from '../types'
import { AlertTriangle, Loader2 } from 'lucide-react'

export default function NewCase() {
  const navigate = useNavigate()
  const { setCurrentCase, setCurrentDiagnosis, addToHistory, setError } = useStore()
  const [loading, setLoading] = useState(false)
  const [error, setLocalError] = useState<string | null>(null)

  const handleSubmit = async (clinicalCase: ClinicalCase) => {
    setLoading(true)
    setLocalError(null)
    setCurrentCase(clinicalCase)

    try {
      const result = await api.diagnose(clinicalCase)
      setCurrentDiagnosis(result)
      addToHistory(clinicalCase, result)
      navigate('/app/diagnostico')
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al procesar el diagnóstico'
      setLocalError(msg)
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      {loading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm">
          <div className="glass-card p-8 text-center max-w-sm mx-4">
            <Loader2 className="w-12 h-12 text-brand-500 animate-spin mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Analizando caso clínico...</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Buscando evidencia en +35M papers científicos, generando diagnósticos diferenciales y
              verificando seguridad farmacológica.
            </p>
            <div className="mt-4 space-y-2">
              <ProgressStep label="Expandiendo consulta PubMed" done />
              <ProgressStep label="Buscando literatura científica" done />
              <ProgressStep label="Analizando con IA" />
              <ProgressStep label="Verificando seguridad" pending />
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 rounded-xl severity-critical flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium">Error en el diagnóstico</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      <CaseForm onSubmit={handleSubmit} isLoading={loading} />
    </div>
  )
}

function ProgressStep({ label, done, pending }: { label: string; done?: boolean; pending?: boolean }) {
  return (
    <div className={`flex items-center gap-2 text-sm ${pending ? 'text-slate-400' : done ? 'text-brand-600' : 'text-brand-500 font-medium'}`}>
      {done ? (
        <span className="w-4 h-4 rounded-full bg-brand-500 flex items-center justify-center text-white text-xs">✓</span>
      ) : pending ? (
        <span className="w-4 h-4 rounded-full border-2 border-slate-300 dark:border-slate-600" />
      ) : (
        <Loader2 className="w-4 h-4 animate-spin" />
      )}
      {label}
    </div>
  )
}
