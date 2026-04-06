import { Dashboard } from "@/components/Dashboard";
import { DataCoverage } from "@/components/DataCoverage";
import type { Manifest } from "@/lib/types";
import manifestJson from "../public/data/manifest.json";

const manifest = manifestJson as Manifest;

export default function HomePage() {
  return (
    <>
      <h1 className="page-title">Climate in the headlines</h1>
      <p className="page-lead">Eight outlets, one snapshot. Updated by the collector.</p>
      <DataCoverage manifest={manifest} />
      <Dashboard />
    </>
  );
}
