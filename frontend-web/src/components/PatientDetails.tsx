import type { PatientDetails as PatientDetailsType } from "../types/api";

interface PatientDetailsProps {
  details: PatientDetailsType;
}

export function PatientDetails({ details }: PatientDetailsProps) {
  const entries = Object.entries(details).filter(([, value]) => value !== null && value !== undefined && String(value).trim() !== "");
  if (!entries.length) return <p className="muted-copy">No patient details detected.</p>;

  const labelFor = (key: string) => key === "mrn" ? "Record number" : key === "gender" || key === "sex" ? "Sex" : key.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  const valueFor = (key: string, value: string | number | null | undefined) => /name|mrn|identifier|record|id/i.test(key) ? (value === "[REDACTED]" ? value : "Redacted") : String(value);

  return <div className="detail-list">{entries.map(([key, value]) => <div className="detail-row" key={key}><span>{labelFor(key)}</span><strong>{valueFor(key, value)}</strong></div>)}</div>;
}
