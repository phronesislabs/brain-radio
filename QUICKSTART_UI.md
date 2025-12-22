# Brain-Radio Web UI Quickstart

**Last updated: 2025-12-22**

Get Brain-Radio running in 5 minutes! This guide walks you through setting up and using the web interface.

## Prerequisites

Before you begin, you'll need:

1. **Spotify Developer Account** (free)
   - Go to https://developer.spotify.com/dashboard
   - Create a new app
   - Get your Client ID and Client Secret

2. **OpenAI API Key** (paid)
   - Get one from https://platform.openai.com/api-keys
   - You'll enter this in the web UI (stored securely in your session)

3. **Docker** (recommended) or **Node.js 20+** and **Python 3.11+**

## Quick Start with Docker (Recommended)

### Step 1: Configure Spotify App

1. Go to https://developer.spotify.com/dashboard
2. Click "Create app"
3. Fill in:
   - **App name**: Brain-Radio (or any name)
   - **App description**: Functional music playlists
   - **Redirect URI**: `http://127.0.0.1:8000/api/auth/callback`
     - **Important**: Use `127.0.0.1` (not `localhost`) - Spotify blocks `localhost` redirect URIs
4. Click "Save"
5. Copy your **Client ID** and **Client Secret**

### Step 2: Set Environment Variables

Create a `.env` file in the project root:

```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/auth/callback
FRONTEND_URL=http://localhost:3000
```

**Note**: If Spotify blocks `localhost`, use `127.0.0.1` in the redirect URI (as shown above). Make sure the redirect URI in your `.env` file matches exactly what you entered in the Spotify Developer Dashboard.

Or export them in your shell:

```bash
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
export SPOTIFY_REDIRECT_URI="http://127.0.0.1:8000/api/auth/callback"
export FRONTEND_URL="http://localhost:3000"
```

**Note**: If Spotify blocks `localhost`, use `127.0.0.1` in the redirect URI (as shown above). Make sure the redirect URI in your environment variables matches exactly what you entered in the Spotify Developer Dashboard.

### Step 3: Generate package-lock.json (if needed)

If you haven't run `npm install` in the frontend directory yet, generate the lock file:

```bash
cd frontend
npm install
cd ..
```

This creates `package-lock.json` which ensures reproducible builds.

### Step 4: Start the Application

**Option 1: Using the startup script (Recommended)**

```bash
# From project root
./start.sh
```

This script will:
- Check for Docker and required environment variables
- Generate `package-lock.json` if needed
- Start all services using Docker Compose
- Wait for services to be ready
- Automatically open your browser to http://localhost:3000

**Option 2: Manual Docker Compose**

```bash
# From project root
docker-compose up --build
```

Then manually open http://localhost:3000 in your browser.

**What gets started:**
- Backend API on http://127.0.0.1:8000
- Frontend UI on http://localhost:3000

### Step 5: Open the Web UI

1. Open http://localhost:3000 in your browser
2. Click **"Connect with Spotify"**
3. Authorize the app in Spotify
4. When prompted, enter your **OpenAI API key**
5. Start generating playlists!

## Quick Start (Local Development)

If you prefer running locally without Docker:

### Step 1: Install Dependencies

**Backend:**
```bash
# Install Python dependencies using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

**Note**: The `npm install` command will generate `package-lock.json`, which is required for reproducible Docker builds. Make sure to commit this file to version control.

### Step 2: Set Environment Variables

```bash
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
export SPOTIFY_REDIRECT_URI="http://127.0.0.1:8000/api/auth/callback"
```

**Note**: If Spotify blocks `localhost`, use `127.0.0.1` in the redirect URI (as shown above). Make sure the redirect URI matches exactly what you entered in the Spotify Developer Dashboard.

### Step 3: Start Backend (Terminal 1)

```bash
# From project root
uvicorn src.brain_radio.api.main:app --reload --port 8000
```

### Step 4: Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

### Step 5: Open the Web UI

1. Open http://localhost:3000
2. Follow the same steps as Docker setup above

## Using the Web UI

### First Time Setup

1. **Connect Spotify**: Click the green "Connect with Spotify" button
   - You'll be redirected to Spotify to authorize
   - After authorization, you'll return to the app

2. **Enter OpenAI API Key**: A modal will appear automatically
   - Enter your OpenAI API key (starts with `sk-`)
   - Your key is stored securely in your session (not saved to disk)
   - Click "Save"

### Generating Playlists

1. **Select a Mode**:
   - **Focus**: 120-140 BPM, instrumental, steady rhythm (for coding, studying)
   - **Relax**: 60-90 BPM, major keys, acoustic textures (for unwinding)
   - **Sleep**: <60 BPM, ambient/drone (for falling asleep)
   - **Meditation**: Low energy, slow tempo, repetitive (for mindfulness)

2. **Optional Settings**:
   - **Genre**: Enter a genre preference (e.g., "Jazz", "Techno", "Ambient")
   - **Duration**: Set playlist length (15-240 minutes, default: 60)

3. **Generate**: Click on a mode card to start generation
   - The app will show a loading spinner
   - Generation typically takes 30-60 seconds
   - Your playlist will appear below

### Playing Music

**If you have Spotify Premium:**
- Playback controls appear automatically
- Click the play button to start
- Use skip buttons to navigate tracks
- Current track is highlighted in the track list

**If you don't have Premium:**
- Playlists are still generated successfully
- You'll see a message that Premium is required for playback
- You can still view the generated track list

### Settings

- Click the settings button (gear icon) in the top-right to:
  - Update your OpenAI API key
  - Change configuration

## Troubleshooting

### Spotify Won't Accept HTTP Redirect URI

**Important**: Spotify blocks `localhost` redirect URIs. Always use `127.0.0.1` instead.

If you still cannot add the redirect URI:

**Solution 1: Verify you're using 127.0.0.1**
- Make sure you're using: `http://127.0.0.1:8000/api/auth/callback` (not `localhost`)
- Update your environment variable: `SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/auth/callback`

**Solution 2: Set up HTTPS for localhost (Advanced)**
1. Generate a self-signed certificate:
   ```bash
   openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=127.0.0.1"
   ```
2. Update backend to use HTTPS (modify `src/brain_radio/api/main.py` or use a reverse proxy)
3. Use redirect URI: `https://127.0.0.1:8000/api/auth/callback`
4. Accept the self-signed certificate in your browser when prompted

**Note**: For production, you must use HTTPS. The HTTP restriction only applies to localhost development.

### "Spotify OAuth not configured"
- Make sure `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are set
- Check that your `.env` file is in the project root (for Docker)
- Verify environment variables are exported (for local dev)
- Ensure the redirect URI in your code matches exactly what's in Spotify Dashboard

### "Failed to generate playlist"
- Check that your OpenAI API key is valid
- Ensure you have credits in your OpenAI account
- Check browser console and backend logs for detailed errors

### "Spotify Premium is required"
- This is expected if you don't have Premium
- Playlists are still generated, just can't play in browser
- You can view the track list and use Spotify app to play

### Playback not working
- Ensure you have Spotify Premium
- Check browser console for Web Playback SDK errors
- Try refreshing the page
- Make sure no other Spotify app is playing music

### Port already in use
- Backend uses port 8000, frontend uses 3000
- Stop other services using these ports
- Or change ports in `docker-compose.yml` or Vite config

## Next Steps

- Read [README_UI.md](README_UI.md) for detailed setup instructions
- Read [README_DOCKER.md](README_DOCKER.md) for Docker-specific details
- Check [AGENTS.md](AGENTS.md) to understand how the system works
- Review the API docs at http://localhost:8000/docs

## Tips

- **Genre preferences**: Be specific! "Jazz" works better than "music"
- **Duration**: Start with 60 minutes to test, then try longer playlists
- **Mode selection**: Each mode has strict scientific constraints - trust the system
- **API key security**: Your OpenAI key is stored in session only, never on disk
- **Premium benefits**: Premium users get in-browser playback; free users can still generate playlists

## Support

- Check the browser console (F12) for frontend errors
- Check backend logs for API errors
- Review [README_UI.md](README_UI.md) for detailed troubleshooting

Enjoy your scientifically-tuned playlists!

