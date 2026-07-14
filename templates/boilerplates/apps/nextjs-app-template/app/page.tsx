import { Activity, GitBranch, Layers, ShieldCheck } from "lucide-react";

import { StatusBadge } from "@/components/common/StatusBadge";
import { AppShell } from "@/components/layout/AppShell";
import { EventList } from "@/components/dashboard/EventList";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { SummaryCard } from "@/components/dashboard/SummaryCard";
import {
  APP_NAME,
  CURRENT_STATUS,
  SAMPLE_EVENTS,
  SAMPLE_METRICS,
} from "@/lib/constants";

const extensionPoints = [
  "Replace sample metrics with domain APIs or BFF endpoints.",
  "Add role-based navigation and protected routes.",
  "Connect workflow handoff JSON to dashboard widgets.",
  "Add observability panels for logs, traces, and deployment state.",
];

export default function Home() {
  return (
    <AppShell>
      <div className="page-heading">
        <div>
          <p className="eyebrow">Reusable webapp template</p>
          <h1>{APP_NAME}</h1>
        </div>
        <StatusBadge status={CURRENT_STATUS} />
      </div>

      <section
        className="summary-grid"
        aria-label="Application summary"
        id="overview"
      >
        <SummaryCard
          icon={<ShieldCheck aria-hidden="true" />}
          label="Service status"
          value={CURRENT_STATUS}
          detail="Health endpoint ready"
        />
        <SummaryCard
          icon={<Activity aria-hidden="true" />}
          label="Polling"
          value="3000 ms"
          detail="Configurable interval"
        />
        <SummaryCard
          icon={<GitBranch aria-hidden="true" />}
          label="Workflow fit"
          value="AI-ready"
          detail="Small modules and clear boundaries"
        />
        <SummaryCard
          icon={<Layers aria-hidden="true" />}
          label="Extension"
          value="Generic"
          detail="No business-specific logic"
        />
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>Sample metrics</h2>
            <p>Replace these values with service or product metrics.</p>
          </div>
          <div className="metric-list">
            {SAMPLE_METRICS.map((metric) => (
              <MetricCard key={`${metric.source}-${metric.name}`} metric={metric} />
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <h2>Sample event log</h2>
            <p>Use this region for operational or workflow events.</p>
          </div>
          <EventList events={SAMPLE_EVENTS} />
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Next extension points</h2>
          <p>Keep decisions here until the concrete product workflow owns them.</p>
        </div>
        <div className="extension-list">
          {extensionPoints.map((item) => (
            <div className="extension-item" key={item}>
              {item}
            </div>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
