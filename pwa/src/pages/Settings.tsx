import { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Server, Check, X, Loader2, Moon, Sun } from 'lucide-react'
import { useStore } from '../store/useStore'
import { api } from '../api/client'

export default function Settings() {
  const { settings, setSettings, toggleDarkMode } = useStore()
  const [apiUrl, setApiUrl] = useState(settings.apiUrl)
  const [status, setStatus] = useState<'idle' | 'checking' | 'ok' | 'error'>('idle')
  const [saved, setSaved] = useState(false)

  const checkConnection = async () => {
    setStatus('checking')
    try {
      setSettings({ apiUrl })
      await api.healthCheck()
      setStatus('ok')
    } catch {
      setStatus('error')
    }
  }

  const save = () => {
    setSettings({ apiUrl })
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  useEffect(() => {
    checkConnection()
  }, [])

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <SettingsIcon className="w-6 h-6 text-brand-600" />
        <h1 className="text-xl font-bold">Configuración</h1>
      </div>

      {/* API Connection */}
      <div className="glass-card p-6 mb-6">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <Server className="w-5 h-5 text-slate-500" />
          Conexión al Backend
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">URL del API</label>
            <div className="flex gap-3">
              <input
                type="text"
                className="input-field flex-1"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:8000"
              />
              <button onClick={checkConnection} className="btn-secondary" disabled={status === 'checking'}>
                {status === 'checking' ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  'Probar'
                )}
              </button>
            </div>
          </div>

          <div className="flex items-center gap-2 text-sm">
            {status === 'ok' && (
              <>
                <Check className="w-4 h-4 text-green-500" />
                <span className="text-green-600 dark:text-green-400">Conectado al backend</span>
              </>
            )}
            {status === 'error' && (
              <>
                <X className="w-4 h-4 text-red-500" />
                <span className="text-red-600 dark:text-red-400">
                  No se puede conectar. Verificá que el backend esté corriendo.
                </span>
              </>
            )}
          </div>

          <button onClick={save} className="btn-primary">
            {saved ? (
              <>
                <Check className="w-4 h-4" /> Guardado
              </>
            ) : (
              'Guardar Configuración'
            )}
          </button>
        </div>
      </div>

      {/* Appearance */}
      <div className="glass-card p-6 mb-6">
        <h2 className="font-semibold mb-4">Apariencia</h2>
        <button
          onClick={toggleDarkMode}
          className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-700 hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors w-full"
        >
          {settings.darkMode ? (
            <Moon className="w-5 h-5 text-indigo-400" />
          ) : (
            <Sun className="w-5 h-5 text-amber-500" />
          )}
          <div className="text-left">
            <p className="font-medium">Modo {settings.darkMode ? 'Oscuro' : 'Claro'}</p>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Tocá para cambiar a modo {settings.darkMode ? 'claro' : 'oscuro'}
            </p>
          </div>
        </button>
      </div>

      {/* About */}
      <div className="glass-card p-6">
        <h2 className="font-semibold mb-2">Acerca de Vetriage</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Versión 1.0.0 · Copiloto veterinario con IA basado en evidencia científica.
          Powered by RAG sobre +35M papers de PubMed, OpenRouter y búsqueda vectorial FAISS.
        </p>
      </div>
    </div>
  )
}
