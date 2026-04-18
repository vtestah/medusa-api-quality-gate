"use client"

import { HttpTypes } from "@medusajs/types"
import { Container, clx } from "@medusajs/ui"
import Image from "next/image"
import { useState, useRef } from "react"

type ImageGalleryProps = {
  images: HttpTypes.StoreProductImage[]
}

const ImageGallery = ({ images }: ImageGalleryProps) => {
  const [activeIndex, setActiveIndex] = useState(0)
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const isScrollingRef = useRef(false)
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const handleScroll = () => {
    if (isScrollingRef.current) return
    
    if (!scrollContainerRef.current) return
    
    const container = scrollContainerRef.current
    const scrollPosition = container.scrollLeft
    const width = container.clientWidth
    
    // Calculate which image is mostly in view
    const newIndex = Math.round(scrollPosition / width)
    if (newIndex !== activeIndex && newIndex >= 0 && newIndex < images.length) {
      setActiveIndex(newIndex)
    }
  }

  const handleThumbnailClick = (index: number) => {
    setActiveIndex(index)
    
    if (scrollContainerRef.current) {
      isScrollingRef.current = true
      if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current)
      
      const container = scrollContainerRef.current
      container.scrollTo({
        left: index * container.clientWidth,
        behavior: "smooth"
      })
      
      scrollTimeoutRef.current = setTimeout(() => {
        isScrollingRef.current = false
      }, 500)
    }
  }

  if (!images || images.length === 0) {
    return null
  }

  return (
    <div className="flex flex-col-reverse small:flex-row gap-4 w-full relative">
      {/* Thumbnails (Left on desktop, bottom on mobile) */}
      {images.length > 1 && (
        <div className="flex small:flex-col gap-4 overflow-x-auto small:overflow-y-auto no-scrollbar w-full small:w-24 flex-shrink-0 snap-x snap-mandatory p-1 small:p-2 h-auto small:max-h-[600px]">
          {images.map((image, index) => (
            <button
              key={image.id}
              onClick={() => handleThumbnailClick(index)}
              className={clx(
                "relative aspect-[29/34] w-16 small:w-full flex-shrink-0 overflow-hidden rounded-lg bg-ui-bg-subtle transition-opacity duration-200 snap-center focus:outline-none",
                {
                  "opacity-100": activeIndex === index,
                  "opacity-60 hover:opacity-100": activeIndex !== index
                }
              )}
            >
              {!!image.url && (
                <Image
                  src={image.url}
                  alt={`Thumbnail ${index + 1}`}
                  fill
                  sizes="80px"
                  className="object-cover"
                />
              )}
              {/* Border overlay rendered ON TOP of the image */}
              <div 
                className={clx(
                  "absolute inset-0 rounded-lg border-2 transition-colors duration-200 pointer-events-none",
                  {
                    "border-gray-900": activeIndex === index,
                    "border-transparent": activeIndex !== index
                  }
                )}
              />
            </button>
          ))}
        </div>
      )}

      {/* Main Image Slider */}
      <div className="relative w-full flex-1">
        <Container className="relative aspect-[29/34] w-full overflow-hidden bg-ui-bg-subtle p-0 rounded-2xl shadow-sm border-0">
          <div 
            ref={scrollContainerRef}
            onScroll={handleScroll}
            className="flex w-full h-full overflow-x-auto snap-x snap-mandatory no-scrollbar scroll-smooth"
          >
            {images.map((image, index) => (
              <div
                key={image.id}
                className="w-full h-full flex-shrink-0 snap-center relative"
              >
                {!!image.url && (
                  <Image
                    src={image.url}
                    priority={index === 0}
                    className="absolute inset-0 object-cover"
                    alt={`Product image ${index + 1}`}
                    fill
                    sizes="(max-width: 576px) 100vw, (max-width: 768px) 50vw, (max-width: 992px) 50vw, 800px"
                  />
                )}
              </div>
            ))}
          </div>
        </Container>

        {/* Mobile Dots */}
        {images.length > 1 && (
          <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-2 small:hidden">
            {images.map((_, index) => (
              <div
                key={index}
                className={clx(
                  "h-1.5 rounded-full transition-all duration-300",
                  {
                    "bg-black w-4": activeIndex === index,
                    "bg-black/30 w-1.5": activeIndex !== index
                  }
                )}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ImageGallery
