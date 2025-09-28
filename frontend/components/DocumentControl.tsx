'use client'

import { useState } from 'react'
import { useTranslation } from '@/lib/i18n'
import { useNotifications } from '@/lib/context'

interface DocumentControlProps {
  onClose?: () => void
}

export function DocumentControl({ onClose }: DocumentControlProps) {
  const { t, language } = useTranslation()
  const { addNotification } = useNotifications()
  const [isUploading, setIsUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        addNotification({
          type: 'error',
          title: t('error'),
          message: language === 'ru' 
            ? 'Пожалуйста, выберите PDF файл'
            : language === 'en'
            ? 'Please select a PDF file'
            : '请选择PDF文件'
        })
        return
      }
      setSelectedFile(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      addNotification({
        type: 'error',
        title: t('error'),
        message: language === 'ru'
          ? 'Пожалуйста, выберите файл для загрузки'
          : language === 'en'
          ? 'Please select a file to upload'
          : '请选择要上传的文件'
      })
      return
    }

    setIsUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('enovia_id', 'NORMO-CONTROL')
      formData.append('revision', '0')

      const response = await fetch('/api/pdf/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const result = await response.json()
      
      addNotification({
        type: 'success',
        title: language === 'ru' ? 'Нормоконтроль завершен' : language === 'en' ? 'Document Control Completed' : '文档控制完成',
        message: language === 'ru' 
          ? `PDF документ "${selectedFile.name}" успешно обработан. Добавлено ${result.qr_codes_count} QR-кодов.`
          : language === 'en'
          ? `PDF document "${selectedFile.name}" successfully processed. Added ${result.qr_codes_count} QR codes.`
          : `PDF文档"${selectedFile.name}"已成功处理。添加了${result.qr_codes_count}个QR码。`
      })

      // Reset form
      setSelectedFile(null)
      if (onClose) onClose()
      
    } catch (error) {
      addNotification({
        type: 'error',
        title: t('error'),
        message: language === 'ru'
          ? 'Ошибка при загрузке файла'
          : language === 'en'
          ? 'Error uploading file'
          : '上传文件时出错'
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleClose = () => {
    setSelectedFile(null)
    if (onClose) onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="card max-w-md p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {language === 'ru'
              ? 'Нормоконтроль документа'
              : language === 'en'
              ? 'Document Control'
              : '文档控制'}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="mb-6">
          <p className="mb-4 text-gray-600 dark:text-gray-300">
            {language === 'ru'
              ? 'Загрузите PDF документ для проведения нормоконтроля и добавления QR-кодов'
              : language === 'en'
              ? 'Upload a PDF document for document control and QR code addition'
              : '上传PDF文档进行文档控制和QR码添加'}
          </p>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {language === 'ru' ? 'Выберите PDF файл:' : language === 'en' ? 'Select PDF file:' : '选择PDF文件：'}
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 dark:file:bg-primary-900 dark:file:text-primary-300"
            />
          </div>

          {selectedFile && (
            <div className="mb-4 rounded-md bg-gray-100 p-3 dark:bg-gray-800">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                <span className="font-medium">
                  {language === 'ru' ? 'Выбранный файл:' : language === 'en' ? 'Selected file:' : '所选文件：'}
                </span>
                <br />
                {selectedFile.name}
                <br />
                <span className="text-xs text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </p>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {language === 'ru' ? 'Обработка...' : language === 'en' ? 'Processing...' : '处理中...'}
              </div>
            ) : (
              language === 'ru' ? 'Начать нормоконтроль' : language === 'en' ? 'Start Document Control' : '开始文档控制'
            )}
          </button>
          <button
            onClick={handleClose}
            className="btn-secondary"
          >
            {language === 'ru' ? 'Отмена' : language === 'en' ? 'Cancel' : '取消'}
          </button>
        </div>
      </div>
    </div>
  )
}

