import React, { useState } from 'react';
import { api } from '../api';
import { UploadBox, RunButton, Tile, Empty } from '../components.jsx';

export default function Segmentation() {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const run = async () => {
    if (!image) return;
    setLoading(true); setError(null);
    try {
      setResult(await api.segment(image));
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const stages = result?.stages || [];
  const stats = result?.stats;

  return (
    <div className="page">
      <div className="page-head">
        <h2>Segmentation</h2>
        <p>Watch the full segmentation pipeline step by step — from the raw input through
           preprocessing, instance masks, overlay, and contour extraction (YOLOv8-seg).</p>
      </div>

      <div className="split">
        <div className="card section-gap">
          <h3>Image</h3>
          <UploadBox image={image} onImage={(d) => { setImage(d); setResult(null); }} />
          <RunButton onClick={run} disabled={!image} loading={loading}>Run Segmentation</RunButton>
          {error && <div className="alert">⚠ {error}</div>}
          {stats && (
            <div className="tiles">
              <Tile value={stats.instances} label="Instances" />
              <Tile value={`${stats.total_coverage_pct}%`} label="Mask Coverage" />
            </div>
          )}
        </div>

        <div className="section-gap">
          <div className="card">
            <h3>Segmentation Process</h3>
            {stages.length === 0 && !loading && <Empty icon="◫">Run segmentation to see each step of the pipeline.</Empty>}
            {loading && <Empty icon="◫">Processing…</Empty>}
            {stages.length > 0 && (
              <div className="stages">
                {stages.map((s, i) => (
                  <div className="stage" key={i}>
                    <div className="num">{i + 1}</div>
                    <img src={s.image} alt={s.title} />
                    <div className="cap">
                      <div className="t">{s.title.replace(/^\d+\.\s*/, '')}</div>
                      <div className="d">{s.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {stats && stats.per_instance.length > 0 && (
            <div className="card">
              <h3>Per-Instance Regions</h3>
              <table className="table">
                <thead>
                  <tr><th>#</th><th>Region</th><th className="num">Area (px)</th><th className="num">Coverage</th></tr>
                </thead>
                <tbody>
                  {stats.per_instance.map((r) => (
                    <tr key={r.id}>
                      <td>{r.id + 1}</td>
                      <td>{r.label || 'object'}</td>
                      <td className="num">{r.area_px.toLocaleString()}</td>
                      <td className="num">{r.coverage_pct}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
