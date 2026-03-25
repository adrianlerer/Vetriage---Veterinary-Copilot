import { useState } from 'react'
import { ChevronDown, ChevronUp, Award, TestTube, Pill } from 'lucide-react'
import type { DifferentialDiagnosis } from '../../types'

interface Props {
  differentials: DifferentialDiagnosis[]
}

function probColor(p: number) {
  if (p >= 70) return { bar: 'bg-emerald-500', text: 'text-emerald-700 dark:text-emerald-400' }
  if (p >= 40) return { bar: 'bg-amber-500', text: 'text-amber-700 dark:text-amber-400' }
  return { bar: 'bg-red-500', text: 'text-red-700 dark:text-red-400' }
}

function GradeBadge({ score }: { score: string }) {
  const colorMap: Record<string, string> = {
    A: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
    B: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
    C: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
    D: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
  }
  const letter = score.charAt(0).toUpperCase()
  const cls = colorMap[letter] ?? 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-bold ${cls}`}
      title={`GRADE: ${score}`}
    >
      <Award className="h-3 w-3" />
      {score}
    </span>
  )
}

export function DifferentialList({ differentials }: Props) {
  const [expanded, setExpanded] = useState<Set<number>>(new Set())

  const toggle = (i: number) =>
    setExpanded((prev) => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })

  if (differentials.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-gray-500 dark:text-gray-400">
        No se encontraron diagnosticos diferenciales.
      </p>
    )
  }

  return (
    <ol className="space-y-3">
      {differentials.map((dx, i) => {
        const open = expanded.has(i)
        const colors = probColor(dx.probability)

        return (
          <li
            key={i}
            className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800/60"
          >
            {/* Header */}
            <button
              onClick={() => toggle(i)}
              className="flex w-full items-center gap-4 px-5 py-4 text-left"
            >
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-bold text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                {i + 1}
              </span>

              <div className="min-w-0 flex-1">
                <div className="mb-1.5 flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {dx.diagnosis}
                  </span>
                  <GradeBadge score={dx.gradeScore} />
                </div>

                {/* Probability bar */}
                <div className="flex items-center gap-3">
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
                    <div
                      className={`h-full rounded-full transition-all ${colors.bar}`}
                      style={{ width: `${Math.min(dx.probability, 100)}%` }}
                    />
                  </div>
                  <span className={`text-xs font-semibold tabular-nums ${colors.text}`}>
                    {dx.probability}%
                  </span>
                </div>
              </div>

              {open ? (
                <ChevronUp className="h-5 w-5 shrink-0 text-gray-400" />
              ) : (
                <ChevronDown className="h-5 w-5 shrink-0 text-gray-400" />
              )}
            </button>

            {/* Expanded details */}
            {open && (
              <div className="border-t border-gray-100 bg-gray-50/60 px-5 py-4 dark:border-gray-700 dark:bg-gray-900/30">
                {/* Razonamiento */}
                <p className="mb-4 text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                  {dx.reasoning}
                </p>

                {/* Hallazgos clave */}
                {dx.keyFindings.length > 0 && (
                  <div className="mb-3">
                    <h4 className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      Hallazgos clave
                    </h4>
                    <ul className="space-y-1">
                      {dx.keyFindings.map((f, fi) => (
                        <li
                          key={fi}
                          className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300"
                        >
                          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-500" />
                          {f}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Pruebas sugeridas */}
                {dx.suggestedTests.length > 0 && (
                  <div className="mb-3">
                    <h4 className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      <TestTube className="h-3.5 w-3.5" />
                      Pruebas sugeridas
                    </h4>
                    <ul className="space-y-1">
                      {dx.suggestedTests.map((t, ti) => (
                        <li
                          key={ti}
                          className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300"
                        >
                          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500" />
                          {t}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Tratamiento */}
                {dx.treatment && (
                  <div>
                    <h4 className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      <Pill className="h-3.5 w-3.5" />
                      Tratamiento
                    </h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {dx.treatment}
                    </p>
                  </div>
                )}
              </div>
            )}
          </li>
        )
      })}
    </ol>
  )
}
