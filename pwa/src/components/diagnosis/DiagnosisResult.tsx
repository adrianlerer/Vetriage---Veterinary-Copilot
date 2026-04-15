import { useState } from 'react'
import {
  Clock,
  Activity,
  ShieldAlert,
  ChevronRight,
  BookOpen,
} from 'lucide-react'
import type { DiagnosisResult as DiagnosisResultType } from '../../types'
import { WikiDifferentialCard } from './WikiDifferentialCard'
import { SafetyAlerts } from '../safety/SafetyAlerts'
import { ConfidenceChart } from './ConfidenceChart'
import { TreatmentPlan } from './TreatmentPlan'
import { EvidencePanel } from './EvidencePanel'

interface Props {
  diagnosis: DiagnosisResultType
  species?: string
  breed?: string
}

export function DiagnosisResultView({ diagnosis, species, breed }: Props) {
  const [showAlerts, setShowAlerts] = useState(false)
  const [showPlan, setShowPlan] = useState(false)
  const [showEvidence, setShowEvidence] = useState(false)

  const criticalAlerts = diagnosis.safetyAlerts.filter(
    (a) => a.severity === 'CRITICAL' || a.severity === 'HIGH'
  )

  return (
    <div className="space-y-4">
      {/* ── Critical Alerts Banner ──────────────────────── */}
      {criticalAlerts.length > 0 && (
        <div className="rounded-xl border border-red-300 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950/40">
          <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
            <ShieldAlert className="h-5 w-5" />
            <span className="font-bold text-sm">
              {criticalAlerts.length} alerta{criticalAlerts.length > 1 ? 's' : ''} de seguridad
            </span>
          </div>
          {criticalAlerts.map((a, i) => (
            <p key={i} className="mt-1 text-sm text-red-600 dark:text-red-300">
              <strong>{a.title}:</strong> {a.action}
            </p>
          ))}
        </div>
      )}

      {/* ── Summary Card ───────────────────────────────── */}
      <div className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-lg backdrop-blur-md dark:border-white/10 dark:bg-white/5">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-teal-600 dark:text-teal-400" />
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              Wiki Diagnóstica
            </h2>
          </div>
          {diagnosis.processingTime != null && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-teal-100 px-3 py-1 text-xs font-medium text-teal-800 dark:bg-teal-900/40 dark:text-teal-300">
              <Clock className="h-3.5 w-3.5" />
              {(diagnosis.processingTime / 1000).toFixed(1)}s
            </span>
          )}
        </div>
        <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
          {diagnosis.summary}
        </p>
      </div>

      {/* ── Confidence Overview ─────────────────────────── */}
      {diagnosis.differentials.length > 0 && (
        <div className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-lg backdrop-blur-md dark:border-white/10 dark:bg-white/5">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-900 dark:text-white">
            <Activity className="h-4 w-4" />
            Probabilidades
          </h3>
          <ConfidenceChart differentials={diagnosis.differentials} />
        </div>
      )}

      {/* ── Differential Wiki Cards ────────────────────── */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider px-1">
          Diagnósticos Diferenciales
        </h3>
        {diagnosis.differentials.map((dx, i) => (
          <WikiDifferentialCard
            key={i}
            differential={dx}
            index={i}
            species={species || ''}
            breed={breed}
            caseContext={diagnosis.summary}
          />
        ))}
      </div>

      {/* ── Collapsible Sections ────────────────────────── */}
      <div className="space-y-2">
        {/* Treatment Plan */}
        <CollapsibleSection
          title="Plan Terapéutico General"
          isOpen={showPlan}
          onToggle={() => setShowPlan(!showPlan)}
          badge={diagnosis.treatmentPlan.treatmentPlan.length > 0 ? `${diagnosis.treatmentPlan.treatmentPlan.length} pasos` : undefined}
        >
          <TreatmentPlan plan={diagnosis.treatmentPlan} />
        </CollapsibleSection>

        {/* Evidence */}
        {diagnosis.citedPapers.length > 0 && (
          <CollapsibleSection
            title="Evidencia / PubMed"
            isOpen={showEvidence}
            onToggle={() => setShowEvidence(!showEvidence)}
            badge={`${diagnosis.citedPapers.length} papers`}
          >
            <EvidencePanel papers={diagnosis.citedPapers} />
          </CollapsibleSection>
        )}

        {/* Safety Alerts (non-critical, full list) */}
        {diagnosis.safetyAlerts.length > 0 && (
          <CollapsibleSection
            title="Alertas de Seguridad"
            isOpen={showAlerts}
            onToggle={() => setShowAlerts(!showAlerts)}
            badge={`${diagnosis.safetyAlerts.length}`}
            badgeColor="red"
          >
            <SafetyAlerts alerts={diagnosis.safetyAlerts} />
          </CollapsibleSection>
        )}
      </div>

      {/* ── Disclaimer ─────────────────────────────────── */}
      <p className="text-xs text-gray-400 dark:text-gray-500 text-center px-4 pt-2">
        ⚕️ Generado por IA. Herramienta de apoyo — no reemplaza el juicio clínico profesional.
      </p>
    </div>
  )
}

// ── Collapsible Section ─────────────────────────────────

function CollapsibleSection({
  title,
  isOpen,
  onToggle,
  badge,
  badgeColor = 'gray',
  children,
}: {
  title: string
  isOpen: boolean
  onToggle: () => void
  badge?: string
  badgeColor?: 'gray' | 'red' | 'teal'
  children: React.ReactNode
}) {
  const badgeColors = {
    gray: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
    red: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400',
    teal: 'bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-400',
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800/60 overflow-hidden">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between px-5 py-3.5 text-left hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
      >
        <span className="flex items-center gap-2.5">
          <ChevronRight
            className={`h-4 w-4 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-90' : ''}`}
          />
          <span className="text-sm font-semibold text-gray-900 dark:text-white">
            {title}
          </span>
          {badge && (
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${badgeColors[badgeColor]}`}>
              {badge}
            </span>
          )}
        </span>
      </button>
      {isOpen && (
        <div className="border-t border-gray-100 dark:border-gray-700 px-5 py-4">
          {children}
        </div>
      )}
    </div>
  )
}
