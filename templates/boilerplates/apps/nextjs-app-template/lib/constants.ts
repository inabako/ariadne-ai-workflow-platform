import type { AppEvent, AppMetric, AppStatus } from "./types";

export const APP_NAME =
  process.env.NEXT_PUBLIC_APP_NAME?.trim() || "Sample Next.js App";

export const APP_VERSION =
  process.env.NEXT_PUBLIC_APP_VERSION?.trim() || "0.1.0";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || "http://localhost:3000";

export const POLLING_INTERVAL_MS = Number(
  process.env.NEXT_PUBLIC_POLLING_INTERVAL_MS ?? 3000,
);

export const CURRENT_STATUS: AppStatus = "UP";

export const SAMPLE_METRICS: AppMetric[] = [
  {
    timestamp: new Date().toISOString(),
    source: "webapp",
    name: "Availability",
    value: 99.95,
    unit: "%",
  },
  {
    timestamp: new Date().toISOString(),
    source: "api",
    name: "API latency",
    value: 124,
    unit: "ms",
  },
  {
    timestamp: new Date().toISOString(),
    source: "workflow",
    name: "Open actions",
    value: 7,
  },
];

export const SAMPLE_EVENTS: AppEvent[] = [
  {
    timestamp: new Date().toISOString(),
    level: "INFO",
    source: "health",
    message: "Health endpoint responded successfully.",
  },
  {
    timestamp: new Date().toISOString(),
    level: "WARN",
    source: "workflow",
    message: "Replace sample data before connecting production services.",
  },
  {
    timestamp: new Date().toISOString(),
    level: "INFO",
    source: "dashboard",
    message: "Dashboard shell loaded.",
  },
];
