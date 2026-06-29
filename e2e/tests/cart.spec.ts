import { test } from "../src/fixtures";

// Cart/checkout flow: add the first catalog product, then assert the
// market-specific shipping options appear at the cart/checkout step.
// The add-to-cart selectors are intentionally locale/role based; confirm them
// against the live storefront DOM on the first `make up && make e2e` run.
test.describe("cart & market-driven shipping", () => {
  test("market shipping options are offered for the cart", async ({
    storePage,
    cartPage,
    page,
  }) => {
    await storePage.open();
    await storePage.firstProductLink().click();

    await page
      .getByRole("button", { name: /(в корзину|добавить|add to cart|add to bag)/i })
      .first()
      .click();

    await cartPage.open();
    await cartPage.expectMarketShippingMethods();
  });
});
