import { useState } from "react";

import AnalyticsDashboard from "./components/AnalyticsDashboard.jsx";
import ShortenForm from "./components/ShortenForm.jsx";

export default function App() {
  const [lastShortCode, setLastShortCode] = useState("");

  return (
    <div className="page">
      <h1>URL Shortener</h1>
      <ShortenForm onShortened={(result) => setLastShortCode(result.short_code)} />
      <AnalyticsDashboard prefillCode={lastShortCode} />
    </div>
  );
}
