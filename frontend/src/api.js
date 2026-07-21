const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // non-JSON error body, fall back to statusText
    }
    const error = new Error(detail);
    error.status = res.status;
    throw error;
  }
  return res.json();
}

export async function shortenUrl({ longUrl, customAlias, expiresAt }) {
  const res = await fetch(`${API_BASE_URL}/api/shorten`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      long_url: longUrl,
      custom_alias: customAlias || undefined,
      expires_at: expiresAt || undefined,
    }),
  });
  return handleResponse(res);
}

export async function getAnalytics(shortCode) {
  const res = await fetch(`${API_BASE_URL}/api/analytics/${encodeURIComponent(shortCode)}`);
  return handleResponse(res);
}
