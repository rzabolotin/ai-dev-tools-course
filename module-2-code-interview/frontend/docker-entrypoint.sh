#!/bin/sh
set -e

echo "🚀 Starting Nuxt application..."

# Install npm dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
else
    echo "✅ npm dependencies already installed"
fi

# Start Nuxt development server
echo "✨ Starting Nuxt dev server on port 3000..."
exec npm run dev
