// ── Caso Clínico ──────────────────────────────────────────────

export type Species = 'dog' | 'cat' | 'horse' | 'bird' | 'exotic' | 'cattle'

export interface VitalSigns {
  temperature?: number
  heartRate?: number
  respiratoryRate?: number
  weight?: number
  bodyConditionScore?: number
  mucousMembranes?: string
  capillaryRefillTime?: number
  hydrationStatus?: string
}

export interface LabResult {
  name: string
  value: string
  unit: string
  referenceRange?: string
  abnormal?: boolean
}

export interface ClinicalCase {
  id?: string
  species: Species
  breed: string
  age: string
  sex: string
  weight: number
  patientName: string
  ownerName?: string
  chiefComplaint: string
  symptoms: string[]
  duration: string
  history: string
  vitalSigns: VitalSigns
  labResults: LabResult[]
  currentMedications: string[]
  physicalExam: string
  attachments?: { name: string; type: string; category: string; size: number; dataUrl?: string }[]
  createdAt?: string
}

// ── Diagnóstico ──────────────────────────────────────────────

export interface DifferentialDiagnosis {
  diagnosis: string
  probability: number
  gradeScore: string
  oneLiner: string
  keyFindings: string[]
  wikiSections: string[]
  // Legacy fields (backward compat)
  reasoning?: string
  suggestedTests?: string[]
  treatment?: string
}

export interface WikiExpandedSection {
  title: string
  content: string
  keyPoints: string[]
  references: string[]
  relatedSections: string[]
  diagnosis: string
  section: string
  processingTime: number
}

export interface CitedPaper {
  pmid?: string
  doi?: string
  title: string
  authors: string
  journal: string
  year: number
  relevanceScore?: number
  url?: string
  isPreprint?: boolean
}

export interface SafetyAlert {
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'
  category: string
  title: string
  description: string
  action: string
  references?: string[]
}

export interface TreatmentPlan {
  diagnosticPlan: string[]
  treatmentPlan: string[]
  monitoring: string[]
  followUp: string
  prognosis: string
}

export interface DiagnosisResult {
  id: string
  caseId: string
  differentials: DifferentialDiagnosis[]
  treatmentPlan: TreatmentPlan
  citedPapers: CitedPaper[]
  safetyAlerts: SafetyAlert[]
  summary: string
  timestamp: string
  processingTime?: number
}

// ── Store ────────────────────────────────────────────────────

export interface AppSettings {
  apiUrl: string
  darkMode: boolean
}

export interface AppState {
  settings: AppSettings
  currentCase: Partial<ClinicalCase> | null
  currentDiagnosis: DiagnosisResult | null
  caseHistory: { case: ClinicalCase; diagnosis: DiagnosisResult }[]
  isLoading: boolean
  error: string | null
  sidebarOpen: boolean

  setSettings: (s: Partial<AppSettings>) => void
  setCurrentCase: (c: Partial<ClinicalCase> | null) => void
  setCurrentDiagnosis: (d: DiagnosisResult | null) => void
  addToHistory: (c: ClinicalCase, d: DiagnosisResult) => void
  setLoading: (l: boolean) => void
  setError: (e: string | null) => void
  toggleSidebar: () => void
  toggleDarkMode: () => void
}
