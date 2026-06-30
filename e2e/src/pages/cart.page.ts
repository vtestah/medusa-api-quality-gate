import { expect, type Locator } from "@playwright/test";
import { BasePage } from "./base.page";

export class CartPage extends BasePage {
  async open(): Promise<void> {
    await this.page.goto(this.marketPath("/cart"));
  }

  /** Cart page container (data-testid="cart-container"). */
  container(): Locator {
    return this.page.getByTestId("cart-container");
  }

  /** Empty-cart state (data-testid="empty-cart-message"). */
  emptyCartMessage(): Locator {
    return this.page.getByTestId("empty-cart-message");
  }

  /** Delivery options block shown at the checkout shipping step
   *  (data-testid="delivery-options-container"). */
  deliveryOptions(): Locator {
    return this.page.getByTestId("delivery-options-container");
  }

  /** Individual selectable delivery options (data-testid="delivery-option-radio"). */
  deliveryOptionRadios(): Locator {
    return this.page.getByTestId("delivery-option-radio");
  }

  /**
   * Market-driven shipping options should be offered at the cart/checkout step.
   * README proof points: RU -> Курьер / ПВЗ / Самовывоз, US -> Standard / Express.
   * Scopes to the delivery options container when it is present, otherwise
   * falls back to a page-level text match.
   */
  async expectMarketShippingMethods(): Promise<void> {
    const scoped = (await this.deliveryOptions().count()) > 0;
    for (const method of this.market.shippingMethods) {
      const locator = scoped
        ? this.deliveryOptions().getByText(method, { exact: false })
        : this.page.getByText(method, { exact: false });
      await expect(locator.first()).toBeVisible();
    }
  }
}
