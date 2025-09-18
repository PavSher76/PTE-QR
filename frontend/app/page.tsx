'use client'

import { useState, useEffect } from 'react'
import { QRCodeScanner } from '@/components/QRCodeScanner'
import { DocumentStatus } from '@/components/DocumentStatus'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { LanguageSwitcher } from '@/components/LanguageSwitcher'
import { Logo } from '@/components/Logo'
import { useTranslation } from '@/lib/i18n'
import { useNotifications } from '@/lib/context'

export default function HomePage() {
  const { t, language } = useTranslation()
  const { addNotification } = useNotifications()
  const [scannedData, setScannedData] = useState<string | null>(null)
  const [isScanning, setIsScanning] = useState(false)

  // Update document title when language changes
  useEffect(() => {
    document.title = t('app.title')
  }, [language, t])

  const handleScan = (data: string) => {
    setScannedData(data)
    setIsScanning(false)
    addNotification({
      type: 'success',
      title: t('scan.title'),
      message: t('document.status') + ': ' + data,
    })
  }

  const handleScanError = (error: string) => {
    addNotification({
      type: 'error',
      title: t('error'),
      message: error,
    })
  }

  const handleReset = () => {
    setScannedData(null)
    setIsScanning(false)
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container mx-auto flex-1 px-4 py-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-8 text-center">
            <div className="mb-6 flex items-center justify-center gap-4">
              <Logo size="large" variant="full" />
            </div>
            <div className="mb-4 flex items-center justify-center gap-4">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 via-accent-600 to-primary-600 bg-clip-text text-transparent dark:from-primary-400 dark:via-accent-400 dark:to-primary-400 animate-pulse-slow">
              {t('app.title')}
            </h1>
              <LanguageSwitcher />
            </div>
            <p className="mb-8 text-xl text-secondary-600 dark:text-secondary-300 animate-fade-in">
              {t('app.description')}
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            {/* QR Scanner Section */}
            <div className="card p-6">
              <h2 className="mb-4 text-2xl font-semibold text-primary-700 dark:text-primary-300 animate-slide-up">
                {t('scan.title')}
              </h2>

              {!isScanning && !scannedData && (
                <div className="text-center">
                  <div className="mb-4">
                    <svg
                      className="mx-auto h-24 w-24 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1}
                        d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"
                      />
                    </svg>
                  </div>
                  <p className="mb-4 text-gray-600">{t('scan.instruction')}</p>
                  <button
                    onClick={() => setIsScanning(true)}
                    className="btn-primary"
                  >
                    {t('header.scan')}
                  </button>
                </div>
              )}

              {isScanning && (
                <QRCodeScanner
                  onScan={handleScan}
                  onCancel={() => setIsScanning(false)}
                />
              )}

              {scannedData && (
                <div className="text-center">
                  <div className="mb-4">
                    <svg
                      className="mx-auto h-12 w-12 text-success-500"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                  <p className="mb-4 text-gray-600">{t('success')}</p>
                  <div className="mb-4 rounded-md bg-gray-100 p-3">
                    <code className="break-all text-sm text-gray-800">
                      {scannedData}
                    </code>
                  </div>
                  <button onClick={handleReset} className="btn-secondary mr-2">
                    {t('header.scan')}
                  </button>
                </div>
              )}
            </div>

            {/* Document Status Section */}
            <div className="card p-6">
              <h2 className="mb-4 text-2xl font-semibold text-primary-700 dark:text-primary-300 animate-slide-up">
                {t('document.status')}
              </h2>

              {scannedData ? (
                <DocumentStatus qrData={scannedData} />
              ) : (
                <div className="text-center text-gray-500 dark:text-gray-400">
                  <p>{t('scan.instruction')}</p>
                </div>
              )}
            </div>
          </div>

          {/* Features Section */}
          <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3">
            <div className="card p-6 text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100">
                <svg
                  className="h-6 w-6 text-primary-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                {language === 'ru'
                  ? 'Проверка актуальности'
                  : language === 'en'
                  ? 'Status Verification'
                  : '状态验证'}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {language === 'ru'
                  ? 'Мгновенная проверка актуальности документа и его ревизии'
                  : language === 'en'
                  ? 'Instant verification of document status and revision'
                  : '即时验证文档状态和修订版'}
              </p>
            </div>

            <div className="card p-6 text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-success-100">
                <svg
                  className="h-6 w-6 text-success-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                {language === 'ru'
                  ? 'Веб-интерфейс'
                  : language === 'en'
                  ? 'Web Interface'
                  : '网络界面'}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {language === 'ru'
                  ? 'Современный веб-интерфейс для работы с документами'
                  : language === 'en'
                  ? 'Modern web interface for document management'
                  : '用于文档管理的现代网络界面'}
              </p>
            </div>

            <div className="card p-6 text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-warning-100">
                <svg
                  className="h-6 w-6 text-warning-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                {language === 'ru'
                  ? 'Безопасность'
                  : language === 'en'
                  ? 'Security'
                  : '安全性'}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {language === 'ru'
                  ? 'HMAC подпись обеспечивает защиту от подделки QR-кодов'
                  : language === 'en'
                  ? 'HMAC signature provides protection against QR code forgery'
                  : 'HMAC签名提供防止二维码伪造的保护'}
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
