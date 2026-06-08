import React, { useEffect, useState } from 'react';
import { api } from './api';
import Dashboard from './sections/Dashboard.jsx';
import Detection from './sections/Detection.jsx';
import Classification from './sections/Classification.jsx';
import Segmentation from './sections/Segmentation.jsx';
import Analytics from './sections/Analytics.jsx';

const TABS = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'detection', label: 'Detection' },
  { key: 'classification', label: 'Classification' },
  { key: 'segmentation', label: 'Segmentation' },
  { key: 'analytics', label: 'Analytics' },
];

const validTab = (h) => TABS.some((t) => t.key === h) ? h : 'dashboard';

export default function App() {
  const [tab, setTabState] = useState(() => validTab(window.location.hash.slice(1)));
  const [online, setOnline] = useState(null);

  const setTab = (key) => { setTabState(key); window.location.hash = key; };

  useEffect(() => {
    const onHash = () => setTabState(validTab(window.location.hash.slice(1)));
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  useEffect(() => {
    let active = true;
    const ping = () => api.health().then(() => active && setOnline(true)).catch(() => active && setOnline(false));
    ping();
    const id = setInterval(ping, 15000);
    return () => { active = false; clearInterval(id); };
  }, []);

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="logo">ATC·VISION</span>
          <span className="tag">Detection · Classification · Segmentation</span>
        </div>
        <div className="status">
          <span className={`dot${online ? '' : ' off'}`} />
          {online == null ? 'connecting' : online ? 'system online' : 'backend offline'}
        </div>
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button key={t.key} className={`tab${tab === t.key ? ' active' : ''}`}
                  onClick={() => setTab(t.key)}>{t.label}</button>
        ))}
      </nav>

      {tab === 'dashboard' && <Dashboard onNavigate={setTab} />}
      {tab === 'detection' && <Detection />}
      {tab === 'classification' && <Classification />}
      {tab === 'segmentation' && <Segmentation />}
      {tab === 'analytics' && <Analytics />}
    </div>
  );
}
