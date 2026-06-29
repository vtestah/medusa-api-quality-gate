import { type Page, expect } from "@playwright/test";
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

  /** next-intl sets <html lang>; assert it matches the market locale. */
  async expectLocalizedHtmlLang(): Promise<void> {
    await expect(this.page.locator("html")).toHaveAttribute(
      "lang",
      this.market.locale,
    );
  }
}
