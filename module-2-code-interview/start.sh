#!/bin/bash

echo "🚀 Starting Code Interview Platform..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Copy .env.example to .env if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from .env.example..."
    cp backend/.env.example backend/.env
fi

echo "🔨 Building and starting containers..."
echo "   This may take a few minutes on first run..."
echo ""

# Start Docker Compose
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Application is ready!"
    echo ""
    echo "📍 Access the application:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   Health:    http://localhost:8000/health"
    echo ""
    echo "📖 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 To stop:"
    echo "   docker-compose down"
    echo ""
else
    echo ""
    echo "❌ Error: Some containers failed to start"
    echo "   Run 'docker-compose logs' to see details"
    exit 1
fi
