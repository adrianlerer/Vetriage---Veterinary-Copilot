/**
 * Vercel Serverless Function: /api/expand
 * 
 * Recibe un diagnóstico + sección wiki y genera contenido expandido.
 * Estilo Karpathy: profundidad técnica, evidencia, dosis precisas.
 */

import type { VercelRequest, VercelResponse } from '@vercel/node'

// ── Types ─────────────────────────────────────────────────

interface ExpandRequest {
  diagnosis: string
  section: string  // fisiopatologia | diagnostico | tratamiento | pronostico | epidemiologia | ...
  species: string
  breed?: string
  context?: string  // resumen del caso original para dar contexto
}

// ── LLM Config (shared logic with diagnose.ts) ───────────

interface LLMConfig {
  url: string
  key: string
  provider: 'openrouter' | 'groq' | 'google'
  models?: string[]
  model?: string
}

function getLLMConfig(): LLMConfig | null {
  if (process.env.OPENROUTER_API_KEY) {
    return {
      url: 'https://openrouter.ai/api/v1/chat/completions',
      key: process.env.OPENROUTER_API_KEY,
      models: [
        'qwen/qwen3-next-80b-a3b-instruct:free',
        'google/gemma-4-31b-it:free',
        'nvidia/nemotron-3-super-120b-a12b:free',
        'meta-llama/llama-3.3-70b-instruct:free',
        'nousresearch/hermes-3-llama-3.1-405b:free',
        'openai/gpt-oss-120b:free',
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
  return null
}

// ── Section Prompts ───────────────────────────────────────

const SECTION_PROMPTS: Record<string, string> = {
  fisiopatologia: `Explicá la FISIOPATOLOGÍA de "{diagnosis}" en {species}.
Incluí:
- Mecanismo patogénico paso a paso
- Factores predisponentes por especie/raza
- Patogenia molecular/celular cuando aplique
- Progresión natural de la enfermedad sin tratamiento
Extensión: 300-500 palabras. Terminología veterinaria precisa.`,

  diagnostico: `Detallá el ABORDAJE DIAGNÓSTICO para "{diagnosis}" en {species}.
Incluí:
- Exámenes de laboratorio prioritarios (hemograma, bioquímica, urianálisis)
- Estudios de imagen recomendados
- Tests específicos/gold standard
- Diagnósticos diferenciales a descartar
- Sensibilidad y especificidad de los tests clave cuando se conozcan
Extensión: 300-500 palabras.`,

  tratamiento: `Detallá el PROTOCOLO DE TRATAMIENTO para "{diagnosis}" en {species}.
Incluí:
- Fármacos con DOSIS EXACTAS (mg/kg), vía de administración y frecuencia
- Duración del tratamiento
- Tratamiento de soporte
- Contraindicaciones por especie/raza
- Alternativas terapéuticas si hay resistencia o intolerancia
- Monitoreo durante tratamiento
Extensión: 300-500 palabras. Sé ESPECÍFICO con las dosis.`,

  pronostico: `Detallá el PRONÓSTICO de "{diagnosis}" en {species}.
Incluí:
- Pronóstico con tratamiento vs. sin tratamiento
- Factores que afectan el pronóstico (edad, severidad, comorbilidades)
- Tasa de supervivencia/recuperación cuando se conozca
- Secuelas posibles
- Criterios de eutanasia humanitaria si aplica
- Plan de seguimiento recomendado
Extensión: 200-400 palabras.`,

  epidemiologia: `Detallá la EPIDEMIOLOGÍA de "{diagnosis}" en {species}.
Incluí:
- Prevalencia e incidencia
- Distribución geográfica (con foco en Sudamérica/Argentina si aplica)
- Factores de riesgo poblacionales
- Estacionalidad
- Potencial zoonótico
Extensión: 200-400 palabras.`,
}

const DEFAULT_SECTION_PROMPT = `Proporcioná información detallada y basada en evidencia sobre la sección "{section}" de "{diagnosis}" en {species}. Extensión: 200-400 palabras. Terminología veterinaria precisa.`

// ── System Prompt ─────────────────────────────────────────

const EXPAND_SYSTEM = `Sos un especialista veterinario con acceso a la base de conocimiento más actualizada. Respondés con rigor científico, citando evidencia cuando es posible.

REGLAS:
- Respondé SIEMPRE en español.
- Usá terminología médica veterinaria precisa.
- Sé ESPECÍFICO: dosis en mg/kg, vías, frecuencias, duraciones.
- Cuando cites evidencia, mencioná autor/año o guía clínica.
- Considerá contraindicaciones por especie y raza.

Respondé EXCLUSIVAMENTE con JSON válido (sin markdown, sin backticks):

{
  "title": "Título de la sección",
  "content": "Contenido completo en texto plano con párrafos separados por \\n\\n",
  "keyPoints": ["Punto clave 1", "Punto clave 2", "Punto clave 3"],
  "references": ["Referencia o guía clínica 1", "Referencia 2"],
  "relatedSections": ["seccion_relacionada_1", "seccion_relacionada_2"]
}`

// ── LLM Call ──────────────────────────────────────────────

async function callLLM(config: LLMConfig, userMessage: string): Promise<string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${config.key}`,
  }
  if (config.provider === 'openrouter') {
    headers['HTTP-Referer'] = 'https://vetriage.vercel.app'
    headers['X-Title'] = 'VetrIAge Veterinary Copilot'
  }

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
          { role: 'system', content: EXPAND_SYSTEM },
          { role: 'user', content: userMessage },
        ],
        temperature: 0.3,
        max_tokens: 2048,
        response_format: { type: 'json_object' },
      }),
    })

    if (res.ok) {
      const data = await res.json()
      console.log(`Expand generated using model: ${model}`)
      return data.choices?.[0]?.message?.content || ''
    }

    if (res.status === 429 || res.status === 503) {
      console.log(`Model ${model} rate limited (${res.status}), trying next...`)
      continue
    }

    const err = await res.text()
    throw new Error(`LLM API error ${res.status}: ${err}`)
  }

  throw new Error('Todos los modelos están temporalmente ocupados.')
}

// ── Robust JSON Repair ────────────────────────────────────

function repairJSON(raw: string): any {
  let s = raw.trim()
  if (s.startsWith('```')) {
    s = s.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '')
  }
  const firstBrace = s.indexOf('{')
  if (firstBrace === -1) throw new Error('No JSON found')
  s = s.substring(firstBrace)
  s = s.replace(/,\s*([\]\}])/g, '$1')
  s = s.replace(/(["'])\s*\n\s*(["'])/g, '$1 $2')

  try { return JSON.parse(s) } catch { /* repair */ }

  // Truncate to last safe position and close brackets
  let inString = false, escapeNext = false, lastSafePos = 0
  const stack: string[] = []
  for (let i = 0; i < s.length; i++) {
    const ch = s[i]
    if (escapeNext) { escapeNext = false; continue }
    if (ch === '\\' && inString) { escapeNext = true; continue }
    if (ch === '"' && !escapeNext) { inString = !inString; continue }
    if (inString) continue
    if (ch === '{') stack.push('}')
    else if (ch === '[') stack.push(']')
    else if (ch === '}' || ch === ']') { stack.pop(); lastSafePos = i + 1 }
    else if (ch === ',') { lastSafePos = i }
  }

  if (lastSafePos <= 1) throw new Error('Cannot repair JSON')

  let repaired = s.substring(0, lastSafePos).replace(/,\s*$/, '')
  // Re-scan for open brackets
  const openStack: string[] = []
  inString = false; escapeNext = false
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
  while (openStack.length > 0) repaired += openStack.pop()
  repaired = repaired.replace(/,\s*([\]\}])/g, '$1')

  return JSON.parse(repaired) // throws if still broken
}

function parseExpandResponse(raw: string): any {
  try {
    return repairJSON(raw)
  } catch {
    // Absolute fallback: return raw content
    return {
      title: 'Información expandida',
      content: raw.replace(/[{}"\[\]]/g, '').trim(),
      keyPoints: [],
      references: [],
      relatedSections: [],
    }
  }
}

// ── Handler ───────────────────────────────────────────────

export default async function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })

  const startTime = Date.now()

  try {
    const { diagnosis, section, species, breed, context }: ExpandRequest = req.body

    if (!diagnosis || !section || !species) {
      return res.status(400).json({ error: 'Se requiere diagnosis, section y species.' })
    }

    const config = getLLMConfig()
    if (!config) {
      return res.status(503).json({ error: 'No hay proveedor de IA configurado.' })
    }

    // Build the section-specific prompt
    const template = SECTION_PROMPTS[section] || DEFAULT_SECTION_PROMPT
    let prompt = template
      .replace(/\{diagnosis\}/g, diagnosis)
      .replace(/\{species\}/g, species)
      .replace(/\{section\}/g, section)

    if (breed) prompt += `\nRaza: ${breed}.`
    if (context) prompt += `\n\nContexto del caso original:\n${context}`

    const rawResponse = await callLLM(config, prompt)
    const parsed = parseExpandResponse(rawResponse)

    return res.status(200).json({
      ...parsed,
      diagnosis,
      section,
      processingTime: Date.now() - startTime,
    })
  } catch (err) {
    console.error('Expand error:', err)
    const message = err instanceof Error ? err.message : 'Error interno'
    return res.status(500).json({ error: `Error al expandir: ${message}` })
  }
}
