# Brain-Radio Docker Setup

This guide explains how to run Brain-Radio using Docker, which provides a production-like environment locally.

## Prerequisites

- Docker and Docker Compose installed
- Spotify Developer Account credentials
- OpenAI API key (will be prompted in the UI)

## Quick Start

### 1. Set Environment Variables

Create a `.env` file in the project root (this is only for Docker Compose, not for the app):

```bash
# Spotify OAuth (required)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/auth/callback

# Optional: Frontend URL (defaults to http://localhost:3000)
FRONTEND_URL=http://localhost:3000
```

**Note:** The `.env` file is only used by Docker Compose to pass environment variables to containers. The application itself does not read `.env` files. In production, these would be set in your container orchestration platform (Kubernetes, ECS, etc.).

### 2. Configure Spotify App

1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Add redirect URI: `http://127.0.0.1:8000/api/auth/callback` (use `127.0.0.1`, not `localhost` - Spotify blocks `localhost`)
4. Copy Client ID and Client Secret to `.env` file
5. Set required scopes:
   - `user-read-playback-state`
   - `user-modify-playback-state`
   - `user-read-currently-playing`
   - `streaming`

### 3. Run with Docker Compose

**Production mode:**
```bash
docker-compose up --build
```

**Development mode (with hot reload):**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 5. First-Time Setup

1. Click "Connect with Spotify" to authenticate
2. You'll be redirected to Spotify to authorize the app
3. After returning, you'll be prompted to enter your OpenAI API key
4. Enter your OpenAI API key (get it from https://platform.openai.com/api-keys)
5. The key is stored securely in your session

## Architecture

### Services

- **backend**: FastAPI server running on port 8000
- **frontend**: Nginx serving React app on port 3000 (production) or Vite dev server (development)

### Data Storage

- **Sessions**: Currently stored in-memory (will be lost on restart)
- **OpenAI API Key**: Stored in user session (encrypted in production)
- **Spotify Tokens**: Stored in user session with automatic refresh

## Production Deployment

For production deployment:

1. **Use a proper session store:**
   - Add Redis service to docker-compose.yml
   - Update session storage in `src/brain_radio/api/main.py`

2. **Set environment variables in your platform:**
   - Kubernetes: ConfigMaps/Secrets
   - AWS ECS: Task definitions
   - Heroku: Config vars
   - Docker Swarm: Docker secrets

3. **Update CORS origins:**
   - Set `FRONTEND_URL` to your production frontend URL
   - Update `cors_origins` in `src/brain_radio/api/main.py`

4. **Use HTTPS:**
   - Update `SPOTIFY_REDIRECT_URI` to use HTTPS
   - Configure SSL/TLS termination (nginx, cloudflare, etc.)

5. **Secure cookie settings:**
   - Set `secure=True` for cookies in production
   - Use `SameSite` attribute appropriately

## Environment Variables

### Required (for Spotify OAuth)
- `SPOTIFY_CLIENT_ID`: Spotify app client ID
- `SPOTIFY_CLIENT_SECRET`: Spotify app client secret
- `SPOTIFY_REDIRECT_URI`: OAuth callback URL (must match Spotify app settings)

### Optional
- `FRONTEND_URL`: Frontend URL for CORS and redirects (default: http://localhost:3000)

### User-Provided (via UI)
- OpenAI API key: Entered through the web interface and stored in session

## Troubleshooting

### OAuth Issues
- Ensure redirect URI matches exactly in Spotify dashboard
- Check that environment variables are set correctly
- Verify cookies are enabled in browser

### Container Issues
```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild containers
docker-compose up --build --force-recreate
```

### Port Conflicts
If ports 3000 or 8000 are in use, update `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change host port
```

## Development

For local development with hot reload:

```bash
docker-compose -f docker-compose.dev.yml up
```

This will:
- Mount source code as volumes
- Enable hot reload for both frontend and backend
- Use Vite dev server for frontend

## Security Notes

1. **Session Storage**: Currently in-memory. Use Redis or database in production.
2. **API Keys**: OpenAI keys are stored in session. Consider encryption at rest.
3. **Secrets**: Never commit `.env` files or expose secrets in logs.
4. **HTTPS**: Always use HTTPS in production for OAuth callbacks.

