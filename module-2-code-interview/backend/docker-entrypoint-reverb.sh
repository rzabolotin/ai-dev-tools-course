#!/bin/bash
set -e

echo "🚀 Starting Laravel Reverb WebSocket server..."

# Create necessary directories (lightweight check)
mkdir -p storage/framework/{cache,sessions,views}
mkdir -p storage/logs

# Wait for database (to ensure Laravel can connect if needed)
echo "⏳ Waiting for database..."
while ! nc -z db 3306; do
  sleep 1
done
echo "✅ Database is ready!"

# Wait a bit more for database to be fully ready
sleep 2

# Clear config cache to ensure fresh config
echo "🧹 Clearing config cache..."
php artisan config:clear

# Show Reverb configuration for debugging
echo "📋 Reverb Configuration:"
php artisan config:show reverb

# Start Reverb WebSocket server with verbose logging
echo "🌐 Starting Reverb on 0.0.0.0:8080 with verbose logging..."
php artisan reverb:start --host=0.0.0.0 --port=8080 --debug -vvv
