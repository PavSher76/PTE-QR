import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AppProvider } from '@/lib/context';
import { NotificationContainer } from '@/components/NotificationContainer';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'PTE QR System',
  description: 'Система проверки актуальности документов через QR-коды',
  keywords: ['PTE', 'QR', 'документы', 'актуальность', 'ENOVIA'],
  authors: [{ name: 'PTI' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <AppProvider>
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            {children}
            <NotificationContainer />
          </div>
        </AppProvider>
      </body>
    </html>
  );
}
