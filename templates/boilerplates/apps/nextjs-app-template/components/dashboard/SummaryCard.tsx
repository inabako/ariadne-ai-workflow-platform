import type { ReactNode } from "react";

type SummaryCardProps = {
  icon: ReactNode;
  label: string;
  value: string;
  detail: string;
};

export function SummaryCard({ icon, label, value, detail }: SummaryCardProps) {
  return (
    <article className="summary-card">
      <span className="summary-icon">{icon}</span>
      <div>
        <div className="summary-label">{label}</div>
        <div className="summary-value">{value}</div>
      </div>
      <div className="summary-detail">{detail}</div>
    </article>
  );
}
