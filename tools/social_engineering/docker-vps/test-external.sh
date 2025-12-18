#!/bin/bash

echo "🎯 Seeker External Test Setup"
echo "============================="
echo ""
echo "⚠️  ETHICAL HACKING CHECKLIST:"
echo "✅ Do you have EXPLICIT PERMISSION from your friend?"
echo "✅ Have you explained what you're testing?"
echo "✅ Will you share the results with them?"
echo "✅ Will you delete the data after the test?"
echo ""
read -p "Type 'YES' if all above are true: " confirm

if [ "$confirm" != "YES" ]; then
    echo "❌ Test cancelled. Get proper permission first!"
    exit 1
fi

echo ""
echo "📋 Setup Instructions:"
echo ""
echo "1. First, get your ngrok auth token:"
echo "   - Go to https://dashboard.ngrok.com/signup"
echo "   - Sign up (free)"
echo "   - Copy your authtoken"
echo ""
read -p "Have you signed up for ngrok? (y/n): " ngrok_ready

if [ "$ngrok_ready" != "y" ]; then
    echo "Please sign up at https://dashboard.ngrok.com/signup first"
    exit 1
fi

echo ""
read -p "Enter your ngrok authtoken: " authtoken
ngrok config add-authtoken "$authtoken"

echo ""
echo "🚀 Starting Seeker..."
echo ""
echo "Choose a template when prompted:"
echo "  0 - NearYou (simple, fast)"
echo "  6 - Google ReCaptcha (looks professional)"
echo ""
echo "After Seeker starts, I'll launch ngrok in another terminal"
echo ""

# Start Seeker in background
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999" &
SEEKER_PID=$!

sleep 5

# Open a new terminal with ngrok
echo ""
echo "🌐 Starting ngrok tunnel..."
echo ""
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)' && ngrok http 9999"'

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📱 Next Steps:"
echo "1. Check the NEW TERMINAL WINDOW for your ngrok URL"
echo "2. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)"
echo "3. Send that URL to your friend"
echo "4. Watch THIS terminal for incoming data"
echo ""
echo "⏸️  When done testing:"
echo "  - Press Ctrl+C in THIS window to stop Seeker"
echo "  - Press Ctrl+C in the NGROK window"
echo "  - Review results with your friend"
echo ""
echo "📊 Collected data will be saved in:"
echo "   /opt/seeker/db/results.csv (inside VPS)"
echo ""