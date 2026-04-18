"use client"

import { getMarketConfig } from "@lib/data/markets"
import { useParams } from "next/navigation"

export const useMarket = () => {
  const params = useParams<{ countryCode?: string }>()

  return getMarketConfig(
    typeof params.countryCode === "string" ? params.countryCode : null
  )
}
