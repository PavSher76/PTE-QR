/**
 * Application constants
 */

export const APP_CONFIG = {
  name: 'PTE-QR System',
  version: '1.0.0',
  description: 'Document actuality verification system',
  author: 'PTI Team',
  repository: 'https://github.com/company/pte-qr',
  support: 'support@pti.ru',
} as const;

export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  version: 'v1',
  timeout: 30000,
  retries: 3,
  endpoints: {
    health: '/health',
    documents: '/documents',
    qrcodes: '/qrcodes',
    qrVerify: '/qr/verify',
    admin: '/admin',
    auth: '/auth',
  },
} as const;

export const QR_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_QR_BASE_URL || 'https://qr.pti.ru',
  signatureAlgorithm: 'sha256',
  signatureLength: 64,
  timestampTolerance: 3600, // 1 hour in seconds
  minSize: 100,
  maxSize: 1000,
  defaultSize: 200,
  errorCorrectionLevel: 'M' as const,
  quietZone: 4,
} as const;

export const ENOVIA_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_ENOVIA_URL || 'https://enovia.pti.ru',
  timeout: 10000,
  retries: 2,
  endpoints: {
    documentMeta: '/api/documents',
    revisionMeta: '/api/revisions',
    latestReleased: '/api/latest-released',
  },
  oauth: {
    clientId: process.env.NEXT_PUBLIC_ENOVIA_CLIENT_ID || '',
    redirectUri: process.env.NEXT_PUBLIC_ENOVIA_REDIRECT_URI || '',
    scope: 'read:documents read:revisions',
  },
} as const;

export const CACHE_CONFIG = {
  ttl: {
    documentStatus: 300, // 5 minutes
    qrCode: 3600, // 1 hour
    userProfile: 1800, // 30 minutes
    statusMapping: 86400, // 24 hours
  },
  keys: {
    documentStatus: (docUid: string, revision: string, page: number) => 
      `doc:${docUid}:${revision}:${page}`,
    qrCode: (docUid: string, revision: string, page: number) => 
      `qr:${docUid}:${revision}:${page}`,
    userProfile: (userId: string) => `user:${userId}`,
    statusMapping: 'status:mapping',
  },
} as const;

export const SECURITY_CONFIG = {
  jwt: {
    secret: process.env.JWT_SECRET || 'your-secret-key',
    expiresIn: '24h',
    issuer: 'pte-qr-system',
    audience: 'pte-qr-users',
  },
  hmac: {
    secret: process.env.HMAC_SECRET || 'your-hmac-secret',
    algorithm: 'sha256',
  },
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    skipSuccessfulRequests: true,
  },
  cors: {
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
    credentials: true,
  },
} as const;

export const UI_CONFIG = {
  theme: {
    default: 'light' as const,
    storageKey: 'pte-qr-theme',
  },
  language: {
    default: 'ru' as const,
    supported: ['ru', 'en', 'zh'] as const,
    storageKey: 'pte-qr-language',
  },
  breakpoints: {
    mobile: 768,
    tablet: 1024,
    desktop: 1200,
  },
  animations: {
    duration: {
      fast: 150,
      normal: 300,
      slow: 500,
    },
    easing: {
      ease: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
  },
} as const;

export const VALIDATION_CONFIG = {
  patterns: {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    phone: /^\+?[1-9]\d{1,14}$/,
    url: /^https?:\/\/.+/,
    docUid: /^[A-Za-z0-9_-]+$/,
    revision: /^[A-Za-z0-9._-]+$/,
    page: /^\d+$/,
    timestamp: /^\d{10}$/,
    signature: /^[A-Fa-f0-9]+$/,
  },
  limits: {
    docUid: { min: 1, max: 100 },
    revision: { min: 1, max: 50 },
    page: { min: 1, max: 10000 },
    signature: { length: 64 },
    timestamp: { tolerance: 3600 },
  },
} as const;

export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  CONNECTION_ERROR: 'CONNECTION_ERROR',
  API_ERROR: 'API_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  QR_INVALID_FORMAT: 'QR_INVALID_FORMAT',
  QR_INVALID_SIGNATURE: 'QR_INVALID_SIGNATURE',
  QR_EXPIRED: 'QR_EXPIRED',
  QR_SCAN_FAILED: 'QR_SCAN_FAILED',
  DOCUMENT_NOT_FOUND: 'DOCUMENT_NOT_FOUND',
  REVISION_NOT_FOUND: 'REVISION_NOT_FOUND',
  DOCUMENT_ACCESS_DENIED: 'DOCUMENT_ACCESS_DENIED',
  CAMERA_ACCESS_DENIED: 'CAMERA_ACCESS_DENIED',
  CAMERA_NOT_AVAILABLE: 'CAMERA_NOT_AVAILABLE',
  CAMERA_ERROR: 'CAMERA_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
  VALIDATION_FAILED: 'VALIDATION_FAILED',
  OPERATION_FAILED: 'OPERATION_FAILED',
} as const;

export const BUSINESS_STATUSES = {
  ACTUAL: 'Актуальный',
  OUTDATED: 'Устаревший',
  DRAFT: 'Черновик',
  REVIEW: 'На рассмотрении',
  APPROVED: 'Утвержден',
  REJECTED: 'Отклонен',
  ARCHIVED: 'Архивный',
} as const;

export const ENOVIA_STATES = {
  DRAFT: 'Draft',
  IN_WORK: 'In Work',
  IN_REVIEW: 'In Review',
  APPROVED: 'Approved',
  RELEASED: 'Released',
  OBSOLETE: 'Obsolete',
  ARCHIVED: 'Archived',
} as const;

export const USER_ROLES = {
  GUEST: 'guest',
  EMPLOYEE: 'employee',
  ADMIN: 'admin',
} as const;

export const PERMISSIONS = {
  [USER_ROLES.GUEST]: [
    'read:document:status',
    'scan:qr:code',
  ],
  [USER_ROLES.EMPLOYEE]: [
    'read:document:status',
    'scan:qr:code',
    'generate:qr:code',
    'read:document:meta',
  ],
  [USER_ROLES.ADMIN]: [
    'read:document:status',
    'scan:qr:code',
    'generate:qr:code',
    'read:document:meta',
    'write:status:mapping',
    'read:audit:log',
    'manage:users',
  ],
} as const;

export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
} as const;

export const NOTIFICATION_DURATIONS = {
  SHORT: 3000,
  NORMAL: 5000,
  LONG: 10000,
  PERSISTENT: 0,
} as const;

export const FILE_TYPES = {
  PDF: 'application/pdf',
  PNG: 'image/png',
  JPEG: 'image/jpeg',
  SVG: 'image/svg+xml',
} as const;

export const MIME_TYPES = {
  PDF: 'application/pdf',
  PNG: 'image/png',
  JPEG: 'image/jpeg',
  SVG: 'image/svg+xml',
  JSON: 'application/json',
  TEXT: 'text/plain',
  HTML: 'text/html',
} as const;

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

export const STORAGE_KEYS = {
  THEME: 'pte-qr-theme',
  LANGUAGE: 'pte-qr-language',
  USER: 'pte-qr-user',
  TOKEN: 'pte-qr-token',
  SETTINGS: 'pte-qr-settings',
  CACHE: 'pte-qr-cache',
} as const;