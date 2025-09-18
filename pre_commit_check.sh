# Backend
cd backend
pip install -r requirements.txt
black .
isort .
flake8 .
mypy app/
pytest

# Frontend
cd frontend
npm install
npm run lint
npm run format:check
npm run type-check
npm test
npm run build

