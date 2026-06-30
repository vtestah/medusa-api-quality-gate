import { test, expect } from "../src/fixtures";

// Add a product to the cart and confirm the cart count updates. The
// market-specific shipping contract (RU vs US methods) is covered by the Python
// API suite (tests/cart/test_cart_shipping_markets); this spec exercises the
// storefront add-to-cart flow across both markets.
test.describe("cart", () => {
  test("adding a product updates the cart count", async ({ productPage }) => {
    await productPage.open("basis-heavy-tee");

    await productPage.addFirstAvailableVariantToCart();

    // The header cart badge updates after a server revalidation, which is slow
    // in dev mode, so give it room beyond the default assertion timeout.
    await expect(productPage.navCartLink()).toContainText("(1)", {
      timeout: 20000,
    });
  });
});
