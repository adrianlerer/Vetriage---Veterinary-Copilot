import { Link } from 'react-router-dom'
import {
  Stethoscope,
  Search,
  ShieldCheck,
  BookOpen,
  FileText,
  WifiOff,
  Brain,
  ArrowRight,
  CheckCircle2,
  ExternalLink,
  Database,
  FlaskConical,
} from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'Diagnóstico basado en evidencia',
    description:
      'Consulta en tiempo real contra +35 millones de papers de PubMed/NCBI. Cada sugerencia viene respaldada por literatura científica verificable.',
  },
  {
    icon: ShieldCheck,
    title: 'Seguridad farmacológica',
    description:
      'Alertas automáticas de contraindicaciones y dosis por especie. Reducción del riesgo de errores de medicación.',
  },
  {
    icon: Search,
    title: 'Búsqueda de literatura científica',
    description:
      'Incluyendo preprints de bioRxiv/medRxiv, con citas en formato APA, Vancouver, JAVMA o Nature.',
  },
  {
    icon: FileText,
    title: 'Reportes clínicos',
    description:
      'Generación de informes SOAP exportables a PDF. Documentación profesional en segundos.',
  },
  {
    icon: WifiOff,
    title: 'Funciona offline',
    description:
      'Es una PWA instalable en celular, tablet o PC. Seguí trabajando aunque no tengas conexión.',
  },
  {
    icon: Database,
    title: 'RAG sobre bases científicas reales',
    description:
      'Backend con Retrieval-Augmented Generation sobre Claude, conectado a bases científicas reales. No alucina: cada respuesta viene con referencias verificables.',
  },
]

const techHighlights = [
  'PubMed / NCBI: +35M papers',
  'bioRxiv / medRxiv preprints',
  'Citas APA, Vancouver, JAVMA, Nature',
  'Informes SOAP exportables a PDF',
  'PWA instalable multiplataforma',
  'RAG + Claude AI',
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-brand-950">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-white/5 bg-slate-900/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600 shadow-lg shadow-brand-600/30">
              <Stethoscope className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">Vetriage</span>
          </div>
          <Link
            to="/app"
            className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/25 transition-all hover:bg-brand-500 hover:shadow-brand-500/40"
          >
            Probar ahora <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-20 pt-16 sm:pt-24">
        {/* Background glow */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-brand-600/10 blur-[120px]" />
          <div className="absolute -bottom-20 right-0 h-[400px] w-[400px] rounded-full bg-brand-500/5 blur-[100px]" />
        </div>

        <div className="relative mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-brand-500/20 bg-brand-500/10 px-4 py-1.5 text-sm text-brand-300">
            <FlaskConical className="h-3.5 w-3.5" />
            Copiloto veterinario con IA
          </div>
          <h1 className="mb-6 text-4xl font-extrabold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl">
            Diagnóstico veterinario
            <br />
            <span className="bg-gradient-to-r from-brand-400 to-brand-300 bg-clip-text text-transparent">
              basado en evidencia
            </span>
          </h1>
          <p className="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-slate-400">
            Plataforma web que asiste al veterinario clínico con acceso en tiempo real a +35 millones
            de papers científicos. Cada respuesta incluye referencias verificables.
          </p>
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link
              to="/app"
              className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-4 text-base font-semibold text-white shadow-xl shadow-brand-600/30 transition-all hover:bg-brand-500 hover:shadow-brand-500/40"
            >
              Probar Vetriage <ArrowRight className="h-5 w-5" />
            </Link>
            <a
              href="https://github.com/adrianlerer/Vetriage---Veterinary-Copilot"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/50 px-8 py-4 text-base font-semibold text-slate-300 transition-all hover:border-slate-600 hover:bg-slate-800 hover:text-white"
            >
              Ver en GitHub <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 text-center">
            <h2 className="mb-3 text-3xl font-bold text-white sm:text-4xl">
              Herramientas para el veterinario moderno
            </h2>
            <p className="mx-auto max-w-2xl text-slate-400">
              Desde el diagnóstico diferencial hasta el reporte clínico, todo respaldado por
              evidencia científica.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <div
                key={f.title}
                className="group rounded-2xl border border-slate-700/50 bg-slate-800/30 p-6 backdrop-blur-sm transition-all hover:border-brand-500/30 hover:bg-slate-800/60"
              >
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-brand-600/10 text-brand-400 transition-colors group-hover:bg-brand-600/20">
                  <f.icon className="h-6 w-6" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-white">{f.title}</h3>
                <p className="text-sm leading-relaxed text-slate-400">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech stack strip */}
      <section className="border-y border-slate-700/50 bg-slate-800/20 px-6 py-12">
        <div className="mx-auto max-w-6xl">
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
            {techHighlights.map((t) => (
              <div key={t} className="flex items-center gap-2 text-sm text-slate-400">
                <CheckCircle2 className="h-4 w-4 text-brand-500" />
                {t}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-12 text-center text-3xl font-bold text-white sm:text-4xl">
            Cómo funciona
          </h2>
          <div className="grid gap-8 sm:grid-cols-3">
            {[
              {
                step: '01',
                title: 'Ingresá el caso',
                desc: 'Especie, raza, síntomas, signos vitales, resultados de laboratorio.',
              },
              {
                step: '02',
                title: 'Análisis con IA',
                desc: 'El sistema consulta PubMed, bioRxiv y bases farmacológicas en tiempo real.',
              },
              {
                step: '03',
                title: 'Resultado verificable',
                desc: 'Diagnóstico diferencial con referencias, alertas de seguridad y reporte SOAP.',
              },
            ].map((s) => (
              <div key={s.step} className="text-center">
                <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-brand-500/30 bg-brand-500/10 text-xl font-bold text-brand-400">
                  {s.step}
                </div>
                <h3 className="mb-2 text-lg font-semibold text-white">{s.title}</h3>
                <p className="text-sm text-slate-400">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 pb-20 pt-8">
        <div className="mx-auto max-w-3xl rounded-2xl border border-brand-500/20 bg-gradient-to-br from-brand-600/10 to-brand-500/5 p-10 text-center backdrop-blur-sm sm:p-14">
          <BookOpen className="mx-auto mb-4 h-10 w-10 text-brand-400" />
          <h2 className="mb-3 text-2xl font-bold text-white sm:text-3xl">
            Probá Vetriage ahora
          </h2>
          <p className="mx-auto mb-8 max-w-lg text-slate-400">
            Sin registro. Sin costo. Accedé al copiloto veterinario y consultá la base científica
            más grande del mundo.
          </p>
          <Link
            to="/app"
            className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-4 text-base font-semibold text-white shadow-xl shadow-brand-600/30 transition-all hover:bg-brand-500 hover:shadow-brand-500/40"
          >
            Ir al Copiloto <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 px-6 py-8">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Stethoscope className="h-4 w-4" />
            Vetriage — Copiloto Veterinario con IA
          </div>
          <div className="flex items-center gap-6 text-sm text-slate-500">
            <a
              href="https://github.com/adrianlerer/Vetriage---Veterinary-Copilot"
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-slate-300"
            >
              GitHub
            </a>
            <span>IntegridAI</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
