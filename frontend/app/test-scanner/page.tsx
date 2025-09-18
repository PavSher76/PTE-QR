'use client'

import { useState } from 'react'
import { QRCodeScanner } from '@/components/QRCodeScanner'

export default function TestScannerPage() {
  const [scannedData, setScannedData] = useState<string | null>(null)
  const [showScanner, setShowScanner] = useState(false)

  const handleScan = (data: string) => {
    setScannedData(data)
    setShowScanner(false)
  }

  const handleCancel = () => {
    setShowScanner(false)
  }

  const startScanning = () => {
    setScannedData(null)
    setShowScanner(true)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-2xl px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Тест QR-сканера с звуковыми и визуальными эффектами
          </h1>
          <p className="text-gray-600">
            Нажмите кнопку ниже, чтобы протестировать новый функционал сканирования
          </p>
        </div>

        <div className="card p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Новые возможности:</h2>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Визуальная обратная связь при успешном сканировании
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Визуальная анимация успеха (зеленая рамка + галочка)
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Счетчик попыток сканирования
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Индикатор процесса сканирования
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Визуальная обратная связь при ошибке доступа к камере
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Счетчик попыток сканирования для обратной связи
            </li>
          </ul>
        </div>

        {!showScanner && (
          <div className="text-center">
            <button
              onClick={startScanning}
              className="btn-primary px-8 py-3 text-lg"
            >
              🎯 Начать сканирование QR-кода
            </button>
          </div>
        )}

        {showScanner && (
          <div className="card p-6">
            <QRCodeScanner onScan={handleScan} onCancel={handleCancel} />
          </div>
        )}

        {scannedData && (
          <div className="card p-6 mt-6">
            <h3 className="text-lg font-semibold text-green-600 mb-4">
              🎉 QR-код успешно отсканирован!
            </h3>
            <div className="bg-gray-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Содержимое QR-кода:</p>
              <code className="text-sm font-mono break-all">{scannedData}</code>
            </div>
            <button
              onClick={startScanning}
              className="btn-primary mt-4"
            >
              Сканировать еще один QR-код
            </button>
          </div>
        )}

        <div className="card p-6 mt-6">
          <h3 className="text-lg font-semibold mb-4">Инструкции для тестирования:</h3>
          <ol className="space-y-2 text-gray-700 list-decimal list-inside">
            <li>Нажмите кнопку "Начать сканирование"</li>
            <li>Разрешите доступ к камере (если потребуется)</li>
            <li>Наведите камеру на QR-код</li>
            <li>Обратите внимание на звуковые и визуальные эффекты</li>
            <li>При успешном сканировании услышите приятный звук и увидите зеленую анимацию</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
