#!/bin/bash

echo "🔒 Starting Seeker Self-Test"
echo "============================"
echo ""
echo "⚠️  IMPORTANT: This is for SELF-TESTING ONLY!"
echo "   Only use on systems you own or have explicit permission to test."
echo ""
echo "🎯 Test Setup:"
echo "1. Seeker will start a web server on localhost:8080"
echo "2. You'll get a link to share (don't actually share it)"
echo "3. Visit the link yourself to see what data would be collected"
echo "4. This demonstrates what the tool captures"
echo ""

read -p "Press Enter to continue with self-test..."

echo ""
echo "🚀 Starting Seeker..."
echo "📍 Access at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop when done testing"

docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 8080"