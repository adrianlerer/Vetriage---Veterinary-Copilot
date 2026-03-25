import { ShieldAlert } from 'lucide-react'
import { DrugChecker } from '../components/safety/DrugChecker'

export default function DrugSafety() {
  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <ShieldAlert className="w-6 h-6 text-brand-600" />
        <div>
          <h1 className="text-xl font-bold">Seguridad Farmacológica</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Verificá contraindicaciones e interacciones medicamentosas por especie
          </p>
        </div>
      </div>
      <DrugChecker />
    </div>
  )
}
