'use client';

import { useState } from 'react';
import { QRCodeScanner } from '@/components/QRCodeScanner';
import { DocumentStatus } from '@/components/DocumentStatus';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { useTranslation } from '@/lib/i18n';
import { useNotifications } from '@/lib/context';

export default function HomePage() {
  const { t } = useTranslation();
  const { addNotification } = useNotifications();
  const [scannedData, setScannedData] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);

  const handleScan = (data: string) => {
    setScannedData(data);
    setIsScanning(false);
    addNotification({
      type: 'success',
      title: t('qr.scan'),
      message: t('document.status') + ': ' + data,
    });
  };

  const handleScanError = (error: string) => {
    addNotification({
      type: 'error',
      title: t('qr.scanFailed'),
      message: error,
    });
  };

  const handleReset = () => {
    setScannedData(null);
    setIsScanning(false);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {t('app.title')}
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
              {t('app.description')}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* QR Scanner Section */}
            <div className="card p-6">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                {t('qr.scan')}
              </h2>
              
              {!isScanning && !scannedData && (
                <div className="text-center">
                  <div className="mb-4">
                    <svg className="mx-auto h-24 w-24 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                    </svg>
                  </div>
                  <p className="text-gray-600 mb-4">
                    Наведите камеру на QR-код документа для проверки его актуальности
                  </p>
                  <button
                    onClick={() => setIsScanning(true)}
                    className="btn-primary"
                  >
                    Начать сканирование
                  </button>
                </div>
              )}

              {isScanning && (
                <QRCodeScanner
                  onScan={handleScan}
                  onCancel={() => setIsScanning(false)}
                />
              )}

              {scannedData && (
                <div className="text-center">
                  <div className="mb-4">
                    <svg className="mx-auto h-12 w-12 text-success-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <p className="text-gray-600 mb-4">
                    QR-код успешно отсканирован
                  </p>
                  <div className="bg-gray-100 p-3 rounded-md mb-4">
                    <code className="text-sm text-gray-800 break-all">
                      {scannedData}
                    </code>
                  </div>
                  <button
                    onClick={handleReset}
                    className="btn-secondary mr-2"
                  >
                    Сканировать еще
                  </button>
                </div>
              )}
            </div>

            {/* Document Status Section */}
            <div className="card p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Статус документа
              </h2>
              
              {scannedData ? (
                <DocumentStatus qrData={scannedData} />
              ) : (
                <div className="text-center text-gray-500">
                  <p>Отсканируйте QR-код для проверки статуса документа</p>
                </div>
              )}
            </div>
          </div>

          {/* Features Section */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card p-6 text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Проверка актуальности
              </h3>
              <p className="text-gray-600">
                Мгновенная проверка актуальности документа и его ревизии
              </p>
            </div>

            <div className="card p-6 text-center">
              <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-success-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Мобильная версия
              </h3>
              <p className="text-gray-600">
                Оптимизировано для использования на мобильных устройствах
              </p>
            </div>

            <div className="card p-6 text-center">
              <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-warning-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Безопасность
              </h3>
              <p className="text-gray-600">
                HMAC подпись обеспечивает защиту от подделки QR-кодов
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
