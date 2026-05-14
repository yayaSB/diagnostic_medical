import React, { useState, useEffect } from 'react';
import { History, Search, X, FileText } from 'lucide-react';

export function HistoryPanel({ onLoadSession, currentThreadId }) {
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Charger depuis localStorage
    const saved = JSON.parse(localStorage.getItem('medical_history') || '[]');
    setHistory(saved);
  }, []);

  const saveToHistory = (data) => {
    if (!data?.thread_id) return;
    
    const entry = {
      thread_id: data.thread_id,
      date: new Date().toISOString(),
      case: data.state?.initial_case || 'Sans titre',
      status: data.status,
      has_report: !!data.state?.final_report,
    };

    const existing = JSON.parse(localStorage.getItem('medical_history') || '[]');
    const filtered = existing.filter(h => h.thread_id !== data.thread_id);
    const updated = [entry, ...filtered].slice(0, 50); // Max 50
    
    localStorage.setItem('medical_history', JSON.stringify(updated));
    setHistory(updated);
  };

  const filtered = history.filter(h => 
    h.case.toLowerCase().includes(search.toLowerCase()) ||
    h.thread_id.includes(search)
  );

  const formatDate = (iso) => {
    return new Date(iso).toLocaleDateString('fr-FR', {
      day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
    });
  };

  if (!isOpen) {
    return (
      <button 
        className="historyToggle" 
        onClick={() => setIsOpen(true)}
        style={{
          position: 'fixed', right: '20px', top: '20px', zIndex: 100,
          background: '#2c3e50', color: 'white', border: 'none',
          padding: '10px 15px', borderRadius: '8px', cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: '8px'
        }}
      >
        <History size={20} />
        Historique ({history.length})
      </button>
    );
  }

  return (
    <div style={{
      position: 'fixed', right: 0, top: 0, width: '350px', height: '100vh',
      background: 'white', boxShadow: '-4px 0 15px rgba(0,0,0,0.1)',
      zIndex: 1000, display: 'flex', flexDirection: 'column'
    }}>
      <div style={{
        padding: '20px', borderBottom: '1px solid #eee',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center'
      }}>
        <h3 style={{ margin: 0 }}>Historique</h3>
        <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
          <X size={24} />
        </button>
      </div>

      <div style={{ padding: '15px' }}>
        <div style={{ position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: '10px', top: '10px', color: '#999' }} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher..."
            style={{ width: '100%', padding: '8px 8px 8px 35px', borderRadius: '6px', border: '1px solid #ddd' }}
          />
        </div>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '0 15px' }}>
        {filtered.map(entry => (
          <div 
            key={entry.thread_id}
            onClick={() => onLoadSession(entry.thread_id)}
            style={{
              padding: '12px', marginBottom: '8px', borderRadius: '8px',
              border: '1px solid #eee', cursor: 'pointer',
              background: entry.thread_id === currentThreadId ? '#e3f2fd' : 'white',
              transition: 'background 0.2s'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 500, fontSize: '0.9em' }}>
                {entry.case.length > 30 ? entry.case.slice(0, 30) + '...' : entry.case}
              </span>
              {entry.has_report && <FileText size={16} color="#4caf50" />}
            </div>
            <div style={{ fontSize: '0.75em', color: '#666', marginTop: '4px' }}>
              {formatDate(entry.date)} · {entry.status === 'completed' ? 'Terminé' : 'En cours'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}