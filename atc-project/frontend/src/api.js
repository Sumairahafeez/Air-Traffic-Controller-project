// Backend API client.
export const API_URL = 'https://mustafanoor-airtrafficcontrol.hf.space';

async function postImage(path, imageBase64) {
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageBase64 }),
  });
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try { msg = (await res.json()).error || msg; } catch { /* ignore */ }
    throw new Error(msg);
  }
  return res.json();
}

export const api = {
  health: () => fetch(`${API_URL}/health`).then((r) => r.json()),
  classify: (img) => postImage('/classify', img),
  detect: (img) => postImage('/detect', img),
  segment: (img) => postImage('/segment', img),
  analyze: (img) => postImage('/analyze', img),
  analytics: () => fetch(`${API_URL}/analytics`).then((r) => {
    if (!r.ok) throw new Error('Could not load analytics');
    return r.json();
  }),
  plotUrl: (path) => `${API_URL}${path}`,
  generateReport: async (data) => {
    const res = await fetch(`${API_URL}/generate_report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      let msg = `Report generation failed (${res.status})`;
      try { msg = (await res.json()).error || msg; } catch { /* ignore */ }
      throw new Error(msg);
    }
    return res.blob();
  },
};
