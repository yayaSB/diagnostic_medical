import React, { useState } from 'react';
import { GitCompare, X } from 'lucide-react';

export function CompareView({ reports, onClose }) {
  const [selected, setSelected] = useState([null, null]);

  if (!reports || reports.length < 2) {
    return <div style={{ padding: 20 }}>Minimum 2 rapports requis</div>;
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      zIndex: 2000, display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <div style={{
        background: 'white', width: '90%', maxWidth: 1200, height: '90%',
        borderRadius: 12, display: 'flex', flexDirection: 'column'
      }}>
        <div style={{
          padding: '20px', borderBottom: '1px solid #eee',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center'
        }}>
          <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 10 }}>
            <GitCompare size={24} /> Comparaison de cas
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <X size={24} />
          </button>
        </div>

        <div style={{ display: 'flex', gap: 20, padding: 20, flex: 1, overflow: 'hidden' }}>
          {/* Sélecteur gauche */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
            <select 
              value={selected[0] || ''} 
              onChange={(e) => setSelected([e.target.value, selected[1]])}
              style={{ padding: 10, borderRadius: 6, border: '1px solid #ddd' }}
            >
              <option value="">Choisir un cas...</option>
              {reports.map((r, i) => (
                <option key={i} value={i}>Cas {i+1}: {r.case?.slice(0, 40)}...</option>
              ))}
            </select>
            <div style={{ flex: 1, overflow: 'auto', background: '#f5f5f5', padding: 15, borderRadius: 8 }}>
              {selected[0] !== null && (
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85em' }}>
                  {reports[selected[0]].report}
                </pre>
              )}
            </div>
          </div>

          {/* Sélecteur droite */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
            <select 
              value={selected[1] || ''} 
              onChange={(e) => setSelected([selected[0], e.target.value])}
              style={{ padding: 10, borderRadius: 6, border: '1px solid #ddd' }}
            >
              <option value="">Choisir un cas...</option>
              {reports.map((r, i) => (
                <option key={i} value={i}>Cas {i+1}: {r.case?.slice(0, 40)}...</option>
              ))}
            </select>
            <div style={{ flex: 1, overflow: 'auto', background: '#f5f5f5', padding: 15, borderRadius: 8 }}>
              {selected[1] !== null && (
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85em' }}>
                  {reports[selected[1]].report}
                </pre>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}