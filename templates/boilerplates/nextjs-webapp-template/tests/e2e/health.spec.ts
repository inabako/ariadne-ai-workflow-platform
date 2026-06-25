import { expect, test } from "@playwright/test";

test("health endpoint returns UP", async ({ request }) => {
  const response = await request.get("/api/health");
  expect(response.ok()).toBe(true);

  const body = await response.json();
  expect(body.status).toBe("UP");
  expect(body.service).toBeTruthy();
  expect(body.timestamp).toBeTruthy();
});

test("dashboard page renders", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Sample Next\.js App/i })).toBeVisible();
  await expect(page.getByText("Sample metrics")).toBeVisible();
  await expect(page.getByText("Sample event log")).toBeVisible();
});
