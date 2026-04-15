import { useState } from 'react'
import {
  ChevronDown,
  ChevronUp,
  Award,
  Loader2,
  Microscope,
  Stethoscope,
  Pill,
  HeartPulse,
  Globe,
  BookOpen,
  Lightbulb,
  ExternalLink,
} from 'lucide-react'
import type { DifferentialDiagnosis, WikiExpandedSection } from '../../types'

interface Props {
  differential: DifferentialDiagnosis
  index: number
  species: string
  breed?: string
  caseContext: string
}

// ── Section metadata ─────────────────────────────────────

const SECTION_META: Record<string, { label: string; icon: typeof Microscope; color: string }> = {
  fisiopatologia: { label: 'Fisiopatología', icon: Microscope, color: 'text-purple-600 dark:text-purple-400' },
  diagnostico: { label: 'Diagnóstico', icon: Stethoscope, color: 'text-blue-600 dark:text-blue-400' },
  tratamiento: { label: 'Tratamiento', icon: Pill, color: 'text-emerald-600 dark:text-emerald-400' },
  pronostico: { label: 'Pronóstico', icon: HeartPulse, color: 'text-amber-600 dark:text-amber-400' },
  epidemiologia: { label: 'Epidemiología', icon: Globe, color: 'text-rose-600 dark:text-rose-400' },
}

function probColor(p: number) {
  if (p >= 50) return { bar: 'bg-emerald-500', text: 'text-emerald-700 dark:text-emerald-400', ring: 'ring-emerald-500/20' }
  if (p >= 25) return { bar: 'bg-amber-500', text: 'text-amber-700 dark:text-amber-400', ring: 'ring-amber-500/20' }
  return { bar: 'bg-red-500', text: 'text-red-700 dark:text-red-400', ring: 'ring-red-500/20' }
}

function GradeBadge({ score }: { score: string }) {
  const letter = score.charAt(0).toUpperCase()
  const colorMap: Record<string, string> = {
    A: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
    B: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
    C: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
    D: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
  }
  const cls = colorMap[letter] ?? 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'

  return (
    <span className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-bold ${cls}`} title={`Nivel de evidencia: ${letter}`}>
      <Award className="h-3 w-3" />
      {letter}
    </span>
  )
}

// ── Expanded Section View ─────────────────────────────────

function ExpandedSectionView({ data, onClose }: { data: WikiExpandedSection; onClose: () => void }) {
  return (
    <div className="mt-3 rounded-lg border border-teal-200 bg-teal-50/50 p-4 dark:border-teal-800 dark:bg-teal-950/30">
      <div className="flex items-center justify-between mb-3">
        <h5 className="font-semibold text-sm text-teal-800 dark:text-teal-300 flex items-center gap-2">
          <BookOpen className="h-4 w-4" />
          {data.title}
        </h5>
        <button
          onClick={onClose}
          className="text-xs text-teal-600 hover:text-teal-800 dark:text-teal-400 dark:hover:text-teal-200"
        >
          Cerrar
        </button>
      </div>

      {/* Content paragraphs */}
      <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
        {data.content.split('\n\n').map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>

      {/* Key Points */}
      {data.keyPoints.length > 0 && (
        <div className="mt-4">
          <h6 className="text-xs font-semibold uppercase tracking-wider text-teal-700 dark:text-teal-400 mb-2 flex items-center gap-1.5">
            <Lightbulb className="h-3.5 w-3.5" />
            Puntos clave
          </h6>
          <ul className="space-y-1">
            {data.keyPoints.map((kp, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-500" />
                {kp}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* References */}
      {data.references.length > 0 && (
        <div className="mt-3 pt-3 border-t border-teal-200/60 dark:border-teal-800/60">
          <h6 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1.5 flex items-center gap-1.5">
            <ExternalLink className="h-3 w-3" />
            Referencias
          </h6>
          <ul className="space-y-0.5">
            {data.references.map((ref, i) => (
              <li key={i} className="text-xs text-gray-500 dark:text-gray-400 italic">
                {ref}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Processing time */}
      <p className="mt-2 text-xs text-gray-400 dark:text-gray-500 text-right">
        Generado en {(data.processingTime / 1000).toFixed(1)}s
      </p>
    </div>
  )
}

// ── Main Component ────────────────────────────────────────

export function WikiDifferentialCard({ differential: dx, index, species, breed, caseContext }: Props) {
  const [isOpen, setIsOpen] = useState(index === 0) // First one open by default
  const [expandedSections, setExpandedSections] = useState<Record<string, WikiExpandedSection>>({})
  const [loadingSection, setLoadingSection] = useState<string | null>(null)
  const [sectionError, setSectionError] = useState<string | null>(null)

  const colors = probColor(dx.probability)
  const sections = dx.wikiSections || ['fisiopatologia', 'diagnostico', 'tratamiento', 'pronostico']

  const handleExpand = async (section: string) => {
    // Toggle if already loaded
    if (expandedSections[section]) {
      const next = { ...expandedSections }
      delete next[section]
      setExpandedSections(next)
      return
    }

    setLoadingSection(section)
    setSectionError(null)

    try {
      const res = await fetch('/api/expand', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          diagnosis: dx.diagnosis,
          section,
          species: species || 'no especificada',
          breed: breed || undefined,
          context: caseContext,
        }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({ error: res.statusText }))
        throw new Error(body.error || `Error ${res.status}`)
      }

      const data: WikiExpandedSection = await res.json()
      setExpandedSections((prev) => ({ ...prev, [section]: data }))
    } catch (err) {
      setSectionError(err instanceof Error ? err.message : 'Error al expandir')
    } finally {
      setLoadingSection(null)
    }
  }

  return (
    <div className={`rounded-xl border shadow-sm transition-all hover:shadow-md overflow-hidden ${
      index === 0
        ? 'border-teal-200 bg-white dark:border-teal-800 dark:bg-gray-800/80'
        : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800/60'
    }`}>
      {/* ── Header ───────────────────────────────────── */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center gap-4 px-5 py-4 text-left"
      >
        {/* Rank badge */}
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${colors.bar} text-white font-bold text-sm shadow-sm`}>
          {dx.probability}%
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-bold text-gray-900 dark:text-white">
              {dx.diagnosis}
            </span>
            <GradeBadge score={dx.gradeScore} />
          </div>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 line-clamp-1">
            {dx.oneLiner || dx.reasoning || ''}
          </p>
        </div>

        {isOpen ? (
          <ChevronUp className="h-5 w-5 shrink-0 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 shrink-0 text-gray-400" />
        )}
      </button>

      {/* ── Expanded Content ─────────────────────────── */}
      {isOpen && (
        <div className="border-t border-gray-100 dark:border-gray-700 px-5 py-4 space-y-4">
          {/* Key Findings */}
          {dx.keyFindings.length > 0 && (
            <div>
              <h4 className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Hallazgos clave
              </h4>
              <div className="flex flex-wrap gap-2">
                {dx.keyFindings.map((f, fi) => (
                  <span
                    key={fi}
                    className="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300"
                  >
                    {f}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* ── Wiki Section Buttons (Profundizar) ──── */}
          <div>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
              Profundizar
            </h4>
            <div className="flex flex-wrap gap-2">
              {sections.map((section) => {
                const meta = SECTION_META[section] || { label: section, icon: BookOpen, color: 'text-gray-600' }
                const Icon = meta.icon
                const isLoading = loadingSection === section
                const isExpanded = !!expandedSections[section]

                return (
                  <button
                    key={section}
                    onClick={() => handleExpand(section)}
                    disabled={isLoading}
                    className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition-all ${
                      isExpanded
                        ? 'bg-teal-100 text-teal-800 ring-1 ring-teal-300 dark:bg-teal-900/40 dark:text-teal-300 dark:ring-teal-700'
                        : 'bg-gray-50 text-gray-600 hover:bg-gray-100 hover:text-gray-800 dark:bg-gray-700/50 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200'
                    } ${isLoading ? 'opacity-60 cursor-wait' : ''}`}
                  >
                    {isLoading ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Icon className={`h-3.5 w-3.5 ${isExpanded ? 'text-teal-600 dark:text-teal-400' : meta.color}`} />
                    )}
                    {meta.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* ── Error ──────────────────────────────── */}
          {sectionError && (
            <p className="text-xs text-red-500 dark:text-red-400">
              {sectionError}
            </p>
          )}

          {/* ── Expanded Sections Content ──────────── */}
          {Object.entries(expandedSections).map(([section, data]) => (
            <ExpandedSectionView
              key={section}
              data={data}
              onClose={() => {
                const next = { ...expandedSections }
                delete next[section]
                setExpandedSections(next)
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
