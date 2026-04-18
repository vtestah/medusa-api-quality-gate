import { retrieveCart } from "@lib/data/cart"
import { retrieveCustomer } from "@lib/data/customer"
import { getTranslator } from "@i18n/get-messages"
import { getMarketConfig } from "@lib/data/markets"
import CartTemplate from "@modules/cart/templates"
import { Metadata } from "next"
import { notFound } from "next/navigation"

export async function generateMetadata(props: {
  params: Promise<{ countryCode: string }>
}): Promise<Metadata> {
  const { countryCode } = await props.params
  const market = getMarketConfig(countryCode)
  const t = await getTranslator(countryCode)

  return {
    title: t("Metadata.cartTitle", { brand: market.brandName }),
    description: t("Metadata.cartDescription", { brand: market.brandName }),
  }
}

export default async function Cart() {
  const cart = await retrieveCart().catch((error) => {
    console.error(error)
    return notFound()
  })

  const customer = await retrieveCustomer()

  return <CartTemplate cart={cart} customer={customer} />
}
