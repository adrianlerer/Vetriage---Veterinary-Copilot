import {
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  Info,
  AlertOctagon,
  ArrowRight,
} from 'lucide-react'
import type { SafetyAlert } from '../../types'

interface Props {
  alerts: SafetyAlert[]
}

const severityOrder: Record<SafetyAlert['severity'], number> = {
  CRITICAL: 0,
  HIGH: 1,
  MEDIUM: 2,
  LOW: 3,
  INFO: 4,
}

const severityConfig: Record<
  SafetyAlert['severity'],
  {
    border: string
    bg: string
    icon: React.ReactNode
    badge: string
    label: string
  }
> = {
  CRITICAL: {
    border: 'border-red-500',
    bg: 'bg-red-50 dark:bg-red-950/30',
    icon: <AlertOctagon className="h-5 w-5 text-red-600 dark:text-red-400" />,
    badge: 'bg-red-600 text-white',
    label: 'CRITICO',
  },
  HIGH: {
    border: 'border-orange-500',
    bg: 'bg-orange-50 dark:bg-orange-950/30',
    icon: <ShieldAlert className="h-5 w-5 text-orange-600 dark:text-orange-400" />,
    badge: 'bg-orange-500 text-white',
    label: 'ALTO',
  },
  MEDIUM: {
    border: 'border-amber-500',
    bg: 'bg-amber-50 dark:bg-amber-950/30',
    icon: <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />,
    badge: 'bg-amber-500 text-white',
    label: 'MEDIO',
  },
  LOW: {
    border: 'border-blue-400',
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    icon: <ShieldCheck className="h-5 w-5 text-blue-500 dark:text-blue-400" />,
    badge: 'bg-blue-500 text-white',
    label: 'BAJO',
  },
  INFO: {
    border: 'border-gray-300 dark:border-gray-600',
    bg: 'bg-gray-50 dark:bg-gray-800/40',
    icon: <Info className="h-5 w-5 text-gray-500 dark:text-gray-400" />,
    badge: 'bg-gray-500 text-white',
    label: 'INFO',
  },
}

export function SafetyAlerts({ alerts }: Props) {
  const sorted = [...alerts].sort(
    (a, b) => severityOrder[a.severity] - severityOrder[b.severity]
  )

  if (sorted.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-12 text-gray-400 dark:text-gray-500">
        <ShieldCheck className="h-10 w-10" />
        <p className="text-sm">No se detectaron alertas de seguridad.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {sorted.map((alert, i) => {
        const cfg = severityConfig[alert.severity]
        const isCritical = alert.severity === 'CRITICAL'

        return (
          <div
            key={i}
            className={`rounded-xl border-l-4 ${cfg.border} ${cfg.bg} p-4 shadow-sm ${
              isCritical ? 'animate-pulse-subtle' : ''
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5 shrink-0">{cfg.icon}</div>

              <div className="min-w-0 flex-1">
                <div className="mb-1 flex flex-wrap items-center gap-2">
                  <span
                    className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-bold uppercase leading-none ${cfg.badge}`}
                  >
                    {cfg.label}
                  </span>
                  {alert.category && (
                    <span className="text-[10px] font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      {alert.category}
                    </span>
                  )}
                </div>

                <h4 className="mb-1 text-sm font-semibold text-gray-900 dark:text-white">
                  {alert.title}
                </h4>

                <p className="mb-2 text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                  {alert.description}
                </p>

                {alert.action && (
                  <div className="flex items-center gap-1.5 text-xs font-medium text-teal-700 dark:text-teal-400">
                    <ArrowRight className="h-3.5 w-3.5" />
                    <span>{alert.action}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )
      })}

      {/* Inline CSS for subtle pulse animation */}
      <style>{`
        @keyframes pulse-subtle {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.85; }
        }
        .animate-pulse-subtle {
          animation: pulse-subtle 2.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  )
}
