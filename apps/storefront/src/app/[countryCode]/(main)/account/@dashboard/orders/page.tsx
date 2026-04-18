import { Metadata } from "next"

import { getTranslator } from "@i18n/get-messages"
import { getMarketConfig } from "@lib/data/markets"
import OrderOverview from "@modules/account/components/order-overview"
import { notFound } from "next/navigation"
import { listOrders } from "@lib/data/orders"
import Divider from "@modules/common/components/divider"
import TransferRequestForm from "@modules/account/components/transfer-request-form"

export async function generateMetadata(props: {
  params: Promise<{ countryCode: string }>
}): Promise<Metadata> {
  const { countryCode } = await props.params
  const market = getMarketConfig(countryCode)
  const t = await getTranslator(countryCode)

  return {
    title: t("Metadata.ordersTitle", { brand: market.brandName }),
    description: t("Metadata.ordersDescription", { brand: market.brandName }),
  }
}

export default async function Orders(props: {
  params: Promise<{ countryCode: string }>
}) {
  const { countryCode } = await props.params
  const t = await getTranslator(countryCode)
  const orders = await listOrders()

  if (!orders) {
    notFound()
  }

  return (
    <div className="w-full" data-testid="orders-page-wrapper">
      <div className="mb-8 flex flex-col gap-y-4">
        <h1 className="text-2xl-semi">{t("AccountPages.ordersHeading")}</h1>
        <p className="text-base-regular">{t("AccountPages.ordersDescription")}</p>
      </div>
      <div>
        <OrderOverview orders={orders} />
        <Divider className="my-16" />
        <TransferRequestForm />
      </div>
    </div>
  )
}
