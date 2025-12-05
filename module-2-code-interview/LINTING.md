# Linting and Formatting

This project uses a comprehensive set of linters and formatters to ensure code quality and consistency.

## Quick Start

```bash
# Run all linters (backend + frontend)
make lint

# Run linters separately
make backend_lint
make frontend_lint

# Auto-format code
make format
make backend_format
make frontend_format
```

## Backend (Python)

### Tools

- **flake8** - Style guide enforcement (PEP 8)
- **black** - Code formatter
- **isort** - Import statement organizer
- **mypy** - Static type checker

### Configuration

All configuration is in `backend_fastapi/pyproject.toml` and `backend_fastapi/.flake8`

### Key Settings

- Line length: 100 characters
- Python version: 3.11
- Black-compatible import sorting

### Manual Commands

```bash
# Inside backend container
docker-compose exec backend flake8 app/
docker-compose exec backend black app/
docker-compose exec backend isort app/
docker-compose exec backend mypy app/
```

## Frontend (TypeScript/Vue)

### Tools

- **ESLint** - JavaScript/TypeScript linter
- **Prettier** - Code formatter
- **@typescript-eslint** - TypeScript-specific linting rules
- **eslint-plugin-vue** - Vue.js-specific linting rules

### Configuration

- `.eslintrc.cjs` - ESLint configuration
- `.prettierrc` - Prettier configuration
- `.prettierignore` - Files to ignore

### Key Settings

- Line length: 100 characters
- Single quotes
- Semicolons: true
- Tab width: 2 spaces

### Manual Commands

```bash
# Inside frontend container
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run lint:fix
docker-compose exec frontend npm run format
```

## CI/CD Integration

These linters will be integrated into GitHub Actions to run on:
- Pull requests
- Push to master

## Notes

- **Warnings vs Errors**: The lint command allows warnings (like `any` types) but fails on errors
- **Auto-fix**: Use `make format` to automatically fix most issues
- **Pre-commit**: Consider adding pre-commit hooks in the future
