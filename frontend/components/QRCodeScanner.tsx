'use client'

import { useEffect, useRef, useState } from 'react'
import { useTranslation } from '@/lib/i18n'

interface QRCodeScannerProps {
  onScan: (data: string) => void
  onCancel: () => void
}

export function QRCodeScanner({ onScan, onCancel }: QRCodeScannerProps) {
  const { t } = useTranslation()
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [isScanning, setIsScanning] = useState(false)

  useEffect(() => {
    startCamera()
    return () => {
      stopCamera()
    }
  }, [])

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
        setIsScanning(true)
      }
    } catch (err) {
      setError(t('error.cameraAccess'))
      console.error('Camera error:', err)
    }
  }

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      stream.getTracks().forEach((track) => track.stop())
    }
    setIsScanning(false)
  }

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const context = canvas.getContext('2d')

    if (!context) return

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    context.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Here you would typically use a QR code library like jsQR
    // For now, we'll simulate a successful scan
    setTimeout(() => {
      onScan('https://qr.pti.ru/r/3D-00001234/B/3?ts=1703123456&t=abc123def456')
    }, 2000)
  }

  const handleCancel = () => {
    stopCamera()
    onCancel()
  }

  if (error) {
    return (
      <div className="text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-danger-100">
          <svg
            className="h-8 w-8 text-danger-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        </div>
        <p className="mb-4 text-danger-600">{error}</p>
        <button onClick={handleCancel} className="btn-secondary">
          {t('scan.close')}
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <video
          ref={videoRef}
          className="h-64 w-full rounded-lg bg-gray-100 object-cover"
          playsInline
          muted
        />
        <canvas ref={canvasRef} className="hidden" />

        {/* QR Code overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-48 w-48 rounded-lg border-2 border-primary-500 bg-transparent">
            <div className="absolute left-0 top-0 h-6 w-6 rounded-tl-lg border-l-2 border-t-2 border-primary-500"></div>
            <div className="absolute right-0 top-0 h-6 w-6 rounded-tr-lg border-r-2 border-t-2 border-primary-500"></div>
            <div className="absolute bottom-0 left-0 h-6 w-6 rounded-bl-lg border-b-2 border-l-2 border-primary-500"></div>
            <div className="absolute bottom-0 right-0 h-6 w-6 rounded-br-lg border-b-2 border-r-2 border-primary-500"></div>
          </div>
        </div>
      </div>

      <div className="text-center">
        <p className="mb-4 text-gray-600">{t('scan.cameraInstruction')}</p>

        {isScanning && (
          <div className="mb-4 flex items-center justify-center space-x-2">
            <div className="h-2 w-2 animate-pulse rounded-full bg-primary-500"></div>
            <div
              className="h-2 w-2 animate-pulse rounded-full bg-primary-500"
              style={{ animationDelay: '0.2s' }}
            ></div>
            <div
              className="h-2 w-2 animate-pulse rounded-full bg-primary-500"
              style={{ animationDelay: '0.4s' }}
            ></div>
          </div>
        )}

        <div className="flex space-x-2">
          <button
            onClick={captureFrame}
            className="btn-primary flex-1"
            disabled={!isScanning}
          >
            {t('scan.scan')}
          </button>
          <button onClick={handleCancel} className="btn-secondary flex-1">
            {t('scan.cancel')}
          </button>
        </div>
      </div>
    </div>
  )
}
