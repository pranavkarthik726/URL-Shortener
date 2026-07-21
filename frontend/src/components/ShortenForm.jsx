import { useState } from "react";

import { shortenUrl } from "../api.js";

export default function ShortenForm({ onShortened }) {
  const [longUrl, setLongUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [copied, setCopied] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setSubmitting(true);
    try {
      const data = await shortenUrl({ longUrl, customAlias, expiresAt });
      setResult(data);
      onShortened?.(data);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCopy() {
    if (!result) return;
    await navigator.clipboard.writeText(result.short_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <section className="card">
      <h2>Shorten a URL</h2>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Long URL
          <input
            type="url"
            required
            placeholder="https://example.com/some/long/path"
            value={longUrl}
            onChange={(e) => setLongUrl(e.target.value)}
          />
        </label>
        <label>
          Custom alias (optional)
          <input
            type="text"
            placeholder="my-link"
            value={customAlias}
            onChange={(e) => setCustomAlias(e.target.value)}
          />
        </label>
        <label>
          Expires on (optional)
          <input type="date" value={expiresAt} onChange={(e) => setExpiresAt(e.target.value)} />
        </label>
        <button type="submit" disabled={submitting}>
          {submitting ? "Shortening..." : "Shorten"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <a href={result.short_url} target="_blank" rel="noreferrer">
            {result.short_url}
          </a>
          <button type="button" onClick={handleCopy}>
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      )}
    </section>
  );
}
