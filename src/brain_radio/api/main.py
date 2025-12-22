"""FastAPI application for Brain-Radio web interface."""

import base64
import os
import secrets
import time
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from brain_radio.agents.supervisor import SupervisorAgent
from brain_radio.api.constants import (
    OAUTH_STATE_EXPIRY_SECONDS,
    SESSION_DURATION_SECONDS,
    SPOTIFY_SCOPES,
    TOKEN_EXPIRY_SECONDS,
)
from brain_radio.models import Mode, PlaylistRequest, PlaylistResult

app = FastAPI(title="Brain-Radio API", version="0.1.0")

# Get frontend URL from environment
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# CORS configuration - allow frontend URL from environment
cors_origins = list(
    set(
        [
            FRONTEND_URL,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Spotify OAuth configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/api/auth/callback")
# Spotify OAuth configuration

# In-memory session storage (in production, use Redis or database)
sessions: dict[str, dict] = {}


def get_session_id(request: Request) -> Optional[str]:
    """Get session ID from cookies."""
    return request.cookies.get("session_id")


def _create_spotify_auth_header() -> str:
    """Create Basic auth header for Spotify API."""
    credentials = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    return f"Basic {credentials}"


class PlaylistGenerateRequest(BaseModel):
    mode: Mode
    genre: Optional[str] = None
    duration_minutes: Optional[int] = 60


class OpenAIConfigRequest(BaseModel):
    api_key: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Brain-Radio API", "version": "0.1.0"}


@app.get("/api/auth/login")
async def login():
    """Initiate Spotify OAuth flow."""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Spotify OAuth not configured. Please contact the administrator.",
        )

    state = secrets.token_urlsafe(32)
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES,
        "state": state,
        "show_dialog": "false",
    }

    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    response = RedirectResponse(url=auth_url)
    response.set_cookie("oauth_state", state, httponly=True, max_age=OAUTH_STATE_EXPIRY_SECONDS)
    return response


@app.get("/api/auth/callback")
async def callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    request: Request = None,
):
    """Handle Spotify OAuth callback."""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")

    # Verify state
    stored_state = request.cookies.get("oauth_state") if request else None
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Exchange code for tokens
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        auth_header = _create_spotify_auth_header()
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            data=token_data,
            headers={"Authorization": auth_header},
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {response.text}")

        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")

        # Get user info
        user_response = await client.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info")

        user_data = user_response.json()
        is_premium = user_data.get("product") == "premium"

        # Create session
        session_id = secrets.token_urlsafe(32)
        sessions[session_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user_data.get("id"),
            "is_premium": is_premium,
            "expires_at": time.time() + tokens.get("expires_in", TOKEN_EXPIRY_SECONDS),
        }

        # Redirect to frontend
        redirect_url = FRONTEND_URL
        response = RedirectResponse(url=redirect_url)
        response.set_cookie(
            "session_id", session_id, httponly=True, max_age=SESSION_DURATION_SECONDS
        )
        response.delete_cookie("oauth_state")
        return response


@app.get("/api/auth/token")
async def get_token(session_id: Optional[str] = Depends(get_session_id)):
    """Get current access token."""
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = sessions[session_id]

    # Refresh token if expired
    if time.time() >= session["expires_at"]:
        if not session.get("refresh_token"):
            raise HTTPException(status_code=401, detail="Session expired")

        # Refresh the token
        async with httpx.AsyncClient() as client:
            auth_header = _create_spotify_auth_header()
            refresh_response = await client.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": session["refresh_token"],
                },
                headers={"Authorization": auth_header},
            )

            if refresh_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Failed to refresh token")

            new_tokens = refresh_response.json()
            session["access_token"] = new_tokens["access_token"]
            session["expires_at"] = time.time() + new_tokens.get("expires_in", TOKEN_EXPIRY_SECONDS)
            if "refresh_token" in new_tokens:
                session["refresh_token"] = new_tokens["refresh_token"]

    return {"access_token": session["access_token"]}


@app.get("/api/auth/status")
async def auth_status(session_id: Optional[str] = Depends(get_session_id)):
    """Check authentication status."""
    if not session_id or session_id not in sessions:
        return {"authenticated": False, "has_openai_key": False}

    session = sessions[session_id]
    return {
        "authenticated": True,
        "is_premium": session.get("is_premium", False),
        "user_id": session.get("user_id"),
        "has_openai_key": bool(session.get("openai_api_key")),
    }


@app.post("/api/config/openai")
async def set_openai_key(
    config: OpenAIConfigRequest,
    session_id: Optional[str] = Depends(get_session_id),
):
    """Store OpenAI API key in session."""
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Store API key in session (in production, use encrypted storage)
    sessions[session_id]["openai_api_key"] = config.api_key
    return {"status": "ok", "message": "OpenAI API key stored"}


@app.get("/api/config/openai/status")
async def get_openai_status(session_id: Optional[str] = Depends(get_session_id)):
    """Check if OpenAI API key is configured."""
    if not session_id or session_id not in sessions:
        return {"configured": False}

    return {"configured": bool(sessions[session_id].get("openai_api_key"))}


@app.post("/api/playlist/generate", response_model=PlaylistResult)
async def generate_playlist(
    request: PlaylistGenerateRequest,
    session_id: Optional[str] = Depends(get_session_id),
):
    """Generate a playlist for the specified mode."""
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = sessions[session_id]
    openai_api_key = session.get("openai_api_key")

    if not openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured. Please provide your API key in settings.",
        )

    # Create playlist request
    playlist_request = PlaylistRequest(
        mode=request.mode,
        genre=request.genre,
        duration_minutes=request.duration_minutes or 60,
    )

    # Initialize supervisor with user's OpenAI API key
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)
    supervisor = SupervisorAgent(llm=llm)

    try:
        result = await supervisor.generate_playlist(playlist_request)
        return result
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Invalid OpenAI API key. Please check your API key and try again.",
            )
        raise HTTPException(status_code=500, detail=f"Failed to generate playlist: {str(e)}")


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
