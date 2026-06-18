import { test, expect } from "@playwright/test";

test("WebGL backend runs supported ops and reports ALL OK", async ({ page }) => {
  await page.goto("/test/model_test/runner/standard.html");

  // WebGL2 is broadly available, but headless GL (and float-texture support)
  // can be flaky; skip cleanly if unavailable and defer to real-machine checks.
  const hasWebGL2 = await page.evaluate(() => {
    const c = document.createElement("canvas");
    return !!c.getContext("webgl2");
  });
  test.skip(
    !hasWebGL2,
    "WebGL2 unavailable in this headless browser; verify on a real machine (docs/testing.md)",
  );

  for (const cb of await page.locator('input[name="backend"]').all()) {
    const value = await cb.getAttribute("value");
    if (value === "webgl") {
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
