import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import type { DifferentialDiagnosis } from '../../types'

interface Props {
  differentials: DifferentialDiagnosis[]
}

function getBarColor(probability: number): string {
  if (probability >= 70) return '#10b981' // emerald-500
  if (probability >= 40) return '#f59e0b' // amber-500
  return '#ef4444' // red-500
}

export function ConfidenceChart({ differentials }: Props) {
  const data = differentials.map((dx) => ({
    name:
      dx.diagnosis.length > 28
        ? dx.diagnosis.slice(0, 25) + '...'
        : dx.diagnosis,
    fullName: dx.diagnosis,
    probability: dx.probability,
  }))

  if (data.length === 0) return null

  return (
    <ResponsiveContainer width="100%" height={Math.max(data.length * 48, 120)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 0, right: 24, bottom: 0, left: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} opacity={0.15} />
        <XAxis
          type="number"
          domain={[0, 100]}
          tickFormatter={(v: number) => `${v}%`}
          tick={{ fontSize: 11 }}
          stroke="#9ca3af"
        />
        <YAxis
          type="category"
          dataKey="name"
          width={160}
          tick={{ fontSize: 12 }}
          stroke="#9ca3af"
        />
        <Tooltip
          formatter={(value: number) => [`${value}%`, 'Probabilidad']}
          labelFormatter={(_label: string, payload: Array<{ payload?: { fullName?: string } }>) =>
            payload?.[0]?.payload?.fullName ?? _label
          }
          contentStyle={{
            borderRadius: '0.75rem',
            border: '1px solid #e5e7eb',
            fontSize: '0.8rem',
          }}
        />
        <Bar dataKey="probability" radius={[0, 6, 6, 0]} barSize={20}>
          {data.map((entry, index) => (
            <Cell key={index} fill={getBarColor(entry.probability)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
