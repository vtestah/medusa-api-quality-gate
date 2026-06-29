import { test } from "../src/fixtures";

test.describe("localization & market", () => {
  test("html lang matches the market locale", async ({ homePage }) => {
    await homePage.open();
    await homePage.expectLocalizedHtmlLang();
  });

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
