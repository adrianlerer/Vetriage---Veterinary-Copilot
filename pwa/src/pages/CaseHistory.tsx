import { useStore } from '../store/useStore'
import { History, Trash2, Stethoscope } from 'lucide-react'
import { Link } from 'react-router-dom'

const speciesEmoji: Record<string, string> = {
  dog: '🐕', cat: '🐈', horse: '🐴', bird: '🐦', exotic: '🦎', cattle: '🐄',
}

export default function CaseHistory() {
  const { caseHistory, setCurrentCase, setCurrentDiagnosis } = useStore()

  const loadCase = (index: number) => {
    const h = caseHistory[index]
    setCurrentCase(h.case)
    setCurrentDiagnosis(h.diagnosis)
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <History className="w-6 h-6 text-brand-600" />
        <h1 className="text-xl font-bold">Historial de Casos</h1>
        <span className="chip">{caseHistory.length} casos</span>
      </div>

      {caseHistory.length === 0 ? (
        <div className="text-center py-20">
          <Stethoscope className="w-16 h-16 mx-auto mb-4 text-slate-300 dark:text-slate-600" />
          <p className="text-slate-500 dark:text-slate-400">No hay casos en el historial.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {caseHistory.map((h, i) => (
            <Link
              key={i}
              to="/app/diagnostico"
              onClick={() => loadCase(i)}
              className="glass-card p-5 flex items-center justify-between hover:shadow-xl transition-all duration-200 group block"
            >
              <div className="flex items-center gap-4">
                <span className="text-3xl">{speciesEmoji[h.case.species] || '🐾'}</span>
                <div>
                  <p className="font-semibold group-hover:text-brand-600 transition-colors">
                    {h.case.patientName || 'Sin nombre'}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {h.case.breed} · {h.case.age} · {h.case.sex}
                  </p>
                  <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">
                    {h.case.chiefComplaint?.slice(0, 80)}
                  </p>
                </div>
              </div>
              <div className="text-right flex-shrink-0 ml-4">
                <p className="font-medium text-brand-600">
                  {h.diagnosis.differentials?.[0]?.diagnosis || '—'}
                </p>
                <p className="text-sm text-slate-400">
                  {h.diagnosis.differentials?.[0]?.probability
                    ? `${h.diagnosis.differentials[0].probability}%`
                    : ''}
                </p>
                {h.diagnosis.safetyAlerts?.some((a) => a.severity === 'CRITICAL') && (
                  <span className="inline-block mt-1 px-2 py-0.5 text-xs font-semibold bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full">
                    Alerta Crítica
                  </span>
                )}
                <p className="text-xs text-slate-400 mt-1">
                  {h.diagnosis.timestamp ? new Date(h.diagnosis.timestamp).toLocaleDateString('es') : ''}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
