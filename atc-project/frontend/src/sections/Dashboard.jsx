import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { UploadBox, Viewer, RunButton, Tile, Empty } from '../components.jsx';

const CAPS = [
  { key: 'detection', icon: '⊡', title: 'Detection', desc: 'Locate & box every aircraft on a runway, named by type.' },
  { key: 'classification', icon: '✈', title: 'Classification', desc: 'Identify a single aircraft type with confidence.' },
  { key: 'segmentation', icon: '◫', title: 'Segmentation', desc: 'Step-by-step instance mask pipeline.' },
  { key: 'analytics', icon: '▤', title: 'Analytics', desc: 'Trained-model accuracy & per-class metrics.' },
];

export default function Dashboard({ onNavigate }) {
  const [health, setHealth] = useState(null);
  const [accuracy, setAccuracy] = useState(null);
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
    api.analytics().then((d) => setAccuracy(d?.metrics?.accuracy)).catch(() => {});
  }, []);

  const run = async () => {
    if (!image) return;
    setLoading(true); setError(null);
    try { setResult(await api.analyze(image)); }
    catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div className="page section-gap">
      <div className="page-head">
        <h2>Air Traffic Control Vision System</h2>
        <p>A unified pipeline for aircraft <b>detection</b>, <b>classification</b>, and <b>segmentation</b>.
           Detection & segmentation use pretrained YOLOv8; classification uses a custom ResNet-50 trained on 8 aircraft types.</p>
      </div>

      <div className="tiles">
        <Tile value={health ? 'Online' : 'Offline'} label="Backend" />
        <Tile value={health?.classes?.length ?? '—'} label="Aircraft Types" />
        <Tile value={accuracy != null ? `${(accuracy * 100).toFixed(1)}%` : '—'} label="Classifier Accuracy" />
        <Tile value="YOLOv8m-seg" label="Detector / Segmenter" />
      </div>

      <div className="tiles">
        {CAPS.map((c) => (
          <button key={c.key} className="card tight" style={{ textAlign: 'left', cursor: 'pointer' }}
                  onClick={() => onNavigate(c.key)}>
            <div style={{ fontSize: 24 }}>{c.icon}</div>
            <div style={{ fontWeight: 700, marginTop: 8 }}>{c.title}</div>
            <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>{c.desc}</div>
          </button>
        ))}
      </div>

      <div className="split">
        <div className="card section-gap">
          <h3>Full Pipeline</h3>
          <p className="muted" style={{ fontSize: 12, marginTop: -6 }}>
            Run detection + classification + segmentation on one image.</p>
          <UploadBox image={image} onImage={(d) => { setImage(d); setResult(null); }} />
          <RunButton onClick={run} disabled={!image} loading={loading}>Run Full Analysis</RunButton>
          {error && <div className="alert">⚠ {error}</div>}
          {result && (
            <div className="tiles">
              <Tile value={result.summary.total_aircraft} label="Detected" />
              <Tile value={result.summary.classified} label="Classified" />
              <Tile value={result.summary.segmented_instances} label="Segmented" />
            </div>
          )}
        </div>

        <Viewer src={result?.image || image} loading={loading} loadingText="Running full pipeline…"
                placeholderIcon="📡" placeholderText="Upload an image to run the full pipeline" />
      </div>

      {!health && (
        <div className="alert">⚠ Backend not reachable at <code>localhost:5000</code>. Start it with
          <code> python app.py</code> in the <code>backend/</code> folder.</div>
      )}
    </div>
  );
}
