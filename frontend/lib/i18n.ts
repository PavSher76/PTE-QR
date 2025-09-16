/**
 * Internationalization (i18n) utilities
 */

export interface Translation {
  [key: string]: string | Translation;
}

export interface I18nConfig {
  defaultLanguage: string;
  supportedLanguages: string[];
  fallbackLanguage: string;
  namespace: string;
}

export interface I18nInstance {
  language: string;
  t: (key: string, params?: Record<string, any>) => string;
  changeLanguage: (language: string) => void;
  getLanguage: () => string;
  getSupportedLanguages: () => string[];
}

const translations: Record<string, Translation> = {
  ru: {
    app: {
      title: 'PTE-QR Система',
      description: 'Проверка актуальности документов',
      loading: 'Загрузка...',
      error: 'Ошибка',
      success: 'Успешно',
      cancel: 'Отмена',
      confirm: 'Подтвердить',
      save: 'Сохранить',
      delete: 'Удалить',
      edit: 'Редактировать',
      close: 'Закрыть',
      back: 'Назад',
      next: 'Далее',
      previous: 'Предыдущий',
      search: 'Поиск',
      filter: 'Фильтр',
      sort: 'Сортировка',
      refresh: 'Обновить',
    },
    auth: {
      login: 'Войти',
      logout: 'Выйти',
      ssoLogin: 'Войти через SSO',
      unauthorized: 'Необходима авторизация',
      accessDenied: 'Доступ запрещен',
      sessionExpired: 'Сессия истекла',
      loginRequired: 'Требуется вход в систему',
    },
    qr: {
      scan: 'Сканировать QR-код',
      scanPlaceholder: 'Наведите камеру на QR-код',
      invalid: 'Неверный QR-код',
      expired: 'QR-код устарел',
      invalidSignature: 'Неверная подпись QR-кода',
      scanFailed: 'Ошибка при сканировании',
      cameraAccessDenied: 'Доступ к камере запрещен',
      cameraNotAvailable: 'Камера недоступна',
      cameraError: 'Ошибка камеры',
      generate: 'Сгенерировать QR-код',
      download: 'Скачать QR-код',
      copy: 'Копировать ссылку',
      copied: 'Ссылка скопирована',
    },
    document: {
      status: 'Статус документа',
      actual: 'Актуальный',
      outdated: 'Устаревший',
      draft: 'Черновик',
      review: 'На рассмотрении',
      approved: 'Утвержден',
      rejected: 'Отклонен',
      archived: 'Архивный',
      notFound: 'Документ не найден',
      accessDenied: 'Доступ к документу запрещен',
      revision: 'Ревизия',
      page: 'Страница',
      releasedAt: 'Дата выпуска',
      supersededBy: 'Заменен на',
      docUid: 'ID документа',
      businessStatus: 'Бизнес-статус',
      enoviaState: 'Состояние ENOVIA',
    },
    error: {
      network: 'Ошибка сети. Проверьте подключение к интернету.',
      timeout: 'Превышено время ожидания ответа от сервера.',
      connection: 'Ошибка подключения к серверу.',
      api: 'Ошибка API сервера.',
      server: 'Внутренняя ошибка сервера.',
      validation: 'Ошибка валидации данных.',
      unknown: 'Неизвестная ошибка.',
      retry: 'Повторить попытку',
      contactSupport: 'Обратитесь в службу поддержки',
    },
    notification: {
      success: 'Операция выполнена успешно',
      error: 'Произошла ошибка',
      warning: 'Внимание',
      info: 'Информация',
      dismiss: 'Закрыть',
      dismissAll: 'Закрыть все',
    },
    settings: {
      title: 'Настройки',
      theme: 'Тема',
      language: 'Язык',
      notifications: 'Уведомления',
      privacy: 'Конфиденциальность',
      about: 'О программе',
      version: 'Версия',
      build: 'Сборка',
      lastUpdate: 'Последнее обновление',
    },
    admin: {
      title: 'Администрирование',
      statusMapping: 'Сопоставление статусов',
      auditLog: 'Журнал аудита',
      users: 'Пользователи',
      system: 'Система',
      backup: 'Резервное копирование',
      restore: 'Восстановление',
      maintenance: 'Обслуживание',
    },
    common: {
      yes: 'Да',
      no: 'Нет',
      ok: 'ОК',
      apply: 'Применить',
      reset: 'Сбросить',
      clear: 'Очистить',
      select: 'Выбрать',
      selectAll: 'Выбрать все',
      deselectAll: 'Отменить выбор',
      loading: 'Загрузка...',
      noData: 'Нет данных',
      noResults: 'Результаты не найдены',
      tryAgain: 'Попробовать снова',
    },
  },
  en: {
    app: {
      title: 'PTE-QR System',
      description: 'Document actuality verification',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      cancel: 'Cancel',
      confirm: 'Confirm',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',
      close: 'Close',
      back: 'Back',
      next: 'Next',
      previous: 'Previous',
      search: 'Search',
      filter: 'Filter',
      sort: 'Sort',
      refresh: 'Refresh',
    },
    auth: {
      login: 'Login',
      logout: 'Logout',
      ssoLogin: 'Login with SSO',
      unauthorized: 'Authorization required',
      accessDenied: 'Access denied',
      sessionExpired: 'Session expired',
      loginRequired: 'Login required',
    },
    qr: {
      scan: 'Scan QR code',
      scanPlaceholder: 'Point camera at QR code',
      invalid: 'Invalid QR code',
      expired: 'QR code expired',
      invalidSignature: 'Invalid QR code signature',
      scanFailed: 'Scan failed',
      cameraAccessDenied: 'Camera access denied',
      cameraNotAvailable: 'Camera not available',
      cameraError: 'Camera error',
      generate: 'Generate QR code',
      download: 'Download QR code',
      copy: 'Copy link',
      copied: 'Link copied',
    },
    document: {
      status: 'Document status',
      actual: 'Actual',
      outdated: 'Outdated',
      draft: 'Draft',
      review: 'Under review',
      approved: 'Approved',
      rejected: 'Rejected',
      archived: 'Archived',
      notFound: 'Document not found',
      accessDenied: 'Document access denied',
      revision: 'Revision',
      page: 'Page',
      releasedAt: 'Released at',
      supersededBy: 'Superseded by',
      docUid: 'Document ID',
      businessStatus: 'Business status',
      enoviaState: 'ENOVIA state',
    },
    error: {
      network: 'Network error. Check your internet connection.',
      timeout: 'Server response timeout exceeded.',
      connection: 'Server connection error.',
      api: 'API server error.',
      server: 'Internal server error.',
      validation: 'Data validation error.',
      unknown: 'Unknown error.',
      retry: 'Retry',
      contactSupport: 'Contact support',
    },
    notification: {
      success: 'Operation completed successfully',
      error: 'An error occurred',
      warning: 'Warning',
      info: 'Information',
      dismiss: 'Dismiss',
      dismissAll: 'Dismiss all',
    },
    settings: {
      title: 'Settings',
      theme: 'Theme',
      language: 'Language',
      notifications: 'Notifications',
      privacy: 'Privacy',
      about: 'About',
      version: 'Version',
      build: 'Build',
      lastUpdate: 'Last update',
    },
    admin: {
      title: 'Administration',
      statusMapping: 'Status mapping',
      auditLog: 'Audit log',
      users: 'Users',
      system: 'System',
      backup: 'Backup',
      restore: 'Restore',
      maintenance: 'Maintenance',
    },
    common: {
      yes: 'Yes',
      no: 'No',
      ok: 'OK',
      apply: 'Apply',
      reset: 'Reset',
      clear: 'Clear',
      select: 'Select',
      selectAll: 'Select all',
      deselectAll: 'Deselect all',
      loading: 'Loading...',
      noData: 'No data',
      noResults: 'No results found',
      tryAgain: 'Try again',
    },
  },
  zh: {
    app: {
      title: 'PTE-QR 系统',
      description: '文档有效性验证',
      loading: '加载中...',
      error: '错误',
      success: '成功',
      cancel: '取消',
      confirm: '确认',
      save: '保存',
      delete: '删除',
      edit: '编辑',
      close: '关闭',
      back: '返回',
      next: '下一步',
      previous: '上一步',
      search: '搜索',
      filter: '筛选',
      sort: '排序',
      refresh: '刷新',
    },
    auth: {
      login: '登录',
      logout: '退出',
      ssoLogin: '通过 SSO 登录',
      unauthorized: '需要授权',
      accessDenied: '访问被拒绝',
      sessionExpired: '会话已过期',
      loginRequired: '需要登录',
    },
    qr: {
      scan: '扫描二维码',
      scanPlaceholder: '将摄像头对准二维码',
      invalid: '无效的二维码',
      expired: '二维码已过期',
      invalidSignature: '二维码签名无效',
      scanFailed: '扫描失败',
      cameraAccessDenied: '摄像头访问被拒绝',
      cameraNotAvailable: '摄像头不可用',
      cameraError: '摄像头错误',
      generate: '生成二维码',
      download: '下载二维码',
      copy: '复制链接',
      copied: '链接已复制',
    },
    document: {
      status: '文档状态',
      actual: '有效',
      outdated: '已过期',
      draft: '草稿',
      review: '审核中',
      approved: '已批准',
      rejected: '已拒绝',
      archived: '已归档',
      notFound: '文档未找到',
      accessDenied: '文档访问被拒绝',
      revision: '版本',
      page: '页面',
      releasedAt: '发布日期',
      supersededBy: '被替换为',
      docUid: '文档ID',
      businessStatus: '业务状态',
      enoviaState: 'ENOVIA 状态',
    },
    error: {
      network: '网络错误。请检查您的网络连接。',
      timeout: '服务器响应超时。',
      connection: '服务器连接错误。',
      api: 'API 服务器错误。',
      server: '内部服务器错误。',
      validation: '数据验证错误。',
      unknown: '未知错误。',
      retry: '重试',
      contactSupport: '联系技术支持',
    },
    notification: {
      success: '操作成功完成',
      error: '发生错误',
      warning: '警告',
      info: '信息',
      dismiss: '关闭',
      dismissAll: '关闭全部',
    },
    settings: {
      title: '设置',
      theme: '主题',
      language: '语言',
      notifications: '通知',
      privacy: '隐私',
      about: '关于',
      version: '版本',
      build: '构建',
      lastUpdate: '最后更新',
    },
    admin: {
      title: '管理',
      statusMapping: '状态映射',
      auditLog: '审计日志',
      users: '用户',
      system: '系统',
      backup: '备份',
      restore: '恢复',
      maintenance: '维护',
    },
    common: {
      yes: '是',
      no: '否',
      ok: '确定',
      apply: '应用',
      reset: '重置',
      clear: '清除',
      select: '选择',
      selectAll: '全选',
      deselectAll: '取消全选',
      loading: '加载中...',
      noData: '无数据',
      noResults: '未找到结果',
      tryAgain: '重试',
    },
  },
};

const defaultConfig: I18nConfig = {
  defaultLanguage: 'ru',
  supportedLanguages: ['ru', 'en', 'zh'],
  fallbackLanguage: 'ru',
  namespace: 'translation',
};

export class I18n implements I18nInstance {
  private config: I18nConfig;
  private currentLanguage: string;
  private listeners: Array<(language: string) => void> = [];

  constructor(config: Partial<I18nConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
    this.currentLanguage = this.config.defaultLanguage;
  }

  t(key: string, params?: Record<string, any>): string {
    const translation = this.getTranslation(key);
    
    if (params) {
      return this.interpolate(translation, params);
    }
    
    return translation;
  }

  changeLanguage(language: string): void {
    if (this.config.supportedLanguages.includes(language)) {
      this.currentLanguage = language;
      this.notifyListeners();
    }
  }

  getLanguage(): string {
    return this.currentLanguage;
  }

  getSupportedLanguages(): string[] {
    return [...this.config.supportedLanguages];
  }

  addLanguageChangeListener(listener: (language: string) => void): () => void {
    this.listeners.push(listener);
    
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  private getTranslation(key: string): string {
    const keys = key.split('.');
    let translation: any = translations[this.currentLanguage];
    
    for (const k of keys) {
      if (translation && typeof translation === 'object' && k in translation) {
        translation = translation[k];
      } else {
        // Fallback to default language
        translation = translations[this.config.fallbackLanguage];
        for (const fallbackKey of keys) {
          if (translation && typeof translation === 'object' && fallbackKey in translation) {
            translation = translation[fallbackKey];
          } else {
            return key; // Return key if translation not found
          }
        }
        break;
      }
    }
    
    return typeof translation === 'string' ? translation : key;
  }

  private interpolate(text: string, params: Record<string, any>): string {
    return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return params[key] !== undefined ? String(params[key]) : match;
    });
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.currentLanguage));
  }
}

export const i18n = new I18n();

export function useTranslation(): { t: (key: string, params?: Record<string, any>) => string; language: string } {
  const [language, setLanguage] = React.useState(i18n.getLanguage());
  
  React.useEffect(() => {
    const unsubscribe = i18n.addLanguageChangeListener(setLanguage);
    return unsubscribe;
  }, []);
  
  return {
    t: i18n.t.bind(i18n),
    language,
  };
}

export function detectLanguage(): string {
  if (typeof window === 'undefined') {
    return 'ru';
  }
  
  // Check localStorage
  const savedLanguage = localStorage.getItem('pte-qr-language');
  if (savedLanguage && i18n.getSupportedLanguages().includes(savedLanguage)) {
    return savedLanguage;
  }
  
  // Check browser language
  const browserLanguage = navigator.language.split('-')[0];
  if (i18n.getSupportedLanguages().includes(browserLanguage)) {
    return browserLanguage;
  }
  
  // Check for Chinese variants
  const fullLanguage = navigator.language.toLowerCase();
  if (fullLanguage.startsWith('zh')) {
    return 'zh';
  }
  
  // Return default
  return i18n.getLanguage();
}

export function saveLanguage(language: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('pte-qr-language', language);
  }
}

export function loadLanguage(): string {
  const detectedLanguage = detectLanguage();
  i18n.changeLanguage(detectedLanguage);
  return detectedLanguage;
}