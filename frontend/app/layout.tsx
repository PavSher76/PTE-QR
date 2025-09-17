import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AppProvider } from '@/lib/context'
import { LanguageProvider } from '@/lib/i18n'
import { NotificationContainer } from '@/components/NotificationContainer'
import { ThemeWrapper } from '@/components/ThemeWrapper'

const inter = Inter({ subsets: ['latin'] })

// Viewport configuration
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

// Default metadata - will be overridden by client-side localization
export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'),
  title: 'PTE QR System',
  description: 'Document status verification system via QR codes',
  keywords: ['PTE', 'QR', 'documents', 'status', 'ENOVIA'],
  authors: [{ name: 'PTI' }],
  icons: {
    icon: '/favicon.svg',
    shortcut: '/favicon.svg',
    apple: '/favicon.svg',
  },
  openGraph: {
    title: 'PTE QR System',
    description: 'Document status verification system via QR codes',
    type: 'website',
    images: [
      {
        url: '/images/logo.svg',
        width: 120,
        height: 120,
        alt: 'PTE QR Logo',
      },
    ],
  },
  twitter: {
    card: 'summary',
    title: 'PTE QR System',
    description: 'Document status verification system via QR codes',
    images: ['/images/logo.svg'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <LanguageProvider>
          <AppProvider>
            <ThemeWrapper>
              <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
                {children}
                <NotificationContainer />
              </div>
            </ThemeWrapper>
          </AppProvider>
        </LanguageProvider>
      </body>
    </html>
  )
}
