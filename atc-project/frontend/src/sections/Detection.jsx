import React, { useState } from 'react';
import { api } from '../api';
import { UploadBox, Viewer, RunButton, Tile, Empty } from '../components.jsx';

export default function Detection() {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const run = async () => {
    if (!image) return;
    setLoading(true); setError(null);
    try {
      setResult(await api.detect(image));
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const dets = result?.detections || [];

  return (
    <div className="page">
      <div className="page-head">
        <h2>Detection</h2>
        <p>Upload an airport / runway scene. YOLOv8 locates every aircraft and draws a bounding box;
           each box is then named by the trained ResNet-50 classifier with its position and size.</p>
      </div>

      <div className="split">
        <div className="card section-gap">
          <h3>Runway Image</h3>
          <UploadBox image={image} onImage={(d) => { setImage(d); setResult(null); }}
                     hint="Airport, runway, or apron photo" />
          <RunButton onClick={run} disabled={!image} loading={loading}>Detect Aircraft</RunButton>
          {error && <div className="alert">⚠ {error}</div>}
          {result && (
            <div className="tiles">
              <Tile value={result.summary.total} label="Aircraft" />
              <Tile value={`${(result.summary.avg_confidence * 100).toFixed(0)}%`} label="Avg Det. Conf" />
            </div>
          )}
        </div>

        <div className="section-gap">
          <Viewer src={result?.image || image} loading={loading} loadingText="Detecting aircraft…"
                  placeholderIcon="⊡" placeholderText="Detected boxes appear here" />

          <div className="card">
            <h3>Detections ({dets.length})</h3>
            {dets.length === 0 && !loading && <Empty icon="⊡">No aircraft detected yet.</Empty>}
            {dets.map((d) => (
              <div className="item" key={d.id}>
                <div className="item-head">
                  <span className="name">#{d.id + 1} · {d.label}</span>
                  {d.category && <span className="chip outline">{d.category}</span>}
                </div>
                {d.classification_confidence != null && (
                  <div className="kv"><span>Type confidence</span><b>{(d.classification_confidence * 100).toFixed(1)}%</b></div>
                )}
                <div className="kv"><span>Detection confidence</span><b>{(d.detection_confidence * 100).toFixed(1)}%</b></div>
                <div className="kv"><span>Position (center)</span><b>{d.center[0]}, {d.center[1]}</b></div>
                <div className="kv"><span>Box (x, y, w, h)</span><b>{d.box.join(', ')}</b></div>
                <div className="kv"><span>Area</span><b>{d.area_px.toLocaleString()} px²</b></div>
                {d.top_k && (
                  <div className="kv"><span>Alternatives</span>
                    <b>{d.top_k.slice(1).map((t) => `${t.class_name} ${(t.confidence * 100).toFixed(0)}%`).join(' · ') || '—'}</b>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
