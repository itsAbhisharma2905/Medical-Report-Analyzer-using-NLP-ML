import type { ReactNode } from "react";
import { Icon } from "./Icon";

interface ResultCardProps {
  title: string;
  eyebrow: string;
  icon: "medical" | "pulse" | "clipboard" | "document";
  children: ReactNode;
  accent?: "blue" | "green" | "violet" | "amber";
}

export function ResultCard({ title, eyebrow, icon, children, accent = "blue" }: ResultCardProps) {
  return (
    <article className={`result-card accent-${accent}`}>
      <div className="result-card-header"><span className="result-card-icon"><Icon name={icon} /></span><div><span>{eyebrow}</span><h3>{title}</h3></div></div>
      <div className="result-card-body">{children}</div>
    </article>
  );
}
