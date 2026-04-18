import { Metadata } from "next"

import { getTranslator } from "@i18n/get-messages"
import { getMarketConfig } from "@lib/data/markets"
import LoginTemplate from "@modules/account/templates/login-template"

export async function generateMetadata(props: {
  params: Promise<{ countryCode: string }>
}): Promise<Metadata> {
  const { countryCode } = await props.params
  const market = getMarketConfig(countryCode)
  const t = await getTranslator(countryCode)

  return {
    title: t("Metadata.signInTitle", { brand: market.brandName }),
    description: t("Metadata.signInDescription", { brand: market.brandName }),
  }
}

export default function Login() {
  return <LoginTemplate />
}
