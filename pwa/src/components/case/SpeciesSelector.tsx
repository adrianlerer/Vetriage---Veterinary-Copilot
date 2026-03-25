import React from 'react';
import type { Species } from '../../types';

interface SpeciesSelectorProps {
  value: Species;
  onChange: (s: Species) => void;
}

const speciesOptions: { id: Species; label: string; emoji: string }[] = [
  { id: 'dog', label: 'Perro', emoji: '\uD83D\uDC15' },
  { id: 'cat', label: 'Gato', emoji: '\uD83D\uDC08' },
  { id: 'horse', label: 'Caballo', emoji: '\uD83D\uDC34' },
  { id: 'bird', label: 'Ave', emoji: '\uD83D\uDC26' },
  { id: 'exotic', label: 'Ex\u00F3tico', emoji: '\uD83E\uDD8E' },
  { id: 'cattle', label: 'Bovino', emoji: '\uD83D\uDC04' },
];

const SpeciesSelector: React.FC<SpeciesSelectorProps> = ({ value, onChange }) => {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Especie
      </label>
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
        {speciesOptions.map((sp) => {
          const isSelected = value === sp.id;
          return (
            <button
              key={sp.id}
              type="button"
              onClick={() => onChange(sp.id)}
              className={`
                flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all
                cursor-pointer select-none
                ${
                  isSelected
                    ? 'border-brand-600 bg-brand-50 dark:bg-brand-900/20 shadow-[0_0_12px_rgba(var(--color-brand-600),0.3)]'
                    : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-brand-300 dark:hover:border-brand-500'
                }
              `}
            >
              <span className="text-3xl mb-1" role="img" aria-label={sp.label}>
                {sp.emoji}
              </span>
              <span
                className={`text-sm font-medium ${
                  isSelected
                    ? 'text-brand-700 dark:text-brand-300'
                    : 'text-gray-700 dark:text-gray-300'
                }`}
              >
                {sp.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default SpeciesSelector;
