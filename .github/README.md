# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the PTE-QR system.

## Workflows

### 1. CI/CD Pipeline (`ci.yml`)

Main continuous integration and deployment pipeline that runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Backend Tests**: Runs Python tests with PostgreSQL and Redis services
- **Frontend Tests**: Runs Node.js tests, linting, type checking, and build
- **Docker Build**: Builds and tests Docker images
- **Security Scan**: Runs Trivy vulnerability scanner
- **Deploy Staging**: Deploys to staging environment (develop branch only)
- **Deploy Production**: Deploys to production environment (main branch only)

### 2. Code Quality (`code-quality.yml`)

Code quality checks that run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Backend Quality**: Runs Black, isort, Flake8, and MyPy
- **Frontend Quality**: Runs ESLint, Prettier, and TypeScript checks
- **Security Audit**: Runs safety and npm audit
- **Performance Test**: Runs Lighthouse CI for performance testing

## Configuration Files

### Backend
- `mypy.ini`: MyPy type checking configuration
- `.flake8`: Flake8 linting configuration
- `pyproject.toml`: Black, isort, and pytest configuration

### Frontend
- `jest.config.js`: Jest testing configuration
- `jest.setup.js`: Jest setup and mocks
- `.prettierrc`: Prettier formatting configuration
- `.lighthouserc.json`: Lighthouse CI configuration

## Caching

The workflows use GitHub Actions caching to speed up builds:
- **Node.js**: Caches npm dependencies using `package-lock.json`
- **Python**: Caches pip dependencies using `requirements.txt`
- **Docker**: Uses GitHub Actions cache for Docker layers

## Environment Variables

Required environment variables for deployment:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ENOVIA_BASE_URL`: ENOVIA PLM system URL
- `JWT_SECRET_KEY`: JWT signing secret
- `HMAC_SECRET_KEY`: HMAC signing secret

## Security

- All workflows run security scans using Trivy
- Dependencies are audited for vulnerabilities
- Secrets are managed through GitHub Secrets
- Docker images are scanned for security issues

## Performance

- Lighthouse CI runs performance tests on the frontend
- Coverage reports are generated for both backend and frontend
- Build artifacts are cached to improve build times

## Troubleshooting

### Common Issues

1. **Cache Miss**: If dependencies change, the cache will be invalidated automatically
2. **Type Errors**: Run `mypy app/` locally to check type issues
3. **Linting Errors**: Run `black .` and `flake8 .` locally to fix formatting
4. **Test Failures**: Check the test logs in the Actions tab

### Local Development

To run the same checks locally:

```bash
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
```
