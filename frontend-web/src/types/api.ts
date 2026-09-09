export interface PatientDetails {
  name?: string;
  mrn?: string;
  age?: string | number;
  gender?: string;
  sex?: string;
  [key: string]: string | number | null | undefined;
}

export interface Entity {
  text: string;
  label: string;
  start?: number;
  end?: number;
  confidence?: number;
  source?: string;
}

export type EntityGroups = Record<string, Entity[]>;

export interface Explanation {
  entity: string;
  label: string;
  confidence?: number;
  reason: string;
}

export interface AnalysisMetadata {
  text_length?: number;
  entity_count?: number;
  privacy?: string;
}

export interface AnalyzeResponse {
  report_id: string | null;
  source_name: string | null;
  patient_details: PatientDetails;
  entities: EntityGroups;
  summary: string;
  explanations: Explanation[];
  metadata: AnalysisMetadata;
}

export interface AnalyzeTextRequest {
  text: string;
  persist?: boolean;
}

export interface HealthResponse {
  status: string;
  service?: string;
}
