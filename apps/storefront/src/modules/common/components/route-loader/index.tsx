"use client"

import { useEffect, useState, useCallback } from "react"

/**
 * A slim top progress bar (YouTube-style) that shows during
 * Next.js App Router navigations. It intercepts <a> clicks and
 * listens for popstate to detect route changes.
 */
const RouteLoader = () => {
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)

  const startLoading = useCallback(() => {
    setLoading(true)
    setProgress(15)
  }, [])

  const finishLoading = useCallback(() => {
    setProgress(100)
    setTimeout(() => {
      setLoading(false)
      setProgress(0)
    }, 300)
  }, [])

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    if (loading && progress < 90) {
      interval = setInterval(() => {
        setProgress((prev) => {
          // Slow down as we approach 90%
          const increment = prev < 30 ? 8 : prev < 60 ? 4 : prev < 80 ? 1 : 0.5
          return Math.min(prev + increment, 90)
        })
      }, 400)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [loading, progress])

  useEffect(() => {
    // Intercept link clicks for internal navigation
    const handleClick = (e: MouseEvent) => {
      const anchor = (e.target as HTMLElement).closest("a")
      if (!anchor) return

      const href = anchor.getAttribute("href")
      if (!href) return

      // Skip external links, hash links, and links with target
      if (
        href.startsWith("http") ||
        href.startsWith("#") ||
        anchor.target === "_blank" ||
        e.ctrlKey ||
        e.metaKey
      ) {
        return
      }

      // Only trigger if navigating to a different path
      if (href !== window.location.pathname) {
        startLoading()
      }
    }

    // Listen for popstate (browser back/forward)
    const handlePopState = () => {
      startLoading()
    }

    document.addEventListener("click", handleClick, true)
    window.addEventListener("popstate", handlePopState)

    // MutationObserver to detect when the page content changes (route completed)
    const observer = new MutationObserver(() => {
      if (loading) {
        finishLoading()
      }
    })

    observer.observe(document.querySelector("main") || document.body, {
      childList: true,
      subtree: true,
    })

    return () => {
      document.removeEventListener("click", handleClick, true)
      window.removeEventListener("popstate", handlePopState)
      observer.disconnect()
    }
  }, [loading, startLoading, finishLoading])

  if (!loading && progress === 0) return null

  return (
    <div className="fixed top-0 left-0 right-0 z-[9999] h-[3px] pointer-events-none">
      <div
        className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 shadow-[0_0_10px_rgba(99,102,241,0.5)] transition-all ease-out"
        style={{
          width: `${progress}%`,
          transitionDuration: progress === 100 ? "200ms" : "400ms",
        }}
      />
    </div>
  )
}

export default RouteLoader
