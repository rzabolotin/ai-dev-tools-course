#!/bin/bash
set -e

echo "🚀 Starting Laravel application..."

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p storage/framework/{cache,sessions,views}
mkdir -p storage/logs

# Copy .env.example to .env if .env doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Install composer dependencies if vendor doesn't exist
if [ ! -f vendor/autoload.php ]; then
    echo "📦 Installing composer dependencies..."
    composer install --no-interaction --prefer-dist --optimize-autoloader
else
    echo "✅ Composer dependencies already installed"
fi

# Generate application key if not set
if ! grep -q "APP_KEY=base64:" .env; then
    echo "🔑 Generating application key..."
    php artisan key:generate --force
fi

# Wait for database
echo "⏳ Waiting for database..."
while ! nc -z db 3306; do
  sleep 1
done
echo "✅ Database is ready!"

# Wait a bit more for database to be fully ready
sleep 3

# Run migrations
echo "🗄️  Running migrations..."
php artisan migrate --force || echo "⚠️  Migrations failed or already run"

# Clear caches
echo "🔧 Optimizing application..."
php artisan cache:clear || true
php artisan route:clear || true
php artisan view:clear || true

# Start Laravel development server
echo "✨ Starting Laravel server on port 8000..."
php artisan serve --host=0.0.0.0 --port=8000
