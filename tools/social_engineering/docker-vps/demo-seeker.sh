#!/bin/bash

echo "🔒 Seeker Demo - Social Engineering Tool"
echo "========================================"
echo ""
echo "⚠️  EDUCATIONAL PURPOSE ONLY!"
echo "   This demonstrates how social engineering attacks work."
echo ""
echo "🎯 What Seeker does:"
echo "   • Creates fake web pages (Google, Facebook, Instagram, etc.)"
echo "   • Requests location permission from visitors" 
echo "   • Logs IP addresses, browser info, and geolocation"
echo "   • Shows real-time visitor data"
echo ""
echo "🧪 Safe Testing:"
echo "   • We'll run it on port 9999"
echo "   • You can visit http://localhost:9999 yourself"
echo "   • See what data it would collect from you"
echo "   • Learn how these attacks work to protect yourself"
echo ""

read -p "Press Enter to start Seeker demo..."

echo ""
echo "🚀 Starting Seeker on port 9999..."
echo "📍 Visit: http://localhost:9999"
echo ""
echo "Choose a template when prompted (try option 1 for Google)"
echo "Press Ctrl+C to stop when done"
echo ""

# Kill any existing seeker processes
docker exec -it whitehacking-vps pkill -f seeker.py 2>/dev/null

# Start Seeker interactively
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999"