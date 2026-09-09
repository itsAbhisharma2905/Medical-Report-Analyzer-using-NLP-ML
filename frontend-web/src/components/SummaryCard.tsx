import { Icon } from "./Icon";

interface SummaryCardProps {
  summary: string;
}

export function SummaryCard({ summary }: SummaryCardProps) {
  return <article className="summary-card"><div className="summary-icon"><Icon name="spark" /></div><div><span className="card-eyebrow">GENERATED OVERVIEW</span><h3>Summary</h3><p>{summary}</p></div></article>;
}
