"use client"

import {
  NextIntlClientProvider,
} from "next-intl"

import { StorefrontMessages } from "./get-messages"
import { AppLocale } from "./types"

type StorefrontIntlProviderProps = {
  children: React.ReactNode
  locale: AppLocale
  messages: StorefrontMessages
}

export default function StorefrontIntlProvider({
  children,
  locale,
  messages,
}: StorefrontIntlProviderProps) {
  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      {children}
    </NextIntlClientProvider>
  )
}
