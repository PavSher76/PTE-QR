'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { useTranslation } from '@/lib/i18n'
import jsQR from 'jsqr'

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
  const [scanSuccess, setScanSuccess] = useState(false)
  const [scanAttempts, setScanAttempts] = useState(0)
  const [isCapturing, setIsCapturing] = useState(false)

  const captureFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !isScanning || scanSuccess || isCapturing) return

    setIsCapturing(true)
    
    const video = videoRef.current
    const canvas = canvasRef.current
    const context = canvas.getContext('2d', { willReadFrequently: true })

    if (!context) {
      setIsCapturing(false)
      return
    }

    // Check if video has valid dimensions
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      // Video not ready yet, try again later
      setIsCapturing(false)
      setTimeout(() => {
        if (isScanning && !scanSuccess) {
          captureFrame()
        }
      }, 100)
      return
    }

    try {
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      context.drawImage(video, 0, 0, canvas.width, canvas.height)

      // Get image data from canvas
      const imageData = context.getImageData(0, 0, canvas.width, canvas.height)
      
      // Use jsQR to detect QR code
      const code = jsQR(imageData.data, imageData.width, imageData.height)
      
      if (code) {
        // Success! QR code detected
        setScanSuccess(true)
        
        // Show success animation briefly before calling onScan
        setTimeout(() => {
          onScan(code.data)
        }, 500)
      } else {
        // Increment scan attempts for visual feedback
        setScanAttempts(prev => prev + 1)
        
        // If no QR code found, try again after a short delay
        setTimeout(() => {
          if (isScanning && !scanSuccess) {
            captureFrame()
          }
        }, 100)
      }
    } catch (error) {
      console.warn('Canvas processing error:', error)
    } finally {
      setIsCapturing(false)
    }
  }, [isScanning, onScan, scanSuccess, scanAttempts, isCapturing])

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play().catch((playError) => {
          console.warn('Video play failed:', playError)
        })
        setIsScanning(true)
        setScanSuccess(false)
        setScanAttempts(0)
        setIsCapturing(false)
        
        // Start automatic scanning when video is ready
        videoRef.current.onloadedmetadata = () => {
          // Wait a bit more to ensure video is fully ready
          setTimeout(() => {
            if (isScanning && !scanSuccess) {
              captureFrame()
            }
          }, 200)
        }
      }
    } catch (err) {
      setError(t('error.cameraAccess'))
      console.error('Camera error:', err)
    }
  }, [t, captureFrame])

  useEffect(() => {
    startCamera()
    return () => {
      stopCamera()
    }
  }, [startCamera])

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      stream.getTracks().forEach((track) => track.stop())
    }
    setIsScanning(false)
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
          <div className={`h-48 w-48 rounded-lg border-2 bg-transparent transition-all duration-300 ${
            scanSuccess 
              ? 'border-green-500 shadow-lg shadow-green-500/50 scale-105' 
              : 'border-primary-500'
          }`}>
            <div className={`absolute left-0 top-0 h-6 w-6 rounded-tl-lg border-l-2 border-t-2 transition-colors duration-300 ${
              scanSuccess ? 'border-green-500' : 'border-primary-500'
            }`}></div>
            <div className={`absolute right-0 top-0 h-6 w-6 rounded-tr-lg border-r-2 border-t-2 transition-colors duration-300 ${
              scanSuccess ? 'border-green-500' : 'border-primary-500'
            }`}></div>
            <div className={`absolute bottom-0 left-0 h-6 w-6 rounded-bl-lg border-b-2 border-l-2 transition-colors duration-300 ${
              scanSuccess ? 'border-green-500' : 'border-primary-500'
            }`}></div>
            <div className={`absolute bottom-0 right-0 h-6 w-6 rounded-br-lg border-b-2 border-r-2 transition-colors duration-300 ${
              scanSuccess ? 'border-green-500' : 'border-primary-500'
            }`}></div>
          </div>
          
          {/* Success checkmark animation */}
          {scanSuccess && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="animate-pulse">
                <svg 
                  className="h-16 w-16 text-green-500" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={3} 
                    d="M5 13l4 4L19 7" 
                  />
                </svg>
              </div>
            </div>
          )}
          
          {/* Scanning indicator */}
          {isScanning && !scanSuccess && (
            <div className="absolute top-4 right-4">
              <div className="flex space-x-1">
                <div className="h-2 w-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="h-2 w-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="h-2 w-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="text-center">
        <p className={`mb-4 transition-colors duration-300 ${
          scanSuccess 
            ? 'text-green-600 font-semibold' 
            : 'text-gray-600'
        }`}>
          {scanSuccess 
            ? '✅ QR-код успешно отсканирован!' 
            : t('scan.cameraInstruction')
          }
        </p>

        {isScanning && !scanSuccess && (
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

        {/* Scan attempts counter */}
        {isScanning && !scanSuccess && scanAttempts > 0 && (
          <p className="mb-4 text-sm text-gray-500">
            Попыток сканирования: {scanAttempts}
          </p>
        )}

        <div className="flex space-x-2">
          <button
            onClick={captureFrame}
            className={`flex-1 transition-all duration-300 ${
              scanSuccess
                ? 'btn-success'
                : 'btn-primary'
            }`}
            disabled={!isScanning || scanSuccess}
          >
            {scanSuccess ? '✓ Отсканировано' : t('scan.scan')}
          </button>
          <button onClick={handleCancel} className="btn-secondary flex-1">
            {t('scan.cancel')}
          </button>
        </div>
      </div>
    </div>
  )
}

export default QRCodeScanner
