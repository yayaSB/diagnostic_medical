import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react';

const colors = {
  red: { bg: '#fee2e2', border: '#ef4444', text: '#991b1b', icon: AlertTriangle },
  orange: { bg: '#ffedd5', border: '#f97316', text: '#9a3412', icon: AlertCircle },
  yellow: { bg: '#fef9c3', border: '#eab308', text: '#854d0e', icon: AlertCircle },
  green: { bg: '#dcfce7', border: '#22c55e', text: '#166534', icon: CheckCircle }
};

export function UrgencyBadge({ urgency }) {
  if (!urgency) return null;
  
  const style = colors[urgency.color] || colors.green;
  const Icon = style.icon;
  
  return (
    <div style={{
      background: style.bg,
      border: `2px solid ${style.border}`,
      borderRadius: 12,
      padding: '15px 20px',
      marginBottom: 15,
      display: 'flex',
      alignItems: 'center',
      gap: 15
    }}>
      <Icon size={32} color={style.border} />
      <div>
        <div style={{ fontSize: '0.85em', color: style.text, opacity: 0.8 }}>
          Score d'urgence: {urgency.score}/100
        </div>
        <div style={{ fontSize: '1.3em', fontWeight: 'bold', color: style.text }}>
          {urgency.label}
        </div>
        <div style={{ fontSize: '0.9em', color: style.text }}>
          {urgency.action}
        </div>
      </div>
    </div>
  );
}