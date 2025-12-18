#!/bin/bash

echo "🔒 Simple Seeker Test - NearYou Template"
echo "======================================="
echo ""
echo "This will start Seeker with the simplest template"
echo "Visit http://localhost:9999 to see the fake geolocation page"
echo ""
echo "Press Ctrl+C in this terminal to stop Seeker when done"
echo ""

# Start Seeker with NearYou template (option 0)
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && echo '0' | python3 seeker.py -p 9999"