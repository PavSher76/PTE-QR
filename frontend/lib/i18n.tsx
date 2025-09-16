/**
 * Internationalization utilities
 */

'use client';

import { useState, useEffect, createContext, useContext } from 'react';

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
    'error.notFound': 'Документ не найден',
    'error.invalidParams': 'Неверные параметры',
    'error.serverError': 'Ошибка сервера',
    'loading': 'Загрузка...',
    'success': 'Успешно',
    'error': 'Ошибка',
    'warning': 'Предупреждение',
    'info': 'Информация'
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
    'error.notFound': 'Document not found',
    'error.invalidParams': 'Invalid parameters',
    'error.serverError': 'Server error',
    'loading': 'Loading...',
    'success': 'Success',
    'error': 'Error',
    'warning': 'Warning',
    'info': 'Information'
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
    'error.notFound': '文档未找到',
    'error.invalidParams': '参数无效',
    'error.serverError': '服务器错误',
    'loading': '加载中...',
    'success': '成功',
    'error': '错误',
    'warning': '警告',
    'info': '信息'
  }
};

type Language = keyof typeof translations;

// Language context
const LanguageContext = createContext<{
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, params?: Record<string, any>) => string;
}>({
  language: 'ru',
  setLanguage: () => {},
  t: (key: string) => key
});

// Language provider component
export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>('ru');

  // Load language from localStorage on mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('pte-qr-language') as Language;
    if (savedLanguage && translations[savedLanguage]) {
      setLanguageState(savedLanguage);
    }
  }, []);

  // Save language to localStorage when changed
  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('pte-qr-language', lang);
  };

  const t = (key: string, params?: Record<string, any>) => {
    const translation = translations[language]?.[key as keyof typeof translations[typeof language]] || key;
    
    if (params) {
      return Object.keys(params).reduce((str, param) => {
        return str.replace(`{{${param}}}`, params[param]);
      }, translation);
    }
    
    return translation;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

// Hook to use translations
export function useTranslation() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within LanguageProvider');
  }
  return context;
}

// Hook to get current language
export function useLanguage() {
  const { language, setLanguage } = useTranslation();
  return { language, setLanguage };
}