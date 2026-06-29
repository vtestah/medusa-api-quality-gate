import { defineConfig, devices } from "@playwright/test";
import type { TestOptions } from "./src/fixtures";

// Storefront base URL; overridable for CI / non-default hosts.
const baseURL = process.env.STOREFRONT_BASE_URL ?? "http://localhost:8000";

export default defineConfig<TestOptions>({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  // Each market is a project: same specs, different localized prefix/currency.
  projects: [
    {
      name: "ru",
      use: { ...devices["Desktop Chrome"], marketCode: "ru" },
    },
    {
      name: "us",
      use: { ...devices["Desktop Chrome"], marketCode: "us" },
    },
  ],
});
