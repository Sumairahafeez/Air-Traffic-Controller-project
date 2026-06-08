import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { Tile, Bar, Empty } from '../components.jsx';

const pct = (x) => (x == null ? '—' : `${(x * 100).toFixed(2)}%`);

export default function Analytics() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.analytics().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="page"><Empty icon="✕">{error}. Is the backend running?</Empty></div>;
  if (!data) return <div className="page"><Empty icon="◷">Loading model analytics…</Empty></div>;

  const m = data.metrics || {};
  const report = m.classification_report || {};
  const perClassAcc = m.per_class_accuracy || {};
  const classes = data.class_names || [];

  return (
    <div className="page section-gap">
      <div className="page-head">
        <h2>Model Analytics</h2>
        <p>Evaluation of the trained ResNet-50 classifier ({classes.length} aircraft types).
           Metrics computed on the held-out test set.</p>
      </div>

      <div className="tiles">
        <Tile value={pct(m.accuracy)} label="Accuracy" />
        <Tile value={pct(m.precision_weighted)} label="Precision (w)" />
        <Tile value={pct(m.recall_weighted)} label="Recall (w)" />
        <Tile value={pct(m.f1_weighted)} label="F1 (w)" />
        {m.inference_time_ms_per_image != null &&
          <Tile value={`${m.inference_time_ms_per_image.toFixed(0)} ms`} label="Inference / image" />}
      </div>

      <div className="grid2">
        <div className="card">
          <h3>Per-Class Accuracy</h3>
          {classes.map((c) => perClassAcc[c] != null && <Bar key={c} label={c} value={perClassAcc[c]} />)}
        </div>

        <div className="card">
          <h3>Precision / Recall / F1 by Class</h3>
          <table className="table">
            <thead>
              <tr><th>Class</th><th>Category</th><th className="num">Prec</th><th className="num">Rec</th><th className="num">F1</th><th className="num">N</th></tr>
            </thead>
            <tbody>
              {classes.map((c) => {
                const r = report[c] || {};
                return (
                  <tr key={c}>
                    <td><b>{c}</b></td>
                    <td className="muted">{data.category_map?.[c] || '—'}</td>
                    <td className="num">{r.precision != null ? r.precision.toFixed(3) : '—'}</td>
                    <td className="num">{r.recall != null ? r.recall.toFixed(3) : '—'}</td>
                    <td className="num">{r['f1-score'] != null ? r['f1-score'].toFixed(3) : '—'}</td>
                    <td className="num">{r.support != null ? r.support : '—'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {data.plots && Object.keys(data.plots).length > 0 && (
        <div className="grid2">
          {data.plots.confusion_matrix && (
            <div className="plot"><h4>Confusion Matrix</h4>
              <img src={api.plotUrl(data.plots.confusion_matrix)} alt="confusion matrix" /></div>
          )}
          {data.plots.class_distribution && (
            <div className="plot"><h4>Class Distribution</h4>
              <img src={api.plotUrl(data.plots.class_distribution)} alt="class distribution" /></div>
          )}
          {data.plots.sample_images && (
            <div className="plot" style={{ gridColumn: '1 / -1' }}><h4>Sample Images</h4>
              <img src={api.plotUrl(data.plots.sample_images)} alt="samples" /></div>
          )}
        </div>
      )}

      <div className="card">
        <h3>Model Card</h3>
        <div className="kv"><span>Architecture</span><b>{(data.comparison?.[0]?.model) || 'resnet50'}</b></div>
        <div className="kv"><span>Classes</span><b>{classes.join(', ')}</b></div>
        <div className="kv"><span>Test samples</span><b>{report['weighted avg']?.support ?? '—'}</b></div>
        <div className="kv"><span>Checkpoint</span><b>{m.evaluated_checkpoint || 'resnet50_best.pth'}</b></div>
      </div>
    </div>
  );
}
