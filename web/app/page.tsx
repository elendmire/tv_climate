import { Dashboard } from "@/components/Dashboard";

export default function HomePage() {
  return (
    <>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "0.35rem" }}>
        Climate-related mentions in Turkish news headlines
      </h1>
      <p className="muted" style={{ marginBottom: "1.5rem" }}>
        Live data is loaded from static JSON produced by the collector (no database, no API keys).
        Article titles remain in Turkish; this interface is English-only.
      </p>
      <Dashboard />
    </>
  );
}
