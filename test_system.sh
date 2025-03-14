#!/bin/bash

# Test script for Telegram AI Agent

echo "Starting Telegram AI Agent test suite..."
echo "----------------------------------------"

# Check if Docker and Docker Compose are installed
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "Docker and Docker Compose are installed."
echo "----------------------------------------"

# Check if .env file exists
echo "Checking environment configuration..."
if [ ! -f "./deployment/.env" ]; then
    echo "Error: .env file not found in deployment directory."
    echo "Please create a .env file based on the .env.example template."
    exit 1
fi

echo "Environment configuration found."
echo "----------------------------------------"

# Test backend code
echo "Testing backend code..."
cd backend/telegram_ai_agent
source ../../venv/bin/activate
python manage.py check
if [ $? -ne 0 ]; then
    echo "Backend code check failed."
    exit 1
fi

# Run backend tests
echo "Running backend unit tests..."
python manage.py test
if [ $? -ne 0 ]; then
    echo "Backend tests failed."
    exit 1
fi

echo "Backend tests passed."
echo "----------------------------------------"

# Test frontend code
echo "Testing frontend code..."
cd ../../frontend
npm run lint
if [ $? -ne 0 ]; then
    echo "Frontend linting failed."
    exit 1
fi

echo "Frontend linting passed."
echo "----------------------------------------"

# Test Docker Compose configuration
echo "Testing Docker Compose configuration..."
cd ../deployment
docker-compose config
if [ $? -ne 0 ]; then
    echo "Docker Compose configuration is invalid."
    exit 1
fi

echo "Docker Compose configuration is valid."
echo "----------------------------------------"

# Test building Docker images
echo "Building Docker images (this may take a while)..."
docker-compose build
if [ $? -ne 0 ]; then
    echo "Docker image build failed."
    exit 1
fi

echo "Docker images built successfully."
echo "----------------------------------------"

# Test starting containers
echo "Starting containers for integration testing..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Failed to start containers."
    exit 1
fi

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Test backend API
echo "Testing backend API..."
curl -s http://localhost:8000/api/ > /dev/null
if [ $? -ne 0 ]; then
    echo "Backend API is not responding."
    docker-compose down
    exit 1
fi

echo "Backend API is responding."
echo "----------------------------------------"

# Test frontend
echo "Testing frontend..."
curl -s http://localhost:3000/ > /dev/null
if [ $? -ne 0 ]; then
    echo "Frontend is not responding."
    docker-compose down
    exit 1
fi

echo "Frontend is responding."
echo "----------------------------------------"

# Stop containers
echo "Stopping containers..."
docker-compose down

echo "All tests passed successfully!"
echo "The Telegram AI Agent system is ready for deployment."
