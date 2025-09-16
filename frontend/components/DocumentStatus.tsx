'use client';

import { useState, useEffect } from 'react';
import { DocumentStatusData } from '@/types/document';
import { useTranslation } from '@/lib/i18n';
import { useNotifications } from '@/lib/context';

interface DocumentStatusProps {
  qrData: string;
}

export function DocumentStatus({ qrData }: DocumentStatusProps) {
  const [status, setStatus] = useState<DocumentStatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (qrData) {
      checkDocumentStatus(qrData);
    }
  }, [qrData]);

  const checkDocumentStatus = async (qrUrl: string) => {
    try {
      setLoading(true);
      setError(null);

      // Parse QR URL to extract parameters
      const url = new URL(qrUrl);
      const pathParts = url.pathname.split('/');
      const docUid = pathParts[2];
      const revision = pathParts[3];
      const page = parseInt(pathParts[4]);

      // Call API to get document status
      const response = await fetch(`/api/v1/documents/${docUid}/revisions/${revision}/status?page=${page}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Документ или ревизия не найдены');
        } else if (response.status === 410) {
          // Document is outdated, but we still want to show the status
          const data = await response.json();
          setStatus(data);
          return;
        } else {
          throw new Error('Ошибка при получении статуса документа');
        }
      }

      const data = await response.json();
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    } finally {
      setLoading(false);
    }
  };

  const getStatusConfig = (businessStatus: string) => {
    const configs = {
      'APPROVED_FOR_CONSTRUCTION': {
        text: 'Утверждена в производство работ',
        color: 'success',
        icon: '✅',
        bgColor: 'bg-success-50',
        borderColor: 'border-success-200',
        textColor: 'text-success-800'
      },
      'ACCEPTED_BY_CUSTOMER': {
        text: 'Принята Заказчиком',
        color: 'primary',
        icon: '✅',
        bgColor: 'bg-primary-50',
        borderColor: 'border-primary-200',
        textColor: 'text-primary-800'
      },
      'CHANGES_INTRODUCED_GET_NEW': {
        text: 'Внесены изменения — получите новый документ',
        color: 'danger',
        icon: '⚠️',
        bgColor: 'bg-danger-50',
        borderColor: 'border-danger-200',
        textColor: 'text-danger-800'
      },
      'IN_WORK': {
        text: 'На доработке',
        color: 'gray',
        icon: '🔄',
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
        textColor: 'text-gray-800'
      }
    };

    return configs[businessStatus as keyof typeof configs] || configs['IN_WORK'];
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Проверка статуса документа...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="w-16 h-16 bg-danger-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-danger-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Ошибка</h3>
        <p className="text-danger-600 mb-4">{error}</p>
        <button
          onClick={() => checkDocumentStatus(qrData)}
          className="btn-primary"
        >
          Попробовать снова
        </button>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Статус документа не найден</p>
      </div>
    );
  }

  const statusConfig = getStatusConfig(status.business_status);

  return (
    <div className="space-y-6">
      {/* Status Header */}
      <div className={`p-6 rounded-lg border-2 ${statusConfig.bgColor} ${statusConfig.borderColor}`}>
        <div className="text-center">
          <div className="text-4xl mb-4">{statusConfig.icon}</div>
          <h3 className={`text-xl font-semibold ${statusConfig.textColor} mb-2`}>
            {statusConfig.text}
          </h3>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusConfig.bgColor} ${statusConfig.textColor}`}>
            {status.is_actual ? 'Актуален' : 'Устарел'}
          </div>
        </div>
      </div>

      {/* Document Information */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-900">Информация о документе</h4>
        
        <div className="grid grid-cols-1 gap-4">
          <div className="flex justify-between items-center py-2 border-b border-gray-200">
            <span className="text-gray-600">Документ:</span>
            <span className="font-medium text-gray-900">{status.doc_uid}</span>
          </div>
          
          <div className="flex justify-between items-center py-2 border-b border-gray-200">
            <span className="text-gray-600">Ревизия:</span>
            <span className="font-medium text-gray-900">{status.revision}</span>
          </div>
          
          <div className="flex justify-between items-center py-2 border-b border-gray-200">
            <span className="text-gray-600">Страница:</span>
            <span className="font-medium text-gray-900">{status.page}</span>
          </div>
          
          <div className="flex justify-between items-center py-2 border-b border-gray-200">
            <span className="text-gray-600">Статус ENOVIA:</span>
            <span className="font-medium text-gray-900">{status.enovia_state}</span>
          </div>
          
          {status.released_at && (
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-gray-600">Дата выпуска:</span>
              <span className="font-medium text-gray-900">
                {new Date(status.released_at).toLocaleDateString('ru-RU')}
              </span>
            </div>
          )}
          
          {status.superseded_by && (
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-gray-600">Заменена на:</span>
              <span className="font-medium text-gray-900">{status.superseded_by}</span>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3">
        {status.links.openDocument && (
          <a
            href={status.links.openDocument}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary w-full text-center"
          >
            Открыть документ
          </a>
        )}
        
        {status.links.openLatest && (
          <a
            href={status.links.openLatest}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-danger w-full text-center"
          >
            Перейти к актуальной ревизии
          </a>
        )}
        
        {!status.is_actual && !status.links.openLatest && (
          <div className="text-center text-gray-500 text-sm">
            Для доступа к актуальной ревизии требуется авторизация
          </div>
        )}
      </div>
    </div>
  );
}
