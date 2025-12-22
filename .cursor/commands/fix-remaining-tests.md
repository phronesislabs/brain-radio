# Fix Remaining Test Failures

## Context

The codebase currently has **98.8% test coverage** (exceeding the 95% target), but **15 tests are failing**. All failing tests are related to CLI execution and API OAuth flow mocking. The goal is to get all tests passing while maintaining the high coverage.

## Current Status

- **Passing tests**: 105
- **Failing tests**: 15
- **Coverage**: 98.8%

## Failing Tests

### API Tests (2 failures)

1. **`tests/test_api.py::TestAuthEndpoints::test_login_with_spotify_config`**
   - **Issue**: Test expects a 307 redirect to Spotify OAuth, but gets 404 or 500
   - **Root cause**: The test needs to properly mock or set environment variables for Spotify OAuth configuration
   - **Location**: `tests/test_api.py` around line 68-78
   - **Related code**: `src/brain_radio/api/main.py` - `/api/auth/login` endpoint (around line 70-85)

2. **`tests/test_api.py::TestOAuthCallback::test_callback_token_exchange_success`**
   - **Issue**: Test expects 307 redirect after successful token exchange, but gets 200
   - **Root cause**: Async HTTP client mocking (`httpx.AsyncClient`) is not working correctly
   - **Location**: `tests/test_api.py` around line 280-344
   - **Related code**: `src/brain_radio/api/main.py` - `/api/auth/callback` endpoint (around line 90-150)

### CLI Tests (13 failures)

All CLI tests are failing due to issues with mocking `asyncio.run()` in the CLI execution path. The CLI uses `asyncio.run(supervisor.generate_playlist(request))` which is difficult to mock properly.

**Failing tests:**
- `tests/test_cli.py::TestCLIGenerate::test_generate_valid_mode_default`
- `tests/test_cli.py::TestCLIGenerate::test_generate_with_genre`
- `tests/test_cli.py::TestCLIGenerate::test_generate_with_duration`
- `tests/test_cli.py::TestCLIGenerate::test_generate_dry_run`
- `tests/test_cli.py::TestCLIGenerate::test_generate_all_modes`
- `tests/test_cli.py::TestCLIGenerate::test_generate_with_multiple_tracks`
- `tests/test_cli.py::TestCLIGenerate::test_generate_shows_verification_summary`
- `tests/test_cli.py::TestCLIExecution::test_generate_with_all_parameters`
- `tests/test_cli.py::TestCLIExecution::test_generate_dry_run_mode`
- `tests/test_cli.py::TestCLIExecution::test_generate_with_empty_playlist`
- `tests/test_cli_execution.py::TestCLIExecutionPaths::test_generate_with_genre_echo`
- `tests/test_cli_execution.py::TestCLIExecutionPaths::test_generate_dry_run_echo`
- `tests/test_cli_execution.py::TestCLIExecutionPaths::test_generate_track_listing`
- `tests/test_cli_execution.py::TestCLIExecutionPaths::test_generate_more_than_10_tracks`

**Root cause**: The CLI code in `src/brain_radio/cli.py` calls `asyncio.run(supervisor.generate_playlist(request))` at line 61. Tests are trying to mock `asyncio.run` but the mocking isn't working correctly, causing:
- Exit code 2 (typer argument parsing error) instead of 0
- Tests that check for specific output in `result.stdout` fail because the command doesn't execute properly

## Technical Details

### CLI Structure

The CLI function `generate()` in `src/brain_radio/cli.py`:
1. Validates mode (lines 40-44)
2. Creates `PlaylistRequest` (line 46)
3. Echoes configuration (lines 48-53)
4. Initializes `SupervisorAgent` and `ChatOpenAI` (lines 58-59)
5. Calls `asyncio.run(supervisor.generate_playlist(request))` (line 61)
6. Echoes results (lines 63-74)

### API Structure

The API OAuth endpoints in `src/brain_radio/api/main.py`:
- `/api/auth/login` (line ~70): Redirects to Spotify OAuth if `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are set
- `/api/auth/callback` (line ~90): Handles OAuth callback, exchanges code for token using `httpx.AsyncClient`

## Requirements

1. **Fix all 15 failing tests** to pass
2. **Maintain 95%+ coverage** (currently 98.8%)
3. **Follow existing test patterns** - don't rewrite tests unnecessarily
4. **Use proper mocking** - ensure mocks work correctly with async code

## Suggested Approach

### For API Tests

1. **`test_login_with_spotify_config`**:
   - Option A: Use `monkeypatch` to set environment variables before importing/creating the test client
   - Option B: Mock the constants directly: `patch("brain_radio.api.main.SPOTIFY_CLIENT_ID", "test_id")`
   - Option C: Create a fixture that sets up a test client with proper environment

2. **`test_callback_token_exchange_success`**:
   - Fix the `httpx.AsyncClient` async context manager mocking
   - Ensure `__aenter__` and `__aexit__` are properly mocked as async functions
   - Verify the mock client's `post()` and `get()` methods return the expected responses

### For CLI Tests

1. **Option A: Mock `asyncio.run` correctly**
   - Ensure `mock_asyncio.run.return_value = mock_result` is set before the command runs
   - Verify the mock is applied at the right level (module-level patch)

2. **Option B: Refactor CLI to be more testable**
   - Extract the async execution into a separate function that can be mocked more easily
   - Or use dependency injection for `asyncio.run`

3. **Option C: Use integration-style testing**
   - Actually run the async code but mock the `SupervisorAgent.generate_playlist` method
   - This might be more reliable but slower

## Testing

Run tests with:
```bash
docker-compose --profile test run --rm test pytest -v
```

Check coverage with:
```bash
docker-compose --profile test run --rm test pytest --cov=src/brain_radio --cov-report=term-missing --cov-report=xml:coverage/coverage.xml
```

## Success Criteria

- All 15 tests pass
- Coverage remains ≥ 95%
- No new test failures introduced
- Code follows existing patterns and style

## Notes

- The codebase uses `pytest`, `unittest.mock`, and `typer.testing.CliRunner`
- Tests run in Docker containers - use `docker-compose --profile test run --rm test` to run tests
- The project uses `ruff` for linting - ensure code passes linting
- See existing passing tests for patterns (e.g., `tests/test_cli.py::TestCLIGenerate::test_generate_invalid_mode` works correctly)

