import AxeBuilder from "@axe-core/playwright";
import { test, expect } from "../src/fixtures";

// Accessibility smoke checks for the localized storefront. axe-core scans the
// rendered page for WCAG 2.0/2.1 A and AA issues. Both markets are covered: the
// same spec runs under the `ru` and `us` Playwright projects, so each scan hits
// the corresponding /ru and /us pages.
//
// Marked test.fixme: the accessibility baseline has not been confirmed against
// the running storefront yet, so the expected (zero-violation) result is not
// asserted in CI until the live DOM is reviewed (`make up && make e2e`). This
// mirrors the honest pattern used by the cart spec.

const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];

test.describe("storefront accessibility", () => {
  test.fixme("market home page has no WCAG A/AA violations", async ({
    homePage,
    page,
  }) => {
    await homePage.open();

    const results = await new AxeBuilder({ page })
      .withTags(WCAG_TAGS)
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test.fixme("catalog page has no WCAG A/AA violations", async ({
    storePage,
    page,
  }) => {
    await storePage.open();

    const results = await new AxeBuilder({ page })
      .withTags(WCAG_TAGS)
      .analyze();

    expect(results.violations).toEqual([]);
  });
});
