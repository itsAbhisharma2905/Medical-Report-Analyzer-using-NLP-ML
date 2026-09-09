import { useEffect, useRef, useState } from "react";
import { Icon } from "./Icon";
import { ErrorMessage } from "./ErrorMessage";

interface FileUploadProps {
  onAnalyze: (file: File) => void | Promise<void>;
  disabled?: boolean;
  resetKey?: number;
}

const MAX_FILE_SIZE = 25 * 1024 * 1024;

function formatFileSize(size: number) {
  if (size < 1024 * 1024) return `${Math.max(1, Math.round(size / 1024))} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileUpload({ onAnalyze, disabled = false, resetKey = 0 }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFile(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }, [resetKey]);

  const acceptFile = (candidate: File | undefined) => {
    if (!candidate) return;
    if (candidate.type !== "application/pdf" && !candidate.name.toLowerCase().endsWith(".pdf")) {
      setError("Please choose a PDF file to continue.");
      return;
    }
    if (candidate.size > MAX_FILE_SIZE) {
      setError("This file is larger than the 25 MB limit.");
      return;
    }
    setError(null);
    setFile(candidate);
  };

  return (
    <div className="upload-panel">
      <div
        className={`dropzone ${isDragging ? "is-dragging" : ""} ${file ? "has-file" : ""}`}
        onDragEnter={(event) => { event.preventDefault(); setIsDragging(true); }}
        onDragOver={(event) => event.preventDefault()}
        onDragLeave={(event) => { event.preventDefault(); setIsDragging(false); }}
        onDrop={(event) => { event.preventDefault(); setIsDragging(false); acceptFile(event.dataTransfer.files[0]); }}
      >
        <input ref={inputRef} type="file" accept="application/pdf,.pdf" onChange={(event) => acceptFile(event.target.files?.[0])} />
        {file ? (
          <div className="selected-file">
            <span className="file-icon"><Icon name="file" /></span>
            <div className="file-meta"><strong>{file.name}</strong><span>{formatFileSize(file.size)} · PDF document</span></div>
            <button className="icon-button" type="button" disabled={disabled} onClick={() => { setFile(null); if (inputRef.current) inputRef.current.value = ""; }} aria-label="Remove selected file"><Icon name="trash" /></button>
          </div>
        ) : (
          <button className="dropzone-action" type="button" onClick={() => inputRef.current?.click()}>
            <span className="upload-icon"><Icon name="upload" /></span>
            <strong>Drop your report here, or <u>browse</u></strong>
            <span>Upload a PDF to begin extracting insights</span>
          </button>
        )}
      </div>
      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}
      <div className="upload-footer"><span><Icon name="check" /> Supported format: PDF</span><span>Maximum size: 25 MB</span></div>
      <button className="button button-primary full-width" type="button" disabled={!file || disabled} onClick={() => file && onAnalyze(file)}>
        Analyze report <Icon name="arrow" />
      </button>
    </div>
  );
}
