import { useStore } from '../store/useStore'
import type { ClinicalCase, DiagnosisResult } from '../types'

function getApiUrl(): string {
  return useStore.getState().settings.apiUrl
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${getApiUrl()}${path}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`Error ${res.status}: ${body || res.statusText}`)
  }
  return res.json()
}

// ── API Endpoints ────────────────────────────────────────────

export const api = {
  healthCheck: () => request<{ status: string }>('/api/v2/health'),

  diagnose: (clinicalCase: ClinicalCase) =>
    request<DiagnosisResult>('/api/v2/diagnose', {
      method: 'POST',
      body: JSON.stringify({
        species: clinicalCase.species,
        breed: clinicalCase.breed,
        age: clinicalCase.age,
        sex: clinicalCase.sex,
        weight: clinicalCase.weight,
        patient_name: clinicalCase.patientName,
        chief_complaint: clinicalCase.chiefComplaint,
        symptoms: clinicalCase.symptoms,
        duration: clinicalCase.duration,
        history: clinicalCase.history,
        vital_signs: clinicalCase.vitalSigns,
        lab_results: clinicalCase.labResults,
        current_medications: clinicalCase.currentMedications,
        physical_exam: clinicalCase.physicalExam,
      }),
    }),

  safetyCheck: (data: {
    species: string
    breed: string
    medications: string[]
    age?: string
    weight?: number
  }) =>
    request<{ alerts: Array<{ severity: string; title: string; description: string; action: string }> }>(
      '/api/v2/safety-check',
      { method: 'POST', body: JSON.stringify(data) }
    ),

  searchLiterature: (query: string) =>
    request<{ papers: Array<{ title: string; authors: string; journal: string; year: number; pmid?: string; doi?: string }> }>(
      '/api/v2/search-literature',
      { method: 'POST', body: JSON.stringify({ query }) }
    ),

  searchPubmed: (query: string) =>
    request<{ results: unknown[] }>('/api/v2/search-pubmed', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),

  getSpeciesInfo: (species: string) =>
    request<Record<string, unknown>>(`/api/v2/species-info/${species}`),
}
