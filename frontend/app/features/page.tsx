'use client'

import { motion } from 'framer-motion'
import { 
  QrCodeIcon,
  ShieldCheckIcon,
  BoltIcon,
  CloudIcon,
  ChartBarIcon,
  CogIcon,
  GlobeAltIcon,
  LockClosedIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'

export default function FeaturesPage() {
  const mainFeatures = [
    {
      icon: QrCodeIcon,
      title: 'Мгновенное сканирование',
      description: 'Сканируйте QR-коды документов и получайте актуальную информацию за секунды',
      benefits: ['Быстрое сканирование', 'Офлайн работа', 'Поддержка всех форматов'],
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Максимальная безопасность',
      description: 'HMAC подпись и шифрование обеспечивают защиту от подделки документов',
      benefits: ['HMAC подпись', 'Шифрование данных', 'Аудит доступа'],
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: BoltIcon,
      title: 'Высокая производительность',
      description: 'Оптимизированная архитектура обеспечивает быструю работу системы',
      benefits: ['< 200ms отклик', 'Кэширование', 'Масштабируемость'],
      color: 'from-yellow-500 to-orange-500'
    },
    {
      icon: CloudIcon,
      title: 'Облачная интеграция',
      description: 'Полная интеграция с облачными сервисами и корпоративными системами',
      benefits: ['API интеграция', 'Синхронизация', 'Облачное хранение'],
      color: 'from-purple-500 to-pink-500'
    }
  ]

  const technicalFeatures = [
    {
      icon: ChartBarIcon,
      title: 'Аналитика и отчеты',
      description: 'Детальная аналитика использования и автоматические отчеты'
    },
    {
      icon: CogIcon,
      title: 'Настройка под задачи',
      description: 'Гибкая настройка системы под специфику вашего бизнеса'
    },
    {
      icon: GlobeAltIcon,
      title: 'Многоязычность',
      description: 'Поддержка множества языков и локализация интерфейса'
    },
    {
      icon: LockClosedIcon,
      title: 'Контроль доступа',
      description: 'Гранулярный контроль доступа и ролевая модель безопасности'
    },
    {
      icon: DocumentTextIcon,
      title: 'Управление документами',
      description: 'Полный жизненный цикл управления документами'
    },
    {
      icon: ClockIcon,
      title: 'История изменений',
      description: 'Полная история изменений и версионирование документов'
    }
  ]

  const integrations = [
    { name: 'ENOVIA PLM', logo: '🏭', description: 'Прямая интеграция с системой PLM' },
    { name: 'SAP', logo: '📊', description: 'Интеграция с корпоративными системами' },
    { name: 'Microsoft 365', logo: '📧', description: 'Работа с документами Office' },
    { name: 'Google Workspace', logo: '🌐', description: 'Интеграция с Google сервисами' },
    { name: 'Slack', logo: '💬', description: 'Уведомления в корпоративном чате' },
    { name: 'Teams', logo: '👥', description: 'Интеграция с Microsoft Teams' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-16">
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 mb-8"
            >
              <BoltIcon className="w-4 h-4 text-yellow-400 mr-2" />
              <span className="text-sm font-medium text-white">Возможности системы</span>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Мощные
              </span>
              <br />
              <span className="text-white">возможности</span>
            </h1>

            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Все необходимые инструменты для эффективного управления документами 
              в одном современном решении
            </p>
          </motion.div>
        </div>
      </section>

      {/* Main Features */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Основные возможности
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Ключевые функции, которые делают PTE QR Систему незаменимым инструментом
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-8">
            {mainFeatures.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.8 }}
                viewport={{ once: true }}
                className="group relative"
              >
                <div className={`absolute inset-0 bg-gradient-to-r ${feature.color} opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-2xl blur-xl`} />
                <div className="relative bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-8 hover:bg-white/20 transition-all duration-300">
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${feature.color} p-4 mb-6`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-semibold text-white mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-gray-300 mb-6 leading-relaxed">
                    {feature.description}
                  </p>
                  <ul className="space-y-2">
                    {feature.benefits.map((benefit) => (
                      <li key={benefit} className="flex items-center text-gray-300">
                        <CheckCircleIcon className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                        {benefit}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Features */}
      <section className="py-20 bg-white/5 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Технические возможности
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Дополнительные функции для максимальной эффективности работы
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {technicalFeatures.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.8 }}
                viewport={{ once: true }}
                className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/20 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 p-3 mb-4">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-300 text-sm">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Интеграции
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Подключение к популярным корпоративным системам и сервисам
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {integrations.map((integration, index) => (
              <motion.div
                key={integration.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.8 }}
                viewport={{ once: true }}
                className="group bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/20 transition-all duration-300"
              >
                <div className="flex items-center mb-4">
                  <div className="text-3xl mr-4">{integration.logo}</div>
                  <h3 className="text-lg font-semibold text-white">
                    {integration.name}
                  </h3>
                </div>
                <p className="text-gray-300 text-sm mb-4">
                  {integration.description}
                </p>
                <div className="flex items-center text-blue-400 text-sm group-hover:text-blue-300 transition-colors">
                  <span>Подробнее</span>
                  <ArrowRightIcon className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 backdrop-blur-sm border border-white/20 rounded-3xl p-12"
          >
            <BoltIcon className="w-16 h-16 text-yellow-400 mx-auto mb-6" />
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Готовы попробовать?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Начните использовать PTE QR Систему уже сегодня и убедитесь в ее эффективности
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl text-white font-semibold text-lg shadow-2xl hover:shadow-blue-500/25 transition-all duration-300"
              >
                Начать бесплатно
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl text-white font-semibold text-lg hover:bg-white/20 transition-all duration-300"
              >
                Запросить демо
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
