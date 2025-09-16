'use client';

import { useParams, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { DocumentStatus } from '@/components/DocumentStatus';
import { useTranslation } from '@/lib/i18n';
import { useNotifications } from '@/lib/context';
import { validateQRCodeParams } from '@/lib/validation';
import { verifyHMACSignature } from '@/lib/hmac';
import { fetchDocumentStatus } from '@/lib/api';
import { DocumentStatus as DocumentStatusType } from '@/types/document';

export default function QRResolvePage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const { t } = useTranslation();
  const { addNotification } = useNotifications();
  
  const [documentStatus, setDocumentStatus] = useState<DocumentStatusType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const docUid = params.docUid as string;
  const revision = params.revision as string;
  const page = parseInt(params.page as string, 10);
  const signature = searchParams.get('t');
  const timestamp = searchParams.get('ts');

  useEffect(() => {
    const resolveQRCode = async () => {
      try {
        setLoading(true);
        setError(null);

        // Validate QR code parameters
        const qrParams = {
          docUid,
          revision,
          page: page.toString(),
          timestamp: timestamp || '',
          signature: signature || '',
        };

        const validation = validateQRCodeParams(qrParams);
        if (!validation.isValid) {
          throw new Error(validation.errors.join(', '));
        }

        // Verify HMAC signature
        const isValidSignature = verifyHMACSignature(
          docUid,
          revision,
          page,
          parseInt(timestamp || '0', 10),
          signature || ''
        );

        if (!isValidSignature) {
          throw new Error(t('qr.invalidSignature'));
        }

        // Check if QR code is expired
        const now = Math.floor(Date.now() / 1000);
        const qrTimestamp = parseInt(timestamp || '0', 10);
        if (now - qrTimestamp > 3600) { // 1 hour tolerance
          throw new Error(t('qr.expired'));
        }

        // Fetch document status
        const status = await fetchDocumentStatus(docUid, revision, page);
        setDocumentStatus(status);

        addNotification({
          type: 'success',
          title: t('document.status'),
          message: t('document.actual'),
        });

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : t('error.unknown');
        setError(errorMessage);
        
        addNotification({
          type: 'error',
          title: t('error.error'),
          message: errorMessage,
        });
      } finally {
        setLoading(false);
      }
    };

    if (docUid && revision && page && signature && timestamp) {
      resolveQRCode();
    } else {
      setError(t('qr.invalid'));
      setLoading(false);
    }
  }, [docUid, revision, page, signature, timestamp, t, addNotification]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">{t('app.loading')}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="max-w-md mx-auto text-center">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <div className="w-12 h-12 bg-red-100 dark:bg-red-900/40 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
              {t('error.error')}
            </h2>
            <p className="text-red-600 dark:text-red-300 mb-4">
              {error}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              {t('common.tryAgain')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/40 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {t('document.status')}
              </h1>
              <p className="text-gray-600 dark:text-gray-300">
                {t('document.docUid')}: {docUid}
              </p>
            </div>

            {documentStatus && (
              <DocumentStatus data={documentStatus} />
            )}

            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500 dark:text-gray-400">{t('document.revision')}:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-white">{revision}</span>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">{t('document.page')}:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-white">{page}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
