# Exposing Seeker to the Internet for Ethical Testing

⚠️ **IMPORTANT**: Only use this with explicit permission from the person you're testing on!

## Option 1: ngrok (Easiest - Recommended for Quick Tests)

### Install ngrok:
```bash
brew install ngrok
```

### Get Free Account:
1. Sign up at https://ngrok.com
2. Get your auth token
3. Run: `ngrok config add-authtoken YOUR_TOKEN`

### Expose Seeker:
```bash
# In one terminal, start Seeker:
./simple-test.sh

# In another terminal, expose it:
ngrok http 9999
```

**You'll get a public URL like:**
```
https://abc123.ngrok.io
```

Send this URL to your friend!

### Pros:
✅ Super easy and fast
✅ HTTPS by default (looks more legitimate)
✅ No router configuration needed
✅ Free tier available

### Cons:
❌ Random URL each time (paid tier gets custom domains)
❌ Session expires after inactivity

---

## Option 2: Cloudflare Tunnel (Free, More Permanent)

### Install Cloudflare Tunnel:
```bash
brew install cloudflared
```

### Authenticate:
```bash
cloudflared tunnel login
```

### Create Tunnel:
```bash
cloudflared tunnel create seeker-test
```

### Expose Seeker:
```bash
# Start Seeker first
./simple-test.sh

# In another terminal:
cloudflared tunnel --url http://localhost:9999
```

### Pros:
✅ Free forever
✅ Can use custom domain
✅ More stable than ngrok free tier
✅ Good performance

---

## Option 3: Port Forwarding (Most Control)

### Steps:
1. Find your public IP: `curl ifconfig.me`
2. Log into your router (usually 192.168.1.1)
3. Forward port 9999 to your Mac's local IP
4. Configure firewall to allow port 9999

### Pros:
✅ Full control
✅ No third-party service
✅ No data passing through tunnels

### Cons:
❌ Requires router access
❌ Exposes your real IP
❌ More complex setup
❌ May violate ISP terms of service

---

## Recommended Setup for Your Test:

**Use ngrok** - it's the easiest and most professional:

```bash
# Terminal 1: Start Seeker
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999"
# Choose template 0 (NearYou) or 6 (Google ReCaptcha)

# Terminal 2: Expose via ngrok
ngrok http 9999
```

---

## Social Engineering Tips (Ethical Use Only!):

To make your test realistic (with permission):
1. **Use a convincing template** (Google ReCaptcha works well)
2. **Create a believable story** - "Hey, check out this cool link"
3. **Use URL shortener** - Makes ngrok link less suspicious
4. **Time it right** - When your friend is active

---

## Safety & Ethics Checklist:

✅ Explicit permission obtained from target
✅ Clear documentation of test purpose
✅ Plan to explain findings afterward
✅ Delete collected data after test
✅ Use only for educational/authorized purposes
✅ Never use on strangers or without permission

---

## After the Test:

1. Stop Seeker (Ctrl+C)
2. Stop ngrok (Ctrl+C)
3. Review collected data with your friend
4. Explain how the attack worked
5. Share protection strategies
6. Delete the collected data