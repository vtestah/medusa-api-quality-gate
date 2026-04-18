import { getTranslator } from "@i18n/get-messages"
import { getMarketConfig } from "@lib/data/markets"
import { Button, Heading } from "@medusajs/ui"
import LocalizedClientLink from "@modules/common/components/localized-client-link"

const Hero = async ({ countryCode }: { countryCode: string }) => {
  const market = getMarketConfig(countryCode)
  const t = await getTranslator(countryCode)

  return (
    <div className="h-[75vh] w-full border-b border-ui-border-base relative overflow-hidden bg-[linear-gradient(135deg,#f5f7fa_0%,#c3cfe2_100%)]">
      <div className="absolute inset-0 opacity-50 bg-[radial-gradient(circle_at_top_right,#ffffff_0%,transparent_50%),radial-gradient(circle_at_bottom_left,#a1c4fd_0%,transparent_50%)]" />
      <div className="absolute inset-0 z-10 flex flex-col justify-center items-center text-center small:p-32 gap-6">
        <span className="space-y-3">
          <p className="uppercase tracking-[0.3em] text-xs text-ui-fg-subtle">
            {t("Hero.eyebrow")}
          </p>
          <Heading
            level="h1"
            className="text-5xl tracking-tight leading-tight text-ui-fg-base font-medium max-w-4xl"
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
          <Button variant="secondary" className="hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
            {t("Hero.primaryCta")}
          </Button>
        </LocalizedClientLink>
      </div>
    </div>
  )
}

export default Hero
