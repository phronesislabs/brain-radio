# Brain-Radio UI Setup Guide

This guide explains how to set up and run the Brain-Radio web application.

## Architecture

The application consists of two main components:

1. **Frontend**: React + TypeScript application using Vite
2. **Backend**: FastAPI Python server providing OAuth and playlist generation APIs

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Spotify Developer Account with:
  - Client ID
  - Client Secret
  - Redirect URI configured: `http://localhost:8000/api/auth/callback`

## Setup

### Docker (Recommended - Production-like)

See [README_DOCKER.md](README_DOCKER.md) for complete Docker setup.

```bash
# Set environment variables
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
export SPOTIFY_REDIRECT_URI="http://localhost:8000/api/auth/callback"

# Run with Docker Compose
docker-compose up --build
```

### Local Development

**1. Backend Setup:**

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Set environment variables
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
export SPOTIFY_REDIRECT_URI="http://localhost:8000/api/auth/callback"
```

**2. Frontend Setup:**

```bash
cd frontend
npm install
```

**3. Running the Application**

**Terminal 1 - Backend:**
```bash
# From project root
uvicorn src.brain_radio.api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**4. First-Time Setup:**

1. Click "Connect with Spotify" to authenticate
2. Enter your OpenAI API key when prompted (stored securely in your session)
3. Start generating playlists!

## Features

### Mode Selection
- **Focus**: 120-140 BPM, no vocals, steady rhythm
- **Relax**: 60-90 BPM, major keys, acoustic textures
- **Sleep**: <60 BPM, ambient/drone, no sudden transients
- **Meditation**: Low energy, slow tempo, repetitive elements

### Spotify Integration
- OAuth 2.0 authentication flow
- Automatic token refresh
- Web Playback SDK integration (Premium required)
- Playlist generation and playback

### UI Components
- Modern, dark-themed interface
- Responsive design
- Real-time playback controls
- Track queue display
- Premium status detection

## Development

### Frontend Development
```bash
cd frontend
npm run dev        # Start dev server
npm run build      # Build for production
npm run lint       # Run linter
```

### Backend Development
```bash
# Run with auto-reload
uvicorn src.brain_radio.api.main:app --reload

# Run tests
pytest
```

## Environment Variables

**For Docker Compose** (create `.env` file or export):
```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/api/auth/callback
FRONTEND_URL=http://localhost:3000  # Optional
```

**For Local Development** (export in shell):
```bash
export SPOTIFY_CLIENT_ID="your_spotify_client_id"
export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
export SPOTIFY_REDIRECT_URI="http://localhost:8000/api/auth/callback"
```

**Note:** The OpenAI API key is no longer set via environment variable. It's entered through the web UI and stored securely in your session.

## Spotify App Configuration

1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Add redirect URI: `http://localhost:8000/api/auth/callback`
4. Copy Client ID and Client Secret
5. Set required scopes:
   - `user-read-playback-state`
   - `user-modify-playback-state`
   - `user-read-currently-playing`
   - `streaming`

## Troubleshooting

### OAuth Issues
- Ensure redirect URI matches exactly in Spotify dashboard
- Check that SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are set
- Verify cookies are enabled in browser

### Playback Issues
- Spotify Premium is required for in-browser playback
- Check browser console for Web Playback SDK errors
- Ensure device is ready before attempting playback

### API Errors
- Check backend logs for detailed error messages
- Verify OpenAI API key is set
- Ensure all dependencies are installed

## Production Deployment

For production deployment:

1. Set up proper session storage (Redis recommended)
2. Configure HTTPS
3. Update CORS origins
4. Set secure cookie flags
5. Use environment-specific configuration
6. Set up proper logging and monitoring

