import {
  SearchCheck,
  Pill,
  HeartPulse,
  CalendarClock,
  TrendingUp,
} from 'lucide-react'
import type { TreatmentPlan as TreatmentPlanType } from '../../types'

interface Props {
  plan: TreatmentPlanType
}

interface SectionProps {
  icon: React.ReactNode
  title: string
  items?: string[]
  text?: string
}

function Section({ icon, title, items, text }: SectionProps) {
  const hasContent = (items && items.length > 0) || (text && text.trim().length > 0)
  if (!hasContent) return null

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800/60">
      <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-900 dark:text-white">
        {icon}
        {title}
      </h3>

      {items && items.length > 0 && (
        <ul className="space-y-2">
          {items.map((item, i) => (
            <li
              key={i}
              className="flex items-start gap-2 text-sm leading-relaxed text-gray-700 dark:text-gray-300"
            >
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-500" />
              {item}
            </li>
          ))}
        </ul>
      )}

      {text && text.trim().length > 0 && (
        <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
          {text}
        </p>
      )}
    </div>
  )
}

export function TreatmentPlan({ plan }: Props) {
  return (
    <div className="space-y-4">
      <Section
        icon={<SearchCheck className="h-4 w-4 text-blue-500" />}
        title="Plan Diagnostico"
        items={plan.diagnosticPlan}
      />

      <Section
        icon={<Pill className="h-4 w-4 text-emerald-500" />}
        title="Plan Terapeutico"
        items={plan.treatmentPlan}
      />

      <Section
        icon={<HeartPulse className="h-4 w-4 text-rose-500" />}
        title="Monitoreo"
        items={plan.monitoring}
      />

      <Section
        icon={<CalendarClock className="h-4 w-4 text-amber-500" />}
        title="Seguimiento"
        text={plan.followUp}
      />

      <Section
        icon={<TrendingUp className="h-4 w-4 text-violet-500" />}
        title="Pronostico"
        text={plan.prognosis}
      />
    </div>
  )
}
