'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  CogIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ServerIcon,
  KeyIcon,
  LinkIcon,
  CircleStackIcon,
  BellIcon,
  UserGroupIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

interface SystemSettings {
  urlPrefix: string
  documentStatusUrl: string
  systemName: string
  systemDescription: string
  maxDocumentSize: number
  allowedFileTypes: string[]
  sessionTimeout: number
  enableNotifications: boolean
  enableAuditLog: boolean
  enableApiRateLimit: boolean
  apiRateLimit: number
  enableMaintenanceMode: boolean
  maintenanceMessage: string
  enableUserRegistration: boolean
  enableEmailVerification: boolean
  enableTwoFactorAuth: boolean
  enablePasswordReset: boolean
  enableApiDocumentation: boolean
  enableMetrics: boolean
  enableLogging: boolean
  logLevel: string
  enableBackup: boolean
  backupFrequency: string
  enableMonitoring: boolean
  monitoringInterval: number
}

const defaultSettings: SystemSettings = {
  urlPrefix: 'https://pte-qr.example.com',
  documentStatusUrl: '/r',
  systemName: 'PTE QR System',
  systemDescription: 'Система проверки актуальности документов через QR-коды',
  maxDocumentSize: 10485760, // 10MB
  allowedFileTypes: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png'],
  sessionTimeout: 3600, // 1 hour
  enableNotifications: true,
  enableAuditLog: true,
  enableApiRateLimit: true,
  apiRateLimit: 1000,
  enableMaintenanceMode: false,
  maintenanceMessage: 'Система временно недоступна для технического обслуживания',
  enableUserRegistration: false,
  enableEmailVerification: true,
  enableTwoFactorAuth: false,
  enablePasswordReset: true,
  enableApiDocumentation: true,
  enableMetrics: true,
  enableLogging: true,
  logLevel: 'INFO',
  enableBackup: true,
  backupFrequency: 'daily',
  enableMonitoring: true,
  monitoringInterval: 300
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SystemSettings>(defaultSettings)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [activeTab, setActiveTab] = useState('general')

  useEffect(() => {
    // Загружаем настройки с сервера
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const token = localStorage.getItem('pte-qr-token')
      if (!token) {
        setIsLoading(false)
        return
      }

      const response = await fetch('/api/settings', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setSettings(data)
      } else if (response.status === 401) {
        // Token expired, redirect to login
        console.warn('Токен истек, перенаправление на страницу входа')
        localStorage.removeItem('pte-qr-token')
        localStorage.removeItem('pte-qr-user')
        window.location.href = '/'
      } else {
        console.error('Ошибка загрузки настроек:', response.statusText)
      }
    } catch (error) {
      console.error('Ошибка загрузки настроек:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const saveSettings = async () => {
    setIsSaving(true)
    setSaveStatus('idle')
    
    try {
      const token = localStorage.getItem('pte-qr-token')
      if (!token) {
        setSaveStatus('error')
        setTimeout(() => setSaveStatus('idle'), 3000)
        return
      }

      const response = await fetch('/api/settings', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      })

      if (response.ok) {
        const data = await response.json()
        setSettings(data)
        setSaveStatus('success')
        setTimeout(() => setSaveStatus('idle'), 3000)
      } else if (response.status === 401) {
        // Token expired, redirect to login
        console.warn('Токен истек, перенаправление на страницу входа')
        localStorage.removeItem('pte-qr-token')
        localStorage.removeItem('pte-qr-user')
        window.location.href = '/'
      } else {
        console.error('Ошибка сохранения настроек:', response.statusText)
        setSaveStatus('error')
        setTimeout(() => setSaveStatus('idle'), 3000)
      }
    } catch (error) {
      console.error('Ошибка сохранения настроек:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } finally {
      setIsSaving(false)
    }
  }

  const handleSettingChange = (key: keyof SystemSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const tabs = [
    { id: 'general', name: 'Общие', icon: CogIcon },
    { id: 'urls', name: 'URL и ссылки', icon: LinkIcon },
    { id: 'security', name: 'Безопасность', icon: ShieldCheckIcon },
    { id: 'notifications', name: 'Уведомления', icon: BellIcon },
    { id: 'system', name: 'Система', icon: ServerIcon },
    { id: 'users', name: 'Пользователи', icon: UserGroupIcon },
    { id: 'monitoring', name: 'Мониторинг', icon: ChartBarIcon }
  ]

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-lg">Загрузка настроек...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <CogIcon className="w-8 h-8 text-blue-400 mr-3" />
              <h1 className="text-2xl font-bold text-white">Настройки системы</h1>
            </div>
            <div className="flex items-center space-x-4">
              {saveStatus === 'success' && (
                <div className="flex items-center text-green-400">
                  <CheckCircleIcon className="w-5 h-5 mr-2" />
                  <span className="text-sm">Сохранено</span>
                </div>
              )}
              {saveStatus === 'error' && (
                <div className="flex items-center text-red-400">
                  <ExclamationTriangleIcon className="w-5 h-5 mr-2" />
                  <span className="text-sm">Ошибка сохранения</span>
                </div>
              )}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={saveSettings}
                disabled={isSaving}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSaving ? 'Сохранение...' : 'Сохранить'}
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  <tab.icon className="w-5 h-5 mr-3" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6">
              {/* General Settings */}
              {activeTab === 'general' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">Общие настройки</h2>
                  
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Название системы
                      </label>
                      <input
                        type="text"
                        id="system-name"
                        name="system-name"
                        value={settings.systemName}
                        onChange={(e) => handleSettingChange('systemName', e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Введите название системы"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Описание системы
                      </label>
                      <textarea
                        id="system-description"
                        name="system-description"
                        value={settings.systemDescription}
                        onChange={(e) => handleSettingChange('systemDescription', e.target.value)}
                        rows={3}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Введите описание системы"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Максимальный размер документа (байт)
                      </label>
                      <input
                        type="number"
                        id="max-document-size"
                        name="max-document-size"
                        value={settings.maxDocumentSize}
                        onChange={(e) => handleSettingChange('maxDocumentSize', parseInt(e.target.value))}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Разрешенные типы файлов
                      </label>
                      <input
                        type="text"
                        id="allowed-file-types"
                        name="allowed-file-types"
                        value={settings.allowedFileTypes.join(', ')}
                        onChange={(e) => handleSettingChange('allowedFileTypes', e.target.value.split(', '))}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="pdf, doc, docx, xls, xlsx, ppt, pptx, txt, jpg, jpeg, png"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Таймаут сессии (секунды)
                      </label>
                      <input
                        type="number"
                        id="session-timeout"
                        name="session-timeout"
                        value={settings.sessionTimeout}
                        onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </motion.div>
              )}

              {/* URL Settings */}
              {activeTab === 'urls' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">URL и ссылки</h2>
                  
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Префикс для генерации URL
                      </label>
                      <input
                        type="url"
                        id="url-prefix"
                        name="url-prefix"
                        value={settings.urlPrefix}
                        onChange={(e) => handleSettingChange('urlPrefix', e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="https://pte-qr.example.com"
                      />
                      <p className="text-sm text-gray-400 mt-2">
                        Базовый URL для генерации ссылок на статус документов
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Путь к окну статуса документа
                      </label>
                      <input
                        type="text"
                        id="document-status-url"
                        name="document-status-url"
                        value={settings.documentStatusUrl}
                        onChange={(e) => handleSettingChange('documentStatusUrl', e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="/r"
                      />
                      <p className="text-sm text-gray-400 mt-2">
                        Путь к странице отображения статуса документа
                      </p>
                    </div>

                    <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
                      <div className="flex items-start">
                        <InformationCircleIcon className="w-5 h-5 text-blue-400 mr-3 mt-0.5" />
                        <div>
                          <h3 className="text-sm font-medium text-blue-300 mb-1">Пример URL</h3>
                          <p className="text-sm text-blue-200">
                            {settings.urlPrefix}{settings.documentStatusUrl}/[docUid]/[revision]/[page]
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Security Settings */}
              {activeTab === 'security' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">Безопасность</h2>
                  
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Включить регистрацию пользователей</h3>
                        <p className="text-sm text-gray-400">Разрешить новым пользователям регистрироваться в системе</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-user-registration"
                          name="enable-user-registration"
                          checked={settings.enableUserRegistration}
                          onChange={(e) => handleSettingChange('enableUserRegistration', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Подтверждение email</h3>
                        <p className="text-sm text-gray-400">Требовать подтверждение email при регистрации</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-email-verification"
                          name="enable-email-verification"
                          checked={settings.enableEmailVerification}
                          onChange={(e) => handleSettingChange('enableEmailVerification', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Двухфакторная аутентификация</h3>
                        <p className="text-sm text-gray-400">Требовать 2FA для входа в систему</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-two-factor-auth"
                          name="enable-two-factor-auth"
                          checked={settings.enableTwoFactorAuth}
                          onChange={(e) => handleSettingChange('enableTwoFactorAuth', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Сброс пароля</h3>
                        <p className="text-sm text-gray-400">Разрешить пользователям сбрасывать пароли</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-password-reset"
                          name="enable-password-reset"
                          checked={settings.enablePasswordReset}
                          onChange={(e) => handleSettingChange('enablePasswordReset', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Аудит действий</h3>
                        <p className="text-sm text-gray-400">Вести журнал всех действий пользователей</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-audit-log"
                          name="enable-audit-log"
                          checked={settings.enableAuditLog}
                          onChange={(e) => handleSettingChange('enableAuditLog', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Notifications Settings */}
              {activeTab === 'notifications' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">Уведомления</h2>
                  
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Включить уведомления</h3>
                        <p className="text-sm text-gray-400">Показывать уведомления пользователям</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-notifications"
                          name="enable-notifications"
                          checked={settings.enableNotifications}
                          onChange={(e) => handleSettingChange('enableNotifications', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* System Settings */}
              {activeTab === 'system' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">Система</h2>
                  
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Режим обслуживания</h3>
                        <p className="text-sm text-gray-400">Временно отключить систему для обслуживания</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-maintenance-mode"
                          name="enable-maintenance-mode"
                          checked={settings.enableMaintenanceMode}
                          onChange={(e) => handleSettingChange('enableMaintenanceMode', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    {settings.enableMaintenanceMode && (
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Сообщение режима обслуживания
                        </label>
                        <textarea
                          id="maintenance-message"
                          name="maintenance-message"
                          value={settings.maintenanceMessage}
                          onChange={(e) => handleSettingChange('maintenanceMessage', e.target.value)}
                          rows={3}
                          className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Введите сообщение для пользователей"
                        />
                      </div>
                    )}

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">API документация</h3>
                        <p className="text-sm text-gray-400">Включить Swagger UI для API</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-api-documentation"
                          name="enable-api-documentation"
                          checked={settings.enableApiDocumentation}
                          onChange={(e) => handleSettingChange('enableApiDocumentation', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Метрики системы</h3>
                        <p className="text-sm text-gray-400">Собирать метрики производительности</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-metrics"
                          name="enable-metrics"
                          checked={settings.enableMetrics}
                          onChange={(e) => handleSettingChange('enableMetrics', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Логирование</h3>
                        <p className="text-sm text-gray-400">Вести логи системы</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-logging"
                          name="enable-logging"
                          checked={settings.enableLogging}
                          onChange={(e) => handleSettingChange('enableLogging', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    {settings.enableLogging && (
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Уровень логирования
                        </label>
                        <select
                          id="log-level"
                          name="log-level"
                          value={settings.logLevel}
                          onChange={(e) => handleSettingChange('logLevel', e.target.value)}
                          className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="DEBUG">DEBUG</option>
                          <option value="INFO">INFO</option>
                          <option value="WARNING">WARNING</option>
                          <option value="ERROR">ERROR</option>
                          <option value="CRITICAL">CRITICAL</option>
                        </select>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

              {/* Users Settings */}
              {activeTab === 'users' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">Пользователи</h2>
                  
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Регистрация пользователей</h3>
                        <p className="text-sm text-gray-400">Разрешить новым пользователям регистрироваться</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.enableUserRegistration}
                          onChange={(e) => handleSettingChange('enableUserRegistration', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Подтверждение email</h3>
                        <p className="text-sm text-gray-400">Требовать подтверждение email при регистрации</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-email-verification"
                          name="enable-email-verification"
                          checked={settings.enableEmailVerification}
                          onChange={(e) => handleSettingChange('enableEmailVerification', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Monitoring Settings */}
              {activeTab === 'monitoring' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <h2 className="text-2xl font-bold text-white mb-6">Мониторинг</h2>
                  
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Включить мониторинг</h3>
                        <p className="text-sm text-gray-400">Собирать метрики производительности системы</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-monitoring"
                          name="enable-monitoring"
                          checked={settings.enableMonitoring}
                          onChange={(e) => handleSettingChange('enableMonitoring', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    {settings.enableMonitoring && (
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Интервал мониторинга (секунды)
                        </label>
                        <input
                          type="number"
                          id="monitoring-interval"
                          name="monitoring-interval"
                          value={settings.monitoringInterval}
                          onChange={(e) => handleSettingChange('monitoringInterval', parseInt(e.target.value))}
                          className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    )}

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">Автоматическое резервное копирование</h3>
                        <p className="text-sm text-gray-400">Создавать резервные копии данных</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          id="enable-backup"
                          name="enable-backup"
                          checked={settings.enableBackup}
                          onChange={(e) => handleSettingChange('enableBackup', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    {settings.enableBackup && (
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Частота резервного копирования
                        </label>
                        <select
                          id="backup-frequency"
                          name="backup-frequency"
                          value={settings.backupFrequency}
                          onChange={(e) => handleSettingChange('backupFrequency', e.target.value)}
                          className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="hourly">Каждый час</option>
                          <option value="daily">Ежедневно</option>
                          <option value="weekly">Еженедельно</option>
                          <option value="monthly">Ежемесячно</option>
                        </select>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
