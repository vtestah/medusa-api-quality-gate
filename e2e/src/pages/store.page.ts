import { expect, type Locator } from "@playwright/test";
import { BasePage } from "./base.page";

export class StorePage extends BasePage {
  async open(): Promise<void> {
    await this.page.goto(this.marketPath("/store"));
    await expect(this.page).toHaveURL(new RegExp(`${this.market.path}/store`));
  }

  /** Catalog page title (data-testid="store-page-title"). */
  pageTitle(): Locator {
    return this.page.getByTestId("store-page-title");
  }

  /** Product grid container (data-testid="products-list"). */
  productsList(): Locator {
    return this.page.getByTestId("products-list");
  }

  /** Product cards inside the grid (data-testid="product-wrapper"). */
  productCards(): Locator {
    return this.productsList().getByTestId("product-wrapper");
  }

  /** Catalog renders the market currency glyph in pricing (RU ₽ / US $). */
  async expectCurrencyVisible(): Promise<void> {
    await expect(
      this.page.getByText(this.market.currencySymbol, { exact: false }).first(),
    ).toBeVisible();
  }

  /** A localized label should be visible (e.g. RU category "Худи"). */
  async expectTextVisible(text: string): Promise<void> {
    await expect(
      this.page.getByText(text, { exact: false }).first(),
    ).toBeVisible();
  }

  /**
   * First product card link on the catalog. Prefers the real product grid
   * (data-testid="products-list") and its anchor, with a fallback to the
   * previous generic "link wrapping an image" selector so the locator stays
   * resilient if the grid markup changes. The live result should still be
   * confirmed against the running storefront on first use.
   */
  firstProductLink(): Locator {
    return this.page
      .getByTestId("products-list")
      .getByRole("link")
      .or(this.page.getByRole("link").filter({ has: this.page.locator("img") }))
      .first();
  }
}
