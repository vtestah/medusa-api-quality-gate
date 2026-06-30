// Canonical RU/US market profiles. The market is selected by URL prefix
// (/ru, /us); these mirror the runtime proof points documented in the repo README.

export type MarketCode = "ru" | "us";

export interface MarketProfile {
  code: MarketCode;
  path: string; // localized prefix, e.g. "/ru"
  locale: string; // <html lang> value
  currency: string; // ISO code
  currencySymbol: string; // glyph rendered on the catalog
  shippingMethods: string[]; // market-specific shipping options
}

export const MARKETS: Record<MarketCode, MarketProfile> = {
  ru: {
    code: "ru",
    path: "/ru",
    locale: "ru",
    currency: "RUB",
    currencySymbol: "₽",
    shippingMethods: ["Курьер", "ПВЗ", "Самовывоз"],
  },
  us: {
    code: "us",
    path: "/us",
    locale: "en",
    currency: "USD",
    currencySymbol: "$",
    shippingMethods: ["Standard Shipping", "Express Shipping"],
  },
};
