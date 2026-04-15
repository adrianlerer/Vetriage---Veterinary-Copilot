/**
 * Client-side diagnosis orchestrator.
 * 
 * 1. Sends the clinical case to /api/diagnose (Vercel serverless → LLM)
 * 2. In parallel, searches PubMed for cited papers
 * 3. Merges both results into a complete DiagnosisResult
 */

import type { ClinicalCase, DiagnosisResult, CitedPaper } from '../types'
import { searchLiterature } from './pubmed'

// ── PubMed paper search ───────────────────────────────────

async function findCitedPapers(chiefComplaint: string, species: string, topDiagnosis?: string): Promise<CitedPaper[]> {
  const query = topDiagnosis
    ? `${topDiagnosis} ${species}`
    : `${chiefComplaint} ${species}`
  try {
    const results = await searchLiterature(query, { maxResults: 5, includePreprints: false })
    return results.map(r => ({
      pmid: r.pmid,
      title: r.title,
      authors: r.authors || 'Unknown',
      journal: r.journal || 'Unknown',
      year: r.year || new Date().getFullYear(),
      url: r.pmid ? `https://pubmed.ncbi.nlm.nih.gov/${r.pmid}/` : (r.doi ? `https://doi.org/${r.doi}` : undefined),
      relevanceScore: 0.8,
      isPreprint: r.source !== 'pubmed',
    }))
  } catch {
    return []
  }
}

// ── Main diagnosis function ───────────────────────────────

export async function diagnoseLocal(clinicalCase: ClinicalCase): Promise<DiagnosisResult> {
  // Start PubMed search in parallel with LLM call
  const papersPromise = findCitedPapers(clinicalCase.chiefComplaint, clinicalCase.species)

  // Call serverless function
  const res = await fetch('/api/diagnose', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      species: clinicalCase.species,
      breed: clinicalCase.breed,
      age: clinicalCase.age,
      sex: clinicalCase.sex,
      weight: clinicalCase.weight,
      patientName: clinicalCase.patientName,
      chiefComplaint: clinicalCase.chiefComplaint,
      symptoms: clinicalCase.symptoms,
      duration: clinicalCase.duration,
      history: clinicalCase.history,
      vitalSigns: clinicalCase.vitalSigns,
      labResults: clinicalCase.labResults,
      currentMedications: clinicalCase.currentMedications,
      physicalExam: clinicalCase.physicalExam,
      attachments: clinicalCase.attachments?.map(a => ({
        name: a.name,
        type: a.type,
        category: a.category,
        size: a.size,
        // Don't send dataUrl to backend (too large)
      })),
    }),
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }))
    throw new Error(body.error || `Error ${res.status}: ${res.statusText}`)
  }

  const diagnosis: DiagnosisResult = await res.json()

  // Wait for PubMed papers and merge
  const papers = await papersPromise

  // If the LLM returned a top diagnosis, search for more specific papers
  if (diagnosis.differentials?.[0]?.diagnosis) {
    try {
      const specificPapers = await findCitedPapers(
        clinicalCase.chiefComplaint,
        clinicalCase.species,
        diagnosis.differentials[0].diagnosis
      )
      // Merge, deduplicating by pmid
      const seenPmids = new Set(papers.map(p => p.pmid).filter(Boolean))
      for (const p of specificPapers) {
        if (p.pmid && !seenPmids.has(p.pmid)) {
          papers.push(p)
          seenPmids.add(p.pmid)
        }
      }
    } catch {
      // Ignore secondary search failures
    }
  }

  diagnosis.citedPapers = papers

  return diagnosis
}
