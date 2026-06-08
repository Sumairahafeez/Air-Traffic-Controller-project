// Small shared UI primitives for the B&W theme.
import React, { useRef, useState } from 'react';

export function UploadBox({ image, onImage, hint }) {
  const inputRef = useRef(null);
  const [drag, setDrag] = useState(false);

  const handleFiles = (files) => {
    if (!files || !files[0]) return;
    const file = files[0];
    if (!file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = (e) => onImage(e.target.result);
    reader.readAsDataURL(file);
  };

  return (
    <div
      className={`dropzone${drag ? ' drag' : ''}`}
      onClick={() => inputRef.current.click()}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => { e.preventDefault(); setDrag(false); handleFiles(e.dataTransfer.files); }}
    >
      <input ref={inputRef} type="file" accept="image/*" hidden
             onChange={(e) => handleFiles(e.target.files)} />
      {image ? (
        <img src={image} alt="upload preview" />
      ) : (
        <>
          <div className="icon">⊕</div>
          <div style={{ fontWeight: 600, marginTop: 6 }}>Click or drop an image</div>
          <div className="hint">{hint || 'PNG / JPG'}</div>
        </>
      )}
    </div>
  );
}

export function Viewer({ src, loading, loadingText, placeholderIcon = '▦', placeholderText }) {
  return (
    <div className="viewer">
      {src ? <img src={src} alt="result" /> : (
        <div className="placeholder">
          <div className="icon">{placeholderIcon}</div>
          <div style={{ marginTop: 8 }}>{placeholderText || 'No image yet'}</div>
        </div>
      )}
      {loading && (
        <div className="overlay">
          <div className="spinner" />
          <div>{loadingText || 'Processing…'}</div>
        </div>
      )}
    </div>
  );
}

export function Tile({ value, label }) {
  return (
    <div className="tile">
      <div className="v">{value}</div>
      <div className="l">{label}</div>
    </div>
  );
}

export function Bar({ label, value }) {
  const pct = Math.max(0, Math.min(100, value * 100));
  return (
    <div className="bar">
      <span className="lbl" title={label}>{label}</span>
      <span className="track"><span className="fill" style={{ width: `${pct}%` }} /></span>
      <span className="pct">{pct.toFixed(1)}%</span>
    </div>
  );
}

export function Empty({ icon = '▦', children }) {
  return <div className="empty"><div className="icon">{icon}</div><div style={{ marginTop: 10 }}>{children}</div></div>;
}

export function RunButton({ onClick, disabled, loading, children }) {
  return (
    <button className="btn" onClick={onClick} disabled={disabled || loading}>
      {loading ? <><span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Processing…</> : children}
    </button>
  );
}
