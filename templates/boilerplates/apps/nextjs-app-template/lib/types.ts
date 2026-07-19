export type AppStatus = "UP" | "DOWN" | "DEGRADED" | "UNKNOWN";

export type AppEvent = {
  timestamp: string;
  level: "INFO" | "WARN" | "ERROR";
  source: string;
  message: string;
  traceId?: string;
  metadata?: Record<string, unknown>;
};

export type AppMetric = {
  timestamp: string;
  source: string;
  name: string;
  value: number;
  unit?: string;
};

export type HealthResponse = {
  status: AppStatus;
  service: string;
  timestamp: string;
};
