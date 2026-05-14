import React, { useState } from 'react';
import { Camera, Upload, X } from 'lucide-react';

export function ImageUpload({ onAnalyze }) {
  const [preview, setPreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const handleFile = async (file) => {
    if (!file) return;
    
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const analyze = async () => {
    if (!preview) return;
    setAnalyzing(true);
    
    // Envoyer au backend pour analyse
    const response = await fetch('http://localhost:8000/analyze-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: preview.split(',')[1] }) // base64 sans header
    });
    
    const result = await response.json();
    onAnalyze(result.description);
    setAnalyzing(false);
  };

  return (
    <div style={{ border: '2px dashed #ddd', borderRadius: 12, padding: 20, textAlign: 'center' }}>
      {!preview ? (
        <>
          <Camera size={48} color="#999" style={{ margin: '0 auto 10px' }} />
          <p>Glissez une photo ou</p>
          <label style={{ color: '#3498db', cursor: 'pointer' }}>
            <Upload size={16} style={{ display: 'inline', marginRight: 5 }} />
            parcourez
            <input 
              type="file" 
              accept="image/*" 
              onChange={(e) => handleFile(e.target.files[0])}
              style={{ display: 'none' }}
            />
          </label>
        </>
      ) : (
        <div style={{ position: 'relative' }}>
          <img src={preview} style={{ maxWidth: '100%', maxHeight: 200, borderRadius: 8 }} />
          <button 
            onClick={() => setPreview(null)}
            style={{ position: 'absolute', top: -10, right: -10, background: '#e74c3c', color: 'white', border: 'none', borderRadius: '50%', width: 30, height: 30, cursor: 'pointer' }}
          >
            <X size={16} />
          </button>
          <button 
            onClick={analyze}
            disabled={analyzing}
            style={{ marginTop: 10, padding: '10px 20px', background: '#3498db', color: 'white', border: 'none', borderRadius: 6, cursor: 'pointer' }}
          >
            {analyzing ? 'Analyse...' : 'Analyser avec IA'}
          </button>
        </div>
      )}
    </div>
  );
}