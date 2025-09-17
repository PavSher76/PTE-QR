/**
 * Internationalization utilities
 */

'use client'

import React, { useState, useEffect, createContext, useContext } from 'react'

// Extended translations with all necessary keys
const translations = {
  ru: {
    'app.title': 'PTE QR Система',
    'app.description': 'Система проверки актуальности документов через QR-коды',
    'app.keywords': 'PTE, QR, документы, актуальность, ENOVIA',
    'header.title': 'PTE QR Система',
    'header.scan': 'Сканировать QR',
    'header.admin': 'Администрирование',
    'header.logout': 'Выйти',
    'header.login': 'Войти',
    'status.actual': 'АКТУАЛЬНЫЙ',
    'status.outdated': 'УСТАРЕЛ',
    'scan.title': 'Сканирование QR-кода',
    'scan.instruction': 'Отсканируйте QR-код для проверки статуса документа',
    'document.status': 'Статус документа',
    'document.revision': 'Ревизия',
    'document.page': 'Страница',
    'document.lastModified': 'Последнее изменение',
    'document.releasedAt': 'Дата выпуска',
    'document.supersededBy': 'Заменен на',
    'document.openDocument': 'Открыть документ',
    'document.openLatest': 'Открыть последнюю версию',
    'document.document': 'Документ',
    'document.enoviaState': 'Состояние в ENOVIA',
    'document.noData': 'Нет данных для отображения',
    'error.notFound': 'Документ не найден',
    'error.invalidParams': 'Неверные параметры',
    'error.serverError': 'Ошибка сервера',
    'error.cameraAccess': 'Не удалось получить доступ к камере',
    loading: 'Загрузка...',
    success: 'Успешно',
    error: 'Ошибка',
    warning: 'Предупреждение',
    info: 'Информация',
    'scan.cameraInstruction': 'Наведите камеру на QR-код документа',
    'scan.scan': 'Сканировать',
    'scan.cancel': 'Отмена',
    'scan.close': 'Закрыть',
    'settings.about': 'О системе',
    'settings.language': 'Язык',
    'settings.theme': 'Тема',
    'auth.login': 'Войти',
    'auth.logout': 'Выйти',
    'auth.username': 'Имя пользователя',
    'auth.password': 'Пароль',
    'auth.usernamePlaceholder': 'Введите имя пользователя',
    'auth.passwordPlaceholder': 'Введите пароль',
    'auth.loginSuccess': 'Успешный вход',
    'auth.welcomeBack': 'Добро пожаловать!',
    'auth.loginError': 'Ошибка входа',
    'auth.invalidCredentials': 'Неверные учетные данные',
    'auth.networkError': 'Ошибка сети',
    'auth.loggingIn': 'Вход...',
    'auth.cancel': 'Отмена',
    'auth.testCredentials': 'Тестовые учетные данные:',
    'auth.logout': 'Выйти',
    'auth.ssoLogin': 'Войти через SSO',
    'notification.dismiss': 'Закрыть уведомление',
    'footer.title': 'PTE QR Система',
    'footer.description':
      'Система проверки актуальности документов через QR-коды с интеграцией в ENOVIA PLM.',
    'footer.product': 'Продукт',
    'footer.support': 'Поддержка',
    'footer.company': 'Компания',
    'footer.features': 'Возможности',
    'footer.integration': 'Интеграция',
    'footer.api': 'API',
    'footer.documentation': 'Документация',
    'footer.help': 'Помощь',
    'footer.contacts': 'Контакты',
    'footer.about': 'О нас',
    'footer.privacy': 'Политика конфиденциальности',
    'footer.terms': 'Условия использования',
    'footer.copyright': '© 2024 ПТИ. Все права защищены.',
    'document.status': 'Статус документа',
    'document.document': 'Документ',
    'document.revision': 'Ревизия',
    'document.page': 'Страница',
    'document.businessStatus': 'Бизнес-статус',
    'document.enoviaState': 'Состояние ENOVIA',
    'document.isActual': 'Актуальность',
    'document.releasedAt': 'Дата выпуска',
    'document.supersededBy': 'Заменен на',
    'document.lastModified': 'Последнее изменение',
    'document.links': 'Ссылки',
    'document.openDocument': 'Открыть документ',
    'document.openLatest': 'Открыть последнюю версию',
    'document.noData': 'Нет данных для отображения',
    loading: 'Загрузка...',
    error: 'Ошибка',
    'error.serverError': 'Ошибка сервера',
  },
  en: {
    'app.title': 'PTE QR System',
    'app.description': 'Document status verification system via QR codes',
    'app.keywords': 'PTE, QR, documents, status, ENOVIA',
    'header.title': 'PTE QR System',
    'header.scan': 'Scan QR',
    'header.admin': 'Administration',
    'header.logout': 'Logout',
    'header.login': 'Login',
    'status.actual': 'ACTUAL',
    'status.outdated': 'OUTDATED',
    'scan.title': 'QR Code Scanning',
    'scan.instruction': 'Scan QR code to check document status',
    'document.status': 'Document Status',
    'document.revision': 'Revision',
    'document.page': 'Page',
    'document.lastModified': 'Last Modified',
    'document.releasedAt': 'Released At',
    'document.supersededBy': 'Superseded By',
    'document.openDocument': 'Open Document',
    'document.openLatest': 'Open Latest',
    'document.document': 'Document',
    'document.enoviaState': 'ENOVIA State',
    'document.noData': 'No data to display',
    'error.notFound': 'Document not found',
    'error.invalidParams': 'Invalid parameters',
    'error.serverError': 'Server error',
    'error.cameraAccess': 'Failed to access camera',
    loading: 'Loading...',
    success: 'Success',
    error: 'Error',
    warning: 'Warning',
    info: 'Information',
    'scan.cameraInstruction': 'Point camera at document QR code',
    'scan.scan': 'Scan',
    'scan.cancel': 'Cancel',
    'scan.close': 'Close',
    'settings.about': 'About',
    'settings.language': 'Language',
    'settings.theme': 'Theme',
    'auth.login': 'Login',
    'auth.logout': 'Logout',
    'auth.username': 'Username',
    'auth.password': 'Password',
    'auth.usernamePlaceholder': 'Enter username',
    'auth.passwordPlaceholder': 'Enter password',
    'auth.loginSuccess': 'Login successful',
    'auth.welcomeBack': 'Welcome back!',
    'auth.loginError': 'Login error',
    'auth.invalidCredentials': 'Invalid credentials',
    'auth.networkError': 'Network error',
    'auth.loggingIn': 'Logging in...',
    'auth.cancel': 'Cancel',
    'auth.testCredentials': 'Test credentials:',
    'auth.ssoLogin': 'SSO Login',
    'notification.dismiss': 'Dismiss notification',
    'footer.title': 'PTE QR System',
    'footer.description':
      'Document status verification system via QR codes with ENOVIA PLM integration.',
    'footer.product': 'Product',
    'footer.support': 'Support',
    'footer.company': 'Company',
    'footer.features': 'Features',
    'footer.integration': 'Integration',
    'footer.api': 'API',
    'footer.documentation': 'Documentation',
    'footer.help': 'Help',
    'footer.contacts': 'Contacts',
    'footer.about': 'About Us',
    'footer.privacy': 'Privacy Policy',
    'footer.terms': 'Terms of Use',
    'footer.copyright': '© 2024 PTI. All rights reserved.',
  },
  zh: {
    'app.title': 'PTE QR 系统',
    'app.description': '通过二维码验证文档状态的系统',
    'app.keywords': 'PTE, QR, 文档, 状态, ENOVIA',
    'header.title': 'PTE QR 系统',
    'header.scan': '扫描二维码',
    'header.admin': '管理',
    'header.logout': '退出',
    'header.login': '登录',
    'status.actual': '当前',
    'status.outdated': '过时',
    'scan.title': '二维码扫描',
    'scan.instruction': '扫描二维码检查文档状态',
    'document.status': '文档状态',
    'document.revision': '修订版',
    'document.page': '页面',
    'document.lastModified': '最后修改',
    'document.releasedAt': '发布日期',
    'document.supersededBy': '被替换为',
    'document.openDocument': '打开文档',
    'document.openLatest': '打开最新版本',
    'document.document': '文档',
    'document.enoviaState': 'ENOVIA状态',
    'document.noData': '无数据显示',
    'error.notFound': '文档未找到',
    'error.invalidParams': '参数无效',
    'error.serverError': '服务器错误',
    'error.cameraAccess': '无法访问摄像头',
    loading: '加载中...',
    success: '成功',
    error: '错误',
    warning: '警告',
    info: '信息',
    'scan.cameraInstruction': '将摄像头对准文档二维码',
    'scan.scan': '扫描',
    'scan.cancel': '取消',
    'scan.close': '关闭',
    'settings.about': '关于',
    'settings.language': '语言',
    'settings.theme': '主题',
    'auth.login': '登录',
    'auth.logout': '退出',
    'auth.username': '用户名',
    'auth.password': '密码',
    'auth.usernamePlaceholder': '输入用户名',
    'auth.passwordPlaceholder': '输入密码',
    'auth.loginSuccess': '登录成功',
    'auth.welcomeBack': '欢迎回来！',
    'auth.loginError': '登录错误',
    'auth.invalidCredentials': '无效凭据',
    'auth.networkError': '网络错误',
    'auth.loggingIn': '登录中...',
    'auth.cancel': '取消',
    'auth.testCredentials': '测试凭据：',
    'auth.ssoLogin': 'SSO登录',
    'notification.dismiss': '关闭通知',
    'footer.title': 'PTE QR 系统',
    'footer.description': '通过二维码验证文档状态的系统，集成ENOVIA PLM。',
    'footer.product': '产品',
    'footer.support': '支持',
    'footer.company': '公司',
    'footer.features': '功能',
    'footer.integration': '集成',
    'footer.api': 'API',
    'footer.documentation': '文档',
    'footer.help': '帮助',
    'footer.contacts': '联系',
    'footer.about': '关于我们',
    'footer.privacy': '隐私政策',
    'footer.terms': '使用条款',
    'footer.copyright': '© 2024 PTI. 版权所有。',
  },
}

type Language = keyof typeof translations

// Language context
const LanguageContext = createContext<{
  language: Language
  setLanguage: (lang: Language) => void
  t: (key: string, params?: Record<string, any>) => string
}>({
  language: 'ru',
  setLanguage: () => {},
  t: (key: string) => key,
})

// Language provider component
export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>('ru')

  // Load language from localStorage on mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('pte-qr-language') as Language
    if (savedLanguage && translations[savedLanguage]) {
      setLanguageState(savedLanguage)
    }
  }, [])

  // Save language to localStorage when changed
  const setLanguage = (lang: Language) => {
    setLanguageState(lang)
    localStorage.setItem('pte-qr-language', lang)
  }

  const t = (key: string, params?: Record<string, any>) => {
    const translation =
      translations[language]?.[
        key as keyof (typeof translations)[typeof language]
      ] || key

    if (params) {
      return Object.keys(params).reduce((str, param) => {
        return str.replace(`{{${param}}}`, params[param])
      }, translation)
    }

    return translation
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

// Hook to use translations
export function useTranslation() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useTranslation must be used within LanguageProvider')
  }
  return context
}

// Hook to get current language
export function useLanguage() {
  const { language, setLanguage } = useTranslation()
  return { language, setLanguage }
}
