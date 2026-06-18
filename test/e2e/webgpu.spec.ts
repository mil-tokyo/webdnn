import { test, expect } from "@playwright/test";

test("WebGPU backend runs WebGPU-supported ops and reports ALL OK", async ({
  page,
}) => {
  await page.goto("/test/model_test/runner/standard.html");

  // Skip cleanly if this browser/GPU has no WebGPU (CI / unsupported machines).
  const hasWebGPU = await page.evaluate(() => "gpu" in navigator);
  test.skip(
    !hasWebGPU,
    "navigator.gpu unavailable; verify on a real GPU machine (docs/testing.md)",
  );

  // Enable only the WebGPU backend checkbox. The runner uses backendOrder
  // [webgpu, cpu], so ops WebGPU doesn't support fall back to CPU -- ALL OK
  // still means every WebGPU-executed op produced correct numbers.
  for (const cb of await page.locator('input[name="backend"]').all()) {
    const value = await cb.getAttribute("value");
    if (value === "webgpu") {
      if (!(await cb.isChecked())) await cb.check();
    } else if (await cb.isChecked()) {
      await cb.uncheck();
    }
  }

  await page.getByRole("button", { name: "Test" }).click();

  const summary = page.locator("#summary");
  await expect(summary).toBeVisible({ timeout: 100_000 });
  await expect(summary).toContainText("ALL OK");
  await expect(summary).toContainText("0 failed");
});
