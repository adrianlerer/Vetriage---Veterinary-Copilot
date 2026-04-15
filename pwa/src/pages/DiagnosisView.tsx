import { useStore } from '../store/useStore'
import { Link } from 'react-router-dom'
import { ArrowLeft, Stethoscope } from 'lucide-react'
import { DiagnosisResultView } from '../components/diagnosis/DiagnosisResult'

export default function DiagnosisView() {
  const { currentDiagnosis, currentCase } = useStore()

  if (!currentDiagnosis) {
    return (
      <div className="text-center py-20 animate-fade-in">
        <Stethoscope className="w-16 h-16 mx-auto mb-4 text-slate-300 dark:text-slate-600" />
        <h2 className="text-xl font-semibold mb-2">Sin diagnóstico activo</h2>
        <p className="text-slate-500 dark:text-slate-400 mb-6">
          Creá un nuevo caso clínico para obtener un diagnóstico.
        </p>
        <Link to="/app/nuevo-caso" className="btn-primary">
          Nuevo Caso Clínico
        </Link>
      </div>
    )
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <Link to="/app/nuevo-caso" className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-xl font-bold">Resultado del Diagnóstico</h1>
          {currentCase && (
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {currentCase.patientName} · {currentCase.breed} · {currentCase.chiefComplaint?.slice(0, 60)}
            </p>
          )}
        </div>
      </div>
      <DiagnosisResultView diagnosis={currentDiagnosis} />
    </div>
  )
}
