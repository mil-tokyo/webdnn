import { test, expect } from "@playwright/test";
import { existsSync, readFileSync } from "node:fs";

// The WASM backend needs the emscripten-built worker. `ensure-generated-stubs.mjs`
// supplies a stub worker.ts when emscripten isn't set up; with the stub the WASM
// backend can't run and the runner would silently fall back to CPU. To keep this
// spec HONEST, skip unless the REAL worker (built by `npm run shader:wasm`) is present.
const workerPath =
  "src/descriptor_runner/operators/wasm/worker/worker.ts";
const wasmBuilt =
  existsSync(workerPath) && !readFileSync(workerPath, "utf8").includes("STUB:");

test.skip(
  !wasmBuilt,
  "WASM worker is a stub — run `npm run shader:wasm` (emscripten) then `npm run build`. See docs/emscripten-setup.md",
);

test("WASM backend runs supported ops and reports ALL OK", async ({ page }) => {
  await page.goto("/test/model_test/runner/standard.html");

  for (const cb of await page.locator('input[name="backend"]').all()) {
    const value = await cb.getAttribute("value");
    if (value === "wasm") {
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
