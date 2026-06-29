import { expect } from "@playwright/test";
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
}
