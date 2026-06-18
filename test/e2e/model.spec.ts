import { test, expect } from "@playwright/test";

// Verifies the CPU backend headlessly. WebGL/WebGPU require real GPUs and are
// checked on real machines (see docs/testing.md), not here.
test("CPU backend runs all model cases and reports ALL OK", async ({ page }) => {
  await page.goto("/test/model_test/runner/standard.html");

  // Uncheck every backend checkbox so only CPU runs.
  for (const cb of await page.locator('input[name="backend"]').all()) {
    if (await cb.isChecked()) await cb.uncheck();
  }

  await page.getByRole("button", { name: "Test" }).click();

  const summary = page.locator("#summary");
  await expect(summary).toBeVisible({ timeout: 100_000 });
  await expect(summary).toContainText("ALL OK");
  await expect(summary).toContainText("0 failed");
});
