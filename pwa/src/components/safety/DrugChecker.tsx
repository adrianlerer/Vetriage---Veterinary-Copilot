import { useState, useCallback } from 'react'
import { Pill, Plus, X, Search, Loader2 } from 'lucide-react'
import { api } from '../../api/client'
import type { Species, SafetyAlert } from '../../types'
import { SafetyAlerts } from './SafetyAlerts'

const speciesOptions: { value: Species; label: string }[] = [
  { value: 'dog', label: 'Perro' },
  { value: 'cat', label: 'Gato' },
  { value: 'horse', label: 'Caballo' },
  { value: 'bird', label: 'Ave' },
  { value: 'cattle', label: 'Bovino' },
  { value: 'exotic', label: 'Exotico' },
]

export function DrugChecker() {
  const [species, setSpecies] = useState<Species>('dog')
  const [breed, setBreed] = useState('')
  const [medications, setMedications] = useState<string[]>([])
  const [medInput, setMedInput] = useState('')
  const [alerts, setAlerts] = useState<SafetyAlert[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addMedication = useCallback(() => {
    const trimmed = medInput.trim()
    if (trimmed && !medications.includes(trimmed)) {
      setMedications((prev) => [...prev, trimmed])
      setMedInput('')
    }
  }, [medInput, medications])

  const removeMedication = (med: string) => {
    setMedications((prev) => prev.filter((m) => m !== med))
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addMedication()
    }
  }

  const handleCheck = async () => {
    if (medications.length === 0) return
    setLoading(true)
    setError(null)
    setAlerts(null)

    try {
      const res = await api.safetyCheck({
        species,
        breed,
        medications,
      })
      const mapped: SafetyAlert[] = res.alerts.map((a) => ({
        severity: (a.severity as SafetyAlert['severity']) ?? 'MEDIUM',
        category: 'Interaccion farmacologica',
        title: a.title,
        description: a.description,
        action: a.action,
      }))
      setAlerts(mapped)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-white/20 bg-white/10 p-6 shadow-lg backdrop-blur-md dark:border-white/10 dark:bg-white/5">
        <h2 className="mb-5 flex items-center gap-2 text-lg font-bold text-gray-900 dark:text-white">
          <Pill className="h-5 w-5 text-teal-500" />
          Verificador de Seguridad Farmacologica
        </h2>

        {/* Especie */}
        <div className="mb-4">
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Especie
          </label>
          <select
            value={species}
            onChange={(e) => setSpecies(e.target.value as Species)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
          >
            {speciesOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Raza */}
        <div className="mb-4">
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Raza
          </label>
          <input
            type="text"
            value={breed}
            onChange={(e) => setBreed(e.target.value)}
            placeholder="Ej. Labrador Retriever"
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500"
          />
        </div>

        {/* Medicamentos */}
        <div className="mb-5">
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Medicamentos
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={medInput}
              onChange={(e) => setMedInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Agregar medicamento..."
              className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500"
            />
            <button
              type="button"
              onClick={addMedication}
              disabled={!medInput.trim()}
              className="inline-flex items-center gap-1 rounded-lg bg-teal-600 px-3 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          {/* Chips */}
          {medications.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {medications.map((med) => (
                <span
                  key={med}
                  className="inline-flex items-center gap-1 rounded-full bg-teal-100 px-3 py-1 text-xs font-medium text-teal-800 dark:bg-teal-900/40 dark:text-teal-300"
                >
                  {med}
                  <button
                    type="button"
                    onClick={() => removeMedication(med)}
                    className="ml-0.5 rounded-full p-0.5 transition-colors hover:bg-teal-200 dark:hover:bg-teal-800"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Boton verificar */}
        <button
          type="button"
          onClick={handleCheck}
          disabled={loading || medications.length === 0}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-teal-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Search className="h-4 w-4" />
          )}
          {loading ? 'Verificando...' : 'Verificar Seguridad'}
        </button>

        {error && (
          <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
      </div>

      {/* Resultados */}
      {alerts !== null && (
        <div>
          <h3 className="mb-3 text-sm font-semibold text-gray-900 dark:text-white">
            Resultados ({alerts.length} alerta{alerts.length !== 1 ? 's' : ''})
          </h3>
          <SafetyAlerts alerts={alerts} />
        </div>
      )}
    </div>
  )
}
