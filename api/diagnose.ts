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
  oneLiner: string
  keyFindings: string[]
  wikiSections: string[]
  // Legacy fields (kept for backward compat with expand)
  reasoning?: string
  suggestedTests?: string[]
  treatment?: string
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
        'qwen/qwen3-next-80b-a3b-instruct:free',    // Qwen 3 Next 80B — top reasoning, 262K ctx
        'google/gemma-4-31b-it:free',                // Gemma 4 31B — newest Google
        'nvidia/nemotron-3-super-120b-a12b:free',    // Nemotron 120B
        'meta-llama/llama-3.3-70b-instruct:free',    // Llama 3.3 70B — fast & reliable
        'nousresearch/hermes-3-llama-3.1-405b:free', // Hermes 405B
        'openai/gpt-oss-120b:free',                  // GPT-OSS 120B
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

const SYSTEM_PROMPT = `Sos un copiloto veterinario basado en evidencia. Generás diagnósticos diferenciales CONCISOS estilo overview/wiki para veterinarios profesionales.

RESPONDÉ EN ESPAÑOL. Terminología médica veterinaria precisa.

Formato de respuesta: JSON válido (sin markdown, sin backticks). Estructura:

{
  "summary": "Resumen ejecutivo del caso en 2-3 oraciones.",
  "differentials": [
    {
      "diagnosis": "Nombre",
      "probability": 45,
      "gradeScore": "B",
      "oneLiner": "Descripción en UNA oración de por qué este dx es compatible.",
      "keyFindings": ["Hallazgo 1", "Hallazgo 2"],
      "wikiSections": ["fisiopatologia", "diagnostico", "tratamiento", "pronostico"]
    }
  ],
  "safetyAlerts": [
    {
      "severity": "HIGH",
      "category": "Seguridad",
      "title": "Título",
      "description": "Breve",
      "action": "Acción"
    }
  ],
  "treatmentPlan": {
    "diagnosticPlan": ["Paso 1"],
    "treatmentPlan": ["Paso 1"],
    "monitoring": ["Param 1"],
    "followUp": "Seguimiento",
    "prognosis": "Pronóstico"
  }
}

REGLAS CRÍTICAS:
1. Máximo 3 diagnósticos diferenciales. Probabilidades suman ~100%.
2. Cada diferencial lleva un "oneLiner" (1 oración) y "wikiSections" (array de secciones disponibles para expandir).
3. NO incluir razonamientos extensos ni tratamientos detallados — eso se pide después via /expand.
4. keyFindings: máximo 3 items por diferencial.
5. gradeScore: solo la letra (A/B/C/D).
6. Alertas de seguridad: solo CRITICAL y HIGH. MDR1 (Collie, Border Collie, Australian Shepherd) → alertar ivermectina. NUNCA paracetamol en gatos.
7. treatmentPlan: máximo 3 items por array.
8. Si hay adjuntos mencionados, indicar que requieren evaluación profesional.
9. Respuesta total: MÁXIMO 800 tokens. Sé telegráfico.`

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
        max_tokens: 1500,
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

// ── Robust JSON Repair ────────────────────────────────────

/**
 * Repara JSON truncado o malformado del LLM.
 * Estrategia: limpiar → intentar parse → si falla, truncar en último
 * valor completo y cerrar todos los brackets abiertos.
 */
function repairJSON(raw: string): any {
  // Step 1: Clean wrappers
  let s = raw.trim()
  if (s.startsWith('```')) {
    s = s.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '')
  }

  // Step 2: Extract outermost { ... } (may be incomplete)
  const firstBrace = s.indexOf('{')
  if (firstBrace === -1) throw new Error('No se encontró JSON en la respuesta')
  s = s.substring(firstBrace)

  // Step 3: Fix common issues
  s = s.replace(/,\s*([\]\}])/g, '$1')          // trailing commas
  s = s.replace(/(["'])\s*\n\s*(["'])/g, '$1 $2') // broken strings

  // Step 4: Try direct parse
  try { return JSON.parse(s) } catch { /* continue to repair */ }

  // Step 5: Truncate to last complete value, then close open brackets
  // Walk the string tracking depth and string state
  const stack: string[] = []  // tracks open brackets: '{' or '['
  let inString = false
  let escapeNext = false
  let lastSafePos = 0  // position after last complete key:value or array element

  for (let i = 0; i < s.length; i++) {
    const ch = s[i]
    if (escapeNext) { escapeNext = false; continue }
    if (ch === '\\' && inString) { escapeNext = true; continue }
    if (ch === '"' && !escapeNext) {
      inString = !inString
      continue
    }
    if (inString) continue

    if (ch === '{') stack.push('}')
    else if (ch === '[') stack.push(']')
    else if (ch === '}' || ch === ']') {
      stack.pop()
      // After closing a bracket at any depth, this is a safe cut point
      lastSafePos = i + 1
    } else if (ch === ',') {
      // Comma between elements — safe to cut right before this comma
      lastSafePos = i
    }
  }

  // If we're inside a string, try to close it by finding last quote
  if (inString) {
    // Backtrack to find the opening quote of the incomplete string
    const lastQuote = s.lastIndexOf('"', s.length - 1)
    if (lastQuote > 0) {
      // Find the position before this incomplete string value started
      // Look backwards for : (object value) or , or [ (array element)
      let cutPos = lastQuote
      for (let j = lastQuote - 1; j >= 0; j--) {
        if (s[j] === ':' || s[j] === ',' || s[j] === '[') {
          cutPos = j
          break
        }
      }
      // If we hit a colon, we need to go back to before the key too
      if (s[cutPos] === ':') {
        // Go back past the key
        for (let j = cutPos - 1; j >= 0; j--) {
          if (s[j] === ',' || s[j] === '{') {
            cutPos = s[j] === ',' ? j : j + 1
            break
          }
        }
      }
      lastSafePos = cutPos
    }
  }

  if (lastSafePos <= 1) {
    throw new Error('No se pudo recuperar JSON truncado')
  }

  // Cut at safe position
  let repaired = s.substring(0, lastSafePos)
  // Remove any trailing comma
  repaired = repaired.replace(/,\s*$/, '')

  // Re-scan to determine what brackets are still open
  const openStack: string[] = []
  inString = false
  escapeNext = false
  for (let i = 0; i < repaired.length; i++) {
    const ch = repaired[i]
    if (escapeNext) { escapeNext = false; continue }
    if (ch === '\\' && inString) { escapeNext = true; continue }
    if (ch === '"' && !escapeNext) { inString = !inString; continue }
    if (inString) continue
    if (ch === '{') openStack.push('}')
    else if (ch === '[') openStack.push(']')
    else if (ch === '}' || ch === ']') openStack.pop()
  }

  // Close all open brackets
  while (openStack.length > 0) {
    repaired += openStack.pop()
  }

  // Final cleanup and parse
  repaired = repaired.replace(/,\s*([\]\}])/g, '$1')

  try {
    return JSON.parse(repaired)
  } catch (e2) {
    // Last resort: try even more aggressive truncation
    // Find the last complete object in differentials array
    const diffMatch = repaired.match(/"differentials"\s*:\s*\[([\s\S]*)/)
    if (diffMatch) {
      // Find all complete objects in the array
      const arrayContent = diffMatch[1]
      const objects: string[] = []
      let depth = 0, start = -1
      let inStr = false, esc = false
      for (let i = 0; i < arrayContent.length; i++) {
        const c = arrayContent[i]
        if (esc) { esc = false; continue }
        if (c === '\\' && inStr) { esc = true; continue }
        if (c === '"' && !esc) { inStr = !inStr; continue }
        if (inStr) continue
        if (c === '{') { if (depth === 0) start = i; depth++ }
        if (c === '}') { depth--; if (depth === 0 && start >= 0) { objects.push(arrayContent.substring(start, i + 1)); start = -1 } }
      }
      if (objects.length > 0) {
        // Build minimal valid response
        return {
          differentials: objects.map(o => { try { return JSON.parse(o) } catch { return null } }).filter(Boolean),
          summary: 'Diagnóstico parcial (respuesta truncada del modelo).',
          treatmentPlan: {},
          safetyAlerts: [],
        }
      }
    }
    throw new Error(`No se pudo reparar JSON del modelo de IA: ${(e2 as Error).message}`)
  }
}

// ── Parse LLM Response ────────────────────────────────────

function parseLLMResponse(raw: string): Partial<DiagnosisResult> {
  const parsed = repairJSON(raw)

  // Validate and normalize differentials
  const differentials: DifferentialDiagnosis[] = (parsed.differentials || []).slice(0, 3).map((d: any) => ({
    diagnosis: d.diagnosis || 'Diagnóstico no especificado',
    probability: typeof d.probability === 'number' ? d.probability : 20,
    gradeScore: d.gradeScore || d.grade_score || 'D',
    oneLiner: d.oneLiner || d.one_liner || d.reasoning || '',
    keyFindings: (Array.isArray(d.keyFindings || d.key_findings) ? (d.keyFindings || d.key_findings) : []).slice(0, 3),
    wikiSections: Array.isArray(d.wikiSections || d.wiki_sections) ? (d.wikiSections || d.wiki_sections) : ['fisiopatologia', 'diagnostico', 'tratamiento', 'pronostico'],
    // Legacy compat
    reasoning: d.reasoning || d.oneLiner || '',
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
