"""Tests for Brain-Radio API endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from brain_radio.api.main import app, sessions
from brain_radio.models import Mode, PlaylistResult, TrackMetadata


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_sessions():
    """Reset sessions before each test."""
    sessions.clear()
    yield
    sessions.clear()


@pytest.fixture
def mock_openai_key(monkeypatch):
    """Set a mock OpenAI API key in environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Brain-Radio API"
        assert data["version"] == "0.1.0"


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health(self, client):
        """Test health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_login_without_spotify_config(self, client, monkeypatch):
        """Test login fails when Spotify is not configured."""
        # Mock the environment variables to be empty
        with patch("brain_radio.api.main.SPOTIFY_CLIENT_ID", ""), patch(
            "brain_radio.api.main.SPOTIFY_CLIENT_SECRET", ""
        ):
            response = client.get("/api/auth/login")
            assert response.status_code == 500
            assert "not configured" in response.json()["detail"].lower()

    def test_login_with_spotify_config(self, client, monkeypatch):
        """Test login redirects to Spotify OAuth."""
        # Mock the environment variables
        with patch("brain_radio.api.main.SPOTIFY_CLIENT_ID", "test_client_id"), patch(
            "brain_radio.api.main.SPOTIFY_CLIENT_SECRET", "test_secret"
        ), patch(
            "brain_radio.api.main.SPOTIFY_REDIRECT_URI",
            "http://localhost:8000/api/auth/callback",
        ):
            response = client.get("/api/auth/login")
            assert response.status_code == 307  # Redirect
            assert "accounts.spotify.com/authorize" in response.headers["location"]

    def test_auth_status_not_authenticated(self, client):
        """Test auth status when not authenticated."""
        response = client.get("/api/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["has_openai_key"] is False

    def test_auth_status_authenticated(self, client):
        """Test auth status when authenticated."""
        session_id = "test_session_123"
        sessions[session_id] = {
            "access_token": "test_token",
            "user_id": "test_user",
            "is_premium": True,
            "expires_at": 9999999999,
        }
        response = client.get("/api/auth/status", cookies={"session_id": session_id})
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["is_premium"] is True
        assert data["user_id"] == "test_user"
        assert data["has_openai_key"] is False

    def test_get_token_not_authenticated(self, client):
        """Test getting token when not authenticated."""
        response = client.get("/api/auth/token")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_set_openai_key_not_authenticated(self, client):
        """Test setting OpenAI key when not authenticated."""
        response = client.post("/api/config/openai", json={"api_key": "sk-test"})
        assert response.status_code == 401

    def test_set_openai_key_authenticated(self, client):
        """Test setting OpenAI key when authenticated."""
        session_id = "test_session_123"
        sessions[session_id] = {
            "access_token": "test_token",
            "expires_at": 9999999999,
        }
        response = client.post(
            "/api/config/openai",
            json={"api_key": "sk-test-key"},
            cookies={"session_id": session_id},
        )
        assert response.status_code == 200
        assert sessions[session_id]["openai_api_key"] == "sk-test-key"

    def test_get_openai_status_not_configured(self, client):
        """Test OpenAI status when not configured."""
        session_id = "test_session_123"
        sessions[session_id] = {
            "access_token": "test_token",
            "expires_at": 9999999999,
        }
        response = client.get("/api/config/openai/status", cookies={"session_id": session_id})
        assert response.status_code == 200
        assert response.json()["configured"] is False

    def test_get_openai_status_configured(self, client):
        """Test OpenAI status when configured."""
        session_id = "test_session_123"
        sessions[session_id] = {
            "access_token": "test_token",
            "openai_api_key": "sk-test-key",
            "expires_at": 9999999999,
        }
        response = client.get("/api/config/openai/status", cookies={"session_id": session_id})
        assert response.status_code == 200
        assert response.json()["configured"] is True

    def test_get_openai_status_no_session(self, client):
        """Test OpenAI status when no session (line 255)."""
        response = client.get("/api/config/openai/status")
        assert response.status_code == 200
        assert response.json()["configured"] is False


class TestPlaylistGeneration:
    """Tests for playlist generation endpoint."""

    @pytest.fixture
    def authenticated_session(self):
        """Create an authenticated session with OpenAI key."""
        session_id = "test_session_123"
        sessions[session_id] = {
            "access_token": "test_token",
            "openai_api_key": "sk-test-key",
            "expires_at": 9999999999,
        }
        return session_id

    def test_generate_playlist_not_authenticated(self, client):
        """Test playlist generation when not authenticated."""
        response = client.post(
            "/api/playlist/generate",
            json={"mode": "focus", "duration_minutes": 60},
        )
        assert response.status_code == 401

    def test_generate_playlist_no_openai_key(self, client, authenticated_session):
        """Test playlist generation without OpenAI key."""
        sessions[authenticated_session]["openai_api_key"] = None
        response = client.post(
            "/api/playlist/generate",
            json={"mode": "focus", "duration_minutes": 60},
            cookies={"session_id": authenticated_session},
        )
        assert response.status_code == 400
        assert "OpenAI API key" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_playlist_success(self, client, authenticated_session, mock_openai_key):
        """Test successful playlist generation."""
        # Mock the supervisor to return a result
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[
                TrackMetadata(
                    spotify_id="test1",
                    spotify_uri="spotify:track:test1",
                    name="Test Track",
                    artist="Test Artist",
                    bpm=130.0,
                    source="spotify_features",
                )
            ],
            total_duration_ms=180000,
            verification_summary={"approved": 1, "rejected": 0},
        )

        with patch("brain_radio.api.main.SupervisorAgent") as mock_supervisor_class:
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            response = client.post(
                "/api/playlist/generate",
                json={"mode": "focus", "duration_minutes": 60, "genre": "Techno"},
                cookies={"session_id": authenticated_session},
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["tracks"]) == 1
            assert data["tracks"][0]["name"] == "Test Track"

    @pytest.mark.asyncio
    async def test_generate_playlist_invalid_api_key(self, client, authenticated_session):
        """Test playlist generation with invalid OpenAI key."""
        with patch("brain_radio.api.main.SupervisorAgent") as mock_supervisor_class:
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(
                side_effect=Exception("Invalid api_key")
            )
            mock_supervisor_class.return_value = mock_supervisor

            response = client.post(
                "/api/playlist/generate",
                json={"mode": "focus", "duration_minutes": 60},
                cookies={"session_id": authenticated_session},
            )
            assert response.status_code == 401
            assert "Invalid OpenAI API key" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_playlist_general_error(self, client, authenticated_session, mock_openai_key):
        """Test playlist generation with general error."""
        with patch("brain_radio.api.main.SupervisorAgent") as mock_supervisor_class:
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(side_effect=Exception("General error"))
            mock_supervisor_class.return_value = mock_supervisor

            response = client.post(
                "/api/playlist/generate",
                json={"mode": "focus", "duration_minutes": 60},
                cookies={"session_id": authenticated_session},
            )
            assert response.status_code == 500
            assert "Failed to generate playlist" in response.json()["detail"]


class TestOAuthCallback:
    """Tests for OAuth callback endpoint."""

    def test_callback_with_error(self, client):
        """Test callback with OAuth error."""
        response = client.get("/api/auth/callback?error=access_denied")
        assert response.status_code == 400
        assert "OAuth error" in response.json()["detail"]

    def test_callback_missing_code(self, client):
        """Test callback without code parameter."""
        response = client.get("/api/auth/callback?state=test_state")
        assert response.status_code == 400
        assert "Missing code" in response.json()["detail"]

    def test_callback_missing_state(self, client):
        """Test callback without state parameter."""
        response = client.get("/api/auth/callback?code=test_code")
        assert response.status_code == 400
        assert "Missing code" in response.json()["detail"]

    def test_callback_invalid_state(self, client):
        """Test callback with invalid state."""
        response = client.get(
            "/api/auth/callback?code=test_code&state=invalid_state",
            cookies={"oauth_state": "different_state"},
        )
        assert response.status_code == 400
        assert "Invalid state" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_callback_token_exchange_success(self, client):
        """Test successful OAuth callback with token exchange."""
        # Mock httpx to return successful token exchange and user info
        mock_token_response = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
        }
        mock_user_response = {
            "id": "test_user_id",
            "product": "premium",
        }

        # Create a proper async context manager mock
        mock_client = AsyncMock()
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = mock_token_response

        mock_user_resp = MagicMock()
        mock_user_resp.status_code = 200
        mock_user_resp.json.return_value = mock_user_response

        # Set up the mock to return different responses for post and get
        async def post_side_effect(*args, **kwargs):
            return mock_token_resp

        async def get_side_effect(*args, **kwargs):
            return mock_user_resp

        mock_client.post = AsyncMock(side_effect=post_side_effect)
        mock_client.get = AsyncMock(side_effect=get_side_effect)

        with patch("brain_radio.api.main.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            # Set up OAuth state cookie
            state = "test_state_123"
            response = client.get(
                f"/api/auth/callback?code=test_code&state={state}",
                cookies={"oauth_state": state},
            )

            # Should redirect to frontend
            assert response.status_code == 307
            # Session should be created
            assert len(sessions) == 1
            session_id = list(sessions.keys())[0]
            assert sessions[session_id]["access_token"] == "test_access_token"
            assert sessions[session_id]["user_id"] == "test_user_id"
            assert sessions[session_id]["is_premium"] is True

    @pytest.mark.asyncio
    async def test_callback_token_exchange_failure(self, client):
        """Test OAuth callback when token exchange fails."""
        mock_client = AsyncMock()
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 400
        mock_token_resp.text = "Invalid code"

        mock_client.post = AsyncMock(return_value=mock_token_resp)

        with patch("brain_radio.api.main.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            state = "test_state_123"
            response = client.get(
                f"/api/auth/callback?code=invalid_code&state={state}",
                cookies={"oauth_state": state},
            )

            assert response.status_code == 400
            assert "Token exchange failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_callback_user_info_failure(self, client):
        """Test OAuth callback when user info fetch fails."""
        mock_token_response = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
        }

        mock_client = AsyncMock()
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = mock_token_response

        mock_user_resp = MagicMock()
        mock_user_resp.status_code = 401

        async def post_side_effect(*args, **kwargs):
            return mock_token_resp

        async def get_side_effect(*args, **kwargs):
            return mock_user_resp

        mock_client.post = AsyncMock(side_effect=post_side_effect)
        mock_client.get = AsyncMock(side_effect=get_side_effect)

        with patch("brain_radio.api.main.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            state = "test_state_123"
            response = client.get(
                f"/api/auth/callback?code=test_code&state={state}",
                cookies={"oauth_state": state},
            )

            assert response.status_code == 400
            assert "Failed to fetch user info" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_token_refresh(self, client):
        """Test token refresh when expired."""
        import time

        session_id = "test_session_123"
        sessions[session_id] = {
            "access_token": "old_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() - 100,  # Expired
        }

        mock_refresh_response = {
            "access_token": "new_access_token",
            "expires_in": 3600,
        }

        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_refresh_response

        mock_client.post = AsyncMock(return_value=mock_resp)

        with patch("brain_radio.api.main.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            response = client.get("/api/auth/token", cookies={"session_id": session_id})

            assert response.status_code == 200
            assert response.json()["access_token"] == "new_access_token"
            assert sessions[session_id]["access_token"] == "new_access_token"

    @pytest.mark.asyncio
    async def test_get_token_refresh_failure(self, client):
        """Test token refresh failure."""
        import time

        session_id = "test_session_123"
        sessions[session_id] = {
            "access_token": "old_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time.time() - 100,  # Expired
        }

        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 401

        mock_client.post = AsyncMock(return_value=mock_resp)

        with patch("brain_radio.api.main.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            response = client.get("/api/auth/token", cookies={"session_id": session_id})

            assert response.status_code == 401
            assert "Failed to refresh token" in response.json()["detail"]

    def test_get_token_expired_no_refresh_token(self, client):
        """Test token retrieval when expired and no refresh token."""
        import time

        session_id = "test_session_123"
        sessions[session_id] = {
            "access_token": "old_token",
            "expires_at": time.time() - 100,  # Expired, no refresh_token
        }

        response = client.get("/api/auth/token", cookies={"session_id": session_id})

        assert response.status_code == 401
        assert "Session expired" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_token_refresh_with_new_refresh_token(self, client):
        """Test token refresh when new refresh token is provided."""
        import time

        session_id = "test_session_123"
        sessions[session_id] = {
            "access_token": "old_token",
            "refresh_token": "old_refresh_token",
            "expires_at": time.time() - 100,
        }

        mock_refresh_response = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
        }

        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_refresh_response

        mock_client.post = AsyncMock(return_value=mock_resp)

        with patch("brain_radio.api.main.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            response = client.get("/api/auth/token", cookies={"session_id": session_id})

            assert response.status_code == 200
            assert sessions[session_id]["refresh_token"] == "new_refresh_token"

