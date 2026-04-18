export const APP_LOCALES = ["ru-RU", "en-US"] as const

export type AppLocale = (typeof APP_LOCALES)[number]
