/**
 * Direct PubMed E-utilities + bioRxiv API client
 * No backend required — queries NCBI and bioRxiv public APIs directly.
 *
 * NCBI E-utilities docs: https://www.ncbi.nlm.nih.gov/books/NBK25500/
 * bioRxiv API docs: https://api.biorxiv.org/
 */

export interface Paper {
  title: string
  authors: string
  journal: string
  year: number
  pmid?: string
  doi?: string
  abstract?: string
  source: 'pubmed' | 'biorxiv' | 'medrxiv'
}

const EUTILS_BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
const BIORXIV_API = 'https://api.biorxiv.org/details/biorxiv'

// ─── PubMed ──────────────────────────────────────────────

async function searchPubMedIds(query: string, maxResults = 20): Promise<string[]> {
  const veterinaryQuery = `(${query}) AND (veterinary OR animal OR canine OR feline OR equine OR bovine OR avian)`
  const params = new URLSearchParams({
    db: 'pubmed',
    term: veterinaryQuery,
    retmax: String(maxResults),
    sort: 'relevance',
    retmode: 'json',
  })

  const res = await fetch(`${EUTILS_BASE}/esearch.fcgi?${params}`)
  if (!res.ok) throw new Error(`PubMed search failed: ${res.status}`)
  const data = await res.json()
  return data?.esearchresult?.idlist ?? []
}

async function fetchPubMedPapers(pmids: string[]): Promise<Paper[]> {
  if (pmids.length === 0) return []

  const params = new URLSearchParams({
    db: 'pubmed',
    id: pmids.join(','),
    retmode: 'xml',
    rettype: 'abstract',
  })

  const res = await fetch(`${EUTILS_BASE}/efetch.fcgi?${params}`)
  if (!res.ok) throw new Error(`PubMed fetch failed: ${res.status}`)
  const xml = await res.text()

  return parsePubMedXml(xml)
}

function parsePubMedXml(xml: string): Paper[] {
  const parser = new DOMParser()
  const doc = parser.parseFromString(xml, 'text/xml')
  const articles = doc.querySelectorAll('PubmedArticle')
  const papers: Paper[] = []

  articles.forEach((article) => {
    const pmid = article.querySelector('PMID')?.textContent ?? ''
    const title = article.querySelector('ArticleTitle')?.textContent ?? 'Sin título'

    // Authors
    const authorNodes = article.querySelectorAll('Author')
    const authorNames: string[] = []
    authorNodes.forEach((a) => {
      const last = a.querySelector('LastName')?.textContent ?? ''
      const initials = a.querySelector('Initials')?.textContent ?? ''
      if (last) authorNames.push(`${last} ${initials}`.trim())
    })
    const authors = authorNames.length > 0 ? authorNames.join(', ') : 'Autores no disponibles'

    // Journal
    const journal = article.querySelector('Journal Title')?.textContent
      ?? article.querySelector('ISOAbbreviation')?.textContent
      ?? article.querySelector('MedlineTA')?.textContent
      ?? 'Journal desconocido'

    // Year
    const yearStr =
      article.querySelector('PubDate Year')?.textContent
      ?? article.querySelector('PubDate MedlineDate')?.textContent?.slice(0, 4)
      ?? '0'
    const year = parseInt(yearStr, 10) || 0

    // Abstract
    const abstractParts: string[] = []
    article.querySelectorAll('AbstractText').forEach((node) => {
      abstractParts.push(node.textContent ?? '')
    })
    const abstract = abstractParts.join(' ').trim()

    // DOI
    const doiNode = article.querySelector('ArticleId[IdType="doi"]')
    const doi = doiNode?.textContent ?? undefined

    papers.push({ title, authors, journal, year, pmid, doi, abstract, source: 'pubmed' })
  })

  return papers
}

// ─── bioRxiv ─────────────────────────────────────────────

async function searchBioRxiv(query: string, maxResults = 10): Promise<Paper[]> {
  // bioRxiv API: search recent preprints (last 90 days)
  const now = new Date()
  const from = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
  const fromStr = from.toISOString().slice(0, 10)
  const toStr = now.toISOString().slice(0, 10)

  try {
    const res = await fetch(
      `${BIORXIV_API}/${fromStr}/${toStr}/0/${maxResults}`,
      { signal: AbortSignal.timeout(8000) }
    )
    if (!res.ok) return []
    const data = await res.json()
    const collection: Paper[] = []

    const queryTerms = query.toLowerCase().split(/\s+/)
    for (const item of data?.collection ?? []) {
      const text = `${item.title} ${item.abstract ?? ''}`.toLowerCase()
      const isVet = /veterinar|animal|canine|feline|equine|bovine|avian|dog|cat|horse|cattle|poultry/.test(text)
      const matchesQuery = queryTerms.some((t) => text.includes(t))

      if (isVet && matchesQuery) {
        collection.push({
          title: item.title ?? 'Sin título',
          authors: item.authors ?? '',
          journal: 'bioRxiv (preprint)',
          year: parseInt(item.date?.slice(0, 4), 10) || now.getFullYear(),
          doi: item.doi,
          abstract: item.abstract?.slice(0, 500),
          source: 'biorxiv',
        })
      }
    }

    return collection
  } catch {
    // bioRxiv API can be slow or fail; don't block results
    return []
  }
}

// ─── Public API ──────────────────────────────────────────

export async function searchLiterature(
  query: string,
  options?: { maxResults?: number; includePreprints?: boolean }
): Promise<Paper[]> {
  const max = options?.maxResults ?? 20
  const includePreprints = options?.includePreprints ?? true

  const [pmids, preprints] = await Promise.all([
    searchPubMedIds(query, max),
    includePreprints ? searchBioRxiv(query) : Promise.resolve([]),
  ])

  const pubmedPapers = await fetchPubMedPapers(pmids)

  return [...pubmedPapers, ...preprints]
}
