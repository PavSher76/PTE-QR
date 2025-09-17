# CI/CD Configuration

## GitHub Actions Workflow

This project uses GitHub Actions for continuous integration and deployment.

### Workflow Structure

The CI/CD pipeline consists of three main jobs:

1. **Test** - Runs all tests (backend and frontend)
2. **Build** - Builds and pushes Docker images
3. **Deploy** - Deploys to production (main branch only)

### Database Configuration

#### Local Development
- **Host**: `postgres` (Docker service)
- **User**: `pte_qr`
- **Password**: `pte_qr_dev`
- **Database**: `pte_qr`

#### CI/CD Testing
- **Host**: `localhost` (GitHub Actions service)
- **User**: `postgres`
- **Password**: `postgres`
- **Database**: `pte_qr_test`

### Environment Variables

The following environment variables are used in CI/CD:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pte_qr_test

# Redis
REDIS_URL=redis://localhost:6379

# Security (test values)
JWT_SECRET_KEY=test-jwt-secret-key
SECRET_KEY=test-secret-key
QR_HMAC_SECRET=test-qr-hmac-secret
```

### Database Setup

The CI pipeline automatically sets up the test database using `init_ci_db.sql`:

1. Creates the `pte_qr` schema
2. Creates all required tables
3. Inserts test data
4. Verifies the setup

### Running Tests Locally

#### Using Docker Compose (Recommended)
```bash
# Start services
docker-compose up -d

# Run backend tests
make test-backend

# Run frontend tests
make test-frontend

# Run all tests
make test
```

#### Using Local Services
```bash
# Setup test database
make setup-db

# Run tests in CI mode
make test-ci
```

### Troubleshooting

#### Database Connection Issues

If you see errors like:
```
psycopg2.OperationalError: could not translate host name "postgres" to address
```

**Solution**: Make sure you're using the correct database URL for your environment:

- **Docker Compose**: `postgresql://pte_qr:pte_qr_dev@postgres:5432/pte_qr`
- **Local/CI**: `postgresql://postgres:postgres@localhost:5432/pte_qr_test`

#### Role "root" Does Not Exist

If you see errors like:
```
FATAL: role "root" does not exist
```

**Solution**: Use the correct database user:

- **PostgreSQL default user**: `postgres`
- **Not**: `root`

#### Schema Not Found

If you see errors like:
```
relation "pte_qr.users" does not exist
```

**Solution**: Run the database initialization script:

```bash
make setup-db
```

### Database Schema

The test database includes the following tables:

- `pte_qr.users` - User accounts
- `pte_qr.user_roles` - User roles and permissions
- `pte_qr.user_user_roles` - User-role associations
- `pte_qr.documents` - Document metadata
- `pte_qr.qr_codes` - Generated QR codes
- `pte_qr.qr_code_generations` - QR generation history
- `pte_qr.audit_logs` - Audit trail

### Test Data

The CI database is pre-populated with:

- **Test Users**:
  - `testuser` (regular user)
  - `adminuser` (admin user)
- **Test Documents**:
  - `TEST-DOC-001`
  - `TEST-DOC-002`
- **User Roles**:
  - `user` (basic permissions)
  - `admin` (full permissions)

### Security Notes

- Test credentials are safe to use in CI/CD
- Production secrets should be stored in GitHub Secrets
- Database passwords are different for each environment
- JWT secrets are different for each environment

### Monitoring

The CI pipeline includes:

- Database connection verification
- Schema existence checks
- Table structure validation
- Test data verification
- Coverage reporting
- Docker image building
- Security scanning (if configured)
