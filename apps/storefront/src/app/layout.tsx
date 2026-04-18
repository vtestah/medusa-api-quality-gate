import { getBaseURL } from "@lib/util/env"
import { Metadata } from "next"
import "styles/globals.css"
import { Plus_Jakarta_Sans } from "next/font/google"
import RouteLoader from "@modules/common/components/route-loader"

const plusJakarta = Plus_Jakarta_Sans({ 
  subsets: ["latin", "cyrillic-ext"],
  variable: "--font-plus-jakarta"
})

export const metadata: Metadata = {
  metadataBase: new URL(getBaseURL()),
}

export default function RootLayout(props: { children: React.ReactNode }) {
  return (
    <html lang="en" data-mode="light" className={plusJakarta.variable}>
      <body>
        <RouteLoader />
        <main className="relative">{props.children}</main>
      </body>
    </html>
  )
}
