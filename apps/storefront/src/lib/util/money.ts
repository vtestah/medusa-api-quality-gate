import { getMarketLocale } from "@lib/data/markets"
import { isEmpty } from "./isEmpty"

type ConvertToLocaleParams = {
  amount: number
  currency_code: string
  minimumFractionDigits?: number
  maximumFractionDigits?: number
  locale?: string
}

export const convertToLocale = ({
  amount,
  currency_code,
  minimumFractionDigits,
  maximumFractionDigits,
  locale,
}: ConvertToLocaleParams) => {
  return currency_code && !isEmpty(currency_code)
    ? new Intl.NumberFormat(
        getMarketLocale({ currencyCode: currency_code, locale }),
        {
          style: "currency",
          currency: currency_code,
          minimumFractionDigits,
          maximumFractionDigits,
        }
      ).format(amount)
    : amount.toString()
}
