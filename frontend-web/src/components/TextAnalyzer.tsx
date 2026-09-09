import { useEffect, useState } from "react";
import { Icon } from "./Icon";
import { ErrorMessage } from "./ErrorMessage";

interface TextAnalyzerProps {
  onAnalyze: (text: string) => void | Promise<void>;
  disabled?: boolean;
  resetKey?: number;
}

const MAX_CHARS = 5000;

export function TextAnalyzer({ onAnalyze, disabled = false, resetKey = 0 }: TextAnalyzerProps) {
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setText("");
    setError(null);
  }, [resetKey]);

  const analyze = () => {
    if (!text.trim()) {
      setError("Enter some medical text before starting an analysis.");
      return;
    }
    setError(null);
    onAnalyze(text.trim());
  };

  return (
    <div className="text-panel">
      <div className="textarea-wrap">
        <textarea
          value={text}
          maxLength={MAX_CHARS}
          onChange={(event) => setText(event.target.value)}
          placeholder="Paste a medical report, clinical note, or observation here..."
          aria-label="Medical report text"
        />
        <div className="textarea-footer"><span>Text input</span><span>{text.length.toLocaleString()} / {MAX_CHARS.toLocaleString()}</span></div>
      </div>
      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}
      <button className="button button-dark full-width" type="button" disabled={disabled} onClick={analyze}>Analyze text <Icon name="arrow" /></button>
    </div>
  );
}
