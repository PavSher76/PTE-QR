'use client'

export const dynamic = 'force-dynamic'

export default function TestSimplePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-8">
      <h1 className="text-4xl font-bold mb-4">Простая тестовая страница</h1>
      <p className="text-xl">Эта страница не использует useTheme и должна работать без ошибок.</p>
      <div className="mt-8 p-4 bg-white/10 rounded-lg">
        <h2 className="text-2xl font-semibold mb-2">Статус</h2>
        <p>✅ Страница загружается успешно</p>
        <p>✅ Нет ошибок с useTheme</p>
        <p>✅ Стили применяются корректно</p>
      </div>
    </div>
  )
}
