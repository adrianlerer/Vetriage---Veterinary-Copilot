import { ExternalLink, FileText, FlaskConical } from 'lucide-react'
import type { CitedPaper } from '../../types'

interface Props {
  papers: CitedPaper[]
}

export function EvidencePanel({ papers }: Props) {
  if (papers.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-gray-500 dark:text-gray-400">
        No se encontraron referencias bibliograficas.
      </p>
    )
  }

  return (
    <ul className="space-y-3">
      {papers.map((paper, i) => {
        const pubmedUrl = paper.pmid
          ? `https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/`
          : null
        const link = pubmedUrl ?? paper.url ?? (paper.doi ? `https://doi.org/${paper.doi}` : null)

        return (
          <li
            key={i}
            className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800/60"
          >
            <div className="flex items-start gap-3">
              <FileText className="mt-0.5 h-5 w-5 shrink-0 text-teal-500" />

              <div className="min-w-0 flex-1">
                {/* Titulo */}
                <h4 className="mb-1 text-sm font-semibold leading-snug text-gray-900 dark:text-white">
                  {paper.title}
                </h4>

                {/* Autores & revista */}
                <p className="mb-2 text-xs text-gray-500 dark:text-gray-400">
                  {paper.authors}
                  {paper.journal && (
                    <>
                      {' '}
                      &mdash;{' '}
                      <span className="italic">{paper.journal}</span>
                    </>
                  )}
                  {paper.year > 0 && ` (${paper.year})`}
                </p>

                {/* Badges */}
                <div className="flex flex-wrap items-center gap-2">
                  {paper.isPreprint && (
                    <span className="inline-flex items-center gap-1 rounded-md bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-800 dark:bg-purple-900/40 dark:text-purple-300">
                      <FlaskConical className="h-3 w-3" />
                      Preprint
                    </span>
                  )}

                  {paper.pmid && (
                    <a
                      href={pubmedUrl!}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 rounded-md bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 hover:underline dark:bg-blue-900/40 dark:text-blue-300"
                    >
                      PMID: {paper.pmid}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}

                  {!paper.pmid && paper.doi && (
                    <a
                      href={`https://doi.org/${paper.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700 hover:underline dark:bg-gray-700 dark:text-gray-300"
                    >
                      DOI
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}

                  {link && !paper.pmid && !paper.doi && (
                    <a
                      href={link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-teal-600 hover:underline dark:text-teal-400"
                    >
                      Ver fuente
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>

                {/* Relevance bar */}
                {paper.relevanceScore != null && paper.relevanceScore > 0 && (
                  <div className="mt-3 flex items-center gap-2">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      Relevancia
                    </span>
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
                      <div
                        className="h-full rounded-full bg-teal-500"
                        style={{
                          width: `${Math.min(paper.relevanceScore * 100, 100)}%`,
                        }}
                      />
                    </div>
                    <span className="text-xs font-medium tabular-nums text-gray-600 dark:text-gray-300">
                      {Math.round(paper.relevanceScore * 100)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
