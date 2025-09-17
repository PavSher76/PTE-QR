'use client'

import { useState } from 'react'
import { useTranslation } from '@/lib/i18n'
import { useUser } from '@/lib/context'
import { useNotifications } from '@/lib/context'

interface LoginFormProps {
  onClose: () => void
}

export function LoginForm({ onClose }: LoginFormProps) {
  const { t } = useTranslation()
  const { login } = useUser()
  const { addNotification } = useNotifications()
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const result = await login(formData)
      
      if (result.success) {
        addNotification({
          type: 'success',
          title: t('auth.loginSuccess'),
          message: t('auth.welcomeBack'),
        })
        onClose()
      } else {
        addNotification({
          type: 'error',
          title: t('auth.loginError'),
          message: result.error || t('auth.invalidCredentials'),
        })
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: t('auth.loginError'),
        message: t('auth.networkError'),
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t('auth.login')}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('auth.username')}
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              placeholder={t('auth.usernamePlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('auth.password')}
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              placeholder={t('auth.passwordPlaceholder')}
            />
          </div>

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
            >
              {t('auth.cancel')}
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {isLoading ? t('auth.loggingIn') : t('auth.login')}
            </button>
          </div>
        </form>

        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {t('auth.testCredentials')}
          </p>
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
            <p><strong>{t('auth.username')}:</strong> testuser</p>
            <p><strong>{t('auth.password')}:</strong> secret</p>
          </div>
        </div>
      </div>
    </div>
  )
}
