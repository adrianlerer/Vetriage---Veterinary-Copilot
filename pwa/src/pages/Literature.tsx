import { useState } from 'react'
import { BookOpen, Search, ExternalLink, Loader2, FlaskConical, FileText } from 'lucide-react'
import { searchLiterature, type Paper } from '../api/pubmed'

export default function Literature() {
  const [query, setQuery] = useState('')
  const [papers, setPapers] = useState<Paper[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    setError(null)
    try {
      const results = await searchLiterature(query, { maxResults: 20, includePreprints: true })
      setPapers(results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al buscar')
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
        <div className="flex items-center gap-4 mt-3 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <FileText className="w-3 h-3" /> PubMed/NCBI: +35M papers
          </span>
          <span className="flex items-center gap-1">
            <FlaskConical className="w-3 h-3" /> bioRxiv preprints
          </span>
        </div>
      </div>

      {loading && (
        <div className="text-center py-12">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-brand-500 mb-3" />
          <p className="text-slate-500">Buscando en bases de datos científicas...</p>
        </div>
      )}

      {error && (
        <div className="glass-card p-5 mb-4 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
          <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
        </div>
      )}

      {!loading && searched && papers.length === 0 && !error && (
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
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-semibold text-slate-900 dark:text-white mb-1 flex-1">{p.title}</h3>
                <span
                  className={`shrink-0 text-xs px-2 py-0.5 rounded-full font-medium ${
                    p.source === 'pubmed'
                      ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300'
                      : 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
                  }`}
                >
                  {p.source === 'pubmed' ? 'PubMed' : 'bioRxiv'}
                </span>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-300">{p.authors}</p>
              {p.abstract && (
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-3">
                  {p.abstract}
                </p>
              )}
              <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                <span className="font-medium">{p.journal}</span>
                {p.year > 0 && <span>({p.year})</span>}
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
