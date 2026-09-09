import type { Entity } from "../types/api";

interface EntityListProps {
  items: Entity[];
  emptyLabel: string;
}

export function EntityList({ items, emptyLabel = "No structured findings yet" }: EntityListProps) {
  if (!items.length) return <p className="muted-copy">{emptyLabel}</p>;

  return (
    <div className="entity-list">
      {items.map((item, index) => (
        <div className="entity-item" key={`${item.text}-${item.start ?? index}-${index}`}>
          <strong>{item.text}</strong>
          <span>{item.label || "Finding"}</span>
          <small>
            {typeof item.confidence === "number" ? `Confidence: ${Math.round(item.confidence * 100)}%` : "Confidence: unavailable"}
            {item.source ? ` · Source: ${item.source}` : ""}
          </small>
        </div>
      ))}
    </div>
  );
}
