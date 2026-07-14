import type { AppStatus } from "@/lib/types";

type StatusBadgeProps = {
  status: AppStatus;
};

const statusClassName: Record<AppStatus, string> = {
  UP: "status-up",
  DOWN: "status-down",
  DEGRADED: "status-degraded",
  UNKNOWN: "status-unknown",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`status-badge ${statusClassName[status]}`}>
      {status}
    </span>
  );
}
