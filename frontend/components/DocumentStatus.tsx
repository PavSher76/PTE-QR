/**
 * Document Status component
 */

'use client'

import React, { useState, useEffect } from 'react'
import { DocumentStatusData } from '@/types/document'
import { useTranslation } from '@/lib/i18n'
import { fetchDocumentStatus } from '@/lib/api'
import { useNotifications } from '@/lib/context'

interface DocumentStatusProps {
  data?: DocumentStatusData
  qrData?: string
}

function DocumentStatus({ data, qrData }: DocumentStatusProps) {
  const { t } = useTranslation()
  const { addNotification } = useNotifications()
  const [documentData, setDocumentData] = useState<DocumentStatusData | null>(data || null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (qrData && !data) {
      // Parse QR data to extract document information
      // QR data format: doc_uid:revision:page:timestamp:signature
      const parts = qrData.split(':')
      if (parts.length >= 3) {
        const docUid = parts[0]
        const revision = parts[1]
        const page = parts[2]
        
        setIsLoading(true)
        fetchDocumentStatus(docUid, revision, page)
          .then((result) => {
            setDocumentData(result)
          })
          .catch((error) => {
            addNotification({
              type: 'error',
              title: t('error'),
              message: error.message || t('error.serverError'),
            })
          })
          .finally(() => {
            setIsLoading(false)
          })
      }
    }
  }, [qrData, data, addNotification, t])

  if (isLoading) {
    return (
      <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-2 text-gray-600 dark:text-gray-300">{t('loading')}</span>
        </div>
      </div>
    )
  }

  if (!documentData) {
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
            {documentData.doc_uid}
          </p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {t('document.revision')}
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {documentData.revision}
          </p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {t('document.page')}
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {documentData.page}
          </p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {t('document.status')}
          </label>
          <p
            className={`text-lg font-semibold ${
              documentData.is_actual
                ? 'text-green-600 dark:text-green-400'
                : 'text-red-600 dark:text-red-400'
            }`}
          >
            {documentData.is_actual ? t('status.actual') : t('status.outdated')}
          </p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {t('document.enoviaState')}
          </label>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {documentData.enovia_state}
          </p>
        </div>

        {documentData.released_at && (
          <div>
            <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('document.releasedAt')}
            </label>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">
              {new Date(documentData.released_at).toLocaleDateString('ru-RU')}
            </p>
          </div>
        )}

        {documentData.links && (
          <div className="mt-6 flex space-x-4">
            {documentData.links.openDocument && (
              <a
                href={documentData.links.openDocument}
                className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                {t('document.openDocument')}
              </a>
            )}
            {documentData.links.openLatest && (
              <a
                href={documentData.links.openLatest}
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
