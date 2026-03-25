import React from 'react';
import type { VitalSigns } from '../../types';

interface VitalsFormProps {
  values: VitalSigns;
  onChange: (v: VitalSigns) => void;
}

const VitalsForm: React.FC<VitalsFormProps> = ({ values, onChange }) => {
  const update = (field: keyof VitalSigns, raw: string) => {
    const numericFields: (keyof VitalSigns)[] = [
      'temperature',
      'heartRate',
      'respiratoryRate',
      'weight',
      'bodyConditionScore',
      'capillaryRefillTime',
    ];

    if (numericFields.includes(field)) {
      const num = raw === '' ? undefined : parseFloat(raw);
      onChange({ ...values, [field]: num });
    } else {
      onChange({ ...values, [field]: raw || undefined });
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Signos vitales
      </label>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {/* Temperatura */}
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            Temperatura (&deg;C)
          </label>
          <input
            type="number"
            step="0.1"
            className="input-field w-full"
            placeholder="38.5"
            value={values.temperature ?? ''}
            onChange={(e) => update('temperature', e.target.value)}
          />
        </div>

        {/* Frecuencia card\u00EDaca */}
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            FC (lpm)
          </label>
          <input
            type="number"
            className="input-field w-full"
            placeholder="80"
            value={values.heartRate ?? ''}
            onChange={(e) => update('heartRate', e.target.value)}
          />
        </div>

        {/* Frecuencia respiratoria */}
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            FR (rpm)
          </label>
          <input
            type="number"
            className="input-field w-full"
            placeholder="20"
            value={values.respiratoryRate ?? ''}
            onChange={(e) => update('respiratoryRate', e.target.value)}
          />
        </div>

        {/* Peso */}
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            Peso (kg)
          </label>
          <input
            type="number"
            step="0.1"
            className="input-field w-full"
            placeholder="10.0"
            value={values.weight ?? ''}
            onChange={(e) => update('weight', e.target.value)}
          />
        </div>

        {/* Condici\u00F3n corporal */}
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            CC (1-9)
          </label>
          <input
            type="number"
            min="1"
            max="9"
            className="input-field w-full"
            placeholder="5"
            value={values.bodyConditionScore ?? ''}
            onChange={(e) => update('bodyConditionScore', e.target.value)}
          />
        </div>

        {/* Mucosas */}
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            Mucosas
          </label>
          <select
            className="input-field w-full"
            value={values.mucousMembranes ?? ''}
            onChange={(e) => update('mucousMembranes', e.target.value)}
          >
            <option value="">Seleccionar...</option>
            <option value="Rosadas">Rosadas</option>
            <option value="P\u00E1lidas">P\u00E1lidas</option>
            <option value="Ict\u00E9ricas">Ict\u00E9ricas</option>
            <option value="Cian\u00F3ticas">Cian\u00F3ticas</option>
            <option value="Hiperémicas">Hiper\u00E9micas</option>
            <option value="Secas">Secas</option>
          </select>
        </div>

        {/* TRC */}
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            TRC (seg)
          </label>
          <input
            type="number"
            step="0.5"
            className="input-field w-full"
            placeholder="2"
            value={values.capillaryRefillTime ?? ''}
            onChange={(e) => update('capillaryRefillTime', e.target.value)}
          />
        </div>

        {/* Estado de hidrataci\u00F3n */}
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            Estado hidrataci&oacute;n
          </label>
          <select
            className="input-field w-full"
            value={values.hydrationStatus ?? ''}
            onChange={(e) => update('hydrationStatus', e.target.value)}
          >
            <option value="">Seleccionar...</option>
            <option value="Normal">Normal</option>
            <option value="Deshidratación leve (3-5%)">Deshidrataci\u00F3n leve (3-5%)</option>
            <option value="Deshidratación moderada (6-8%)">Deshidrataci\u00F3n moderada (6-8%)</option>
            <option value="Deshidratación severa (>8%)">Deshidrataci\u00F3n severa (&gt;8%)</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default VitalsForm;
