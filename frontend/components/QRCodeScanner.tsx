'use client';

import { useEffect, useRef, useState } from 'react';
import { useTranslation } from '@/lib/i18n';

interface QRCodeScannerProps {
  onScan: (data: string) => void;
  onCancel: () => void;
}

export function QRCodeScanner({ onScan, onCancel }: QRCodeScannerProps) {
  const { t } = useTranslation();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setIsScanning(true);
      }
    } catch (err) {
      setError(t('error.cameraAccess'));
      console.error('Camera error:', err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
    }
    setIsScanning(false);
  };

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Here you would typically use a QR code library like jsQR
    // For now, we'll simulate a successful scan
    setTimeout(() => {
      onScan('https://qr.pti.ru/r/3D-00001234/B/3?ts=1703123456&t=abc123def456');
    }, 2000);
  };

  const handleCancel = () => {
    stopCamera();
    onCancel();
  };

  if (error) {
    return (
      <div className="text-center">
        <div className="w-16 h-16 bg-danger-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-danger-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <p className="text-danger-600 mb-4">{error}</p>
        <button onClick={handleCancel} className="btn-secondary">
          {t('scan.close')}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <video
          ref={videoRef}
          className="w-full h-64 bg-gray-100 rounded-lg object-cover"
          playsInline
          muted
        />
        <canvas
          ref={canvasRef}
          className="hidden"
        />
        
        {/* QR Code overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-48 h-48 border-2 border-primary-500 rounded-lg bg-transparent">
            <div className="absolute top-0 left-0 w-6 h-6 border-t-2 border-l-2 border-primary-500 rounded-tl-lg"></div>
            <div className="absolute top-0 right-0 w-6 h-6 border-t-2 border-r-2 border-primary-500 rounded-tr-lg"></div>
            <div className="absolute bottom-0 left-0 w-6 h-6 border-b-2 border-l-2 border-primary-500 rounded-bl-lg"></div>
            <div className="absolute bottom-0 right-0 w-6 h-6 border-b-2 border-r-2 border-primary-500 rounded-br-lg"></div>
          </div>
        </div>
      </div>

      <div className="text-center">
        <p className="text-gray-600 mb-4">
          {t('scan.cameraInstruction')}
        </p>
        
        {isScanning && (
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
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
          <button
            onClick={handleCancel}
            className="btn-secondary flex-1"
          >
            {t('scan.cancel')}
          </button>
        </div>
      </div>
    </div>
  );
}
