import { formatMetricValue } from "@/lib/format";
import type { AppMetric } from "@/lib/types";

type MetricCardProps = {
  metric: AppMetric;
};

export function MetricCard({ metric }: MetricCardProps) {
  return (
    <article className="metric-card">
      <div>
        <div className="metric-source">{metric.source}</div>
        <div className="metric-name">{metric.name}</div>
      </div>
      <div className="metric-value">
        {formatMetricValue(metric.value, metric.unit)}
      </div>
    </article>
  );
}
