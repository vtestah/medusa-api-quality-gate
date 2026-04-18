import { Metadata } from "next"
import { notFound } from "next/navigation"

import { getTranslator } from "@i18n/get-messages"
import { getMarketConfig } from "@lib/data/markets"
import AddressBook from "@modules/account/components/address-book"

import { getRegion } from "@lib/data/regions"
import { retrieveCustomer } from "@lib/data/customer"

export async function generateMetadata(props: {
  params: Promise<{ countryCode: string }>
}): Promise<Metadata> {
  const { countryCode } = await props.params
  const market = getMarketConfig(countryCode)
  const t = await getTranslator(countryCode)

  return {
    title: t("Metadata.addressesTitle", { brand: market.brandName }),
    description: t("Metadata.addressesDescription", { brand: market.brandName }),
  }
}

export default async function Addresses(props: {
  params: Promise<{ countryCode: string }>
}) {
  const params = await props.params
  const { countryCode } = params
  const t = await getTranslator(countryCode)
  const customer = await retrieveCustomer()
  const region = await getRegion(countryCode)

  if (!customer || !region) {
    notFound()
  }

  return (
    <div className="w-full" data-testid="addresses-page-wrapper">
      <div className="mb-8 flex flex-col gap-y-4">
        <h1 className="text-2xl-semi">{t("AccountPages.addressesHeading")}</h1>
        <p className="text-base-regular">{t("AccountPages.addressesDescription")}</p>
      </div>
      <AddressBook customer={customer} region={region} />
    </div>
  )
}
