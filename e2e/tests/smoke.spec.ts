import { test, expect } from "../src/fixtures";

test.describe("storefront smoke", () => {
  test("root redirects into a localized market", async ({ homePage }) => {
    await homePage.openRootAndExpectMarketRedirect();
  });

  test("market home loads", async ({ homePage, page, market }) => {
    await homePage.open();
    await expect(page).toHaveURL(new RegExp(`${market.path}(/|$|\\?)`));
  });
});
