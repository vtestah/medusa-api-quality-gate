import { expect } from "@playwright/test";
import { BasePage } from "./base.page";

export class CartPage extends BasePage {
  async open(): Promise<void> {
    await this.page.goto(this.marketPath("/cart"));
  }

  /**
   * Market-driven shipping options should be offered at the cart/checkout step.
   * README proof points: RU -> Курьер / ПВЗ / Самовывоз, US -> Standard / Express.
   */
  async expectMarketShippingMethods(): Promise<void> {
    for (const method of this.market.shippingMethods) {
      await expect(
        this.page.getByText(method, { exact: false }).first(),
      ).toBeVisible();
    }
  }
}
