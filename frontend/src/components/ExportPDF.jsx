import React from 'react';
import { jsPDF } from 'jspdf';
import { FileDown } from 'lucide-react';

export function ExportPDF({ data }) {
  const generatePDF = () => {
    const doc = new jsPDF();
    const report = data.state?.final_report || '';
    
    // Header
    doc.setFillColor(44, 62, 80);
    doc.rect(0, 0, 210, 30, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(20);
    doc.text('Rapport d\'Orientation Clinique', 105, 20, { align: 'center' });
    
    // Content
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(11);
    
    const lines = report.split('\n');
    let y = 45;
    
    lines.forEach(line => {
      if (y > 280) {
        doc.addPage();
        y = 20;
      }
      
      if (line.startsWith('#') || line.startsWith('===')) {
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        y += 5;
      } else {
        doc.setFontSize(11);
        doc.setFont('helvetica', 'normal');
      }
      
      const cleanLine = line.replace(/[#=]/g, '').trim();
      if (cleanLine) {
        const splitLines = doc.splitTextToSize(cleanLine, 180);
        doc.text(splitLines, 15, y);
        y += splitLines.length * 6 + 2;
      }
    });
    
    // Footer
    doc.setFontSize(9);
    doc.setTextColor(128, 128, 128);
    doc.text(`Généré le ${new Date().toLocaleDateString('fr-FR')} - Outil pédagogique`, 105, 290, { align: 'center' });
    
    doc.save(`rapport-${data.thread_id?.slice(0, 8)}.pdf`);
  };

  return (
    <button className="secondaryButton" onClick={generatePDF}>
      <FileDown size={18} />
      Exporter PDF
    </button>
  );
}