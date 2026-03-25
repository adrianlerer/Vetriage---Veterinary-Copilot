import { useState } from 'react'
import { BookOpen, Search, ExternalLink, Loader2 } from 'lucide-react'
import { api } from '../api/client'

interface Paper {
  title: string
  authors: string
  journal: string
  year: number
  pmid?: string
  doi?: string
}

export default function Literature() {
  const [query, setQuery] = useState('')
  const [papers, setPapers] = useState<Paper[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    try {
      const res = await api.searchLiterature(query)
      setPapers(res.papers || [])
    } catch {
      setPapers([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <BookOpen className="w-6 h-6 text-brand-600" />
        <div>
          <h1 className="text-xl font-bold">Búsqueda de Literatura</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Buscá en PubMed y bioRxiv literatura veterinaria relevante
          </p>
        </div>
      </div>

      <div className="glass-card p-6 mb-6">
        <div className="flex gap-3">
          <input
            type="text"
            className="input-field flex-1"
            placeholder="Ej: pancreatitis felina diagnóstico ecográfico"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} disabled={loading || !query.trim()} className="btn-primary">
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            Buscar
          </button>
        </div>
      </div>

      {loading && (
        <div className="text-center py-12">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-brand-500 mb-3" />
          <p className="text-slate-500">Buscando en bases de datos científicas...</p>
        </div>
      )}

      {!loading && searched && papers.length === 0 && (
        <div className="text-center py-12 text-slate-400">
          <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p>No se encontraron resultados para esta búsqueda.</p>
        </div>
      )}

      {!loading && papers.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-slate-500 mb-2">{papers.length} resultados encontrados</p>
          {papers.map((p, i) => (
            <div key={i} className="glass-card p-5 hover:shadow-lg transition-shadow">
              <h3 className="font-semibold text-slate-900 dark:text-white mb-1">{p.title}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-300">{p.authors}</p>
              <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                <span className="font-medium">{p.journal}</span>
                <span>({p.year})</span>
                {p.pmid && (
                  <a
                    href={`https://pubmed.ncbi.nlm.nih.gov/${p.pmid}/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-brand-600 hover:text-brand-700"
                  >
                    PMID: {p.pmid} <ExternalLink className="w-3 h-3" />
                  </a>
                )}
                {p.doi && (
                  <a
                    href={`https://doi.org/${p.doi}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-brand-600 hover:text-brand-700"
                  >
                    DOI <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
