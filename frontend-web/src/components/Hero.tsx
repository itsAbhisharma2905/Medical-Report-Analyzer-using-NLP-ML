import { Icon } from "./Icon";

interface HeroProps {
  onUpload: () => void;
  onText: () => void;
}

export function Hero({ onUpload, onText }: HeroProps) {
  return (
    <section className="hero" id="top">
      <div className="hero-copy">
        <div className="eyebrow"><span className="eyebrow-line" /> NLP-powered analysis</div>
        <h1>Understand your medical reports <em>faster.</em></h1>
        <p className="hero-description">
          Transform complex clinical language into structured, readable insights. Upload a PDF or paste medical text to explore key findings in one focused workspace.
        </p>
        <div className="hero-actions">
          <button className="button button-primary" type="button" onClick={onUpload}>
            <Icon name="upload" />
            Upload report
          </button>
          <button className="button button-secondary" type="button" onClick={onText}>
            Analyze text
            <Icon name="arrow" />
          </button>
        </div>
        <div className="hero-note"><Icon name="shield" /> Designed with privacy-conscious workflows in mind</div>
      </div>

      <div className="hero-visual" aria-label="Illustration of structured medical insights">
        <div className="orb orb-one" />
        <div className="orb orb-two" />
        <div className="report-preview">
          <div className="preview-topline"><span className="preview-icon"><Icon name="document" /></span><span>REPORT INSIGHT</span><b>READY</b></div>
          <div className="preview-title">Clinical overview</div>
          <div className="preview-text-line long" /><div className="preview-text-line" /><div className="preview-text-line short" />
          <div className="preview-divider" />
          <div className="preview-grid">
            <div><span className="preview-label">KEY FINDING</span><strong>Structured</strong></div>
            <div><span className="preview-label">CONFIDENCE</span><strong>High</strong></div>
          </div>
          <div className="preview-tag-row"><span>Diagnosis</span><span>Symptoms</span><span>Observations</span></div>
        </div>
        <div className="floating-card insight-card"><span className="floating-icon green"><Icon name="check" /></span><span><b>Insights organized</b><small>Clear and actionable</small></span></div>
        <div className="floating-card privacy-card"><span className="floating-icon blue"><Icon name="lock" /></span><span><b>Privacy first</b><small>Data-conscious design</small></span></div>
      </div>
    </section>
  );
}
