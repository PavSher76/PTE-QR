'use client'

import { useState } from 'react'
import { useTranslation } from '@/lib/i18n'
import { useNotifications } from '@/lib/context'

interface PdfUploadFormProps {
  onClose: () => void
}

export function PdfUploadForm({ onClose }: PdfUploadFormProps) {
  const { language } = useTranslation()
  const { addNotification } = useNotifications()
  const [file, setFile] = useState<File | null>(null)
  const [enoviaId, setEnoviaId] = useState('')
  const [documentTitle, setDocumentTitle] = useState('')
  const [revision, setRevision] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<{
    filename: string
    downloadUrl: string
    qrCodesCount: number
  } | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        addNotification({
          type: 'error',
          title: 'Ошибка',
          message: 'Пожалуйста, выберите PDF файл'
        })
        return
      }
      setFile(selectedFile)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file || !enoviaId.trim() || !documentTitle.trim() || !revision.trim()) {
      addNotification({
        type: 'error',
        title: 'Ошибка',
        message: 'Пожалуйста, заполните все поля'
      })
      return
    }

    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('enovia_id', enoviaId.trim())
      formData.append('title', documentTitle.trim())
      formData.append('revision', revision.trim())

      const token = localStorage.getItem('pte-qr-token')
      if (!token) {
        addNotification({
          type: 'error',
          title: 'Ошибка',
          message: 'Необходимо войти в систему'
        })
        return
      }

      const response = await fetch('/api/pdf/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        setUploadResult({
          filename: result.output_file,
          downloadUrl: result.download_url,
          qrCodesCount: result.qr_codes_count
        })
        addNotification({
          type: 'success',
          title: 'Документ обработан',
          message: `PDF файл "${documentTitle}" успешно обработан. Создано ${result.qr_codes_count} QR-кодов.`
        })
      } else if (response.status === 401) {
        addNotification({
          type: 'error',
          title: 'Ошибка авторизации',
          message: 'Сессия истекла. Пожалуйста, войдите в систему заново.'
        })
        localStorage.removeItem('pte-qr-token')
        localStorage.removeItem('pte-qr-user')
        window.location.href = '/'
      } else {
        const errorData = await response.json()
        addNotification({
          type: 'error',
          title: 'Ошибка загрузки',
          message: errorData.detail || 'Произошла ошибка при загрузке файла'
        })
      }
    } catch (error) {
      console.error('Ошибка загрузки PDF:', error)
      addNotification({
        type: 'error',
        title: 'Ошибка',
        message: 'Произошла ошибка при загрузке файла'
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleDownload = async () => {
    if (!uploadResult) return

    try {
      const token = localStorage.getItem('pte-qr-token')
      if (!token) {
        addNotification({
          type: 'error',
          title: 'Ошибка',
          message: 'Необходимо войти в систему'
        })
        return
      }

      const response = await fetch(`/api/pdf/download?filename=${encodeURIComponent(uploadResult.filename)}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = uploadResult.filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        
        addNotification({
          type: 'success',
          title: 'Успешно',
          message: 'PDF документ с QR-кодами скачан'
        })
      } else {
        addNotification({
          type: 'error',
          title: 'Ошибка скачивания',
          message: 'Не удалось скачать файл'
        })
      }
    } catch (error) {
      console.error('Ошибка скачивания PDF:', error)
      addNotification({
        type: 'error',
        title: 'Ошибка',
        message: 'Произошла ошибка при скачивании файла'
      })
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="card max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
              {language === 'ru'
                ? 'Загрузка PDF документа'
                : language === 'en'
                ? 'PDF Document Upload'
                : 'PDF文档上传'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {language === 'ru'
                  ? 'PDF файл'
                  : language === 'en'
                  ? 'PDF File'
                  : 'PDF文件'}
              </label>
              <input
                type="file"
                id="pdf-file"
                name="pdf-file"
                accept=".pdf"
                onChange={handleFileChange}
                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-colors"
                required
              />
              {file && (
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {language === 'ru'
                    ? `Выбран файл: ${file.name}`
                    : language === 'en'
                    ? `Selected file: ${file.name}`
                    : `已选择文件: ${file.name}`}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {language === 'ru'
                  ? 'ID документа в Эновия'
                  : language === 'en'
                  ? 'ENOVIA Document ID'
                  : 'ENOVIA文档ID'}
              </label>
              <input
                type="text"
                id="enovia-id"
                name="enovia-id"
                value={enoviaId}
                onChange={(e) => setEnoviaId(e.target.value)}
                placeholder={language === 'ru' ? 'Например: DOC-001' : language === 'en' ? 'e.g.: DOC-001' : '例如: DOC-001'}
                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {language === 'ru'
                  ? 'Название документа'
                  : language === 'en'
                  ? 'Document Title'
                  : '文档标题'}
              </label>
              <input
                type="text"
                id="document-title"
                name="document-title"
                value={documentTitle}
                onChange={(e) => setDocumentTitle(e.target.value)}
                placeholder={language === 'ru' ? 'Введите название документа' : language === 'en' ? 'Enter document title' : '输入文档标题'}
                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {language === 'ru'
                  ? 'Ревизия'
                  : language === 'en'
                  ? 'Revision'
                  : '修订版'}
              </label>
              <input
                type="text"
                id="revision"
                name="revision"
                value={revision}
                onChange={(e) => setRevision(e.target.value)}
                placeholder={language === 'ru' ? 'Например: A, B, 1.0' : language === 'en' ? 'e.g.: A, B, 1.0' : '例如: A, B, 1.0'}
                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-colors"
                required
              />
            </div>

            {uploadResult ? (
              <div className="space-y-4 pt-4">
                <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <div className="flex items-center mb-2">
                    <svg className="w-5 h-5 text-green-600 dark:text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3 className="text-sm font-medium text-green-800 dark:text-green-200">
                      {language === 'ru'
                        ? 'Документ обработан'
                        : language === 'en'
                        ? 'Document processed'
                        : '文档已处理'}
                    </h3>
                  </div>
                  <p className="text-sm text-green-700 dark:text-green-300">
                    {language === 'ru'
                      ? `Добавлено ${uploadResult.qrCodesCount} QR-кодов`
                      : language === 'en'
                      ? `Added ${uploadResult.qrCodesCount} QR codes`
                      : `已添加 ${uploadResult.qrCodesCount} 个QR码`}
                  </p>
                </div>
                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={handleDownload}
                    className="btn-primary flex-1"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {language === 'ru'
                      ? 'Скачать PDF'
                      : language === 'en'
                      ? 'Download PDF'
                      : '下载PDF'}
                  </button>
                  <button
                    type="button"
                    onClick={onClose}
                    className="btn-secondary flex-1"
                  >
                    {language === 'ru'
                      ? 'Закрыть'
                      : language === 'en'
                      ? 'Close'
                      : '关闭'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn-secondary flex-1"
                >
                  {language === 'ru'
                    ? 'Отмена'
                    : language === 'en'
                    ? 'Cancel'
                    : '取消'}
                </button>
                <button
                  type="submit"
                  disabled={isUploading}
                  className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUploading
                    ? (language === 'ru'
                        ? 'Загрузка...'
                        : language === 'en'
                        ? 'Uploading...'
                        : '上传中...')
                    : (language === 'ru'
                        ? 'Загрузить'
                        : language === 'en'
                        ? 'Upload'
                        : '上传')}
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}
