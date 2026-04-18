import { Heading, Text } from "@medusajs/ui"
import { useTranslations } from "next-intl"

import InteractiveLink from "@modules/common/components/interactive-link"

const EmptyCartMessage = () => {
  const t = useTranslations("Cart")

  return (
    <div className="py-48 px-2 flex flex-col justify-center items-start" data-testid="empty-cart-message">
      <Heading
        level="h1"
        className="flex flex-row text-3xl-regular gap-x-2 items-baseline"
      >
        {t("emptyTitle")}
      </Heading>
      <Text className="text-base-regular mt-4 mb-6 max-w-[32rem]">
        {t("emptyBody")}
      </Text>
      <div>
        <InteractiveLink href="/store">{t("emptyCta")}</InteractiveLink>
      </div>
    </div>
  )
}

export default EmptyCartMessage
