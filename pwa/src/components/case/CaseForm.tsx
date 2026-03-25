import React, { useState } from 'react';
import type { Species, VitalSigns, LabResult, ClinicalCase } from '../../types';
import SpeciesSelector from './SpeciesSelector';
import SymptomInput from './SymptomInput';
import VitalsForm from './VitalsForm';
import LabResultsForm from './LabResultsForm';
import { FileUpload, type UploadedFile } from './FileUpload';

interface CaseFormProps {
  onSubmit: (c: ClinicalCase) => void;
  isLoading?: boolean;
}

const TOTAL_STEPS = 6;

const stepLabels = [
  'Paciente',
  'Síntomas',
  'Examen',
  'Laboratorio',
  'Archivos',
  'Historial',
];

const CaseForm: React.FC<CaseFormProps> = ({ onSubmit, isLoading = false }) => {
  const [step, setStep] = useState(1);

  // Step 1
  const [species, setSpecies] = useState<Species>('dog');
  const [patientName, setPatientName] = useState('');
  const [breed, setBreed] = useState('');
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('');

  // Step 2
  const [chiefComplaint, setChiefComplaint] = useState('');
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [duration, setDuration] = useState('');

  // Step 3
  const [vitalSigns, setVitalSigns] = useState<VitalSigns>({});
  const [physicalExam, setPhysicalExam] = useState('');

  // Step 4
  const [labResults, setLabResults] = useState<LabResult[]>([]);

  // Step 5 - Archivos
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  // Step 6
  const [currentMedications, setCurrentMedications] = useState<string[]>([]);
  const [history, setHistory] = useState('');

  const next = () => setStep((s) => Math.min(s + 1, TOTAL_STEPS));
  const prev = () => setStep((s) => Math.max(s - 1, 1));

  const handleSubmit = () => {
    const clinicalCase: ClinicalCase = {
      species,
      patientName,
      breed,
      age,
      sex,
      weight: vitalSigns.weight ?? 0,
      chiefComplaint,
      symptoms,
      duration,
      history,
      vitalSigns,
      labResults,
      currentMedications,
      physicalExam,
    };
    onSubmit(clinicalCase);
  };

  /* ── Step indicator ── */
  const StepIndicator = () => (
    <div className="mb-8">
      {/* Progress bar */}
      <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-4">
        <div
          className="absolute inset-y-0 left-0 bg-brand-600 rounded-full transition-all duration-300"
          style={{ width: `${((step - 1) / (TOTAL_STEPS - 1)) * 100}%` }}
        />
      </div>

      {/* Step dots + labels */}
      <div className="flex justify-between">
        {stepLabels.map((label, idx) => {
          const stepNum = idx + 1;
          const isActive = step === stepNum;
          const isCompleted = step > stepNum;
          return (
            <button
              key={label}
              type="button"
              onClick={() => setStep(stepNum)}
              className="flex flex-col items-center gap-1 group"
            >
              <span
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all
                  ${
                    isActive
                      ? 'bg-brand-600 text-white'
                      : isCompleted
                        ? 'bg-brand-200 dark:bg-brand-800 text-brand-700 dark:text-brand-300'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                  }
                `}
              >
                {isCompleted ? '\u2713' : stepNum}
              </span>
              <span
                className={`text-xs hidden sm:block ${
                  isActive
                    ? 'text-brand-700 dark:text-brand-300 font-medium'
                    : 'text-gray-500 dark:text-gray-400'
                }`}
              >
                {label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (step === TOTAL_STEPS) handleSubmit();
        else next();
      }}
      className="space-y-6"
    >
      <StepIndicator />

      {/* ── Step 1: Paciente ── */}
      {step === 1 && (
        <div className="space-y-5">
          <SpeciesSelector value={species} onChange={setSpecies} />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nombre del paciente
              </label>
              <input
                type="text"
                className="input-field w-full"
                placeholder="Ej: Max"
                value={patientName}
                onChange={(e) => setPatientName(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Raza
              </label>
              <input
                type="text"
                className="input-field w-full"
                placeholder="Ej: Labrador Retriever"
                value={breed}
                onChange={(e) => setBreed(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Edad
              </label>
              <input
                type="text"
                className="input-field w-full"
                placeholder="Ej: 5 años"
                value={age}
                onChange={(e) => setAge(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Sexo
              </label>
              <select
                className="input-field w-full"
                value={sex}
                onChange={(e) => setSex(e.target.value)}
              >
                <option value="">Seleccionar...</option>
                <option value="Macho entero">Macho entero</option>
                <option value="Macho castrado">Macho castrado</option>
                <option value="Hembra entera">Hembra entera</option>
                <option value="Hembra esterilizada">Hembra esterilizada</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* ── Step 2: S\u00EDntomas ── */}
      {step === 2 && (
        <div className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Motivo de consulta
            </label>
            <textarea
              className="input-field w-full min-h-[100px]"
              placeholder="Describa el motivo principal de la consulta..."
              value={chiefComplaint}
              onChange={(e) => setChiefComplaint(e.target.value)}
            />
          </div>

          <SymptomInput symptoms={symptoms} onChange={setSymptoms} />

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Duraci&oacute;n de los s&iacute;ntomas
            </label>
            <input
              type="text"
              className="input-field w-full"
              placeholder="Ej: 3 d\u00EDas"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
            />
          </div>
        </div>
      )}

      {/* ── Step 3: Examen ── */}
      {step === 3 && (
        <div className="space-y-5">
          <VitalsForm values={vitalSigns} onChange={setVitalSigns} />

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Examen f&iacute;sico
            </label>
            <textarea
              className="input-field w-full min-h-[120px]"
              placeholder="Hallazgos del examen f\u00EDsico..."
              value={physicalExam}
              onChange={(e) => setPhysicalExam(e.target.value)}
            />
          </div>
        </div>
      )}

      {/* ── Step 4: Laboratorio ── */}
      {step === 4 && (
        <div className="space-y-5">
          <LabResultsForm results={labResults} onChange={setLabResults} />
        </div>
      )}

      {/* ── Step 5: Archivos ── */}
      {step === 5 && (
        <div className="space-y-5">
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Archivos adjuntos
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              Subí radiografías, ecografías, fotos clínicas, análisis de laboratorio, ECG u otros estudios relevantes.
            </p>
            <FileUpload files={uploadedFiles} onChange={setUploadedFiles} />
          </div>
        </div>
      )}

      {/* ── Step 6: Historial ── */}
      {step === 6 && (
        <div className="space-y-5">
          <SymptomInput
            symptoms={currentMedications}
            onChange={setCurrentMedications}
            label="Medicaci\u00F3n actual"
            placeholder="Escribir medicamento..."
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Historial m&eacute;dico
            </label>
            <textarea
              className="input-field w-full min-h-[120px]"
              placeholder="Enfermedades previas, cirug\u00EDas, vacunas..."
              value={history}
              onChange={(e) => setHistory(e.target.value)}
            />
          </div>
        </div>
      )}

      {/* ── Navegaci\u00F3n ── */}
      <div className="flex justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
        {step > 1 ? (
          <button type="button" onClick={prev} className="btn-secondary">
            Anterior
          </button>
        ) : (
          <div />
        )}

        {step < TOTAL_STEPS ? (
          <button type="submit" className="btn-primary">
            Siguiente
          </button>
        ) : (
          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? 'Analizando...' : 'Enviar Diagn\u00F3stico'}
          </button>
        )}
      </div>
    </form>
  );
};

export default CaseForm;
