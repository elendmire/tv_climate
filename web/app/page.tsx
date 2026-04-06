import { Dashboard } from "@/components/Dashboard";

export default function HomePage() {
  return (
    <>
      <h1 className="page-title">Climate in the headlines</h1>
      <p className="page-lead">Eight outlets, one snapshot. Updated by the collector.</p>
      <Dashboard />
    </>
  );
}
