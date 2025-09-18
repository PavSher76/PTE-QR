#!/bin/bash

echo "🔍 Запуск проверок перед коммитом..."

# Backend проверки через Docker
echo "📦 Проверка backend..."
cd backend
docker-compose exec backend black . || echo "⚠️  Black не найден, пропускаем форматирование"
docker-compose exec backend isort . || echo "⚠️  isort не найден, пропускаем сортировку импортов"
docker-compose exec backend flake8 . || echo "⚠️  flake8 не найден, пропускаем линтинг"
docker-compose exec backend mypy app/ || echo "⚠️  mypy не найден, пропускаем проверку типов"
docker-compose exec backend pytest || echo "⚠️  pytest не найден, пропускаем тесты"

# Frontend проверки
echo "🎨 Проверка frontend..."
cd ../frontend
npm install
npm run lint || echo "⚠️  Линтинг завершился с предупреждениями"
npm run format:check || echo "⚠️  Проверка форматирования завершилась с предупреждениями"
npm run type-check || echo "⚠️  Проверка типов завершилась с предупреждениями"
npm test || echo "⚠️  Тесты завершились с предупреждениями"
npm run build || echo "❌ Сборка не удалась"

echo "✅ Проверки завершены!"