#!/bin/bash

echo "🚀 Setting up your Docker VPS..."

# Create directories
mkdir -p data projects

# Build and start the VPS
docker-compose up -d --build

echo "✅ White Hat Hacking VPS is running!"
echo ""
echo "🔒 Access your VPS:"
echo "  SSH: ssh vpsuser@localhost -p 2222"
echo "  Password: password123"
echo ""
echo "🔧 Or enter directly:"
echo "  docker exec -it whitehacking-vps bash"
echo ""
echo "📚 Once inside, type 'hackhelp' for available tools"
echo ""
echo "⚡ Management commands:"
echo "  Stop VPS:    docker-compose down"
echo "  Restart VPS: docker-compose restart"
echo "  View logs:   docker logs whitehacking-vps"
