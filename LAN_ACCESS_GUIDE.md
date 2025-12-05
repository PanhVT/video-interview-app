# LAN Access Setup Guide

## Changes Made

The project is now configured to allow LAN access from other devices. Here are the changes:

### 1. Backend Server (`server/app/main.py`)
- ✅ CORS updated to accept requests from any origin (wildcard `*`)
- ✅ Allows connections from all localhost variations

### 2. Frontend Vite Config (`client/vite.config.js`)
- ✅ Updated to listen on `0.0.0.0` (all network interfaces)
- ✅ Frontend now accessible from any device on the network

### 3. API Configuration (`client/src/shared/config/api.config.js`)
- ✅ Created dynamic API endpoint configuration
- ✅ Auto-detects server IP based on client connection
- ✅ Smart routing: localhost access → localhost API, LAN IP access → LAN IP API

### 4. All API Files Updated
- ✅ `verifyToken.js`
- ✅ `startSession.js`
- ✅ `uploadOne.js`
- ✅ `finishSession.js`
- ✅ `getTranscripts.js`

All now use the dynamic `API_BASE_URL` from configuration.

---

## How to Use on LAN

### Get Your Machine IP Address

**Windows:**
```powershell
ipconfig
# Look for "IPv4 Address" under your network adapter
# Example: 192.168.1.100
```

**Mac/Linux:**
```bash
hostname -I
# or
ifconfig
# Look for inet address (usually starts with 192.168.x.x or 10.0.x.x)
```

### Start the Backend Server

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The `--host 0.0.0.0` makes it listen on all network interfaces.

### Start the Frontend

```bash
cd client
npm install
npm run dev
```

You'll see output like:
```
  VITE v5.0.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/   <-- Use this on other devices
```

### Access from Another Device on the LAN

On any device connected to the same network:

1. Open a web browser
2. Go to: `http://YOUR_MACHINE_IP:5173`
   - Example: `http://192.168.1.100:5173`
3. The app automatically detects your server IP
4. Everything works like normal!

---

## How It Works

```
Other Device on LAN
        ↓
http://192.168.1.100:5173
        ↓
Frontend auto-detects IP: 192.168.1.100
        ↓
API calls go to: http://192.168.1.100:8000/api/*
        ↓
Backend accepts request (CORS allows all origins)
        ↓
Works perfectly!
```

---

## Network Requirements

- ✅ Both devices must be on the same network (WiFi/Ethernet)
- ✅ No firewall blocking ports 5173 (frontend) and 8000 (backend)
- ✅ Devices can reach each other (ping test if unsure)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't connect from another device | Check firewall, ensure same network, verify IP address |
| Connection refused | Backend may not be running on `0.0.0.0:8000` |
| CORS errors | Check if backend CORS is properly configured (`allow_origins: ["*"]`) |
| API calls fail | Verify the IP address is correct, check network connectivity |

