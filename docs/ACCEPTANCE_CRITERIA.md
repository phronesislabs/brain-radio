# Acceptance Criteria & Testing Strategy

## 0. Test Strategy Notes (Important)

- **No real Spotify credentials in CI by default:** unit tests must run fully offline with mocks/fixtures.
- **Live integration tests are opt-in:** if `SPOTIFY_LIVE_TESTS=1` (or similar) and valid credentials exist, run a small suite that hits Spotify + Web Playback SDK in a controlled way.
- **Auditability:** every accept/reject decision must include a reason and the final Spotify track ID/URI used downstream.

## 1. The "Silence" Test (Focus Protocol)

**Goal:** Ensure Focus playback/queues are truly instrumental (or sufficiently low-vocal) per protocol, using the hybrid verifier.

- **Test:** `test_focus_protocol_rejects_vocals`
- **Scenario:** Feed the Researcher (Hybrid Verifier) a list of candidates including known vocal tracks (e.g., "Bohemian Rhapsody") and known instrumental tracks (e.g., "Tycho - Awake").
- **Pass Criteria:**
  - Must reject "Bohemian Rhapsody" with reason including **Contains Vocals** (or “speechiness too high”).
  - Must accept "Awake".
  - Must record which method was used: `spotify_features` or `external_fallback`.

## 2. The "Tempo" Check (Metric Validation)

**Goal:** Verify hybrid BPM retrieval prefers Spotify audio features when available and falls back when needed.

- **Test:** `test_bpm_retrieval_accuracy`
- **Scenario:** Ask Researcher to verify BPM for "Sandstorm by Darude".
- **Pass Criteria:**
  - Returns BPM ~136 (tolerance +/- 5 BPM).
  - If Spotify audio features are available, the verifier must prefer them and annotate `source=spotify_features`.
  - If Spotify audio features are unavailable, it must fall back to external verification and annotate `source=external_fallback`.

## 3. The "Vibe" Alignment

**Goal:** Ensure user taste is respected.

- **Test:** `test_genre_constraint`
- **Scenario:** User requests "Focus" but specifies "Genre: Jazz".
- **Pass Criteria:** Resulting playlist must contain tracks that are BOTH Jazz AND comply with Focus rules (Instrumental, steady rhythm). It should NOT return high-energy Techno.

## 3.1 The "Not Just a Playlist" Tests (Focus Effectiveness Proxies)

**Goal:** Ensure Focus results are *non-distracting and stable* over time, beyond simply “instrumental.”

- **Test:** `test_focus_distraction_score_filters_attention_grabbing_tracks`
- **Scenario:** Provide the scorer/verifier fixtures for tracks that are instrumental-but-distracting, e.g.:
  - high `speechiness` or low `instrumentalness`
  - metadata suggests disruptive versions (`Live`, `Remaster`, `Edit`, `Radio Edit`, `feat.`)
  - high `energy` / high `loudness` (configurable, but Focus default should be conservative)
- **Pass Criteria:**
  - Must reject candidates that violate hard bans with explicit reasons (e.g., **Contains Vocals**, **Disruptive Version**, **Explicit**).
  - Must compute and record a `distraction_score` (even for accepted tracks) with an auditable feature breakdown.
  - Must include the exact final Spotify track ID/URI in the decision record.

- **Test:** `test_focus_stability_constraints`
- **Scenario:** Provide fixtures including “stable” and “unstable” tracks. If Spotify Audio Analysis is present in fixtures, include:
  - high section-change density (too many sections per minute)
  - large loudness swings across sections/segments
  - abrupt dynamic shifts
  Otherwise include precomputed fixture flags (e.g., `high_dynamics_variance=True`) to keep unit tests offline.
- **Pass Criteria:**
  - Must reject “unstable” tracks with reason including **Unstable / High Surprise** (or equivalent).
  - Must accept “stable” tracks when all other Focus constraints pass.
  - Must record which data source was used (`spotify_audio_analysis` vs `heuristic_fallback`).

- **Test:** `test_closed_loop_personalization_respects_protocol`
- **Scenario:** Simulate a session where the user repeatedly early-skips a subset of *otherwise-approved* Focus tracks (e.g., skip within first N seconds). Then request a refreshed queue for the same mode/user.
- **Pass Criteria:**
  - Next queue must down-rank or exclude the repeatedly early-skipped items (or their cluster) while still satisfying Focus hard constraints (no “learning into vocals”).
  - Must record which feedback signal(s) caused each down-rank/exclusion (e.g., `early_skip_rate`), plus a before/after rationale.
  - Must remain auditable: every played/queued URI must be one that passed verification + scoring.

## 4. Authentication & Session Management

**Goal:** Ensure Spotify OAuth and refresh behavior is correct and user-friendly.

- **Test:** `test_oauth_requires_login`
- **Scenario:** Start app/API with no session/token.
- **Pass Criteria:** App prompts for Spotify login; no playback is attempted; API returns a clear unauthenticated response.

- **Test:** `test_token_refresh_keeps_session_alive`
- **Scenario:** Simulate an expired access token with a valid refresh token/session.
- **Pass Criteria:** System refreshes automatically and continues operation without forcing re-login.

- **Test:** `test_required_scopes_present`
- **Scenario:** Provide a token missing required playback scopes.
- **Pass Criteria:** System detects missing scopes and surfaces a clear remediation message (no crash, no silent failure).

## 5. Web Playback SDK (Device + Playback)

**Goal:** Ensure in-browser playback works via Spotify Web Playback SDK when Premium is available.

- **Test:** `test_web_playback_device_ready`
- **Scenario:** Initialize the player with a valid token.
- **Pass Criteria:** Player reaches Ready state and yields a device ID (or an explicit handled error).

- **Test:** `test_playback_starts_in_browser`
- **Scenario:** Select a mode and attempt playback.
- **Pass Criteria:** Playback starts on the SDK device; UI state reflects playing track metadata from Spotify.

- **Test:** `test_mode_switch_clears_old_queue_and_starts_new`
- **Scenario:** Start Focus, then switch to Relax while music is playing.
- **Pass Criteria:** Old queue/context is cleared/stopped; new mode begins promptly; UI updates accordingly.

- **Test:** `test_non_premium_degrades_gracefully`
- **Scenario:** Use a non-Premium account token (or simulated error).
- **Pass Criteria:** Playlist generation still works; app clearly indicates Premium is required for in-browser playback.

## 6. System Integration (Dry Run)

**Goal:** Validate end-to-end orchestration without requiring real playback.

- **Test:** `test_end_to_end_mode_generation_dry_run`
- **Scenario:** Run full pipeline in `--dry-run` mode (no playback), with mocked Spotify + research responses.
- **Pass Criteria:**
  1. Neuro-Composer produces strict constraints.
  2. Catalog Agent resolves 3 candidate Spotify track URIs/IDs (from fixtures).
  3. Researcher approves/rejects with reasons and confidence.
  4. Output JSON matches strict Pydantic schema and includes the final Spotify URIs for approved tracks.

## 7. Compliance & Non-Spotify Audio Guardrail

**Goal:** Ensure Brain-Radio never plays or ships non-Spotify audio.

- **Test:** `test_no_non_spotify_audio_assets_in_repo`
- **Scenario:** Scan repo for audio assets and Brain.fm references.
- **Pass Criteria:** No local audio assets and no Brain.fm playback integrations exist; app refuses to play without Spotify auth.

## 8. Docker & Deployment Readiness

**Goal:** Ensure the system can run in Docker with correct configuration boundaries.

- **Test:** `test_docker_compose_boot_and_health`
- **Scenario:** Bring up the stack with required environment variables (dummy for unit tests).
- **Pass Criteria:** Containers start, health endpoint responds, and missing env vars produce clear errors (no undefined behavior).
