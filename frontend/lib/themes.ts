/**
 * Theme-related utilities
 */

export interface Theme {
  name: string
  colors: {
    primary: string
    secondary: string
    accent: string
    background: string
    surface: string
    text: string
    textSecondary: string
    border: string
    error: string
    warning: string
    success: string
    info: string
  }
  typography: {
    fontFamily: string
    fontSize: {
      xs: string
      sm: string
      base: string
      lg: string
      xl: string
      '2xl': string
      '3xl': string
    }
    fontWeight: {
      normal: number
      medium: number
      semibold: number
      bold: number
    }
    lineHeight: {
      tight: number
      normal: number
      relaxed: number
    }
  }
  spacing: {
    xs: string
    sm: string
    md: string
    lg: string
    xl: string
    '2xl': string
    '3xl': string
  }
  borderRadius: {
    none: string
    sm: string
    md: string
    lg: string
    xl: string
    full: string
  }
  shadows: {
    sm: string
    md: string
    lg: string
    xl: string
  }
  breakpoints: {
    mobile: string
    tablet: string
    desktop: string
  }
}

export const lightTheme: Theme = {
  name: 'light',
  colors: {
    primary: '#2563eb',
    secondary: '#64748b',
    accent: '#f59e0b',
    background: '#ffffff',
    surface: '#f8fafc',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: '#e2e8f0',
    error: '#dc2626',
    warning: '#d97706',
    success: '#16a34a',
    info: '#0891b2',
  },
  typography: {
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  },
  breakpoints: {
    mobile: '768px',
    tablet: '1024px',
    desktop: '1200px',
  },
}

export const darkTheme: Theme = {
  name: 'dark',
  colors: {
    primary: '#3b82f6',
    secondary: '#94a3b8',
    accent: '#fbbf24',
    background: '#0f172a',
    surface: '#1e293b',
    text: '#f1f5f9',
    textSecondary: '#94a3b8',
    border: '#334155',
    error: '#ef4444',
    warning: '#f59e0b',
    success: '#22c55e',
    info: '#06b6d4',
  },
  typography: {
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.3)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.3)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.3)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.3), 0 8px 10px -6px rgb(0 0 0 / 0.3)',
  },
  breakpoints: {
    mobile: '768px',
    tablet: '1024px',
    desktop: '1200px',
  },
}

export const themes: Record<string, Theme> = {
  light: lightTheme,
  dark: darkTheme,
}


export function applyTheme(theme: Theme): void {
  const root = document.documentElement

  // Apply CSS custom properties
  Object.entries(theme.colors).forEach(([key, value]) => {
    root.style.setProperty(`--color-${key}`, value)
  })

  Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
    root.style.setProperty(`--font-size-${key}`, value)
  })

  Object.entries(theme.spacing).forEach(([key, value]) => {
    root.style.setProperty(`--spacing-${key}`, value)
  })

  Object.entries(theme.borderRadius).forEach(([key, value]) => {
    root.style.setProperty(`--border-radius-${key}`, value)
  })

  Object.entries(theme.shadows).forEach(([key, value]) => {
    root.style.setProperty(`--shadow-${key}`, value)
  })

  // Apply theme class
  root.className = root.className.replace(/theme-\w+/g, '')
  root.classList.add(`theme-${theme.name}`)
}

export function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') {
    return 'light'
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

export function watchSystemTheme(
  callback: (theme: 'light' | 'dark') => void
): () => void {
  if (typeof window === 'undefined') {
    return () => {}
  }

  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

  const handleChange = (e: MediaQueryListEvent) => {
    callback(e.matches ? 'dark' : 'light')
  }

  mediaQuery.addEventListener('change', handleChange)

  return () => {
    mediaQuery.removeEventListener('change', handleChange)
  }
}

export function createThemeCSS(theme: Theme): string {
  return `
    :root {
      ${Object.entries(theme.colors)
        .map(([key, value]) => `--color-${key}: ${value};`)
        .join('\n      ')}
      
      ${Object.entries(theme.typography.fontSize)
        .map(([key, value]) => `--font-size-${key}: ${value};`)
        .join('\n      ')}
      
      ${Object.entries(theme.spacing)
        .map(([key, value]) => `--spacing-${key}: ${value};`)
        .join('\n      ')}
      
      ${Object.entries(theme.borderRadius)
        .map(([key, value]) => `--border-radius-${key}: ${value};`)
        .join('\n      ')}
      
      ${Object.entries(theme.shadows)
        .map(([key, value]) => `--shadow-${key}: ${value};`)
        .join('\n      ')}
    }
    
    .theme-${theme.name} {
      background-color: var(--color-background);
      color: var(--color-text);
    }
  `
}

export function generateThemeCSS(): string {
  return Object.values(themes).map(createThemeCSS).join('\n')
}

export function getTheme(): string {
  const stored = localStorage.getItem('pte_qr_theme')
  return stored || 'light'
}

export function setTheme(theme: string): void {
  localStorage.setItem('pte_qr_theme', theme)
}

export function toggleTheme(): string {
  const current = getTheme()
  const newTheme = current === 'light' ? 'dark' : 'light'
  setTheme(newTheme)
  return newTheme
}


export function isDarkMode(): boolean {
  return getTheme() === 'dark'
}

export function getThemeColors(theme: string): any {
  return themes[theme] || themes.light
}


export function removeTheme(): void {
  localStorage.removeItem('pte_qr_theme')
}

export function getThemeCSS(theme: string): string {
  return createThemeCSS(getThemeColors(theme))
}
