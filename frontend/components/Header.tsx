'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useTheme } from '@/lib/context'
import { useTranslation } from '@/lib/i18n'
import { useUser } from '@/lib/context'
import { Logo } from './Logo'
import { LoginForm } from './LoginForm'

export function Header() {
  const { theme, toggleTheme } = useTheme()
  const { t, language, setLanguage } = useTranslation()
  const { user, logout, isAuthenticated } = useUser()
  const [showLoginForm, setShowLoginForm] = useState(false)

  return (
    <header className="border-b border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-3">
              <Logo size="medium" variant="compact" />
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                {t('app.title')}
              </span>
            </Link>
          </div>

          <nav className="hidden items-center space-x-6 md:flex">
            <Link
              href="/about"
              className="text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
            >
              {t('settings.about')}
            </Link>
          </nav>

          <div className="flex items-center space-x-4">
            {/* Language Toggle */}
            <div className="relative">
              <select
                value={language}
                onChange={(e) =>
                  setLanguage(e.target.value as 'ru' | 'en' | 'zh')
                }
                className="cursor-pointer border-none bg-transparent text-gray-600 outline-none transition-colors hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
                title={t('settings.language')}
              >
                <option value="ru">RU</option>
                <option value="en">EN</option>
                <option value="zh">中文</option>
              </select>
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
              title={t('settings.theme')}
            >
              {theme === 'light' ? (
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                  />
                </svg>
              ) : (
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                  />
                </svg>
              )}
            </button>

            {/* Settings Link - Only for Admin */}
            {isAuthenticated && user?.isAdmin && (
              <Link
                href="/settings"
                className="text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
                title="Настройки системы"
              >
                <svg
                  className="h-5 w-5"
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
              </Link>
            )}

            {/* User Menu */}
            {isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {user?.username}
                </span>
                <button
                  onClick={logout}
                  className="text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
                >
                  {t('auth.logout')}
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowLoginForm(true)}
                className="btn-secondary text-sm"
              >
                {t('auth.login')}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Login Form Modal */}
      {showLoginForm && <LoginForm onClose={() => setShowLoginForm(false)} />}
    </header>
  )
}
