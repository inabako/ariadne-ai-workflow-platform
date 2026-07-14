import { describe, expect, it } from "vitest";

import { formatMetricValue } from "@/lib/format";

describe("formatMetricValue", () => {
  it("formats integers without units", () => {
    expect(formatMetricValue(1200)).toBe("1,200");
  });

  it("formats decimal values with units", () => {
    expect(formatMetricValue(99.955, "%")).toBe("99.96 %");
  });
});
