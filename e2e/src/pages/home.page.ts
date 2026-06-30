import { expect, type Locator } from "@playwright/test";
import { BasePage } from "./base.page";

export class HomePage extends BasePage {
  /** Open the market home, e.g. /ru or /us. */
  async open(): Promise<void> {
    await this.page.goto(this.marketPath());
    await expect(this.page).toHaveURL(
      new RegExp(`${this.market.path}/?($|\\?)`),
    );
  }

  /** Root path should redirect into a localized market (README: "/" -> "/ru"). */
  async openRootAndExpectMarketRedirect(): Promise<void> {
    await this.page.goto("/");
    await expect(this.page).toHaveURL(/\/(ru|us)(\/|$|\?)/);
  }

  /** Hero headline; role-based so it holds across the RU/US locales. */
  heading(): Locator {
    return this.page.getByRole("heading", { level: 1 }).first();
  }

  /** Hero call-to-action into the catalog. Targeted by href suffix so it does
   *  not depend on the localized button label. */
  catalogLink(): Locator {
    return this.page.locator('a[href$="/store"]').first();
  }
}
