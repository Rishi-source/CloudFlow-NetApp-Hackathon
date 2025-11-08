#!/bin/bash

echo "🚀 CloudFlow Intelligence Platform Setup"
echo "========================================"
echo ""

if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your credentials if needed."
    echo ""
fi

echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

echo ""
echo "✅ CloudFlow Intelligence Platform is starting up!"
echo ""
echo "📊 Access points:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "📝 Services:"
echo "   MongoDB: localhost:27017"
echo "   Redis: localhost:6379"
echo "   Kafka: localhost:9092"
echo ""
echo "🔍 To view logs:"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo ""
echo "🎉 Happy hacking!"
