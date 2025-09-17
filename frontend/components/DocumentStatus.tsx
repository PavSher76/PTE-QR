/**
 * Document Status component
 */

'use client'

import React from 'react'
import { DocumentStatusData } from '@/types/document'
import { useTranslation } from '@/lib/i18n'

interface DocumentStatusProps {
  data?: DocumentStatusData
  qrData?: string
}

function DocumentStatus({ data, qrData }: DocumentStatusProps) {
  const { t } = useTranslation()

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
        openLatest: '#',
      },
    }
  }

  if (!data) {
    return (
      <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
        <p className="text-gray-500">{t('document.noData')}</p>
      </div>
    )
  }
  return (
    <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
      <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
        {t('document.status')}
      </h2>

      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {t('document.document')}
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {data.doc_uid}
          </p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {t('document.revision')}
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {data.revision}
          </p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {t('document.page')}
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {data.page}
          </p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {t('document.status')}
          </label>
          <p
            className={`text-lg font-semibold ${
              data.is_actual
                ? 'text-green-600 dark:text-green-400'
                : 'text-red-600 dark:text-red-400'
            }`}
          >
            {data.is_actual ? t('status.actual') : t('status.outdated')}
          </p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {t('document.enoviaState')}
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {data.enovia_state}
          </p>
        </div>

        {data.released_at && (
          <div>
            <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('document.releasedAt')}
            </label>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">
              {new Date(data.released_at).toLocaleDateString('ru-RU')}
            </p>
          </div>
        )}

        {data.links && (
          <div className="mt-6 flex space-x-4">
            {data.links.openDocument && (
              <a
                href={data.links.openDocument}
                className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                {t('document.openDocument')}
              </a>
            )}
            {data.links.openLatest && (
              <a
                href={data.links.openLatest}
                className="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                {t('document.openLatest')}
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export { DocumentStatus }
export default DocumentStatus
