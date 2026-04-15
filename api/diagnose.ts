/**
 * Vercel Serverless Function: /api/diagnose
 * 
 * Recibe un caso clínico veterinario y genera diagnóstico
 * diferencial usando LLM (Groq / OpenRouter / Google Gemini).
 * 
 * La API key se mantiene segura del lado del servidor.
 */

import type { VercelRequest, VercelResponse } from '@vercel/node'

// ── Types ─────────────────────────────────────────────────

interface ClinicalCaseInput {
  species: string
  breed?: string
  age?: string
  sex?: string
  weight?: number
  patientName?: string
  chiefComplaint: string
  symptoms?: string[]
  duration?: string
  history?: string
  vitalSigns?: Record<string, unknown>
  labResults?: Array<{ name: string; value: string; unit: string; referenceRange?: string; abnormal?: boolean }>
  currentMedications?: string[]
  physicalExam?: string
  attachments?: Array<{ name: string; type: string; category: string; size: number }>
}

interface DifferentialDiagnosis {
  diagnosis: string
  probability: number
  gradeScore: string
  reasoning: string
  keyFindings: string[]
  suggestedTests: string[]
  treatment: string
}

interface SafetyAlert {
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'
  category: string
  title: string
  description: string
  action: string
}

interface DiagnosisResult {
  id: string
  caseId: string
  differentials: DifferentialDiagnosis[]
  treatmentPlan: {
    diagnosticPlan: string[]
    treatmentPlan: string[]
    monitoring: string[]
    followUp: string
    prognosis: string
  }
  citedPapers: Array<{
    title: string
    authors: string
    journal: string
    year: number
    pmid?: string
    url?: string
  }>
  safetyAlerts: SafetyAlert[]
  summary: string
  timestamp: string
  processingTime: number
}

// ── LLM Provider Configuration ────────────────────────────

interface LLMConfig {
  url: string
  key: string
  provider: 'openrouter' | 'groq' | 'google'
  model?: string
  models?: string[]
}

function getLLMConfig(): LLMConfig | null {
  // Try providers in order of preference
  if (process.env.OPENROUTER_API_KEY) {
    return {
      url: 'https://openrouter.ai/api/v1/chat/completions',
      key: process.env.OPENROUTER_API_KEY,
      // Models to try in order of preference (fallback on rate limit)
      models: [
        'meta-llama/llama-3.3-70b-instruct:free',   // Fast & reliable
        'google/gemma-4-31b-it:free',               // Gemma 4 — newest Google
        'nvidia/nemotron-3-super-120b-a12b:free',    // Nemotron 120B
        'nousresearch/hermes-3-llama-3.1-405b:free', // 405B params
        'openai/gpt-oss-120b:free',                  // OpenAI open source
      ],
      provider: 'openrouter',
    }
  }
  if (process.env.GROQ_API_KEY) {
    return {
      url: 'https://api.groq.com/openai/v1/chat/completions',
      key: process.env.GROQ_API_KEY,
      model: 'llama-3.3-70b-versatile',
      provider: 'groq',
    }
  }
  if (process.env.GOOGLE_AI_KEY) {
    return {
      url: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${process.env.GOOGLE_AI_KEY}`,
      key: process.env.GOOGLE_AI_KEY,
      model: 'gemini-2.0-flash',
      provider: 'google',
    }
  }
  return null
}

// ── System Prompt ─────────────────────────────────────────

const SYSTEM_PROMPT = `Sos un sistema de diagnóstico veterinario basado en evidencia, diseñado para asistir a médicos veterinarios profesionales. Tu función es analizar casos clínicos y generar diagnósticos diferenciales con rigor científico.

IMPORTANTE:
- Respondé SIEMPRE en español.
- Usá terminología médica veterinaria precisa.
- Basá tus diagnósticos en evidencia científica actual.
- Incluí siempre el disclaimer de que es una herramienta de apoyo, no reemplaza el juicio clínico.
- Sé específico con dosis, vías de administración y frecuencias.
- Considerá siempre las contraindicaciones por especie y raza.

Respondé EXCLUSIVAMENTE con un JSON válido (sin markdown, sin backticks, sin texto adicional) con esta estructura exacta:

{
  "differentials": [
    {
      "diagnosis": "Nombre del diagnóstico",
      "probability": 45,
      "gradeScore": "B – Evidencia moderada basada en signos clínicos",
      "reasoning": "Explicación detallada de por qué este diagnóstico es compatible con los hallazgos...",
      "keyFindings": ["Hallazgo clave 1", "Hallazgo clave 2"],
      "suggestedTests": ["Test diagnóstico 1", "Test diagnóstico 2"],
      "treatment": "Protocolo de tratamiento detallado con dosis específicas..."
    }
  ],
  "treatmentPlan": {
    "diagnosticPlan": ["Plan diagnóstico paso 1", "Paso 2"],
    "treatmentPlan": ["Tratamiento paso 1", "Paso 2"],
    "monitoring": ["Parámetro a monitorear 1", "Parámetro 2"],
    "followUp": "Plan de seguimiento...",
    "prognosis": "Pronóstico general..."
  },
  "safetyAlerts": [
    {
      "severity": "HIGH",
      "category": "Seguridad Farmacológica",
      "title": "Título de la alerta",
      "description": "Descripción detallada...",
      "action": "Acción recomendada..."
    }
  ],
  "summary": "Resumen ejecutivo del caso y hallazgos principales..."
}

Reglas:
1. Generá entre 2 y 5 diagnósticos diferenciales, ordenados por probabilidad.
2. Las probabilidades deben sumar ~100%.
3. Incluí alertas de seguridad cuando aplique (interacciones, contraindicaciones por especie/raza).
4. Para razas con mutación MDR1 (Collie, Border Collie, Australian Shepherd, Shetland), SIEMPRE alertar sobre ivermectina.
5. NUNCA recomendar paracetamol/acetaminofén en gatos.
6. Incluí grados de evidencia (A=fuerte, B=moderada, C=débil, D=opinión experta).
7. El gradeScore debe incluir la letra y una breve justificación.
8. Si hay archivos adjuntos mencionados, indicar que deben ser evaluados por el profesional.`

// ── Build User Message ────────────────────────────────────

function buildUserMessage(c: ClinicalCaseInput): string {
  const speciesNames: Record<string, string> = {
    dog: 'Canino', cat: 'Felino', horse: 'Equino',
    bird: 'Ave', exotic: 'Exótico', cattle: 'Bovino',
  }

  let msg = `CASO CLÍNICO VETERINARIO\n\n`
  msg += `Especie: ${speciesNames[c.species] || c.species}\n`
  if (c.breed) msg += `Raza: ${c.breed}\n`
  if (c.age) msg += `Edad: ${c.age}\n`
  if (c.sex) msg += `Sexo: ${c.sex}\n`
  if (c.weight) msg += `Peso: ${c.weight} kg\n`
  if (c.patientName) msg += `Paciente: ${c.patientName}\n`

  msg += `\nMotivo de consulta: ${c.chiefComplaint}\n`

  if (c.symptoms && c.symptoms.length > 0) {
    msg += `Síntomas: ${c.symptoms.join(', ')}\n`
  }
  if (c.duration) msg += `Duración: ${c.duration}\n`

  if (c.vitalSigns && Object.keys(c.vitalSigns).length > 0) {
    msg += `\nSignos vitales:\n`
    for (const [key, val] of Object.entries(c.vitalSigns)) {
      if (val != null && val !== '' && val !== 0) {
        const labels: Record<string, string> = {
          temperature: 'Temperatura', heartRate: 'FC', respiratoryRate: 'FR',
          weight: 'Peso', bodyConditionScore: 'CC', mucousMembranes: 'Mucosas',
          capillaryRefillTime: 'TRC', hydrationStatus: 'Hidratación',
        }
        msg += `  ${labels[key] || key}: ${val}\n`
      }
    }
  }

  if (c.physicalExam) msg += `\nExamen físico: ${c.physicalExam}\n`

  if (c.labResults && c.labResults.length > 0) {
    msg += `\nResultados de laboratorio:\n`
    for (const lab of c.labResults) {
      msg += `  ${lab.name}: ${lab.value} ${lab.unit}`
      if (lab.referenceRange) msg += ` (ref: ${lab.referenceRange})`
      if (lab.abnormal) msg += ` ⚠️`
      msg += '\n'
    }
  }

  if (c.currentMedications && c.currentMedications.length > 0) {
    msg += `\nMedicación actual: ${c.currentMedications.join(', ')}\n`
  }

  if (c.history) msg += `\nHistorial médico: ${c.history}\n`

  if (c.attachments && c.attachments.length > 0) {
    msg += `\nArchivos adjuntos:\n`
    for (const a of c.attachments) {
      msg += `  - ${a.category}: ${a.name} (${(a.size / 1024).toFixed(0)} KB)\n`
    }
  }

  msg += `\nGenerá el diagnóstico diferencial completo para este caso.`
  return msg
}

// ── LLM Call ──────────────────────────────────────────────

async function callLLM(config: LLMConfig, userMessage: string): Promise<string> {
  if (config.provider === 'google') {
    // Google Gemini has a different API format
    const res = await fetch(config.url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [
          { role: 'user', parts: [{ text: SYSTEM_PROMPT + '\n\n' + userMessage }] }
        ],
        generationConfig: {
          temperature: 0.3,
          maxOutputTokens: 4096,
          responseMimeType: 'application/json',
        },
      }),
    })
    if (!res.ok) {
      const err = await res.text()
      throw new Error(`Google API error ${res.status}: ${err}`)
    }
    const data = await res.json()
    return data.candidates?.[0]?.content?.parts?.[0]?.text || ''
  }

  // OpenAI-compatible (Groq, OpenRouter)
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${config.key}`,
  }
  if (config.provider === 'openrouter') {
    headers['HTTP-Referer'] = 'https://vetriage.vercel.app'
    headers['X-Title'] = 'VetrIAge Veterinary Copilot'
  }

  // For OpenRouter: try multiple models with fallback on rate limit
  const modelsToTry = config.models && config.models.length > 0
    ? config.models
    : config.model
      ? [config.model]
      : ['meta-llama/llama-3.3-70b-instruct:free']

  for (const model of modelsToTry) {
    const res = await fetch(config.url, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        model,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: userMessage },
        ],
        temperature: 0.3,
        max_tokens: 4096,
        response_format: { type: 'json_object' },
      }),
    })

    if (res.ok) {
      const data = await res.json()
      console.log(`Diagnosis generated using model: ${model}`)
      return data.choices?.[0]?.message?.content || ''
    }

    // If rate limited (429) or unavailable (503), try next model
    if (res.status === 429 || res.status === 503) {
      console.log(`Model ${model} rate limited (${res.status}), trying next...`)
      continue
    }

    // Other errors: throw immediately
    const err = await res.text()
    throw new Error(`LLM API error ${res.status}: ${err}`)
  }

  throw new Error('Todos los modelos de IA están temporalmente ocupados. Intente de nuevo en unos segundos.')
}

// ── Parse LLM Response ────────────────────────────────────

function parseLLMResponse(raw: string): Partial<DiagnosisResult> {
  // Clean potential markdown wrappers
  let cleaned = raw.trim()
  if (cleaned.startsWith('```')) {
    cleaned = cleaned.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '')
  }

  const parsed = JSON.parse(cleaned)

  // Validate and normalize differentials
  const differentials: DifferentialDiagnosis[] = (parsed.differentials || []).map((d: any) => ({
    diagnosis: d.diagnosis || 'Diagnóstico no especificado',
    probability: typeof d.probability === 'number' ? d.probability : 20,
    gradeScore: d.gradeScore || d.grade_score || 'D – Sin clasificar',
    reasoning: d.reasoning || '',
    keyFindings: Array.isArray(d.keyFindings || d.key_findings) ? (d.keyFindings || d.key_findings) : [],
    suggestedTests: Array.isArray(d.suggestedTests || d.suggested_tests) ? (d.suggestedTests || d.suggested_tests) : [],
    treatment: d.treatment || '',
  }))

  const tp = parsed.treatmentPlan || parsed.treatment_plan || {}
  const treatmentPlan = {
    diagnosticPlan: Array.isArray(tp.diagnosticPlan || tp.diagnostic_plan) ? (tp.diagnosticPlan || tp.diagnostic_plan) : [],
    treatmentPlan: Array.isArray(tp.treatmentPlan || tp.treatment_plan) ? (tp.treatmentPlan || tp.treatment_plan) : [],
    monitoring: Array.isArray(tp.monitoring) ? tp.monitoring : [],
    followUp: tp.followUp || tp.follow_up || 'Reevaluación en 7-10 días.',
    prognosis: tp.prognosis || 'Pronóstico pendiente de estudios complementarios.',
  }

  const safetyAlerts: SafetyAlert[] = (parsed.safetyAlerts || parsed.safety_alerts || []).map((a: any) => ({
    severity: (['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'].includes(a.severity) ? a.severity : 'MEDIUM') as SafetyAlert['severity'],
    category: a.category || 'Alerta Clínica',
    title: a.title || '',
    description: a.description || '',
    action: a.action || '',
  }))

  return {
    differentials,
    treatmentPlan,
    safetyAlerts,
    summary: parsed.summary || '',
  }
}

// ── Handler ───────────────────────────────────────────────

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const startTime = Date.now()

  try {
    const clinicalCase: ClinicalCaseInput = req.body
    if (!clinicalCase?.chiefComplaint || !clinicalCase?.species) {
      return res.status(400).json({ error: 'Se requiere especie y motivo de consulta.' })
    }

    const config = getLLMConfig()
    if (!config) {
      return res.status(503).json({
        error: 'No hay proveedor de IA configurado. Configure GROQ_API_KEY, GOOGLE_AI_KEY, o OPENROUTER_API_KEY.',
      })
    }

    // Build message and call LLM
    const userMessage = buildUserMessage(clinicalCase)
    const rawResponse = await callLLM(config, userMessage)

    // Parse structured response
    const parsed = parseLLMResponse(rawResponse)

    const result: DiagnosisResult = {
      id: `diag_${Date.now()}`,
      caseId: `case_${Date.now()}`,
      differentials: parsed.differentials || [],
      treatmentPlan: parsed.treatmentPlan || {
        diagnosticPlan: [], treatmentPlan: [], monitoring: [],
        followUp: '', prognosis: '',
      },
      citedPapers: [], // Papers are fetched client-side from PubMed
      safetyAlerts: parsed.safetyAlerts || [],
      summary: (parsed.summary || 'Diagnóstico generado.') +
        '\n\n⚕️ Este análisis fue generado por inteligencia artificial y es orientativo. No reemplaza el juicio clínico profesional.',
      timestamp: new Date().toISOString(),
      processingTime: Date.now() - startTime,
    }

    return res.status(200).json(result)
  } catch (err) {
    console.error('Diagnosis error:', err)
    const message = err instanceof Error ? err.message : 'Error interno'
    return res.status(500).json({ error: `Error al generar diagnóstico: ${message}` })
  }
}
