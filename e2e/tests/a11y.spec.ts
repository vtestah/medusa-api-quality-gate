import AxeBuilder from "@axe-core/playwright";
import { test, expect } from "../src/fixtures";

// Accessibility smoke checks. axe-core scans the rendered page for WCAG 2.0/2.1
// A and AA issues. The same spec runs under the ru and us projects, so each scan
// hits the matching /ru and /us pages.
//
// The gate is on critical-impact issues. The upstream Medusa storefront still
// has serious-level findings (mostly color contrast on muted text), which are
// tracked separately and not blocked here; a critical regression should fail.

const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];

test.describe("storefront accessibility", () => {
  test("market home has no critical a11y violations", async ({
    homePage,
    page,
  }) => {
    await homePage.open();

    const results = await new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
    const critical = results.violations.filter((v) => v.impact === "critical");

    expect(critical).toEqual([]);
  });

  test("catalog has no critical a11y violations", async ({
    storePage,
    page,
  }) => {
    await storePage.open();

    const results = await new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
    const critical = results.violations.filter((v) => v.impact === "critical");

    expect(critical).toEqual([]);
  });
});
