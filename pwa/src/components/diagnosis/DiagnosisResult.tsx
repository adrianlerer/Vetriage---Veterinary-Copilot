import { useState } from 'react'
import {
  Clock,
  Stethoscope,
  FlaskConical,
  FileText,
  ShieldAlert,
  Activity,
} from 'lucide-react'
import type { DiagnosisResult as DiagnosisResultType } from '../../types'
import { DifferentialList } from './DifferentialList'
import { TreatmentPlan } from './TreatmentPlan'
import { EvidencePanel } from './EvidencePanel'
import { ConfidenceChart } from './ConfidenceChart'
import { SafetyAlerts } from '../safety/SafetyAlerts'

interface Props {
  diagnosis: DiagnosisResultType
}

const tabs = [
  { id: 'differentials', label: 'Diferenciales', icon: Stethoscope },
  { id: 'treatment', label: 'Plan Terapeutico', icon: FlaskConical },
  { id: 'evidence', label: 'Evidencia', icon: FileText },
  { id: 'alerts', label: 'Alertas', icon: ShieldAlert },
] as const

type TabId = (typeof tabs)[number]['id']

export function DiagnosisResultView({ diagnosis }: Props) {
  const [activeTab, setActiveTab] = useState<TabId>('differentials')

  const criticalCount = diagnosis.safetyAlerts.filter(
    (a) => a.severity === 'CRITICAL'
  ).length

  return (
    <div className="space-y-6">
      {/* ── Resumen ─────────────────────────────────────── */}
      <div className="rounded-2xl border border-white/20 bg-white/10 p-6 shadow-lg backdrop-blur-md dark:border-white/10 dark:bg-white/5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Resultado del Diagnostico
          </h2>
          {diagnosis.processingTime != null && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
              <Clock className="h-3.5 w-3.5" />
              {(diagnosis.processingTime / 1000).toFixed(1)}s
            </span>
          )}
        </div>
        <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
          {diagnosis.summary}
        </p>
      </div>

      {/* ── Grafico de confianza ───────────────────────── */}
      {diagnosis.differentials.length > 0 && (
        <div className="rounded-2xl border border-white/20 bg-white/10 p-6 shadow-lg backdrop-blur-md dark:border-white/10 dark:bg-white/5">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-gray-900 dark:text-white">
            <Activity className="h-4 w-4" />
            Probabilidades
          </h3>
          <ConfidenceChart differentials={diagnosis.differentials} />
        </div>
      )}

      {/* ── Tabs ───────────────────────────────────────── */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex gap-2 overflow-x-auto" aria-label="Secciones">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`inline-flex shrink-0 items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'border-teal-500 text-teal-600 dark:text-teal-400'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
                {tab.id === 'alerts' && criticalCount > 0 && (
                  <span className="ml-1 inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-red-500 px-1.5 text-xs font-bold text-white">
                    {criticalCount}
                  </span>
                )}
              </button>
            )
          })}
        </nav>
      </div>

      {/* ── Contenido ──────────────────────────────────── */}
      <div className="min-h-[200px]">
        {activeTab === 'differentials' && (
          <DifferentialList differentials={diagnosis.differentials} />
        )}
        {activeTab === 'treatment' && (
          <TreatmentPlan plan={diagnosis.treatmentPlan} />
        )}
        {activeTab === 'evidence' && (
          <EvidencePanel papers={diagnosis.citedPapers} />
        )}
        {activeTab === 'alerts' && (
          <SafetyAlerts alerts={diagnosis.safetyAlerts} />
        )}
      </div>
    </div>
  )
}
