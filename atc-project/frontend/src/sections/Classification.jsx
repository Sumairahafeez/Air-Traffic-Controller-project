import React, { useState } from 'react';
import { api } from '../api';
import { UploadBox, RunButton, Bar, Empty } from '../components.jsx';

export default function Classification() {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const run = async () => {
    if (!image) return;
    setLoading(true); setError(null);
    try {
      setResult(await api.classify(image));
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const pred = result?.prediction;
  const sorted = pred
    ? Object.entries(pred.all_probabilities).sort((a, b) => b[1] - a[1])
    : [];

  return (
    <div className="page">
      <div className="page-head">
        <h2>Classification</h2>
        <p>Identify a single aircraft type with the trained ResNet-50 model.
           Returns the predicted name, confidence, category, and the full probability distribution.</p>
      </div>

      <div className="split">
        <div className="card section-gap">
          <h3>Aircraft Image</h3>
          <UploadBox image={image} onImage={(d) => { setImage(d); setResult(null); }}
                     hint="A cropped photo of one aircraft" />
          <RunButton onClick={run} disabled={!image} loading={loading}>Classify Aircraft</RunButton>
          {error && <div className="alert">⚠ {error}</div>}
        </div>

        <div className="card">
          <h3>Prediction</h3>
          {!pred && <Empty icon="✈">Upload an aircraft image and run classification.</Empty>}
          {pred && (
            <div className="section-gap">
              <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                <div style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.02em' }}>{pred.class_name}</div>
                <span className="chip">{(pred.confidence * 100).toFixed(2)}% confidence</span>
                <span className="chip outline">{pred.category}</span>
              </div>

              <div>
                <h3>Class Probabilities</h3>
                {sorted.map(([name, p]) => <Bar key={name} label={name} value={p} />)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
