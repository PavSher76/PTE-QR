'use client';

import { useTranslation } from '@/lib/i18n';
import { Logo } from './Logo';

export function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <Logo size="small" variant="compact" />
              <h3 className="text-lg font-semibold">{t('footer.title')}</h3>
            </div>
            <p className="text-gray-400 text-sm">
              {t('footer.description')}
            </p>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold mb-4 uppercase tracking-wider">{t('footer.product')}</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">{t('footer.features')}</a></li>
              <li><a href="#" className="hover:text-white transition-colors">{t('footer.integration')}</a></li>
              <li><a href="#" className="hover:text-white transition-colors">{t('footer.api')}</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold mb-4 uppercase tracking-wider">{t('footer.support')}</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">{t('footer.documentation')}</a></li>
              <li><a href="#" className="hover:text-white transition-colors">{t('footer.help')}</a></li>
              <li><a href="#" className="hover:text-white transition-colors">{t('footer.contacts')}</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold mb-4 uppercase tracking-wider">{t('footer.company')}</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">{t('footer.about')}</a></li>
              <li><a href="#" className="hover:text-white transition-colors">{t('footer.privacy')}</a></li>
              <li><a href="#" className="hover:text-white transition-colors">{t('footer.terms')}</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
          <p>{t('footer.copyright')}</p>
        </div>
      </div>
    </footer>
  );
}
