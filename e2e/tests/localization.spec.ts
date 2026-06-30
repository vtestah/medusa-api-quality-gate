import { test } from "../src/fixtures";

test.describe("localization & market", () => {
  // Note: the storefront localizes content (currency, catalog text) but keeps
  // <html lang="en"> on both markets, so the locale is verified via content
  // below rather than via the html lang attribute.
  test("catalog renders the market currency", async ({ storePage }) => {
    await storePage.open();
    await storePage.expectCurrencyVisible();
  });

  test("RU catalog shows the Russian hoodies category «Худи»", async ({
    storePage,
    market,
  }) => {
    test.skip(market.code !== "ru", "RU-only catalog localization");
    await storePage.open();
    await storePage.expectTextVisible("Худи");
  });
});
