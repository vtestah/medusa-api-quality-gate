import React from "react"
import { CreditCard } from "@medusajs/icons"

import Ideal from "@modules/common/icons/ideal"
import Bancontact from "@modules/common/icons/bancontact"
import PayPal from "@modules/common/icons/paypal"
import { getMarketConfig, getMarketConfigByCurrency } from "@lib/data/markets"

/* Map of payment provider_id to their title and icon. Add in any payment providers you want to use. */
export const paymentInfoMap: Record<
  string,
  { title: string; icon: React.JSX.Element }
> = {
  pp_stripe_stripe: {
    title: "Credit card",
    icon: <CreditCard />,
  },
  "pp_medusa-payments_default": {
    title: "Credit card",
    icon: <CreditCard />,
  },
  "pp_stripe-ideal_stripe": {
    title: "iDeal",
    icon: <Ideal />,
  },
  "pp_stripe-bancontact_stripe": {
    title: "Bancontact",
    icon: <Bancontact />,
  },
  pp_paypal_paypal: {
    title: "PayPal",
    icon: <PayPal />,
  },
  pp_system_default: {
    title: "Manual Payment",
    icon: <CreditCard />,
  },
  // Add more payment providers here
}

export const getPaymentInfoMap = (input?: {
  countryCode?: string | null
  currencyCode?: string | null
}): Record<string, { title: string; icon: React.JSX.Element }> => {
  const market = input?.countryCode
    ? getMarketConfig(input.countryCode)
    : getMarketConfigByCurrency(input?.currencyCode)

  return {
    ...paymentInfoMap,
    pp_stripe_stripe: {
      title:
        market.code === "ru"
          ? "Банковская карта"
          : paymentInfoMap.pp_stripe_stripe.title,
      icon: paymentInfoMap.pp_stripe_stripe.icon,
    },
    "pp_medusa-payments_default": {
      title:
        market.code === "ru"
          ? "Банковская карта"
          : paymentInfoMap["pp_medusa-payments_default"].title,
      icon: paymentInfoMap["pp_medusa-payments_default"].icon,
    },
    pp_system_default: {
      title:
        market.code === "ru"
          ? "Оплата при подтверждении"
          : "Manual payment",
      icon: paymentInfoMap.pp_system_default.icon,
    },
  }
}

// This only checks if it is native stripe or medusa payments for card payments, it ignores the other stripe-based providers
export const isStripeLike = (providerId?: string) => {
  return (
    providerId?.startsWith("pp_stripe_") || providerId?.startsWith("pp_medusa-")
  )
}

export const isPaypal = (providerId?: string) => {
  return providerId?.startsWith("pp_paypal")
}
export const isManual = (providerId?: string) => {
  return providerId?.startsWith("pp_system_default")
}

// Add currencies that don't need to be divided by 100
export const noDivisionCurrencies = [
  "krw",
  "jpy",
  "vnd",
  "clp",
  "pyg",
  "xaf",
  "xof",
  "bif",
  "djf",
  "gnf",
  "kmf",
  "mga",
  "rwf",
  "xpf",
  "htg",
  "vuv",
  "xag",
  "xdr",
  "xau",
]
