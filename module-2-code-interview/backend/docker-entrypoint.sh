#!/bin/bash
set -e

echo "🚀 Starting Laravel application..."

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p storage/framework/{cache,sessions,views}
mkdir -p storage/logs
mkdir -p bootstrap/cache

# Set permissions
chmod -R 775 storage bootstrap/cache
chown -R www-data:www-data storage bootstrap/cache

# Copy .env.example to .env if .env doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
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

# Clear and cache config
echo "🔧 Optimizing application..."
php artisan config:clear || true
php artisan config:cache || true

# Start Reverb WebSocket server in background
echo "🌐 Starting WebSocket server..."
php artisan reverb:start --host=0.0.0.0 --port=8080 --debug &

# Give Reverb a moment to start
sleep 2

# Start Laravel development server
echo "✨ Starting Laravel server on port 8000..."
php artisan serve --host=0.0.0.0 --port=8000
