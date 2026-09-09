import type { AnalyzeResponse } from "../types/api";
import { EntityList } from "./EntityList";
import { Icon } from "./Icon";
import { LoadingState } from "./LoadingState";
import { PatientDetails } from "./PatientDetails";
import { ResultCard } from "./ResultCard";
import { SummaryCard } from "./SummaryCard";

interface AnalysisResultsProps {
  isLoading: boolean;
  result: AnalyzeResponse | null;
  onReset: () => void;
}

function entitiesFor(result: AnalyzeResponse, ...categories: string[]) {
  return categories.flatMap((category) => result.entities[category] ?? []);
}

export function AnalysisResults({ isLoading, result, onReset }: AnalysisResultsProps) {
  return (
    <section className="results-section" id="results">
      <div className="section-heading results-heading">
        <div><span className="section-kicker">INSIGHTS</span><h2>Analysis results</h2></div>
        {result && <span className="success-badge"><Icon name="check" /> API response received</span>}
      </div>
      {isLoading ? <LoadingState /> : result ? (
        <div className="results-content">
          <div className="result-context"><span className="context-icon"><Icon name="document" /></span><div><strong>{result.source_name ?? "Medical report text"}</strong><span>Live API response · Structured findings</span></div><span className="context-check"><Icon name="check" /> Complete</span></div>
          <div className="metadata-strip"><span><b>Source</b>{result.source_name ?? "Text input"}</span><span><b>Text length</b>{result.metadata.text_length ?? "—"}</span><span><b>Entities detected</b>{result.metadata.entity_count ?? "—"}</span></div>
          <div className="result-grid">
            <ResultCard title="Patient information" eyebrow="PROFILE" icon="medical" accent="blue"><PatientDetails details={result.patient_details} /></ResultCard>
            <ResultCard title="Symptoms" eyebrow="CLINICAL SIGNALS" icon="pulse" accent="green"><EntityList items={entitiesFor(result, "SYMPTOM")} emptyLabel="No symptoms detected." /></ResultCard>
            <ResultCard title="Diagnosis" eyebrow="KEY FINDINGS" icon="clipboard" accent="violet"><EntityList items={entitiesFor(result, "DIAGNOSIS")} emptyLabel="No diagnosis detected." /></ResultCard>
            <ResultCard title="Medicines" eyebrow="TREATMENT" icon="document" accent="amber"><EntityList items={entitiesFor(result, "MEDICINE")} emptyLabel="No medicines detected." /></ResultCard>
            <ResultCard title="Tests & observations" eyebrow="MEASUREMENTS" icon="pulse" accent="blue"><EntityList items={entitiesFor(result, "TEST", "OBSERVATION")} emptyLabel="No tests or observations detected." /></ResultCard>
          </div>
          <SummaryCard summary={result.summary} />
          <button className="button button-secondary another-button" type="button" onClick={onReset}><Icon name="upload" /> Analyze another report</button>
        </div>
      ) : (
        <div className="empty-results">
          <div className="empty-illustration"><span><Icon name="document" /></span><i /><i /><i /></div>
          <h3>Your analysis will appear here</h3>
          <p>Upload a medical report or enter medical text to get structured insights.</p>
          <div className="empty-features"><span><Icon name="check" /> Key entities</span><span><Icon name="check" /> Clear summary</span><span><Icon name="check" /> Organized findings</span></div>
        </div>
      )}
    </section>
  );
}
