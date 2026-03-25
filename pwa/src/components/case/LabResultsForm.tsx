import React from 'react';
import type { LabResult } from '../../types';

interface LabResultsFormProps {
  results: LabResult[];
  onChange: (r: LabResult[]) => void;
}

const emptyRow = (): LabResult => ({
  name: '',
  value: '',
  unit: '',
  referenceRange: '',
});

const LabResultsForm: React.FC<LabResultsFormProps> = ({ results, onChange }) => {
  const updateRow = (index: number, field: keyof LabResult, val: string) => {
    const updated = results.map((r, i) =>
      i === index ? { ...r, [field]: val } : r
    );
    onChange(updated);
  };

  const addRow = () => {
    onChange([...results, emptyRow()]);
  };

  const removeRow = (index: number) => {
    onChange(results.filter((_, i) => i !== index));
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Resultados de laboratorio
      </label>

      {results.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                <th className="pb-2 pr-2 font-medium">Nombre</th>
                <th className="pb-2 pr-2 font-medium">Valor</th>
                <th className="pb-2 pr-2 font-medium">Unidad</th>
                <th className="pb-2 pr-2 font-medium">Rango referencia</th>
                <th className="pb-2 w-10"></th>
              </tr>
            </thead>
            <tbody>
              {results.map((row, idx) => (
                <tr key={idx} className="border-b border-gray-100 dark:border-gray-800">
                  <td className="py-2 pr-2">
                    <input
                      type="text"
                      className="input-field w-full"
                      placeholder="Ej: ALT"
                      value={row.name}
                      onChange={(e) => updateRow(idx, 'name', e.target.value)}
                    />
                  </td>
                  <td className="py-2 pr-2">
                    <input
                      type="text"
                      className="input-field w-full"
                      placeholder="120"
                      value={row.value}
                      onChange={(e) => updateRow(idx, 'value', e.target.value)}
                    />
                  </td>
                  <td className="py-2 pr-2">
                    <input
                      type="text"
                      className="input-field w-full"
                      placeholder="U/L"
                      value={row.unit}
                      onChange={(e) => updateRow(idx, 'unit', e.target.value)}
                    />
                  </td>
                  <td className="py-2 pr-2">
                    <input
                      type="text"
                      className="input-field w-full"
                      placeholder="10-120"
                      value={row.referenceRange ?? ''}
                      onChange={(e) => updateRow(idx, 'referenceRange', e.target.value)}
                    />
                  </td>
                  <td className="py-2 text-center">
                    <button
                      type="button"
                      onClick={() => removeRow(idx)}
                      className="text-red-400 hover:text-red-600 transition-colors p-1"
                      aria-label="Eliminar fila"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {results.length === 0 && (
        <p className="text-sm text-gray-400 dark:text-gray-500 mb-3">
          No se han agregado resultados de laboratorio a&uacute;n.
        </p>
      )}

      <button type="button" onClick={addRow} className="btn-secondary mt-3 text-sm">
        + Agregar resultado
      </button>
    </div>
  );
};

export default LabResultsForm;
