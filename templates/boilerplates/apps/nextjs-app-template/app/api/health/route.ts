import { APP_NAME, CURRENT_STATUS } from "@/lib/constants";
import type { HealthResponse } from "@/lib/types";

export function GET(): Response {
  const payload: HealthResponse = {
    status: CURRENT_STATUS,
    service: APP_NAME,
    timestamp: new Date().toISOString(),
  };

  return Response.json(payload);
}
