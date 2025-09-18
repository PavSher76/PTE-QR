'use client'

import { useState, useEffect } from 'react'
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

  useEffect(() => {
    if (showLoginForm) {
      console.log('LoginForm is now visible')
    }
  }, [showLoginForm])

  return (
    <header className="border-b border-white/20 bg-white/80 backdrop-blur-md shadow-lg transition-all duration-300 dark:border-white/10 dark:bg-nk-900/80">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-3">
              <Logo size="medium" variant="compact" />
              <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent dark:from-primary-400 dark:to-accent-400">
                {t('app.title')}
              </span>
            </Link>
          </div>

          <nav className="hidden items-center space-x-6 md:flex">
            <Link
              href="/about"
              className="text-secondary-600 transition-all duration-200 hover:text-primary-600 hover:scale-105 dark:text-secondary-300 dark:hover:text-primary-400"
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
              className="text-gray-600 transition-all duration-200 hover:text-gray-900 hover:scale-110 dark:text-gray-300 dark:hover:text-white"
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

            {/* User Menu */}
            {isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {user?.username}
                </span>
                <button
                  onClick={logout}
                  className="text-secondary-600 transition-all duration-200 hover:text-primary-600 hover:scale-105 dark:text-secondary-300 dark:hover:text-primary-400"
                >
                  {t('auth.logout')}
                </button>
              </div>
            ) : (
              <button
                onClick={() => {
                  console.log('Login button clicked!')
                  setShowLoginForm(true)
                }}
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
