import { Heading } from "@medusajs/ui"
import { getMarketConfig } from "@lib/data/markets"
import LocalizedClientLink from "@modules/common/components/localized-client-link"
import React from "react"

const Help = ({ countryCode }: { countryCode?: string }) => {
  const market = getMarketConfig(countryCode)

  return (
    <div className="mt-6">
      <Heading className="text-base-semi">{market.orderCopy.needHelp}</Heading>
      <div className="text-base-regular my-2">
        <ul className="gap-y-2 flex flex-col">
          <li>
            <LocalizedClientLink href="/contact">
              {market.orderCopy.contact}
            </LocalizedClientLink>
          </li>
          <li>
            <LocalizedClientLink href="/contact">
              {market.orderCopy.returnsExchanges}
            </LocalizedClientLink>
          </li>
        </ul>
      </div>
    </div>
  )
}

export default Help
