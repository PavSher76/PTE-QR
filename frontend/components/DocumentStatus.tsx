/**
 * Document Status component
 */

'use client';

import React from 'react';
import { DocumentStatusData } from '@/types/document';

interface DocumentStatusProps {
  data?: DocumentStatusData;
  qrData?: string;
}

function DocumentStatus({ data, qrData }: DocumentStatusProps) {
  // If we have qrData, create mock data
  if (qrData && !data) {
    data = {
      doc_uid: 'Sample-Document',
      revision: 'A',
      page: 1,
      business_status: 'APPROVED_FOR_CONSTRUCTION',
      enovia_state: 'Released',
      is_actual: true,
      released_at: new Date().toISOString(),
      links: {
        openDocument: '#',
        openLatest: '#'
      }
    };
  }

  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <p className="text-gray-500">Нет данных для отображения</p>
      </div>
    );
  }
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Статус документа
      </h2>
      
      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Документ
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {data.doc_uid}
          </p>
        </div>
        
        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Ревизия
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {data.revision}
          </p>
        </div>
        
        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Страница
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {data.page}
          </p>
        </div>
        
        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Статус
          </label>
          <p className={`text-lg font-semibold ${
            data.is_actual 
              ? 'text-green-600 dark:text-green-400' 
              : 'text-red-600 dark:text-red-400'
          }`}>
            {data.is_actual ? 'АКТУАЛЬНЫЙ' : 'УСТАРЕЛ'}
          </p>
        </div>
        
        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Состояние в ENOVIA
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {data.enovia_state}
          </p>
        </div>
        
        {data.released_at && (
          <div>
            <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
              Дата выпуска
            </label>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">
              {new Date(data.released_at).toLocaleDateString('ru-RU')}
            </p>
          </div>
        )}
        
        {data.links && (
          <div className="flex space-x-4 mt-6">
            {data.links.openDocument && (
              <a
                href={data.links.openDocument}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Открыть документ
              </a>
            )}
            {data.links.openLatest && (
              <a
                href={data.links.openLatest}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Открыть последнюю версию
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export { DocumentStatus };
export default DocumentStatus;