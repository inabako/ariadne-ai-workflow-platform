import type { HealthResponse } from "./types";

export async function fetchHealth(
  baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "",
): Promise<HealthResponse> {
  const response = await fetch(`${baseUrl}/api/health`, {
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }

  return response.json() as Promise<HealthResponse>;
}
