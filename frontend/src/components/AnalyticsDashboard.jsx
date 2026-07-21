import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getAnalytics } from "../api.js";

const ACCENT = "#2a78d6";
const GRID = "#e2e2e2";

export default function AnalyticsDashboard({ prefillCode }) {
  const [shortCode, setShortCode] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (prefillCode) {
      setShortCode(prefillCode);
    }
  }, [prefillCode]);

  async function handleLookup(e) {
    e.preventDefault();
    if (!shortCode) return;
    setError("");
    setData(null);
    setLoading(true);
    try {
      const result = await getAnalytics(shortCode);
      setData(result);
    } catch (err) {
      setError(err.message || "Could not load analytics");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Link Analytics</h2>
      <form onSubmit={handleLookup} className="form form-inline">
        <input
          type="text"
          placeholder="short code, e.g. 3F"
          value={shortCode}
          onChange={(e) => setShortCode(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Loading..." : "View analytics"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {data && (
        <div className="analytics">
          <div className="stat-tile">
            <span className="stat-value">{data.total_clicks}</span>
            <span className="stat-label">total clicks</span>
          </div>

          <div className="chart-block">
            <h3>Clicks over time</h3>
            {data.clicks_over_time.length === 0 ? (
              <p className="empty">No clicks yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={data.clicks_over_time}>
                  <CartesianGrid stroke={GRID} vertical={false} />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke={ACCENT} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="chart-block">
            <h3>Device breakdown</h3>
            {data.device_breakdown.length === 0 ? (
              <p className="empty">No clicks yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data.device_breakdown}>
                  <CartesianGrid stroke={GRID} vertical={false} />
                  <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill={ACCENT} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="chart-block">
            <h3>Location breakdown</h3>
            {data.location_breakdown.length === 0 ? (
              <p className="empty">No clicks yet.</p>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>Location</th>
                    <th>Clicks</th>
                  </tr>
                </thead>
                <tbody>
                  {data.location_breakdown.map((row) => (
                    <tr key={row.label}>
                      <td>{row.label}</td>
                      <td>{row.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
