import { CreateInventoryLevelInput, ExecArgs } from "@medusajs/framework/types"
import {
  ContainerRegistrationKeys,
  Modules,
  ProductStatus,
} from "@medusajs/framework/utils"
import {
  WorkflowResponse,
  createWorkflow,
  transform,
} from "@medusajs/framework/workflows-sdk"
import {
  createApiKeysWorkflow,
  createCollectionsWorkflow,
  createInventoryLevelsWorkflow,
  createProductCategoriesWorkflow,
  createProductsWorkflow,
  createRegionsWorkflow,
  createSalesChannelsWorkflow,
  createShippingOptionsWorkflow,
  createShippingProfilesWorkflow,
  createStockLocationsWorkflow,
  createTaxRegionsWorkflow,
  linkSalesChannelsToApiKeyWorkflow,
  linkSalesChannelsToStockLocationWorkflow,
  updateStoresStep,
  updateStoresWorkflow,
} from "@medusajs/medusa/core-flows"
import { ApiKey } from "../../.medusa/types/query-entry-points"

const updateStoreCurrencies = createWorkflow(
  "update-store-currencies",
  (input: {
    supported_currencies: { currency_code: string; is_default?: boolean }[]
    store_id: string
  }) => {
    const normalizedInput = transform({ input }, (data) => {
      return {
        selector: { id: data.input.store_id },
        update: {
          supported_currencies: data.input.supported_currencies.map(
            (currency) => ({
              currency_code: currency.currency_code,
              is_default: currency.is_default ?? false,
            })
          ),
        },
      }
    })

    const stores = updateStoresStep(normalizedInput)

    return new WorkflowResponse(stores)
  }
)

const updateStoreLocales = createWorkflow(
  "update-store-locales",
  (input: {
    supported_locales: { locale_code: string }[]
    store_id: string
  }) => {
    const normalizedInput = transform({ input }, (data) => {
      return {
        selector: { id: data.input.store_id },
        update: {
          supported_locales: data.input.supported_locales.map((locale) => ({
            locale_code: locale.locale_code,
          })),
        },
      }
    })

    const stores = updateStoresStep(normalizedInput)

    return new WorkflowResponse(stores)
  }
)

type LocaleCode = "en-US" | "ru-RU"

type MarketSeed = {
  code: "ru" | "us"
  regionName: string
  currencyCode: "rub" | "usd"
  stockLocationName: string
  city: string
  countryCode: "RU" | "US"
  shippingSetName: string
  pickupSetName?: string
  shippingOptions: {
    name: string
    label: string
    description: string
    code: string
    amount: number
  }[]
  pickupOption?: {
    name: string
    label: string
    description: string
    code: string
    amount: number
  }
}

type StoreLocaleSeed = {
  code: LocaleCode
  name: string
}

type CategorySeed = {
  description: string
  is_active: boolean
  name: string
  ru: {
    description: string
    name: string
  }
}

type CollectionSeed = {
  handle: string
  ru: {
    title: string
  }
  title: string
}

type ProductTranslationSeed = {
  description: string
  material: string
  title: string
}

const storeLocales: StoreLocaleSeed[] = [
  {
    code: "ru-RU",
    name: "Russian (Russia)",
  },
  {
    code: "en-US",
    name: "English (United States)",
  },
]

const markets: MarketSeed[] = [
  {
    code: "ru",
    regionName: "Russia",
    currencyCode: "rub",
    stockLocationName: "Moscow Hub",
    city: "Moscow",
    countryCode: "RU",
    shippingSetName: "Russia delivery",
    pickupSetName: "Moscow pickup",
    shippingOptions: [
      {
        name: "Courier Delivery",
        label: "Courier",
        description: "Courier delivery in 1-2 business days.",
        code: "courier",
        amount: 390,
      },
      {
        name: "Pickup Point",
        label: "Pickup Point",
        description: "Pickup from a parcel point in 2-3 business days.",
        code: "pickup-point",
        amount: 190,
      },
    ],
    pickupOption: {
      name: "Store Pickup",
      label: "Pickup",
      description: "Collect the order from the Moscow showroom at a convenient time.",
      code: "store-pickup",
      amount: 0,
    },
  },
  {
    code: "us",
    regionName: "United States",
    currencyCode: "usd",
    stockLocationName: "New Jersey Hub",
    city: "Secaucus",
    countryCode: "US",
    shippingSetName: "US delivery",
    shippingOptions: [
      {
        name: "Standard Shipping",
        label: "Standard",
        description: "Delivery in 3-5 business days.",
        code: "standard",
        amount: 12,
      },
      {
        name: "Express Shipping",
        label: "Express",
        description: "Delivery in 1-2 business days.",
        code: "express",
        amount: 25,
      },
    ],
  },
]

const categoryCatalog: CategorySeed[] = [
  {
    description:
      "Heavyweight and relaxed tees built for daily rotation, layering, and repeat wear.",
    is_active: true,
    name: "T-Shirts",
    ru: {
      description:
        "Плотные и расслабленные футболки для ежедневной ротации, многослойных образов и частой носки.",
      name: "Футболки",
    },
  },
  {
    description:
      "Dense fleece hoodies with clean silhouettes for city layering and cool-weather transitions.",
    is_active: true,
    name: "Hoodies",
    ru: {
      description:
        "Плотные худи с чистым силуэтом для города, слоев и прохладной погоды.",
      name: "Худи",
    },
  },
  {
    description:
      "Structured fleece bottoms designed for comfort, movement, and understated daily wear.",
    is_active: true,
    name: "Bottoms",
    ru: {
      description:
        "Брюки и джоггеры из структурного флиса для комфорта, движения и спокойного повседневного образа.",
      name: "Низ",
    },
  },
  {
    description:
      "Low-profile accessories that complete the Basis uniform without visual noise.",
    is_active: true,
    name: "Accessories",
    ru: {
      description:
        "Лаконичные аксессуары, которые дополняют гардероб Basis без лишнего визуального шума.",
      name: "Аксессуары",
    },
  },
]

const collectionCatalog: CollectionSeed[] = [
  {
    handle: "everyday-uniform",
    ru: {
      title: "Повседневная база",
    },
    title: "Everyday Uniform",
  },
  {
    handle: "weekend-rotation",
    ru: {
      title: "Ротация на выходные",
    },
    title: "Weekend Rotation",
  },
]

const productCatalog = [
  {
    title: "Basis Heavy Tee",
    handle: "basis-heavy-tee",
    category: "T-Shirts",
    collection: "Everyday Uniform",
    description:
      "Structured cotton jersey tee built for daily rotation with a clean shoulder line and balanced oversized fit.",
    material: "100% cotton",
    origin_country: "TR",
    weight: 320,
    options: [
      {
        title: "Size",
        values: ["S", "M", "L", "XL"],
      },
      {
        title: "Color",
        values: ["Black", "White"],
      },
    ],
    images: [
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-black-front.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-black-back.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-white-front.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-white-back.png",
      },
    ],
    variants: [
      ["S", "Black"],
      ["M", "Black"],
      ["L", "Black"],
      ["XL", "Black"],
      ["S", "White"],
      ["M", "White"],
      ["L", "White"],
      ["XL", "White"],
    ].map(([size, color]) => ({
      title: `${size} / ${color}`,
      sku: `BASIS-HEAVY-TEE-${size}-${color}`.replace(/\s+/g, "-").toUpperCase(),
      options: {
        Size: size,
        Color: color,
      },
      prices: [
        { amount: 2490, currency_code: "rub" },
        { amount: 29, currency_code: "usd" },
      ],
    })),
  },
  {
    title: "Basis Relaxed Tee",
    handle: "basis-relaxed-tee",
    category: "T-Shirts",
    collection: "Weekend Rotation",
    description:
      "Midweight tee with a relaxed silhouette and softer handfeel for weekend wear and travel layering.",
    material: "100% cotton",
    origin_country: "TR",
    weight: 280,
    options: [
      {
        title: "Size",
        values: ["S", "M", "L", "XL"],
      },
      {
        title: "Color",
        values: ["Black", "White"],
      },
    ],
    images: [
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-white-front.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-white-back.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-black-front.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-black-back.png",
      },
    ],
    variants: [
      ["S", "Black"],
      ["M", "Black"],
      ["L", "Black"],
      ["S", "White"],
      ["M", "White"],
      ["L", "White"],
    ].map(([size, color]) => ({
      title: `${size} / ${color}`,
      sku: `BASIS-RELAXED-TEE-${size}-${color}`.replace(/\s+/g, "-").toUpperCase(),
      options: {
        Size: size,
        Color: color,
      },
      prices: [
        { amount: 1990, currency_code: "rub" },
        { amount: 24, currency_code: "usd" },
      ],
    })),
  },
  {
    title: "Basis City Hoodie",
    handle: "basis-city-hoodie",
    category: "Hoodies",
    collection: "Everyday Uniform",
    description:
      "Core fleece hoodie with a compact hood, dense knit, and minimal exterior branding for clean layering.",
    material: "Cotton blend fleece",
    origin_country: "PT",
    weight: 640,
    options: [
      {
        title: "Size",
        values: ["S", "M", "L", "XL"],
      },
    ],
    images: [
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatshirt-vintage-front.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatshirt-vintage-back.png",
      },
    ],
    variants: ["S", "M", "L", "XL"].map((size) => ({
      title: size,
      sku: `BASIS-CITY-HOODIE-${size}`,
      options: {
        Size: size,
      },
      prices: [
        { amount: 5990, currency_code: "rub" },
        { amount: 69, currency_code: "usd" },
      ],
    })),
  },
  {
    title: "Basis Zip Hoodie",
    handle: "basis-zip-hoodie",
    category: "Hoodies",
    collection: "Weekend Rotation",
    description:
      "Zip-front hoodie designed for travel, layering, and cool-weather transitions with a soft brushed interior.",
    material: "Cotton blend fleece",
    origin_country: "PT",
    weight: 670,
    options: [
      {
        title: "Size",
        values: ["S", "M", "L", "XL"],
      },
    ],
    images: [
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatshirt-vintage-front.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatshirt-vintage-back.png",
      },
    ],
    variants: ["S", "M", "L", "XL"].map((size) => ({
      title: size,
      sku: `BASIS-ZIP-HOODIE-${size}`,
      options: {
        Size: size,
      },
      prices: [
        { amount: 6490, currency_code: "rub" },
        { amount: 79, currency_code: "usd" },
      ],
    })),
  },
  {
    title: "Basis Straight Joggers",
    handle: "basis-straight-joggers",
    category: "Bottoms",
    collection: "Everyday Uniform",
    description:
      "Straight-leg joggers with structured fleece, quiet branding, and enough room for daily city wear.",
    material: "Cotton blend fleece",
    origin_country: "PT",
    weight: 540,
    options: [
      {
        title: "Size",
        values: ["S", "M", "L", "XL"],
      },
    ],
    images: [
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatpants-gray-front.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatpants-gray-back.png",
      },
    ],
    variants: ["S", "M", "L", "XL"].map((size) => ({
      title: size,
      sku: `BASIS-STRAIGHT-JOGGERS-${size}`,
      options: {
        Size: size,
      },
      prices: [
        { amount: 4990, currency_code: "rub" },
        { amount: 59, currency_code: "usd" },
      ],
    })),
  },
  {
    title: "Basis Canvas Cap",
    handle: "basis-canvas-cap",
    category: "Accessories",
    collection: "Weekend Rotation",
    description:
      "Low-profile accessory for daily wear, finished in clean canvas with adjustable back fastening.",
    material: "Canvas cotton",
    origin_country: "CN",
    weight: 120,
    options: [
      {
        title: "Color",
        values: ["Sand", "Black"],
      },
    ],
    images: [
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/shorts-vintage-front.png",
      },
      {
        url: "https://medusa-public-images.s3.eu-west-1.amazonaws.com/shorts-vintage-back.png",
      },
    ],
    variants: ["Sand", "Black"].map((color) => ({
      title: color,
      sku: `BASIS-CANVAS-CAP-${color}`.replace(/\s+/g, "-").toUpperCase(),
      options: {
        Color: color,
      },
      prices: [
        { amount: 1790, currency_code: "rub" },
        { amount: 21, currency_code: "usd" },
      ],
    })),
  },
]

const productRuTranslations: Record<string, ProductTranslationSeed> = {
  "basis-canvas-cap": {
    description:
      "Низкопрофильная кепка на каждый день из плотного канваса с регулируемой посадкой сзади.",
    material: "Плотный хлопковый канвас",
    title: "Кепка Basis Canvas",
  },
  "basis-city-hoodie": {
    description:
      "Базовое худи из плотного флиса с компактным капюшоном, плотным полотном и чистым внешним видом для многослойных образов.",
    material: "Смесовый хлопковый флис",
    title: "Худи Basis City",
  },
  "basis-heavy-tee": {
    description:
      "Структурная футболка из плотного хлопкового джерси для ежедневной ротации, с чистой линией плеча и сбалансированным свободным силуэтом.",
    material: "100% хлопок",
    title: "Футболка Basis Heavy",
  },
  "basis-relaxed-tee": {
    description:
      "Футболка средней плотности со свободным силуэтом и мягкой фактурой для выходных, поездок и многослойных комплектов.",
    material: "100% хлопок",
    title: "Футболка Basis Relaxed",
  },
  "basis-straight-joggers": {
    description:
      "Джоггеры прямого кроя из структурного флиса с спокойным брендингом и комфортной посадкой для города.",
    material: "Смесовый хлопковый флис",
    title: "Джоггеры Basis Straight",
  },
  "basis-zip-hoodie": {
    description:
      "Худи на молнии для поездок, многослойных образов и прохладной погоды с мягкой брашированной изнанкой.",
    material: "Смесовый хлопковый флис",
    title: "Худи Basis Zip",
  },
}

const optionTitleTranslations: Record<string, Record<LocaleCode, string>> = {
  Color: {
    "en-US": "Color",
    "ru-RU": "Цвет",
  },
  Size: {
    "en-US": "Size",
    "ru-RU": "Размер",
  },
}

const optionValueTranslations: Record<string, Record<LocaleCode, string>> = {
  Black: {
    "en-US": "Black",
    "ru-RU": "Черный",
  },
  L: {
    "en-US": "L",
    "ru-RU": "L",
  },
  M: {
    "en-US": "M",
    "ru-RU": "M",
  },
  S: {
    "en-US": "S",
    "ru-RU": "S",
  },
  Sand: {
    "en-US": "Sand",
    "ru-RU": "Песочный",
  },
  White: {
    "en-US": "White",
    "ru-RU": "Белый",
  },
  XL: {
    "en-US": "XL",
    "ru-RU": "XL",
  },
}

const shippingTranslationCatalog: Record<
  string,
  Record<
    LocaleCode,
    {
      description: string
      label: string
      name: string
    }
  >
> = {
  courier: {
    "en-US": {
      description: "Courier delivery in 1-2 business days.",
      label: "Courier",
      name: "Courier Delivery",
    },
    "ru-RU": {
      description: "Доставка курьером за 1-2 рабочих дня.",
      label: "Курьер",
      name: "Курьер",
    },
  },
  express: {
    "en-US": {
      description: "Delivery in 1-2 business days.",
      label: "Express",
      name: "Express Shipping",
    },
    "ru-RU": {
      description: "Доставка за 1-2 рабочих дня.",
      label: "Экспресс",
      name: "Экспресс-доставка",
    },
  },
  "pickup-point": {
    "en-US": {
      description: "Pickup from a parcel point in 2-3 business days.",
      label: "Pickup Point",
      name: "Pickup Point",
    },
    "ru-RU": {
      description: "Получение в пункте выдачи за 2-3 рабочих дня.",
      label: "ПВЗ",
      name: "ПВЗ",
    },
  },
  standard: {
    "en-US": {
      description: "Delivery in 3-5 business days.",
      label: "Standard",
      name: "Standard Shipping",
    },
    "ru-RU": {
      description: "Доставка за 3-5 рабочих дней.",
      label: "Стандарт",
      name: "Стандартная доставка",
    },
  },
  "store-pickup": {
    "en-US": {
      description: "Collect the order from the Moscow showroom at a convenient time.",
      label: "Pickup",
      name: "Store Pickup",
    },
    "ru-RU": {
      description: "Заберите заказ из московского шоурума в удобное время.",
      label: "Самовывоз",
      name: "Самовывоз",
    },
  },
}

const translateOptionTitle = (value: string, locale: LocaleCode) => {
  return optionTitleTranslations[value]?.[locale] ?? value
}

const translateOptionValue = (value: string, locale: LocaleCode) => {
  return optionValueTranslations[value]?.[locale] ?? value
}

const translateVariantTitle = (value: string, locale: LocaleCode) => {
  return value
    .split(" / ")
    .map((part) => translateOptionValue(part, locale))
    .join(" / ")
}

export default async function seedDemoData({ container }: ExecArgs) {
  const logger = container.resolve(ContainerRegistrationKeys.LOGGER)
  const link = container.resolve(ContainerRegistrationKeys.LINK)
  const query = container.resolve(ContainerRegistrationKeys.QUERY)
  const fulfillmentModuleService = container.resolve(Modules.FULFILLMENT)
  const salesChannelModuleService = container.resolve(Modules.SALES_CHANNEL)
  const storeModuleService = container.resolve(Modules.STORE)
  const translationModuleService = container.resolve(Modules.TRANSLATION)

  logger.info("Seeding store data...")

  const [store] = await storeModuleService.listStores()
  let defaultSalesChannel = await salesChannelModuleService.listSalesChannels({
    name: "Default Sales Channel",
  })

  if (!defaultSalesChannel.length) {
    const { result: salesChannelResult } = await createSalesChannelsWorkflow(
      container
    ).run({
      input: {
        salesChannelsData: [
          {
            name: "Default Sales Channel",
          },
        ],
      },
    })

    defaultSalesChannel = salesChannelResult
  }

  await updateStoreCurrencies(container).run({
    input: {
      store_id: store.id,
      supported_currencies: [
        {
          currency_code: "rub",
          is_default: true,
        },
        {
          currency_code: "usd",
        },
      ],
    },
  })

  logger.info("Seeding locales...")

  const { data: existingLocales } = await query.graph({
    entity: "locale",
    fields: ["code"],
  })

  const existingLocaleCodes = new Set(
    (existingLocales as { code: string }[]).map((locale) => locale.code)
  )

  const localesToCreate = storeLocales.filter(
    (locale) => !existingLocaleCodes.has(locale.code)
  )

  if (localesToCreate.length) {
    await translationModuleService.createLocales(
      localesToCreate.map((locale) => ({
        code: locale.code,
        name: locale.name,
      }))
    )
  }

  await updateStoreLocales(container).run({
    input: {
      store_id: store.id,
      supported_locales: storeLocales.map((locale) => ({
        locale_code: locale.code,
      })),
    },
  })

  await updateStoresWorkflow(container).run({
    input: {
      selector: { id: store.id },
      update: {
        default_sales_channel_id: defaultSalesChannel[0].id,
      },
    },
  })

  logger.info("Seeding regions...")

  const { result: regionResult } = await createRegionsWorkflow(container).run({
    input: {
      regions: markets.map((market) => ({
        name: market.regionName,
        currency_code: market.currencyCode,
        countries: [market.code],
        payment_providers: ["pp_system_default"],
      })),
    },
  })

  const regionByCode = Object.fromEntries(
    markets.map((market, index) => [market.code, regionResult[index]])
  ) as Record<MarketSeed["code"], (typeof regionResult)[number]>

  await createTaxRegionsWorkflow(container).run({
    input: markets.map((market) => ({
      country_code: market.code,
      provider_id: "tp_system",
    })),
  })

  logger.info("Seeding stock locations...")

  const { result: stockLocationResult } = await createStockLocationsWorkflow(
    container
  ).run({
    input: {
      locations: markets.map((market) => ({
        name: market.stockLocationName,
        address: {
          city: market.city,
          country_code: market.countryCode,
          address_1: "",
        },
      })),
    },
  })

  const stockLocationByCode = Object.fromEntries(
    markets.map((market, index) => [market.code, stockLocationResult[index]])
  ) as Record<MarketSeed["code"], (typeof stockLocationResult)[number]>

  await updateStoresWorkflow(container).run({
    input: {
      selector: { id: store.id },
      update: {
        default_location_id: stockLocationByCode.ru.id,
      },
    },
  })

  for (const market of markets) {
    await link.create({
      [Modules.STOCK_LOCATION]: {
        stock_location_id: stockLocationByCode[market.code].id,
      },
      [Modules.FULFILLMENT]: {
        fulfillment_provider_id: "manual_manual",
      },
    })
  }

  logger.info("Seeding fulfillment profiles and shipping methods...")

  const shippingProfiles = await fulfillmentModuleService.listShippingProfiles({
    type: "default",
  })

  let shippingProfile = shippingProfiles.length ? shippingProfiles[0] : null

  if (!shippingProfile) {
    const { result: shippingProfileResult } =
      await createShippingProfilesWorkflow(container).run({
        input: {
          data: [
            {
              name: "Default Shipping Profile",
              type: "default",
            },
          ],
        },
      })

    shippingProfile = shippingProfileResult[0]
  }

  const shippingSets: Partial<
    Record<
      MarketSeed["code"],
      {
        shipping: Awaited<
          ReturnType<typeof fulfillmentModuleService.createFulfillmentSets>
        >
        pickup?: Awaited<
          ReturnType<typeof fulfillmentModuleService.createFulfillmentSets>
        >
      }
    >
  > = {}

  for (const market of markets) {
    const shippingSet = await fulfillmentModuleService.createFulfillmentSets({
      name: market.shippingSetName,
      type: "shipping",
      service_zones: [
        {
          name: market.regionName,
          geo_zones: [
            {
              country_code: market.code,
              type: "country",
            },
          ],
        },
      ],
    })

    await link.create({
      [Modules.STOCK_LOCATION]: {
        stock_location_id: stockLocationByCode[market.code].id,
      },
      [Modules.FULFILLMENT]: {
        fulfillment_set_id: shippingSet.id,
      },
    })

    shippingSets[market.code] = { shipping: shippingSet }

    if (market.pickupSetName) {
      const pickupSet = await fulfillmentModuleService.createFulfillmentSets({
        name: market.pickupSetName,
        type: "pickup",
        service_zones: [
          {
            name: `${market.regionName} pickup`,
            geo_zones: [
              {
                country_code: market.code,
                type: "country",
              },
            ],
          },
        ],
      })

      await link.create({
        [Modules.STOCK_LOCATION]: {
          stock_location_id: stockLocationByCode[market.code].id,
        },
        [Modules.FULFILLMENT]: {
          fulfillment_set_id: pickupSet.id,
        },
      })

      shippingSets[market.code]!.pickup = pickupSet
    }
  }

  await createShippingOptionsWorkflow(container).run({
    input: markets
      .flatMap((market) => {
        const shippingSet = shippingSets[market.code]?.shipping
        const pickupSet = shippingSets[market.code]?.pickup
        const region = regionByCode[market.code]

        if (!shippingSet) {
          return []
        }

        const shippingOptions = market.shippingOptions.map((option) => ({
          name: option.name,
          price_type: "flat" as const,
          provider_id: "manual_manual",
          service_zone_id: shippingSet.service_zones[0].id,
          shipping_profile_id: shippingProfile!.id,
          type: {
            label: option.label,
            description: option.description,
            code: option.code,
          },
          prices: [
            {
              region_id: region.id,
              amount: option.amount,
            },
          ],
          rules: [
            {
              attribute: "enabled_in_store",
              value: "true",
              operator: "eq" as const,
            },
            {
              attribute: "is_return",
              value: "false",
              operator: "eq" as const,
            },
          ],
        }))

        if (!market.pickupOption || !pickupSet) {
          return shippingOptions
        }

        return [
          ...shippingOptions,
          {
            name: market.pickupOption.name,
            price_type: "flat" as const,
            provider_id: "manual_manual",
            service_zone_id: pickupSet.service_zones[0].id,
            shipping_profile_id: shippingProfile!.id,
            type: {
              label: market.pickupOption.label,
              description: market.pickupOption.description,
              code: market.pickupOption.code,
            },
            prices: [
              {
                region_id: region.id,
                amount: market.pickupOption.amount,
              },
            ],
            rules: [
              {
                attribute: "enabled_in_store",
                value: "true",
                operator: "eq" as const,
              },
              {
                attribute: "is_return",
                value: "false",
                operator: "eq" as const,
              },
            ],
          },
        ]
      })
      .filter(Boolean),
  })

  for (const market of markets) {
    await linkSalesChannelsToStockLocationWorkflow(container).run({
      input: {
        id: stockLocationByCode[market.code].id,
        add: [defaultSalesChannel[0].id],
      },
    })
  }

  logger.info("Seeding publishable API key...")

  const { data } = await query.graph({
    entity: "api_key",
    fields: ["id"],
    filters: {
      type: "publishable",
    },
  })

  let publishableApiKey = data?.[0] as ApiKey | null

  if (!publishableApiKey) {
    const {
      result: [publishableApiKeyResult],
    } = await createApiKeysWorkflow(container).run({
      input: {
        api_keys: [
          {
            title: "Basis Webshop",
            type: "publishable",
            created_by: "",
          },
        ],
      },
    })

    publishableApiKey = publishableApiKeyResult as ApiKey
  }

  await linkSalesChannelsToApiKeyWorkflow(container).run({
    input: {
      id: publishableApiKey.id,
      add: [defaultSalesChannel[0].id],
    },
  })

  logger.info("Seeding categories and collections...")

  const { result: categoryResult } = await createProductCategoriesWorkflow(
    container
  ).run({
    input: {
      product_categories: categoryCatalog.map((category) => ({
        name: category.name,
        description: category.description,
        is_active: category.is_active,
      })),
    },
  })

  const { result: collectionsResult } = await createCollectionsWorkflow(
    container
  ).run({
    input: {
      collections: collectionCatalog.map((collection) => ({
        title: collection.title,
        handle: collection.handle,
      })),
    },
  })

  logger.info("Seeding products...")

  await createProductsWorkflow(container).run({
    input: {
      products: productCatalog.map((product) => ({
        title: product.title,
        handle: product.handle,
        description: product.description,
        category_ids: [
          categoryResult.find((category) => category.name === product.category)!
            .id,
        ],
        collection_id: collectionsResult.find(
          (collection) => collection.title === product.collection
        )!.id,
        material: product.material,
        origin_country: product.origin_country,
        weight: product.weight,
        status: ProductStatus.PUBLISHED,
        shipping_profile_id: shippingProfile!.id,
        images: product.images,
        options: product.options,
        variants: product.variants,
        sales_channels: [
          {
            id: defaultSalesChannel[0].id,
          },
        ],
      })),
    },
  })

  logger.info("Seeding translations...")

  type SeededProductGraph = {
    description: string | null
    handle: string
    id: string
    material: string | null
    options: {
      id: string
      title: string
      values: {
        id: string
        value: string
      }[]
    }[]
    title: string
    variants: {
      id: string
      title: string
    }[]
  }

  type SeededShippingOptionGraph = {
    id: string
    name: string
    type: {
      code: string
      description: string | null
      id: string
      label: string | null
    } | null
  }

  const { data: seededProductsRaw } = await query.graph({
    entity: "product",
    fields: [
      "id",
      "handle",
      "title",
      "description",
      "material",
      "variants.id",
      "variants.title",
      "options.id",
      "options.title",
      "options.values.id",
      "options.values.value",
    ],
    filters: {
      handle: productCatalog.map((product) => product.handle),
    },
  })

  const seededProducts = seededProductsRaw as SeededProductGraph[]

  const { data: seededShippingOptionsRaw } = await query.graph({
    entity: "shipping_option",
    fields: [
      "id",
      "name",
      "type.id",
      "type.code",
      "type.label",
      "type.description",
    ],
  })

  const seededShippingOptions =
    seededShippingOptionsRaw as SeededShippingOptionGraph[]

  const translationPayloads = storeLocales.flatMap((locale) => {
    const productPayloads = seededProducts.flatMap((product) => {
      const seedProduct = productCatalog.find(
        (catalogProduct) => catalogProduct.handle === product.handle
      )

      if (!seedProduct) {
        return []
      }

      const ruProductCopy = productRuTranslations[seedProduct.handle]

      const productTranslations = [
        {
          reference_id: product.id,
          reference: "product",
          locale_code: locale.code,
          translations: {
            title:
              locale.code === "ru-RU" ? ruProductCopy.title : seedProduct.title,
            description:
              locale.code === "ru-RU"
                ? ruProductCopy.description
                : seedProduct.description,
            material:
              locale.code === "ru-RU"
                ? ruProductCopy.material
                : seedProduct.material,
          },
        },
      ]

      const variantTranslations = product.variants.map((variant) => ({
        reference_id: variant.id,
        reference: "product_variant",
        locale_code: locale.code,
        translations: {
          title: translateVariantTitle(variant.title, locale.code),
        },
      }))

      const optionTranslations = product.options.flatMap((option) => {
        const optionPayload = {
          reference_id: option.id,
          reference: "product_option",
          locale_code: locale.code,
          translations: {
            title: translateOptionTitle(option.title, locale.code),
          },
        }

        const optionValuePayloads = option.values.map((value) => ({
          reference_id: value.id,
          reference: "product_option_value",
          locale_code: locale.code,
          translations: {
            value: translateOptionValue(value.value, locale.code),
          },
        }))

        return [optionPayload, ...optionValuePayloads]
      })

      return [...productTranslations, ...variantTranslations, ...optionTranslations]
    })

    const categoryPayloads = categoryResult.flatMap((category) => {
      const seedCategory = categoryCatalog.find(
        (catalogCategory) => catalogCategory.name === category.name
      )

      if (!seedCategory) {
        return []
      }

      return [
        {
          reference_id: category.id,
          reference: "product_category",
          locale_code: locale.code,
          translations: {
            name:
              locale.code === "ru-RU" ? seedCategory.ru.name : seedCategory.name,
            description:
              locale.code === "ru-RU"
                ? seedCategory.ru.description
                : seedCategory.description,
          },
        },
      ]
    })

    const collectionPayloads = collectionsResult.flatMap((collection) => {
      const seedCollection = collectionCatalog.find(
        (catalogCollection) => catalogCollection.title === collection.title
      )

      if (!seedCollection) {
        return []
      }

      return [
        {
          reference_id: collection.id,
          reference: "product_collection",
          locale_code: locale.code,
          translations: {
            title:
              locale.code === "ru-RU"
                ? seedCollection.ru.title
                : seedCollection.title,
          },
        },
      ]
    })

    const regionPayloads = regionResult.map((region) => ({
      reference_id: region.id,
      reference: "region",
      locale_code: locale.code,
      translations: {
        name:
          locale.code === "ru-RU"
            ? region.name === "Russia"
              ? "Россия"
              : "США"
            : region.name,
      },
    }))

    const shippingPayloads = seededShippingOptions.flatMap((option) => {
      if (!option.type) {
        return []
      }

      const translation = shippingTranslationCatalog[option.type.code]?.[locale.code]

      if (!translation) {
        return []
      }

      return [
        {
          reference_id: option.id,
          reference: "shipping_option",
          locale_code: locale.code,
          translations: {
            name: translation.name,
          },
        },
        {
          reference_id: option.type.id,
          reference: "shipping_option_type",
          locale_code: locale.code,
          translations: {
            label: translation.label,
            description: translation.description,
          },
        },
      ]
    })

    return [
      ...productPayloads,
      ...categoryPayloads,
      ...collectionPayloads,
      ...regionPayloads,
      ...shippingPayloads,
    ]
  })

  await translationModuleService.createTranslations(translationPayloads)

  logger.info("Seeding inventory levels...")

  const { data: inventoryItems } = await query.graph({
    entity: "inventory_item",
    fields: ["id"],
  })

  const inventoryLevels: CreateInventoryLevelInput[] = inventoryItems.flatMap(
    (inventoryItem) =>
      markets.map((market) => ({
        location_id: stockLocationByCode[market.code].id,
        stocked_quantity: 500,
        inventory_item_id: inventoryItem.id,
      }))
  )

  await createInventoryLevelsWorkflow(container).run({
    input: {
      inventory_levels: inventoryLevels,
    },
  })

  logger.info("Finished seeding RU + US demo data.")
}
