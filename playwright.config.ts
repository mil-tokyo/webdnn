import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "test/e2e",
  timeout: 120_000,
  fullyParallel: false,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:8080",
  },
  webServer: {
    command: "npx http-server -c-1 -p 8080 .",
    url: "http://localhost:8080/test/model_test/runner/standard.html",
    reuseExistingServer: true,
    timeout: 60_000,
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        launchOptions: {
          args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan"],
        },
      },
    },
  ],
});
