import { getTranslator } from "@i18n/get-messages"
import { getMarketConfig } from "@lib/data/markets"
import { Button, Heading } from "@medusajs/ui"
import LocalizedClientLink from "@modules/common/components/localized-client-link"

const Hero = async ({ countryCode }: { countryCode: string }) => {
  const market = getMarketConfig(countryCode)
  const t = await getTranslator(countryCode)

  return (
    <div className="h-[75vh] w-full border-b border-ui-border-base relative overflow-hidden bg-[linear-gradient(135deg,#f5f1ea_0%,#f6f7f8_55%,#e7ecef_100%)]">
      <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_top_left,#d4c6aa,transparent_35%),radial-gradient(circle_at_bottom_right,#c2d5dc,transparent_40%)]" />
      <div className="absolute inset-0 z-10 flex flex-col justify-center items-center text-center small:p-32 gap-6">
        <span className="space-y-3">
          <p className="uppercase tracking-[0.3em] text-xs text-ui-fg-subtle">
            {t("Hero.eyebrow")}
          </p>
          <Heading
            level="h1"
            className="text-4xl leading-tight text-ui-fg-base font-normal max-w-4xl"
          >
            {t("Hero.title", { brand: market.brandName })}
          </Heading>
          <Heading
            level="h2"
            className="text-xl leading-8 text-ui-fg-subtle font-normal max-w-2xl"
          >
            {t("Hero.subtitle")}
          </Heading>
        </span>
        <LocalizedClientLink href="/store">
          <Button variant="secondary">{t("Hero.primaryCta")}</Button>
        </LocalizedClientLink>
      </div>
    </div>
  )
}

export default Hero
