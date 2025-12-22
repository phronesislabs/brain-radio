# Brain-Radio

Autonomous agentic system for generating scientifically-tuned Spotify playlists using the user's own music taste.

## Overview

Brain-Radio replaces "Brain.fm" by generating functional music experiences (Focus, Relax, Sleep, Meditation) using Spotify tracks. The system uses autonomous coding agents to verify track metadata (BPM, Key, Instrumental status) through web research, since Spotify's Audio Features API has been deprecated.

## Architecture

Brain-Radio uses a **Hierarchical Agent Swarm** with the following agents:

- **Supervisor Agent**: Orchestrates the workflow using LangGraph
- **Neuro-Composer Agent**: Translates cognitive goals into strict constraints (e.g., Focus = 120-140 BPM, no vocals)
- **Researcher Agent**: Verifies tracks using web research (DuckDuckGo) when Spotify data is unavailable
- **Spotify Catalog Agent**: Resolves tracks to exact Spotify URIs (TODO: to be implemented)

## Installation

### Docker (Recommended)

See [README_DOCKER.md](README_DOCKER.md) for full Docker setup instructions.

```bash
# Set environment variables for Docker Compose
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
export SPOTIFY_REDIRECT_URI="http://localhost:8000/api/auth/callback"

# Run with Docker Compose
docker-compose up --build
```

### Local Development

```bash
# Install dependencies
pip install -e ".[dev]"
cd frontend && npm install

# Set environment variables
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
export SPOTIFY_REDIRECT_URI="http://localhost:8000/api/auth/callback"

# Run backend
uvicorn src.brain_radio.api.main:app --reload

# Run frontend (in another terminal)
cd frontend && npm run dev
```

**Note:** The application no longer requires a `.env` file. Spotify OAuth credentials are set via environment variables, and the OpenAI API key is entered through the web UI.

## Usage

### CLI

```bash
# Generate a Focus playlist
brain-radio generate --mode focus --genre Techno --duration 120

# Generate a Relax playlist
brain-radio generate --mode relax --genre Jazz

# Dry run (no Spotify API calls)
brain-radio generate --mode focus --dry-run
```

### Modes

- **Focus**: 120-140 BPM, no vocals, avoids live/remaster/feat versions
- **Relax**: 60-90 BPM, Major keys, allows vocals
- **Sleep**: <60 BPM, ambient/drone, no sudden transients
- **Meditation**: <70 BPM, low energy, no vocals

## Development

**Important**: All code execution, including tests, must run inside Docker containers. See [README_DOCKER_TESTS.md](README_DOCKER_TESTS.md) for details.

### Running Tests

```bash
# Run all tests in Docker
./scripts/test-docker.sh

# Run with coverage
./scripts/test-docker.sh dev pytest --cov=src/brain_radio --cov-report=html

# Run specific test
./scripts/test-docker.sh dev pytest tests/test_researcher.py::test_focus_protocol_rejects_vocals -v
```

### Running Linting

```bash
# Run ruff in Docker
./scripts/run-docker.sh dev python -m ruff check .
./scripts/run-docker.sh dev python -m ruff format --check .
```

### Project Structure

```
brain-radio/
├── src/
│   └── brain_radio/
│       ├── agents/
│       │   ├── supervisor.py      # Supervisor Agent (LangGraph)
│       │   ├── researcher.py       # Researcher Agent (web research)
│       │   └── neuro_composer.py   # Neuro-Composer Agent
│       ├── models.py               # Pydantic models
│       └── cli.py                  # CLI interface
├── tests/
│   ├── test_researcher.py
│   ├── test_neuro_composer.py
│   ├── test_supervisor.py
│   └── ...
└── pyproject.toml
```

## Key Features

- **Web Research**: Uses DuckDuckGo to find BPM and track metadata when Spotify data is unavailable
- **Protocol Enforcement**: Strict constraints for each mode (BPM ranges, vocal bans, version filtering)
- **Distraction Scoring**: Computes distraction scores for Focus mode to filter attention-grabbing tracks
- **TDD**: Comprehensive test suite based on acceptance criteria

## Critical Rule

**Do not use `spotipy.audio_features()`** - it is deprecated. The Researcher agent must use web research to find track metadata.

## License

MIT

