import React from 'react';
import { Globe } from 'lucide-react';

const languages = [
  { code: 'fr', flag: '🇫🇷', name: 'Français' },
  { code: 'en', flag: '🇬🇧', name: 'English' },
  { code: 'es', flag: '🇪🇸', name: 'Español' },
  { code: 'ar', flag: '🇸🇦', name: 'العربية' }
];

export function LanguageSelector({ current, onChange }) {
  return (
    <div style={{ position: 'relative' }}>
      <select 
        value={current}
        onChange={(e) => onChange(e.target.value)}
        style={{
          padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd',
          background: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5
        }}
      >
        {languages.map(l => (
          <option key={l.code} value={l.code}>
            {l.flag} {l.name}
          </option>
        ))}
      </select>
    </div>
  );
}
