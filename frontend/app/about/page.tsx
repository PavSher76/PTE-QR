'use client'

import { motion } from 'framer-motion'
import { 
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
  ArrowRightIcon,
  BuildingOfficeIcon,
  UsersIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'

export default function AboutPage() {
  const features = [
    {
      icon: ShieldCheckIcon,
      title: 'Безопасность данных',
      description: 'HMAC подпись и шифрование обеспечивают максимальную защиту от подделки документов',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: BoltIcon,
      title: 'Высокая производительность',
      description: 'Оптимизированная архитектура обеспечивает быструю работу системы',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      icon: CloudIcon,
      title: 'Облачная интеграция',
      description: 'Полная интеграция с облачными сервисами и корпоративными системами',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: ChartBarIcon,
      title: 'Аналитика и отчеты',
      description: 'Детальная аналитика использования и автоматические отчеты',
      color: 'from-purple-500 to-pink-500'
    }
  ]

  const technologies = [
    {
      name: 'Frontend',
      icon: CpuChipIcon,
      items: ['Next.js 14', 'React 18', 'TypeScript', 'Tailwind CSS', 'Framer Motion']
    },
    {
      name: 'Backend',
      icon: BuildingOfficeIcon,
      items: ['FastAPI', 'Python 3.11', 'SQLAlchemy', 'Alembic', 'Pydantic']
    },
    {
      name: 'Database',
      icon: DocumentTextIcon,
      items: ['PostgreSQL 15', 'Redis', 'UUID', 'JSONB', 'Full-text search']
    },
    {
      name: 'Infrastructure',
      icon: CloudIcon,
      items: ['Docker', 'Nginx', 'Prometheus', 'Grafana', 'Kubernetes']
    }
  ]

  const team = [
    {
      name: 'Команда разработки',
      role: 'Backend & Frontend',
      description: 'Опытные разработчики с экспертизой в области корпоративных систем'
    },
    {
      name: 'Архитекторы решений',
      role: 'System Design',
      description: 'Специалисты по проектированию масштабируемых систем'
    },
    {
      name: 'DevOps инженеры',
      role: 'Infrastructure',
      description: 'Эксперты по развертыванию и мониторингу приложений'
    }
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
              <BuildingOfficeIcon className="w-4 h-4 text-blue-400 mr-2" />
              <span className="text-sm font-medium text-white">О системе PTE QR</span>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                PTE QR
              </span>
              <br />
              <span className="text-white">Система</span>
            </h1>

            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Современная система проверки актуальности документов через QR-коды 
              с интеграцией в корпоративные системы управления жизненным циклом изделий
            </p>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
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
              Ключевые возможности
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Инновационные технологии для эффективного управления документами
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.8 }}
                viewport={{ once: true }}
                className="group bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/20 transition-all duration-300"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${feature.color} p-3 mb-4`}>
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

      {/* Technologies Section */}
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
              Технологический стек
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Современные технологии для надежной и масштабируемой системы
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {technologies.map((tech, index) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.8 }}
                viewport={{ once: true }}
                className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6"
              >
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 p-2 mr-3">
                    <tech.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">
                    {tech.name}
                  </h3>
                </div>
                <ul className="space-y-2">
                  {tech.items.map((item) => (
                    <li key={item} className="flex items-center text-gray-300 text-sm">
                      <CheckCircleIcon className="w-4 h-4 text-green-400 mr-2 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
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
              Наша команда
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Опытные специалисты, создающие инновационные решения
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {team.map((member, index) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.8 }}
                viewport={{ once: true }}
                className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center"
              >
                <div className="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 p-4 mx-auto mb-4">
                  <UsersIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  {member.name}
                </h3>
                <p className="text-blue-400 text-sm mb-3">
                  {member.role}
                </p>
                <p className="text-gray-300 text-sm">
                  {member.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

    </div>
  )
}
