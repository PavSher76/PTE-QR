/**
 * Internationalization utilities
 */

'use client';

// Simple translations
const translations = {
  ru: {
    'header.title': 'PTE QR System',
    'header.scan': 'Сканировать QR',
    'header.admin': 'Администрирование',
    'header.logout': 'Выйти',
    'header.login': 'Войти',
    'status.actual': 'АКТУАЛЬНЫЙ',
    'status.outdated': 'УСТАРЕЛ',
    'scan.title': 'Сканирование QR-кода',
    'scan.instruction': 'Отсканируйте QR-код для проверки статуса документа'
  },
  en: {
    'header.title': 'PTE QR System',
    'header.scan': 'Scan QR',
    'header.admin': 'Administration',
    'header.logout': 'Logout',
    'header.login': 'Login',
    'status.actual': 'ACTUAL',
    'status.outdated': 'OUTDATED',
    'scan.title': 'QR Code Scanning',
    'scan.instruction': 'Scan QR code to check document status'
  },
  zh: {
    'header.title': 'PTE QR 系统',
    'header.scan': '扫描二维码',
    'header.admin': '管理',
    'header.logout': '退出',
    'header.login': '登录',
    'status.actual': '当前',
    'status.outdated': '过时',
    'scan.title': '二维码扫描',
    'scan.instruction': '扫描二维码检查文档状态'
  }
};

export function useTranslation() {
  const language = 'ru'; // Default language
  
  const t = (key: string, params?: Record<string, any>) => {
    const lang = language as keyof typeof translations;
    const translation = translations[lang]?.[key as keyof typeof translations[typeof lang]] || key;
    
    if (params) {
      return Object.keys(params).reduce((str, param) => {
        return str.replace(`{{${param}}}`, params[param]);
      }, translation);
    }
    
    return translation;
  };
  
  const setLanguage = (lang: string) => {
    // Placeholder - in real implementation would update state
    console.log('Setting language to:', lang);
  };
  
  return {
    t,
    language,
    setLanguage
  };
}