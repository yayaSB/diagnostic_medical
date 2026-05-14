import React, { useEffect, useState } from 'react';
import { Bar, Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement,
  LineElement, ArcElement, Title, Tooltip, Legend
} from 'chart.js';
import { BarChart3, X } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend);

export function Dashboard({ onClose }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const history = JSON.parse(localStorage.getItem('medical_history') || '[]');
    
    // Calculer stats
    const symptomTypes = {};
    const dailyCounts = {};
    const statusCounts = { completed: 0, in_progress: 0, waiting_physician: 0 };
    let totalDuration = 0;
    
    history.forEach(h => {
      // Extraire type symptôme du cas
      const case_lower = h.case.toLowerCase();
      let type = 'Autre';
      if (case_lower.includes('yeux') || case_lower.includes('vision')) type = 'Ophtalmologique';
      else if (case_lower.includes('toux') || case_lower.includes('gorge') || case_lower.includes('respir')) type = 'Respiratoire';
      else if (case_lower.includes('ventre') || case_lower.includes('diahrrée') || case_lower.includes('nausée')) type = 'Digestif';
      else if (case_lower.includes('tête') || case_lower.includes('migraine')) type = 'Neurologique';
      else if (case_lower.includes('peau') || case_lower.includes('rougeur')) type = 'Dermatologique';
      
      symptomTypes[type] = (symptomTypes[type] || 0) + 1;
      
      // Par jour
      const day = h.date.split('T')[0];
      dailyCounts[day] = (dailyCounts[day] || 0) + 1;
      
      // Status
      statusCounts[h.status] = (statusCounts[h.status] || 0) + 1;
    });

    setStats({
      total: history.length,
      symptomTypes,
      dailyCounts,
      statusCounts
    });
  }, []);

  if (!stats) return null;

  const symptomData = {
    labels: Object.keys(stats.symptomTypes),
    datasets: [{
      label: 'Nombre de cas',
      data: Object.values(stats.symptomTypes),
      backgroundColor: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    }]
  };

  const statusData = {
    labels: ['Terminés', 'En cours', 'Attente médecin'],
    datasets: [{
      data: [stats.statusCounts.completed, stats.statusCounts.in_progress, stats.statusCounts.waiting_physician],
      backgroundColor: ['#2ecc71', '#f39c12', '#e74c3c']
    }]
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      zIndex: 2000, display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <div style={{
        background: 'white', width: '90%', maxWidth: 900, height: '90%',
        borderRadius: 12, display: 'flex', flexDirection: 'column', padding: 30
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 10 }}>
            <BarChart3 size={28} /> Tableau de bord
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <X size={24} />
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, flex: 1 }}>
          <div style={{ background: '#f8f9fa', padding: 20, borderRadius: 8 }}>
            <h3>Types de symptômes</h3>
            <Pie data={symptomData} />
          </div>
          
          <div style={{ background: '#f8f9fa', padding: 20, borderRadius: 8 }}>
            <h3>Statut des consultations</h3>
            <Pie data={statusData} />
          </div>
          
          <div style={{ background: '#f8f9fa', padding: 20, borderRadius: 8, gridColumn: '1 / -1' }}>
            <h3>Activité quotidienne</h3>
            <Bar data={{
              labels: Object.keys(stats.dailyCounts).slice(-7),
              datasets: [{
                label: 'Consultations',
                data: Object.values(stats.dailyCounts).slice(-7),
                backgroundColor: '#3498db'
              }]
            }} />
          </div>
        </div>

        <div style={{ marginTop: 20, textAlign: 'center', fontSize: '1.2em', color: '#2c3e50' }}>
          Total: <strong>{stats.total}</strong> consultations
        </div>
      </div>
    </div>
  );
}