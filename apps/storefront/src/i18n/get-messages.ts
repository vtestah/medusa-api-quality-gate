import { getMarketConfig } from "@lib/data/markets"
import { createTranslator } from "next-intl"

import { AppLocale } from "./types"
import enUS from "./messages/en-US.json"

export type StorefrontMessages = typeof enUS

const messageLoaders: Record<
  AppLocale,
  () => Promise<{ default: StorefrontMessages }>
> = {
  "ru-RU": () => import("./messages/ru-RU.json"),
  "en-US": () => import("./messages/en-US.json"),
}

export async function getMessages(
  locale: AppLocale
): Promise<StorefrontMessages> {
  return (await messageLoaders[locale]()).default
}

export async function getIntlConfig(countryCode: string) {
  const market = getMarketConfig(countryCode)
  const locale = market.locale as AppLocale
  const messages = await getMessages(locale)

  return {
    locale,
    market,
    messages,
  }
}

export async function getTranslator(countryCode: string) {
  const { locale, messages } = await getIntlConfig(countryCode)

  return createTranslator({
    locale,
    messages,
  })
}
