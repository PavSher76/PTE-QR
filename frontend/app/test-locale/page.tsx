'use client'

import { useTranslation } from '@/lib/i18n'
import { LanguageSwitcher } from '@/components/LanguageSwitcher'

export default function TestLocalePage() {
  const { t, language } = useTranslation()

  return (
    <div className="min-h-screen bg-gray-50 py-8 dark:bg-gray-900">
      <div className="mx-auto max-w-4xl px-4">
        <div className="rounded-lg bg-white p-8 shadow-lg dark:bg-gray-800">
          <div className="mb-8 flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {t('app.title')} - {t('app.description')}
            </h1>
            <LanguageSwitcher />
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
            {/* App Info */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                App Information
              </h2>
              <div className="space-y-2">
                <p>
                  <strong>Title:</strong> {t('app.title')}
                </p>
                <p>
                  <strong>Description:</strong> {t('app.description')}
                </p>
                <p>
                  <strong>Keywords:</strong> {t('app.keywords')}
                </p>
                <p>
                  <strong>Current Language:</strong> {language}
                </p>
              </div>
            </div>

            {/* Header Translations */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Header Translations
              </h2>
              <div className="space-y-2">
                <p>
                  <strong>Title:</strong> {t('header.title')}
                </p>
                <p>
                  <strong>Scan:</strong> {t('header.scan')}
                </p>
                <p>
                  <strong>Admin:</strong> {t('header.admin')}
                </p>
                <p>
                  <strong>Login:</strong> {t('header.login')}
                </p>
                <p>
                  <strong>Logout:</strong> {t('header.logout')}
                </p>
              </div>
            </div>

            {/* Document Translations */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Document Translations
              </h2>
              <div className="space-y-2">
                <p>
                  <strong>Status:</strong> {t('document.status')}
                </p>
                <p>
                  <strong>Revision:</strong> {t('document.revision')}
                </p>
                <p>
                  <strong>Page:</strong> {t('document.page')}
                </p>
                <p>
                  <strong>Last Modified:</strong> {t('document.lastModified')}
                </p>
                <p>
                  <strong>Released At:</strong> {t('document.releasedAt')}
                </p>
                <p>
                  <strong>Superseded By:</strong> {t('document.supersededBy')}
                </p>
              </div>
            </div>

            {/* Status Translations */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Status Translations
              </h2>
              <div className="space-y-2">
                <p>
                  <strong>Actual:</strong> {t('status.actual')}
                </p>
                <p>
                  <strong>Outdated:</strong> {t('status.outdated')}
                </p>
                <p>
                  <strong>Loading:</strong> {t('loading')}
                </p>
                <p>
                  <strong>Success:</strong> {t('success')}
                </p>
                <p>
                  <strong>Error:</strong> {t('error')}
                </p>
                <p>
                  <strong>Warning:</strong> {t('warning')}
                </p>
                <p>
                  <strong>Info:</strong> {t('info')}
                </p>
              </div>
            </div>

            {/* Scan Translations */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Scan Translations
              </h2>
              <div className="space-y-2">
                <p>
                  <strong>Title:</strong> {t('scan.title')}
                </p>
                <p>
                  <strong>Instruction:</strong> {t('scan.instruction')}
                </p>
              </div>
            </div>

            {/* Error Translations */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Error Translations
              </h2>
              <div className="space-y-2">
                <p>
                  <strong>Not Found:</strong> {t('error.notFound')}
                </p>
                <p>
                  <strong>Invalid Params:</strong> {t('error.invalidParams')}
                </p>
                <p>
                  <strong>Server Error:</strong> {t('error.serverError')}
                </p>
              </div>
            </div>
          </div>

          {/* Language-specific content */}
          <div className="mt-8 rounded-lg bg-gray-100 p-6 dark:bg-gray-700">
            <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
              Language-specific Content
            </h3>
            <div className="space-y-2">
              {language === 'ru' && (
                <div>
                  <p className="text-gray-700 dark:text-gray-300">
                    🇷🇺 <strong>Русский язык:</strong> Система полностью
                    локализована на русский язык. Все элементы интерфейса
                    переведены и адаптированы для русскоязычных пользователей.
                  </p>
                </div>
              )}
              {language === 'en' && (
                <div>
                  <p className="text-gray-700 dark:text-gray-300">
                    🇺🇸 <strong>English:</strong> The system is fully localized
                    for English. All interface elements are translated and
                    adapted for English-speaking users.
                  </p>
                </div>
              )}
              {language === 'zh' && (
                <div>
                  <p className="text-gray-700 dark:text-gray-300">
                    🇨🇳 <strong>中文:</strong> 系统已完全本地化为中文。
                    所有界面元素都已翻译并适应中文用户。
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
