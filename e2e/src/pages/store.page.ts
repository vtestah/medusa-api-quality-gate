import { expect, type Locator } from "@playwright/test";
import { BasePage } from "./base.page";

export class StorePage extends BasePage {
  async open(): Promise<void> {
    await this.page.goto(this.marketPath("/store"));
    await expect(this.page).toHaveURL(new RegExp(`${this.market.path}/store`));
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
   * First product card link on the catalog. Selector is intentionally generic
   * (a link wrapping a product image) and should be confirmed against the live
   * storefront DOM on first run.
   */
  firstProductLink(): Locator {
    return this.page
      .getByRole("link")
      .filter({ has: this.page.locator("img") })
      .first();
  }
}
