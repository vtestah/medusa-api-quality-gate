import { type Locator, type Page, expect } from "@playwright/test";
import type { MarketProfile } from "../market";

export abstract class BasePage {
  constructor(
    protected readonly page: Page,
    protected readonly market: MarketProfile,
  ) {}

  /** Build a market-prefixed path: "/ru" + "/store" -> "/ru/store". */
  protected marketPath(suffix = ""): string {
    return `${this.market.path}${suffix}`;
  }

  /** Header brand/home link (data-testid="nav-store-link" in the storefront nav). */
  navStoreLink(): Locator {
    return this.page.getByTestId("nav-store-link").first();
  }

  /** Header cart link (data-testid="nav-cart-link"); renders for both the
   *  Suspense fallback and the resolved cart button. */
  navCartLink(): Locator {
    return this.page.getByTestId("nav-cart-link").first();
  }

  /** next-intl sets <html lang>; assert it matches the market locale. */
  async expectLocalizedHtmlLang(): Promise<void> {
    await expect(this.page.locator("html")).toHaveAttribute(
      "lang",
      this.market.locale,
    );
  }
}
