import React, { useState, useRef, useEffect } from 'react';

interface SymptomInputProps {
  symptoms: string[];
  onChange: (s: string[]) => void;
  label?: string;
  placeholder?: string;
}

const COMMON_SYMPTOMS = [
  'V\u00F3mitos',
  'Diarrea',
  'Letargia',
  'Anorexia',
  'Poliuria',
  'Polidipsia',
  'Tos',
  'Disnea',
  'Claudicaci\u00F3n',
  'Prurito',
  'Alopecia',
  'Convulsiones',
  'Fiebre',
  'Ictericia',
  'Hematuria',
  'Estreñimiento',
  'Polifagia',
  'P\u00E9rdida de peso',
  'Aumento de peso',
  'Secreción nasal',
  'Secreción ocular',
  'Estornudos',
  'Edema',
  'Ascitis',
  'Ataxia',
  'Debilidad',
  'S\u00EDncope',
  'Temblores',
  'Dolor abdominal',
  'Distensión abdominal',
];

const SymptomInput: React.FC<SymptomInputProps> = ({
  symptoms,
  onChange,
  label = 'S\u00EDntomas',
  placeholder = 'Escribir s\u00EDntoma...',
}) => {
  const [query, setQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const filtered = COMMON_SYMPTOMS.filter(
    (s) =>
      s.toLowerCase().includes(query.toLowerCase()) &&
      !symptoms.some((ex) => ex.toLowerCase() === s.toLowerCase())
  );

  const addSymptom = (symptom: string) => {
    const trimmed = symptom.trim();
    if (trimmed && !symptoms.some((s) => s.toLowerCase() === trimmed.toLowerCase())) {
      onChange([...symptoms, trimmed]);
    }
    setQuery('');
    setShowDropdown(false);
  };

  const removeSymptom = (index: number) => {
    onChange(symptoms.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered.length > 0) {
        addSymptom(filtered[0]);
      } else if (query.trim()) {
        addSymptom(query);
      }
    }
  };

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={wrapperRef}>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label}
      </label>

      <div className="relative">
        <input
          type="text"
          className="input-field w-full"
          placeholder={placeholder}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowDropdown(true);
          }}
          onFocus={() => setShowDropdown(true)}
          onKeyDown={handleKeyDown}
        />

        {showDropdown && query.length > 0 && filtered.length > 0 && (
          <ul className="absolute z-20 mt-1 w-full max-h-48 overflow-y-auto rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg">
            {filtered.map((s) => (
              <li
                key={s}
                className="px-3 py-2 text-sm cursor-pointer hover:bg-brand-50 dark:hover:bg-brand-900/30 text-gray-700 dark:text-gray-300"
                onMouseDown={() => addSymptom(s)}
              >
                {s}
              </li>
            ))}
          </ul>
        )}
      </div>

      {symptoms.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {symptoms.map((symptom, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300"
            >
              {symptom}
              <button
                type="button"
                onClick={() => removeSymptom(idx)}
                className="ml-1 hover:text-red-500 transition-colors"
                aria-label={`Eliminar ${symptom}`}
              >
                &times;
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default SymptomInput;
