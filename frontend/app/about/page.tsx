'use client'

import { useTranslation } from '@/lib/i18n'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'

export default function AboutPage() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              {t('about.title')}
            </h1>
            
            <div className="prose prose-lg dark:prose-invert max-w-none">
              <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
                {t('app.title')}
              </h2>
              
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                {t('about.description')}
              </p>
              
              <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                {t('about.features')}
              </h3>
              
              <ul className="list-disc list-inside text-gray-600 dark:text-gray-300 mb-6 space-y-2">
                <li>{t('about.feature1')}</li>
                <li>{t('about.feature2')}</li>
                <li>{t('about.feature3')}</li>
                <li>{t('about.feature4')}</li>
                <li>{t('about.feature5')}</li>
                <li>{t('about.feature6')}</li>
              </ul>
              
              <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                {t('about.technologies')}
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">{t('about.frontend')}</h4>
                  <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                    <li>• Next.js 14</li>
                    <li>• React 18</li>
                    <li>• TypeScript</li>
                    <li>• Tailwind CSS</li>
                  </ul>
                </div>
                
                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">{t('about.backend')}</h4>
                  <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                    <li>• FastAPI</li>
                    <li>• Python 3.11</li>
                    <li>• PostgreSQL</li>
                    <li>• Redis</li>
                  </ul>
                </div>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                {t('about.contacts')}
              </h3>
              
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <p className="text-gray-700 dark:text-gray-300">
                  {t('about.contactText')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  )
}
