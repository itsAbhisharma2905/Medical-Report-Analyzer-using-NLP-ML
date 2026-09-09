import { useEffect, useRef, useState } from "react";
import { analyzeText, checkHealth, uploadReport } from "../services/api";
import type { AnalyzeResponse } from "../types/api";
import { AnalysisResults } from "../components/AnalysisResults";
import { Disclaimer } from "../components/Disclaimer";
import { ErrorMessage } from "../components/ErrorMessage";
import { FileUpload } from "../components/FileUpload";
import { Header } from "../components/Header";
import { Hero } from "../components/Hero";
import { Icon } from "../components/Icon";
import { TextAnalyzer } from "../components/TextAnalyzer";

type HealthStatus = "checking" | "connected" | "unavailable";

export function Dashboard() {
  const uploadRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [resetKey, setResetKey] = useState(0);
  const [healthStatus, setHealthStatus] = useState<HealthStatus>("checking");

  useEffect(() => {
    let active = true;
    checkHealth()
      .then((healthy) => active && setHealthStatus(healthy ? "connected" : "unavailable"))
      .catch(() => active && setHealthStatus("unavailable"));
    return () => { active = false; };
  }, []);

  const scrollTo = (element: HTMLDivElement | null) => element?.scrollIntoView({ behavior: "smooth", block: "center" });

  const runAnalysis = async (request: () => Promise<AnalyzeResponse>) => {
    if (isLoading) return;
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await request();
      setResult(response);
      window.setTimeout(() => document.getElementById("results")?.scrollIntoView({ behavior: "smooth", block: "start" }), 0);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to analyze the report. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetAnalysis = () => {
    setResult(null);
    setError(null);
    setIsLoading(false);
    setResetKey((current) => current + 1);
    window.setTimeout(() => scrollTo(uploadRef.current), 0);
  };

  return (
    <div className="app-shell">
      <Header />
      <main>
        <Hero onUpload={() => scrollTo(uploadRef.current)} onText={() => scrollTo(textRef.current)} />

        <section className="workspace" id="workspace">
          <div className="workspace-intro"><div><span className="section-kicker">START HERE</span><h2>Choose your input</h2></div><p>Send a PDF or medical text to the deployed FastAPI analysis service.</p></div>
          {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}
          <div className="input-grid">
            <div className="input-card" ref={uploadRef}><div className="input-card-heading"><span className="heading-icon blue"><Icon name="upload" /></span><div><h3>Upload a report</h3><p>Analyze a PDF medical report</p></div><span className="step-number">01</span></div><FileUpload disabled={isLoading} resetKey={resetKey} onAnalyze={(file) => runAnalysis(() => uploadReport(file))} /></div>
            <div className="input-card" ref={textRef}><div className="input-card-heading"><span className="heading-icon violet"><Icon name="document" /></span><div><h3>Analyze text</h3><p>Paste a clinical note or report</p></div><span className="step-number">02</span></div><TextAnalyzer disabled={isLoading} resetKey={resetKey} onAnalyze={(text) => runAnalysis(() => analyzeText(text))} /></div>
          </div>
        </section>

        <AnalysisResults isLoading={isLoading} result={result} onReset={resetAnalysis} />
        <Disclaimer />
      </main>
      <footer className="site-footer"><span>Medical Report Analyzer</span><span className={`api-health health-${healthStatus}`}><i />{healthStatus === "checking" ? "Checking API" : healthStatus === "connected" ? "API Connected" : "API Unavailable"}</span><span>Built for educational and research exploration</span><span>© 2026</span></footer>
    </div>
  );
}
