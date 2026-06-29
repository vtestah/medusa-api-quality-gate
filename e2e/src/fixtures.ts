import { test as base } from "@playwright/test";
import { MARKETS, type MarketCode, type MarketProfile } from "./market";
import { HomePage } from "./pages/home.page";
import { StorePage } from "./pages/store.page";
import { CartPage } from "./pages/cart.page";

// Per-project option: which market this run targets.
export interface TestOptions {
  marketCode: MarketCode;
}

export interface TestFixtures {
  market: MarketProfile;
  homePage: HomePage;
  storePage: StorePage;
  cartPage: CartPage;
}

export const test = base.extend<TestOptions & TestFixtures>({
  marketCode: ["ru", { option: true }],
  market: async ({ marketCode }, use) => {
    await use(MARKETS[marketCode]);
  },
  homePage: async ({ page, market }, use) => {
    await use(new HomePage(page, market));
  },
  storePage: async ({ page, market }, use) => {
    await use(new StorePage(page, market));
  },
  cartPage: async ({ page, market }, use) => {
    await use(new CartPage(page, market));
  },
});

export { expect } from "@playwright/test";
