import { type Locator } from "@playwright/test";
import { BasePage } from "./base.page";

export class ProductPage extends BasePage {
  /** Open a product detail page by its handle. */
  async open(handle: string): Promise<void> {
    await this.page.goto(this.marketPath(`/products/${handle}`));
  }

  /** Variant option groups on the product page (Color, Size, ...). */
  optionGroups(): Locator {
    return this.page.getByTestId("product-options");
  }

  /** Add-to-cart button; stays disabled until an in-stock variant is chosen. */
  addToCartButton(): Locator {
    return this.page.getByTestId("add-product-button");
  }

  /**
   * Select a purchasable variant and add it to the cart. The first value is
   * chosen in every option group except the last; the last group is then tried
   * value by value until the add-to-cart button enables, since some demo
   * variants are intentionally out of stock.
   */
  async addFirstAvailableVariantToCart(): Promise<void> {
    const groups = this.optionGroups();
    const groupCount = await groups.count();
    const addButton = this.addToCartButton();

    for (let i = 0; i < groupCount - 1; i++) {
      await groups.nth(i).getByTestId("option-button").first().click();
    }

    if (groupCount > 0) {
      const lastOptions = groups.nth(groupCount - 1).getByTestId("option-button");
      const optionCount = await lastOptions.count();
      for (let j = 0; j < optionCount; j++) {
        await lastOptions.nth(j).click();
        if (await addButton.isEnabled()) {
          break;
        }
      }
    }

    await addButton.click();
  }
}
