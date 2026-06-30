import { test } from "../src/fixtures";

// Cart/checkout flow: add the first catalog product, then assert the
// market-specific shipping options appear at the cart/checkout step.
// Marked test.fixme: the Medusa storefront requires selecting a variant before
// the add-to-cart button enables, and the exact selectors must be confirmed
// against the live DOM (`make up && make e2e`). The market shipping *contract*
// is already covered by the Python API suite (tests/cart/test_cart_shipping_markets).
test.describe("cart & market-driven shipping", () => {
  test.fixme("market shipping options are offered for the cart", async ({
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
