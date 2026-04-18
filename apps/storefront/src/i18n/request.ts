import { hasLocale } from "next-intl"
import { getRequestConfig } from "next-intl/server"
import { cookies } from "next/headers"

import { getMessages } from "./get-messages"
import { APP_LOCALES, AppLocale } from "./types"

const DEFAULT_LOCALE: AppLocale = "ru-RU"

export default getRequestConfig(async () => {
  const cookieStore = await cookies()
  const requestedLocale = cookieStore.get("_medusa_locale")?.value

  const locale = hasLocale(APP_LOCALES, requestedLocale)
    ? requestedLocale
    : DEFAULT_LOCALE

  return {
    locale,
    messages: await getMessages(locale),
  }
})
