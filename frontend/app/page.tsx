'use client'

import { useState, useEffect } from 'react'
import { QRCodeScanner } from '@/components/QRCodeScanner'
import { DocumentStatus } from '@/components/DocumentStatus'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { LanguageSwitcher } from '@/components/LanguageSwitcher'
import { Logo } from '@/components/Logo'
import { useTranslation } from '@/lib/i18n'
import { useNotifications, useUser } from '@/lib/context'
import { PdfUploadForm } from '@/components/PdfUploadForm'
import { DocumentControl } from '@/components/DocumentControl'
import Link from 'next/link'

export default function HomePage() {
  const { t, language } = useTranslation()
  const { addNotification } = useNotifications()
  const { user, isAuthenticated } = useUser()
  const [scannedData, setScannedData] = useState<string | null>(null)
  const [isScanning, setIsScanning] = useState(false)
  const [showPdfUpload, setShowPdfUpload] = useState(false)
  const [showDocumentControl, setShowDocumentControl] = useState(false)

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
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                {t('app.title')}
              </h1>
              <LanguageSwitcher />
            </div>
            <p className="mb-8 text-xl text-gray-600 dark:text-gray-300">
              {t('app.description')}
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            {/* QR Scanner Section */}
            <div className="card p-6">
              <h2 className="mb-4 text-2xl font-semibold text-gray-900 dark:text-white">
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
              <h2 className="mb-4 text-2xl font-semibold text-gray-900">
                {t('document.status')}
              </h2>

              {scannedData ? (
                <DocumentStatus qrData={scannedData} />
              ) : (
                <div className="text-center text-gray-500">
                  <p>{t('scan.instruction')}</p>
                </div>
              )}
            </div>
          </div>

          {/* Features Section */}
          <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3">
            <button 
              onClick={() => setShowDocumentControl(true)}
              className="card p-6 text-center transition-all duration-200 hover:shadow-lg hover:scale-105"
            >
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 hover:bg-blue-200 transition-colors">
                <svg
                  className="h-6 w-6 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                {t('normocontrol.title')}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {t('normocontrol.description')}
              </p>
            </button>

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
                    d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-gray-900">
                {language === 'ru'
                  ? 'Мобильная версия'
                  : language === 'en'
                  ? 'Mobile Version'
                  : '移动版本'}
              </h3>
              <p className="text-gray-600">
                {language === 'ru'
                  ? 'Оптимизировано для использования на мобильных устройствах'
                  : language === 'en'
                  ? 'Optimized for use on mobile devices'
                  : '针对移动设备使用进行了优化'}
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
              <h3 className="mb-2 text-lg font-semibold text-gray-900">
                {language === 'ru'
                  ? 'Безопасность'
                  : language === 'en'
                  ? 'Security'
                  : '安全性'}
              </h3>
              <p className="text-gray-600">
                {language === 'ru'
                  ? 'HMAC подпись обеспечивает защиту от подделки QR-кодов'
                  : language === 'en'
                  ? 'HMAC signature provides protection against QR code forgery'
                  : 'HMAC签名提供防止二维码伪造的保护'}
              </p>
            </div>
          </div>

          {/* Admin Settings Section */}
          {isAuthenticated && user?.isAdmin && (
            <div className="mt-12">
              <h2 className="mb-6 text-2xl font-bold text-gray-900 dark:text-white text-center">
                {language === 'ru'
                  ? 'Административные функции'
                  : language === 'en'
                  ? 'Administrative Functions'
                  : '管理功能'}
              </h2>
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                <Link href="/settings" className="group">
                  <div className="card p-6 text-center transition-all duration-200 group-hover:shadow-lg group-hover:scale-105">
                    <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100 group-hover:bg-purple-200 transition-colors">
                      <svg
                        className="h-6 w-6 text-purple-600"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                      </svg>
                    </div>
                    <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                      {language === 'ru'
                        ? 'Настройки системы'
                        : language === 'en'
                        ? 'System Settings'
                        : '系统设置'}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      {language === 'ru'
                        ? 'Конфигурирование и настройка системы'
                        : language === 'en'
                        ? 'Configure and customize system settings'
                        : '配置和自定义系统设置'}
                    </p>
                  </div>
                </Link>

                <button 
                  onClick={() => setShowPdfUpload(true)}
                  className="card p-6 text-center transition-all duration-200 hover:shadow-lg hover:scale-105"
                >
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-green-100 hover:bg-green-200 transition-colors">
                    <svg
                      className="h-6 w-6 text-green-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                  </div>
                  <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                    {language === 'ru'
                      ? 'Загрузка PDF'
                      : language === 'en'
                      ? 'PDF Upload'
                      : 'PDF上传'}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {language === 'ru'
                      ? 'Загрузить PDF документ и добавить QR-коды'
                      : language === 'en'
                      ? 'Upload PDF document and add QR codes'
                      : '上传PDF文档并添加QR码'}
                  </p>
                </button>

                <div className="card p-6 text-center opacity-50">
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-gray-100">
                    <svg
                      className="h-6 w-6 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                      />
                    </svg>
                  </div>
                  <h3 className="mb-2 text-lg font-semibold text-gray-500">
                    {language === 'ru'
                      ? 'Управление пользователями'
                      : language === 'en'
                      ? 'User Management'
                      : '用户管理'}
                  </h3>
                  <p className="text-gray-400">
                    {language === 'ru'
                      ? 'Скоро будет доступно'
                      : language === 'en'
                      ? 'Coming soon'
                      : '即将推出'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />

      {/* PDF Upload Modal */}
      {showPdfUpload && (
        <PdfUploadForm onClose={() => setShowPdfUpload(false)} />
      )}

      {/* Document Control Modal */}
      {showDocumentControl && (
        <DocumentControl onClose={() => setShowDocumentControl(false)} />
      )}
    </div>
  )
}
