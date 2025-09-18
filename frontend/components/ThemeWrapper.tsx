'use client'

import { useEffect } from 'react'
import { useTheme } from '@/lib/context'

export function ThemeWrapper({ children }: { children: React.ReactNode }) {
  const { theme } = useTheme()

  useEffect(() => {
    // Apply theme class to document element
    if (typeof window !== 'undefined') {
      const root = document.documentElement
      root.classList.remove('light', 'dark')
      root.classList.add(theme)
    }
  }, [theme])

  return <>{children}</>
}
