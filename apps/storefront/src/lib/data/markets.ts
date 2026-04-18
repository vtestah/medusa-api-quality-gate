export type MarketCode = "ru" | "us"

type MarketHeroCopy = {
  eyebrow: string
  title: string
  subtitle: string
  primaryCta: string
}

type MarketNavCopy = {
  menu: string
  home: string
  store: string
  account: string
  cart: string
  market: string
  backToCart: string
  backShort: string
  cartEmpty: string
  goToCart: string
  exploreProducts: string
  quantity: string
  remove: string
  subtotal: string
  subtotalHint: string
}

type MarketFooterCopy = {
  categories: string
  collections: string
  engineering: string
  github: string
  documentation: string
  sourceCode: string
  rightsReserved: string
  builtWith: string
}

type MarketStoreCopy = {
  allProducts: string
  sortBy: string
  latestArrivals: string
  priceLowToHigh: string
  priceHighToLow: string
}

type MarketUICopy = {
  original: string
  edit: string
  save: string
  cancel: string
  remove: string
}

type MarketCartCopy = {
  title: string
  summary: string
  goToCheckout: string
  signInPromptTitle: string
  signInPromptBody: string
  signIn: string
  emptyTitle: string
  emptyBody: string
  emptyCta: string
  item: string
  quantity: string
  price: string
  total: string
  subtotal: string
  shipping: string
  discount: string
  taxes: string
  subtotalWithHint: string
}

type MarketCheckoutCopy = {
  address: string
  billingAddress: string
  sameAsBilling: string
  contact: string
  delivery: string
  edit: string
  continueToDelivery: string
  continueToPayment: string
  continueToReview: string
  inYourCart: string
  payment: string
  paymentMethod: string
  paymentDetails: string
  cardDetails: string
  cardStepHint: string
  choosePaymentMethod: string
  placeOrder: string
  review: string
  reviewDisclaimer: string
  shippingMethod: string
  shippingMethodHint: string
  pickup: string
  giftCard: string
}

type MarketAccountCopy = {
  welcomeBack: string
  signInSubtitle: string
  signIn: string
  notMember: string
  joinUs: string
  memberTitle: string
  memberSubtitle: string
  alreadyMember: string
  account: string
  hello: string
  overview: string
  profile: string
  addresses: string
  orders: string
  logout: string
  signedInAs: string
  completed: string
  saved: string
  recentOrders: string
  noRecentOrders: string
  datePlaced: string
  orderNumber: string
  totalAmount: string
  shippingAddresses: string
  profileDescription: string
  supportTitle: string
  supportBody: string
  customerService: string
  accountAgreementPrefix: string
  privacyPolicy: string
  termsOfUse: string
}

type MarketProductCopy = {
  viewAll: string
  selectVariant: string
  outOfStock: string
  addToCart: string
  productInformation: string
  shippingAndReturns: string
  material: string
  countryOfOrigin: string
  productType: string
  weight: string
  dimensions: string
  fastDelivery: string
  fastDeliveryBody: string
  simpleExchanges: string
  simpleExchangesBody: string
  easyReturns: string
  easyReturnsBody: string
}

type MarketOrderCopy = {
  thankYou: string
  orderPlaced: string
  summary: string
  orderDetails: string
  backToOverview: string
  orderSummary: string
  confirmationSent: string
  orderDate: string
  orderNumber: string
  orderStatus: string
  paymentStatus: string
  needHelp: string
  contact: string
  returnsExchanges: string
  seeDetails: string
  itemSingle: string
  itemPlural: string
  moreItems: string
}

type MarketMetadataCopy = {
  homeTitle: string
  homeDescription: string
  cartTitle: string
  cartDescription: string
  checkoutTitle: string
  signInTitle: string
  signInDescription: string
  accountTitle: string
  accountDescription: string
  profileTitle: string
  profileDescription: string
  storeTitle: string
}

export type MarketConfig = {
  code: MarketCode
  countryCode: MarketCode
  locale: string
  currencyCode: "rub" | "usd"
  brandName: string
  marketLabel: string
  uiCopy: MarketUICopy
  storeCopy: MarketStoreCopy
  heroCopy: MarketHeroCopy
  navCopy: MarketNavCopy
  footerCopy: MarketFooterCopy
  cartCopy: MarketCartCopy
  checkoutCopy: MarketCheckoutCopy
  accountCopy: MarketAccountCopy
  productCopy: MarketProductCopy
  orderCopy: MarketOrderCopy
  metadata: MarketMetadataCopy
}

export const marketRegistry: Record<MarketCode, MarketConfig> = {
  ru: {
    code: "ru",
    countryCode: "ru",
    locale: "ru-RU",
    currencyCode: "rub",
    brandName: "Basis",
    marketLabel: "Россия",
    uiCopy: {
      original: "Исходная цена",
      edit: "Изменить",
      save: "Сохранить",
      cancel: "Отмена",
      remove: "Удалить",
    },
    storeCopy: {
      allProducts: "Все товары",
      sortBy: "Сортировка",
      latestArrivals: "Новые поступления",
      priceLowToHigh: "Цена: по возрастанию",
      priceHighToLow: "Цена: по убыванию",
    },
    heroCopy: {
      eyebrow: "Российский рынок",
      title: "Basis: базовый гардероб без лишнего шума",
      subtitle:
        "Лаконичные повседневные вещи с понятной посадкой, быстрым fulfilment и ценами в рублях.",
      primaryCta: "Смотреть каталог",
    },
    navCopy: {
      menu: "Меню",
      home: "Главная",
      store: "Каталог",
      account: "Аккаунт",
      cart: "Корзина",
      market: "Рынок",
      backToCart: "Назад в корзину",
      backShort: "Назад",
      cartEmpty: "Корзина пуста.",
      goToCart: "Перейти в корзину",
      exploreProducts: "Смотреть товары",
      quantity: "Количество",
      remove: "Удалить",
      subtotal: "Подытог",
      subtotalHint: "(без доставки и налогов)",
    },
    footerCopy: {
      categories: "Категории",
      collections: "Коллекции",
      engineering: "Инженерия",
      github: "GitHub",
      documentation: "Документация",
      sourceCode: "Исходный код",
      rightsReserved: "Все права защищены.",
      builtWith: "Собрано на",
    },
    cartCopy: {
      title: "Корзина",
      summary: "Сводка",
      goToCheckout: "Перейти к оформлению",
      signInPromptTitle: "Уже есть аккаунт?",
      signInPromptBody: "Войдите, чтобы сохранить адреса и ускорить checkout.",
      signIn: "Войти",
      emptyTitle: "Корзина",
      emptyBody:
        "В корзине пока ничего нет. Начните с базовых вещей, которые легко собрать в повседневный гардероб.",
      emptyCta: "Открыть каталог",
      item: "Товар",
      quantity: "Количество",
      price: "Цена",
      total: "Итого",
      subtotal: "Подытог",
      shipping: "Доставка",
      discount: "Скидка",
      taxes: "Налоги",
      subtotalWithHint: "Подытог (без доставки и налогов)",
    },
    checkoutCopy: {
      address: "Адрес доставки",
      billingAddress: "Платежный адрес",
      sameAsBilling: "Платежный адрес совпадает с адресом доставки",
      contact: "Контакты",
      delivery: "Доставка",
      edit: "Изменить",
      continueToDelivery: "Продолжить к доставке",
      continueToPayment: "Продолжить к оплате",
      continueToReview: "Продолжить к проверке заказа",
      inYourCart: "В корзине",
      payment: "Оплата",
      paymentMethod: "Способ оплаты",
      paymentDetails: "Детали оплаты",
      cardDetails: "Введите данные карты:",
      cardStepHint: "Следующий шаг появится после выбора оплаты.",
      choosePaymentMethod: "Выберите способ оплаты",
      placeOrder: "Оформить заказ",
      review: "Проверка заказа",
      reviewDisclaimer:
        "Нажимая кнопку «Оформить заказ», вы подтверждаете, что ознакомились и принимаете условия продажи, возврата и политику конфиденциальности Basis.",
      shippingMethod: "Способ доставки",
      shippingMethodHint: "Как вам удобно получить заказ?",
      pickup: "Самовывоз",
      giftCard: "Подарочная карта",
    },
    accountCopy: {
      welcomeBack: "С возвращением",
      signInSubtitle: "Войдите, чтобы управлять заказами, адресами и checkout.",
      signIn: "Войти",
      notMember: "Нет аккаунта?",
      joinUs: "Создать аккаунт",
      memberTitle: "Аккаунт клиента Basis",
      memberSubtitle:
        "Создайте профиль, чтобы сохранять адреса и быстрее оформлять заказы.",
      alreadyMember: "Уже зарегистрированы?",
      account: "Аккаунт",
      hello: "Здравствуйте",
      overview: "Обзор",
      profile: "Профиль",
      addresses: "Адреса",
      orders: "Заказы",
      logout: "Выйти",
      signedInAs: "Вход выполнен как",
      completed: "Заполнено",
      saved: "Сохранено",
      recentOrders: "Последние заказы",
      noRecentOrders: "Пока нет заказов",
      datePlaced: "Дата заказа",
      orderNumber: "Номер заказа",
      totalAmount: "Сумма",
      shippingAddresses: "Адреса доставки",
      profileDescription:
        "Проверьте и обновите имя, email, телефон и платежный адрес.",
      supportTitle: "Есть вопросы?",
      supportBody:
        "Частые вопросы и ответы собраны на странице клиентского сервиса Basis.",
      customerService: "Клиентский сервис",
      accountAgreementPrefix:
        "Создавая аккаунт, вы соглашаетесь с документами Basis:",
      privacyPolicy: "Политика конфиденциальности",
      termsOfUse: "Условия использования",
    },
    productCopy: {
      viewAll: "Смотреть все",
      selectVariant: "Выберите вариант",
      outOfStock: "Нет в наличии",
      addToCart: "Добавить в корзину",
      productInformation: "О товаре",
      shippingAndReturns: "Доставка и возврат",
      material: "Материал",
      countryOfOrigin: "Страна производства",
      productType: "Тип товара",
      weight: "Вес",
      dimensions: "Размеры",
      fastDelivery: "Быстрая доставка",
      fastDeliveryBody:
        "Заказ приедет за 1-3 рабочих дня курьером, в ПВЗ или на самовывоз.",
      simpleExchanges: "Простой обмен",
      simpleExchangesBody:
        "Если посадка не подошла, мы быстро заменим размер без лишней бюрократии.",
      easyReturns: "Простой возврат",
      easyReturnsBody:
        "Верните товар и получите возврат по стандартной процедуре без лишних вопросов.",
    },
    orderCopy: {
      thankYou: "Спасибо!",
      orderPlaced: "Заказ успешно оформлен.",
      summary: "Сводка",
      orderDetails: "Детали заказа",
      backToOverview: "Назад к обзору",
      orderSummary: "Сводка заказа",
      confirmationSent: "Мы отправили детали подтверждения заказа на",
      orderDate: "Дата заказа",
      orderNumber: "Номер заказа",
      orderStatus: "Статус заказа",
      paymentStatus: "Статус оплаты",
      needHelp: "Нужна помощь?",
      contact: "Связаться с нами",
      returnsExchanges: "Возвраты и обмен",
      seeDetails: "Открыть заказ",
      itemSingle: "товар",
      itemPlural: "товара",
      moreItems: "ещё",
    },
    metadata: {
      homeTitle: "Basis | Российский ecommerce demo",
      homeDescription:
        "Russian-first dual-market demo storefront for fashion basics with RUB pricing.",
      cartTitle: "Корзина | Basis",
      cartDescription: "Проверьте выбранные товары и переходите к checkout.",
      checkoutTitle: "Оформление заказа | Basis",
      signInTitle: "Вход | Basis",
      signInDescription: "Вход в аккаунт покупателя Basis.",
      accountTitle: "Аккаунт | Basis",
      accountDescription: "Обзор профиля, адресов и заказов в Basis.",
      profileTitle: "Профиль | Basis",
      profileDescription: "Управление персональными данными и адресами Basis.",
      storeTitle: "Каталог | Basis",
    },
  },
  us: {
    code: "us",
    countryCode: "us",
    locale: "en-US",
    currencyCode: "usd",
    brandName: "Basis",
    marketLabel: "United States",
    uiCopy: {
      original: "Original",
      edit: "Edit",
      save: "Save",
      cancel: "Cancel",
      remove: "Remove",
    },
    storeCopy: {
      allProducts: "All products",
      sortBy: "Sort by",
      latestArrivals: "Latest Arrivals",
      priceLowToHigh: "Price: Low -> High",
      priceHighToLow: "Price: High -> Low",
    },
    heroCopy: {
      eyebrow: "US market",
      title: "Basis: clean everyday layers built for repeat wear",
      subtitle:
        "Utility-driven essentials with stable fits, fast fulfillment, and a storefront localized for USD checkout.",
      primaryCta: "Shop the catalog",
    },
    navCopy: {
      menu: "Menu",
      home: "Home",
      store: "Store",
      account: "Account",
      cart: "Cart",
      market: "Market",
      backToCart: "Back to cart",
      backShort: "Back",
      cartEmpty: "Your cart is empty.",
      goToCart: "Go to cart",
      exploreProducts: "Explore products",
      quantity: "Quantity",
      remove: "Remove",
      subtotal: "Subtotal",
      subtotalHint: "(excl. shipping and taxes)",
    },
    footerCopy: {
      categories: "Categories",
      collections: "Collections",
      engineering: "Engineering",
      github: "GitHub",
      documentation: "Documentation",
      sourceCode: "Source code",
      rightsReserved: "All rights reserved.",
      builtWith: "Built with",
    },
    cartCopy: {
      title: "Cart",
      summary: "Summary",
      goToCheckout: "Go to checkout",
      signInPromptTitle: "Already have an account?",
      signInPromptBody: "Sign in to save addresses and speed up checkout.",
      signIn: "Sign in",
      emptyTitle: "Cart",
      emptyBody:
        "Your cart is empty. Start with a few dependable basics and build the rest from there.",
      emptyCta: "Explore products",
      item: "Item",
      quantity: "Quantity",
      price: "Price",
      total: "Total",
      subtotal: "Subtotal",
      shipping: "Shipping",
      discount: "Discount",
      taxes: "Taxes",
      subtotalWithHint: "Subtotal (excl. shipping and taxes)",
    },
    checkoutCopy: {
      address: "Shipping address",
      billingAddress: "Billing address",
      sameAsBilling: "Billing address is the same as shipping",
      contact: "Contact",
      delivery: "Delivery",
      edit: "Edit",
      continueToDelivery: "Continue to delivery",
      continueToPayment: "Continue to payment",
      continueToReview: "Continue to review",
      inYourCart: "In your cart",
      payment: "Payment",
      paymentMethod: "Payment method",
      paymentDetails: "Payment details",
      cardDetails: "Enter your card details:",
      cardStepHint: "Another step will appear after payment selection.",
      choosePaymentMethod: "Select a payment method",
      placeOrder: "Place order",
      review: "Review",
      reviewDisclaimer:
        "By placing your order, you confirm that you have reviewed and accepted Basis terms, returns policy, and privacy policy.",
      shippingMethod: "Shipping method",
      shippingMethodHint: "How would you like your order delivered?",
      pickup: "Pick up your order",
      giftCard: "Gift card",
    },
    accountCopy: {
      welcomeBack: "Welcome back",
      signInSubtitle: "Sign in to manage orders, saved addresses, and checkout.",
      signIn: "Sign in",
      notMember: "Not a member?",
      joinUs: "Join us",
      memberTitle: "Become a Basis member",
      memberSubtitle:
        "Create your profile to save addresses and move through checkout faster.",
      alreadyMember: "Already a member?",
      account: "Account",
      hello: "Hello",
      overview: "Overview",
      profile: "Profile",
      addresses: "Addresses",
      orders: "Orders",
      logout: "Log out",
      signedInAs: "Signed in as",
      completed: "Completed",
      saved: "Saved",
      recentOrders: "Recent orders",
      noRecentOrders: "No recent orders",
      datePlaced: "Date placed",
      orderNumber: "Order number",
      totalAmount: "Total amount",
      shippingAddresses: "Shipping addresses",
      profileDescription:
        "Review and update your name, email, phone number, and billing address.",
      supportTitle: "Got questions?",
      supportBody:
        "You can find frequently asked questions and answers on our customer service page.",
      customerService: "Customer Service",
      accountAgreementPrefix:
        "By creating an account, you agree to Basis",
      privacyPolicy: "Privacy Policy",
      termsOfUse: "Terms of Use",
    },
    productCopy: {
      viewAll: "View all",
      selectVariant: "Select variant",
      outOfStock: "Out of stock",
      addToCart: "Add to cart",
      productInformation: "Product information",
      shippingAndReturns: "Shipping & returns",
      material: "Material",
      countryOfOrigin: "Country of origin",
      productType: "Type",
      weight: "Weight",
      dimensions: "Dimensions",
      fastDelivery: "Fast delivery",
      fastDeliveryBody:
        "Expect delivery in 2-5 business days to your home or selected pickup location.",
      simpleExchanges: "Simple exchanges",
      simpleExchangesBody:
        "If the fit is off, we will help you swap sizes without friction.",
      easyReturns: "Easy returns",
      easyReturnsBody:
        "Return eligible items through the standard workflow and receive a refund.",
    },
    orderCopy: {
      thankYou: "Thank you!",
      orderPlaced: "Your order was placed successfully.",
      summary: "Summary",
      orderDetails: "Order details",
      backToOverview: "Back to overview",
      orderSummary: "Order Summary",
      confirmationSent: "We have sent the order confirmation details to",
      orderDate: "Order date",
      orderNumber: "Order number",
      orderStatus: "Order status",
      paymentStatus: "Payment status",
      needHelp: "Need help?",
      contact: "Contact",
      returnsExchanges: "Returns & Exchanges",
      seeDetails: "See details",
      itemSingle: "item",
      itemPlural: "items",
      moreItems: "more",
    },
    metadata: {
      homeTitle: "Basis | US ecommerce demo",
      homeDescription:
        "Dual-market fashion-basics storefront localized for USD checkout.",
      cartTitle: "Cart | Basis",
      cartDescription: "Review your selection and continue to checkout.",
      checkoutTitle: "Checkout | Basis",
      signInTitle: "Sign in | Basis",
      signInDescription: "Sign in to your Basis customer account.",
      accountTitle: "Account | Basis",
      accountDescription: "Overview of your Basis profile, addresses, and orders.",
      profileTitle: "Profile | Basis",
      profileDescription: "Manage your Basis contact details and billing address.",
      storeTitle: "Store | Basis",
    },
  },
}

export const defaultMarketCode: MarketCode = "ru"

export const isMarketCode = (value?: string | null): value is MarketCode => {
  return value === "ru" || value === "us"
}

export const getMarketConfig = (value?: string | null): MarketConfig => {
  const normalized = value?.toLowerCase()

  if (normalized && isMarketCode(normalized)) {
    return marketRegistry[normalized]
  }

  return marketRegistry[defaultMarketCode]
}

export const getMarketConfigByCurrency = (
  currencyCode?: string | null
): MarketConfig => {
  switch (currencyCode?.toLowerCase()) {
    case "usd":
      return marketRegistry.us
    case "rub":
    default:
      return marketRegistry.ru
  }
}

export const getMarketLocale = (input: {
  countryCode?: string | null
  currencyCode?: string | null
  locale?: string | null
}): string => {
  if (input.locale) {
    return input.locale
  }

  if (input.countryCode) {
    return getMarketConfig(input.countryCode).locale
  }

  return getMarketConfigByCurrency(input.currencyCode).locale
}

export const getMarketOptions = () => {
  return [marketRegistry.ru, marketRegistry.us]
}
