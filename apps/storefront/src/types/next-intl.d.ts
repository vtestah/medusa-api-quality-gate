import enUS from "../i18n/messages/en-US.json"
import { AppLocale } from "../i18n/types"

declare module "next-intl" {
  interface AppConfig {
    Locale: AppLocale
    Messages: typeof enUS
  }
}
