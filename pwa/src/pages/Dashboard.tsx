import { Activity, Clock, ShieldAlert, FileText, ArrowRight, Stethoscope } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useStore } from '../store/useStore'

export default function Dashboard() {
  const { caseHistory } = useStore()

  const totalCases = caseHistory.length
  const criticalAlerts = caseHistory.reduce(
    (acc, h) => acc + h.diagnosis.safetyAlerts.filter((a) => a.severity === 'CRITICAL').length,
    0
  )
  const avgTime =
    caseHistory.length > 0
      ? (
          caseHistory.reduce((acc, h) => acc + (h.diagnosis.processingTime || 0), 0) /
          caseHistory.length
        ).toFixed(1)
      : '—'

  const recentCases = caseHistory.slice(0, 5)

  const stats = [
    { label: 'Casos Analizados', value: totalCases, icon: FileText, color: 'text-brand-600' },
    { label: 'Alertas Críticas', value: criticalAlerts, icon: ShieldAlert, color: 'text-red-500' },
    { label: 'Tiempo Promedio', value: `${avgTime}s`, icon: Clock, color: 'text-amber-500' },
  ]

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero */}
      <div className="glass-card p-8 bg-gradient-to-br from-brand-600 to-brand-800 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Bienvenido a Vetriage</h1>
            <p className="text-brand-100 text-lg max-w-xl">
              Copiloto veterinario con IA. Diagnósticos basados en evidencia de +35 millones de
              papers científicos.
            </p>
          </div>
          <Stethoscope className="w-16 h-16 text-brand-200 opacity-50 hidden md:block" />
        </div>
        <Link to="/nuevo-caso" className="inline-flex items-center gap-2 mt-6 px-6 py-3 bg-white text-brand-700 font-semibold rounded-xl hover:bg-brand-50 transition-colors">
          Nuevo Caso Clínico <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {stats.map((s) => (
          <div key={s.label} className="glass-card p-6 flex items-center gap-4">
            <div className={`p-3 rounded-xl bg-slate-100 dark:bg-slate-700 ${s.color}`}>
              <s.icon className="w-6 h-6" />
            </div>
            <div>
              <p className="text-2xl font-bold">{s.value}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Cases */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Activity className="w-5 h-5 text-brand-600" />
            Casos Recientes
          </h2>
          {caseHistory.length > 0 && (
            <Link to="/historial" className="text-brand-600 hover:text-brand-700 text-sm font-medium">
              Ver todos
            </Link>
          )}
        </div>

        {recentCases.length === 0 ? (
          <div className="text-center py-12 text-slate-400">
            <Stethoscope className="w-12 h-12 mx-auto mb-3 opacity-40" />
            <p>No hay casos aún. Creá tu primer caso clínico.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentCases.map((h, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">
                    {h.case.species === 'dog' ? '🐕' : h.case.species === 'cat' ? '🐈' : h.case.species === 'horse' ? '🐴' : h.case.species === 'bird' ? '🐦' : h.case.species === 'cattle' ? '🐄' : '🦎'}
                  </span>
                  <div>
                    <p className="font-medium">{h.case.patientName || 'Sin nombre'}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {h.case.breed} · {h.case.chiefComplaint?.slice(0, 50)}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-brand-600">
                    {h.diagnosis.differentials?.[0]?.diagnosis || '—'}
                  </p>
                  <p className="text-xs text-slate-400">
                    {h.diagnosis.timestamp ? new Date(h.diagnosis.timestamp).toLocaleDateString('es') : ''}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
