# Code Review: Brain-Radio Codebase

**Review Date**: Generated automatically  
**Reviewer**: AI Code Review Assistant  
**Scope**: Full codebase review based on Clean Code principles

## Executive Summary

The codebase is generally well-structured and follows many Clean Code principles. However, there are several areas for improvement, particularly around:

1. **Magic Numbers**: Many hardcoded values should be named constants
2. **Function Length**: Some functions exceed the recommended 20-line guideline
3. **Code Duplication**: Several patterns are repeated and could be extracted
4. **Global State**: Session management uses global mutable state
5. **Type Safety**: TypeScript uses `any` types in some places
6. **Error Handling**: Some error handling could be more explicit

## Detailed Findings

### 1. Meaningful Names ✅ Mostly Good

**Strengths:**
- Function and class names are generally clear and intention-revealing
- No single-letter names except appropriate loop counters
- Consistent terminology throughout

**Issues Found:**

#### Issue 1.1: Magic Numbers (High Priority)
**Location**: Multiple files

**Problem**: Magic numbers throughout codebase reduce readability and maintainability.

**Examples:**
- `src/brain_radio/api/main.py:163`: `3600` (token expiry)
- `src/brain_radio/api/main.py:169`: `3600 * 24 * 7` (session duration)
- `src/brain_radio/api/main.py:92`: `600` (OAuth state expiry)
- `src/brain_radio/agents/researcher.py:155`: `0.5` (instrumentalness threshold)
- `src/brain_radio/agents/researcher.py:158`: `0.33` (speechiness threshold)
- `src/brain_radio/agents/researcher.py:129`: `0.7` (distraction score threshold)
- `src/brain_radio/agents/researcher.py:202`: `60`, `200` (BPM range)

**Recommendation**: Extract to named constants:

```python
# src/brain_radio/api/main.py
TOKEN_EXPIRY_SECONDS = 3600
SESSION_DURATION_SECONDS = 3600 * 24 * 7  # 7 days
OAUTH_STATE_EXPIRY_SECONDS = 600

# src/brain_radio/agents/researcher.py
INSTRUMENTALNESS_THRESHOLD = 0.5
SPEECHINESS_THRESHOLD = 0.33
DISTRACTION_SCORE_REJECTION_THRESHOLD = 0.7
MIN_BPM = 60
MAX_BPM = 200
```

**Priority**: High - Improves maintainability and readability

---

### 2. Functions ⚠️ Needs Improvement

**Issues Found:**

#### Issue 2.1: Long Functions (Medium Priority)

**Location**: `src/brain_radio/api/main.py:96-171` - `callback()` function (76 lines)

**Problem**: Function exceeds 20-line guideline and does multiple things:
1. Validates OAuth parameters
2. Exchanges code for tokens
3. Fetches user info
4. Creates session
5. Sets cookies and redirects

**Recommendation**: Extract into smaller functions:

```python
async def callback(...):
    """Handle Spotify OAuth callback."""
    _validate_oauth_callback(code, state, error, request)
    tokens = await _exchange_code_for_tokens(code)
    user_data = await _fetch_user_info(tokens["access_token"])
    session_id = _create_user_session(tokens, user_data)
    return _create_redirect_response(session_id)
```

**Priority**: Medium - Improves readability and testability

---

#### Issue 2.2: Long Function (Medium Priority)

**Location**: `src/brain_radio/agents/researcher.py:27-145` - `verify_track()` function (119 lines)

**Problem**: Function is very long and handles multiple verification concerns:
1. Hard ban checks (vocals, live, remaster, feat)
2. BPM verification
3. Energy verification
4. Distraction score calculation

**Recommendation**: Extract verification steps:

```python
async def verify_track(self, track: TrackMetadata, constraints: ProtocolConstraints) -> VerificationResult:
    """Verify a track against protocol constraints."""
    # Check hard bans first
    if hard_ban_result := self._check_hard_bans(track, constraints):
        return hard_ban_result
    
    # Verify BPM if required
    if bpm_result := await self._verify_bpm(track, constraints):
        if not bpm_result.approved:
            return bpm_result
    
    # Verify energy if required
    if energy_result := self._verify_energy(track, constraints):
        if not energy_result.approved:
            return energy_result
    
    # Calculate distraction score for Focus mode
    distraction_score = self._calculate_distraction_score_if_needed(track, constraints)
    
    return self._create_approval_result(track, distraction_score)
```

**Priority**: Medium - Improves maintainability

---

#### Issue 2.3: Code Duplication (Medium Priority)

**Location**: `src/brain_radio/api/main.py:123-126` and `189-192`

**Problem**: Base64 encoding logic is duplicated:

```python
# Appears twice:
credentials = base64.b64encode(
    f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
).decode()
auth_header = f"Basic {credentials}"
```

**Recommendation**: Extract to helper function:

```python
def _create_spotify_auth_header() -> str:
    """Create Basic auth header for Spotify API."""
    credentials = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    return f"Basic {credentials}"
```

**Priority**: Medium - Reduces duplication (DRY principle)

---

#### Issue 2.4: Switch Statement Pattern (Low Priority)

**Location**: `src/brain_radio/agents/neuro_composer.py:24-85`

**Problem**: Long if/elif chain for mode selection. Could use strategy pattern or dictionary mapping.

**Current**: 62 lines of if/elif statements

**Recommendation**: Consider using a strategy pattern or configuration dictionary:

```python
MODE_CONSTRAINTS: dict[Mode, Callable[[str | None], ProtocolConstraints]] = {
    Mode.FOCUS: _create_focus_constraints,
    Mode.RELAX: _create_relax_constraints,
    Mode.SLEEP: _create_sleep_constraints,
    Mode.MEDITATION: _create_meditation_constraints,
}

def compose_constraints(self, mode: Mode, genre: str | None = None) -> ProtocolConstraints:
    if mode not in MODE_CONSTRAINTS:
        raise ValueError(f"Unknown mode: {mode}")
    return MODE_CONSTRAINTS[mode](genre)
```

**Priority**: Low - Current code is readable, but could be more maintainable

---

### 3. Comments ✅ Good

**Strengths:**
- Minimal comments (code is mostly self-documenting)
- No commented-out code
- TODO comments include context

**Issues Found:**

#### Issue 3.1: TODO Comment (Low Priority)

**Location**: `src/brain_radio/agents/supervisor.py:111`

**Problem**: TODO comment without issue tracker reference:

```python
# TODO: This should use Spotify Catalog Agent to search for tracks.
```

**Recommendation**: Add issue reference or create issue:

```python
# TODO(#123): Implement Spotify Catalog Agent to search for tracks
```

**Priority**: Low - Documentation improvement

---

### 4. Formatting ✅ Good

**Strengths:**
- Consistent formatting
- Proper indentation
- Lines within reasonable length

**No issues found.**

---

### 5. Objects and Data Structures ⚠️ Needs Improvement

**Issues Found:**

#### Issue 5.1: Global Mutable State (High Priority)

**Location**: `src/brain_radio/api/main.py:47`

**Problem**: Global dictionary for session storage:

```python
sessions: dict[str, dict] = {}
```

**Issues:**
- Not thread-safe
- No cleanup mechanism
- Hard to test
- Violates encapsulation

**Recommendation**: Create a SessionManager class:

```python
class SessionManager:
    """Manages user sessions with automatic cleanup."""
    
    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._cleanup_interval = 3600  # 1 hour
    
    def create_session(self, user_data: dict, tokens: dict) -> str:
        """Create a new session and return session ID."""
        # Implementation
    
    def get_session(self, session_id: str) -> dict | None:
        """Get session by ID."""
        # Implementation
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        # Implementation

# Global instance (in production, use Redis or database)
session_manager = SessionManager()
```

**Priority**: High - Important for production readiness

---

### 6. Error Handling ⚠️ Needs Improvement

**Issues Found:**

#### Issue 6.1: Silent Error Handling (Medium Priority)

**Location**: `src/brain_radio/agents/researcher.py:181-184`

**Problem**: Exception is caught but silently ignored:

```python
except Exception as e:
    # Log error but continue (fallback will be used)
    pass
    return None
```

**Recommendation**: At minimum, log the error:

```python
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Error researching BPM for {track.name}: {e}")
    return None
```

**Priority**: Medium - Better observability

---

#### Issue 6.2: Generic Exception Handling (Medium Priority)

**Location**: `src/brain_radio/api/main.py:286`

**Problem**: Catching generic `Exception`:

```python
except Exception as e:
    error_msg = str(e)
    # ...
```

**Recommendation**: Catch specific exceptions:

```python
except (OpenAIError, ValueError, RuntimeError) as e:
    # Handle specific errors
except Exception as e:
    # Log unexpected errors
    logger.error(f"Unexpected error generating playlist: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Priority**: Medium - Better error handling

---

### 7. Boundaries ✅ Good

**Strengths:**
- Third-party APIs (Spotify, OpenAI) are used appropriately
- Pydantic models provide good boundaries

**No major issues found.**

---

### 8. Unit Tests ⚠️ Needs Review

**Note**: Test files were not fully reviewed, but structure looks good.

**Recommendations:**
- Ensure all functions have unit tests
- Test coverage should be ≥95% (as per project standards)
- Test error cases explicitly

---

### 9. Classes ✅ Good

**Strengths:**
- Classes are focused and have single responsibility
- Good use of Pydantic models for data structures

**No major issues found.**

---

### 10. SOLID Principles ⚠️ Minor Issues

**Issues Found:**

#### Issue 10.1: Single Responsibility (Low Priority)

**Location**: `frontend/src/App.tsx`

**Problem**: App component handles multiple concerns:
- Authentication state
- OpenAI key management
- Playlist generation
- Error handling
- UI rendering

**Recommendation**: Consider extracting custom hooks:

```typescript
// hooks/useAuth.ts
export function useAuth() {
  // Authentication logic
}

// hooks/useOpenAIKey.ts
export function useOpenAIKey() {
  // OpenAI key management
}

// hooks/usePlaylist.ts
export function usePlaylist() {
  // Playlist generation logic
}
```

**Priority**: Low - Current structure is acceptable for MVP

---

### 11. Type Safety ⚠️ Needs Improvement

**Issues Found:**

#### Issue 11.1: Use of `any` Type (Medium Priority)

**Location**: `frontend/src/components/SpotifyPlayer.tsx:19, 25`

**Problem**: Using `any` type reduces type safety:

```typescript
const [player, setPlayer] = useState<any>(null)
const playerRef = useRef<any>(null)
```

**Recommendation**: Create proper types for Spotify Player:

```typescript
interface SpotifyPlayerInstance {
  connect(): Promise<void>
  disconnect(): void
  pause(): Promise<void>
  nextTrack(): Promise<void>
  // ... other methods
}

const [player, setPlayer] = useState<SpotifyPlayerInstance | null>(null)
const playerRef = useRef<SpotifyPlayerInstance | null>(null)
```

**Priority**: Medium - Improves type safety

---

### 12. Code Smells ⚠️ Found Several

**Issues Found:**

#### Issue 12.1: Long Parameter Lists (Low Priority)

**Location**: `frontend/src/components/SpotifyPlayer.tsx:18`

**Problem**: Component receives multiple props:

```typescript
interface SpotifyPlayerProps {
  playlist: PlaylistResult
  isPremium: boolean
  mode: Mode
}
```

**Status**: ✅ Actually acceptable - 3 props is reasonable

---

#### Issue 12.2: Feature Envy (Low Priority)

**Location**: `src/brain_radio/api/main.py:174-213` - `get_token()` function

**Problem**: Function accesses session dictionary directly and manipulates it.

**Status**: ✅ Acceptable given current architecture, but would be better with SessionManager

---

## Summary of Recommendations

### High Priority
1. **Extract magic numbers to named constants** (Multiple files)
2. **Create SessionManager class** to replace global mutable state (`src/brain_radio/api/main.py`)

### Medium Priority
3. **Refactor long functions** (`callback`, `verify_track`)
4. **Extract duplicated code** (base64 encoding)
5. **Improve error handling** (logging, specific exceptions)
6. **Add TypeScript types** (replace `any` types)

### Low Priority
7. **Refactor switch-like logic** (neuro_composer mode selection)
8. **Extract React hooks** (App component)
9. **Add issue references to TODOs**

## Positive Observations

✅ **Good naming**: Functions and classes have clear, intention-revealing names  
✅ **Good structure**: Code is well-organized into logical modules  
✅ **Type hints**: Python code uses type hints appropriately  
✅ **Documentation**: Docstrings are present and helpful  
✅ **Error handling**: Generally uses exceptions appropriately  
✅ **Test structure**: Test files are well-organized  

## Next Steps

1. Address high-priority items first
2. Create issues/tickets for medium-priority items
3. Consider low-priority items during refactoring cycles
4. Run automated tools (ruff, mypy) to catch additional issues
5. Review test coverage to ensure ≥95%

## Automated Checks

Run these commands to catch additional issues:

```bash
# Python linting
./scripts/run-docker.sh dev python -m ruff check .

# Type checking (if mypy enabled)
./scripts/run-docker.sh dev python -m mypy src/

# Tests
./scripts/test-docker.sh dev
```

---

**Review Status**: ✅ Code is generally clean with room for improvement  
**Recommendation**: Address high-priority items before next major release

