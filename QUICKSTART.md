# Brain-Radio Quick Start Guide

## Project Structure

```
brain-radio/
├── src/
│   └── brain_radio/
│       ├── __init__.py
│       ├── models.py              # Pydantic models (Mode, TrackMetadata, etc.)
│       ├── cli.py                 # CLI interface with typer
│       └── agents/
│           ├── __init__.py
│           ├── supervisor.py     # Supervisor Agent (LangGraph orchestration)
│           ├── researcher.py      # Researcher Agent (web research for BPM/metadata)
│           └── neuro_composer.py  # Neuro-Composer Agent (protocol constraints)
├── tests/
│   ├── test_researcher.py         # Researcher agent tests
│   ├── test_neuro_composer.py     # Neuro-Composer tests
│   ├── test_supervisor.py         # Supervisor orchestration tests
│   ├── test_genre_constraint.py   # Genre constraint tests
│   ├── test_distraction_scoring.py # Distraction scoring tests
│   └── test_end_to_end.py         # End-to-end integration tests
├── pyproject.toml                 # Project configuration
├── README.md                      # Main documentation
└── QUICKSTART.md                  # This file
```

## Installation

```bash
# Install the package in development mode
uv pip install -e ".[dev]"

# Or install dependencies manually
uv pip install langgraph langchain langchain-openai langchain-community \
            pydantic typer duckduckgo-search httpx python-dotenv \
            pytest pytest-asyncio pytest-cov black ruff mypy
```

## Environment Setup

```bash
# Create .env file
cp .env.example .env

# Add your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" >> .env
```

## Running Tests

**All tests must run in Docker containers.** See [README_DOCKER_TESTS.md](README_DOCKER_TESTS.md) for details.

```bash
# Run all tests in Docker
./scripts/test-docker.sh

# Run specific test file
./scripts/test-docker.sh dev pytest tests/test_neuro_composer.py

# Run with coverage
./scripts/test-docker.sh dev pytest --cov=src/brain_radio --cov-report=html

# Run specific test
./scripts/test-docker.sh dev pytest tests/test_researcher.py::test_focus_protocol_rejects_vocals -v
```

## Using the CLI

```bash
# Generate a Focus playlist
brain-radio generate --mode focus --genre Techno --duration 120

# Generate a Relax playlist
brain-radio generate --mode relax --genre Jazz

# Dry run (no Spotify API calls)
brain-radio generate --mode focus --dry-run
```

## Key Components

### 1. Neuro-Composer Agent
- Translates cognitive goals into strict constraints
- Focus mode: 120-140 BPM, no vocals, avoids live/remaster/feat
- Located in `src/brain_radio/agents/neuro_composer.py`

### 2. Researcher Agent
- Verifies tracks using web research (DuckDuckGo)
- Finds BPM when Spotify data is unavailable
- Enforces protocol constraints
- Located in `src/brain_radio/agents/researcher.py`

### 3. Supervisor Agent
- Orchestrates workflow using LangGraph
- Manages state and routes tasks to worker agents
- Located in `src/brain_radio/agents/supervisor.py`

## Critical Implementation Notes

1. **No spotipy.audio_features()**: The Researcher agent uses web research instead
2. **Focus Protocol**: 120-140 BPM, strict no-vocals, avoids disruptive versions
3. **Web Research**: DuckDuckGo search for BPM/metadata when Spotify data unavailable
4. **TDD**: Tests written first/parallel based on ACCEPTANCE_CRITERIA.md

## Next Steps

1. **Implement Spotify Catalog Agent**: Currently mocked in `supervisor._generate_candidates()`
2. **Add Spotify OAuth**: Token management for real API calls
3. **Implement Playback Agent**: Web Playback SDK integration
4. **Add Distraction Scorer**: Enhanced scoring for Focus mode
5. **Add Calibration Agent**: Personalization based on user feedback

## Testing Strategy

- Unit tests run offline with mocks/fixtures
- No real Spotify credentials in CI by default
- Live integration tests opt-in via `SPOTIFY_LIVE_TESTS=1`
- All accept/reject decisions include auditable reasons

