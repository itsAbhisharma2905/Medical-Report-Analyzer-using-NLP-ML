import { Icon } from "./Icon";

interface LoadingStateProps {
  label?: string;
}

export function LoadingState({ label = "Analyzing medical report..." }: LoadingStateProps) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <span className="spinner"><Icon name="spark" /></span>
      <div><strong>{label}</strong><span>Extracting structured insights from your input</span></div>
    </div>
  );
}
