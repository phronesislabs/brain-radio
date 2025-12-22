# Product Requirements Document: Brain-Radio (Spotify Edition)

## 1. Executive Summary

Brain-Radio is a Spotify-powered application that generates and plays “Functional Music” experiences (Focus, Relax, Sleep, Meditation) using the user’s own taste (artists/genres), while enforcing strict protocol constraints (e.g., Focus = low-vocals, steady rhythm).

The MVP is a **web app** that uses **Spotify OAuth** and the **Spotify Web Playback SDK** to play music in the browser (Spotify Premium required for in-browser playback). All music and metadata come from Spotify; Brain-Radio does not host or generate audio.

Because Spotify data is imperfect for “no vocals” and version accuracy (live/remaster/feat.), Brain-Radio uses a **hybrid verification** model:

- Prefer Spotify’s audio features/metadata when available (tempo/energy/speechiness/instrumentalness, explicit, etc.).
- Fall back to external verification (web/DB sources) when Spotify features are missing/insufficient for protocol enforcement.
- Enforce **zero-hallucination identity matching** so the Spotify URI added/played is the exact track that was verified.

## 2. Core Features

### 2.1 The "Protocol" Engine

**Requirement:** The system must support predefined "Neuro-Protocols":

- **Focus (Deep Work):** High consistency, 120-140 BPM, specific genres (Techno, Baroque, Post-Rock), strictly NO vocals.
- **Relax (Decompress):** 60-90 BPM, Major keys, acoustic textures.
- **Sleep (Delta):** <60 BPM, drone/ambient, no sudden transients.
- **Meditation (Mindfulness):** Low energy, slow tempo, repetitive/cyclic elements (ambient/drones/nature), avoid guided speech by default.

**Protocol inputs** (minimum):

- Mode (`focus|relax|sleep|meditation`)
- Optional user constraints (genre(s), seed artists, “avoid live/remaster”, duration/session length)

**Protocol outputs**:

- A machine-readable constraint set (ranges/thresholds + hard bans) used for filtering and verification.

### 2.2 The "Ghost" Research Pipeline

**Requirement:** Because protocol enforcement requires high precision (especially “no vocals” and avoiding disruptive versions), the system must implement a hybrid validation pipeline:

1. **Generate Candidates:** Propose candidate tracks using mode + user taste + safe heuristics (avoid “Live”, “Remaster”, “feat.” for Focus/Sleep).
2. **Resolve Identity (Spotify):** For each candidate, resolve to a specific Spotify track ID/URI (with album/artist disambiguation).
3. **Verify Metrics (Hybrid):**
   - **Primary:** Spotify audio features + Spotify metadata (explicit, duration, preview availability, popularity) when available.
   - **Fallback:** external sources (e.g., Tunebat/MusicBrainz/web research) for tempo/instrumentation, when Spotify data is missing or insufficient.
4. **Filter + Explain:** Strictly enforce protocol constraints; for every rejection, return a structured reason (e.g., “contains vocals”, “tempo out of range”, “live version”, “insufficient confidence”).
5. **Identity Lock (“Zero-Hallucination”):** Only play/add the exact Spotify URI that was verified; never “swap” versions later.

### 2.3 Spotify Integration

**Requirement:**

- **Auth:** Spotify OAuth 2.0 Authorization Code flow (PKCE supported). Access + refresh token lifecycle must be handled.
- **Playback:** Use Spotify Web Playback SDK to create a browser “device” and control playback (play/pause/skip).
- **Catalog + Features:** Use Spotify Web API for track search, metadata, recommendations, and audio features where available.
- **Output options:**
  - **Temporary Queue (default MVP):** play a generated list of Spotify URIs without creating a playlist.
  - **Playlist Materialization (optional):** create/update mode playlists (e.g., `Brain-Radio: Focus`) for persistence.
- **Premium handling:** If the user is not Premium, the system must still allow playlist creation but show a clear message that in-browser playback requires Premium.
- **Zero-Hallucination:** The system must ensure the Spotify URI played/added is the exact track verified by the pipeline.

### 2.4 Functional Effectiveness Engine (Beyond “A Focus Playlist”)

**Requirement:** Brain-Radio must deliver a *Brain.fm-like* **non-distracting focus experience** using **Spotify-only** tracks by combining strict protocol constraints with **measurable distraction/stability proxies** and a **closed-loop personalization** system.

#### 2.4.1 Distraction Proxy Model (Spotify-first)

For Focus mode, every candidate track must be assigned a `distraction_score` with an auditable explanation derived from Spotify data:

- **Hard bans (always reject)**:
  - Lyrics/vocals (e.g., high `speechiness` or low `instrumentalness`, or external verification indicates vocals)
  - Disruptive versions/metadata: `live`, `remaster`, `edit`, `radio edit`, `feat.` (mode-dependent; Focus is strict)
  - Explicit content (configurable; default reject for Focus)
- **Soft penalties / ranking features**:
  - `speechiness` (lower is better), `instrumentalness` (higher is better)
  - `energy` / `loudness` (avoid high-intensity for Focus default)
  - `valence` (avoid extremes; keep “neutral” by default)
  - `tempo` proximity to the Focus target band

All accept/reject decisions must record **the exact Spotify track ID/URI** and the **features/metadata** used.

#### 2.4.2 Stability Constraints (Minimize “Surprise”)

Focus mode must prefer tracks that are stable and low-surprise over time (the “backgroundability” property):

- **If Spotify Audio Analysis is available**: enforce constraints on section/segment variability (e.g., limit abrupt loudness changes, excessive section changes, or strong dynamic swings).
- **If Audio Analysis is unavailable**: fall back to conservative heuristics derived from audio features + metadata and reject when confidence is insufficient.

#### 2.4.3 Closed-loop Personalization (Within Protocol)

Brain-Radio must personalize without breaking protocol constraints by using implicit/explicit feedback:

- **Signals**: early-skip rate (e.g., skip within first N seconds), repeated skips, saves/likes, “session rating,” return frequency.
- **Policy**: explore/exploit (bandit-style) **only inside** Focus constraints; never “learn” into vocals or disruptive versions.
- **Auditability**: store which signals caused the system to down-rank or ban a track (or a track cluster) and record the before/after decision rationale.

#### 2.4.4 Baselines & Evaluation (No Efficacy Claims)

Brain-Radio should not claim medical/scientific efficacy. Instead, it must be evaluated against baselines using behavioral proxies:

- **Baselines**: a “generic focus playlist” fixture (and/or a simple heuristic playlist) for offline tests and dry runs.
- **Metrics**: early-skip rate reduction, longer average uninterrupted listening, improved session satisfaction ratings (self-report), higher repeat usage.

#### 2.4.5 Explicit Non-Goal (Spotify Constraint)

Brain.fm is publicly associated with proprietary modulation/entrainment techniques. **Brain-Radio will not modify Spotify streams** (no amplitude modulation, no DSP on the audio). The product differentiator is: **verification + identity lock + distraction/stability scoring + feedback-driven personalization**.

## 3. Technical Stack

- **Frontend:** TypeScript + React (or similar), integrates Spotify Web Playback SDK, renders mode selection + player UI.
- **Backend:** Python 3.12 (recommended) with a minimal HTTP API for:
  - OAuth callback + token exchange/refresh
  - Session storage and token security
  - Curation/verification endpoints (including optional external research tools)
  - Optional proxy to Spotify APIs to avoid exposing tokens broadly
- **Agent Orchestration:** LangChain / LangGraph (optional but supported) for the curation + verification pipeline.
- **Validation:** `pydantic` for strict schemas (requests, responses, and audit logs).
- **Research tools (fallback):** `tavily-python` or `duckduckgo-search` (or similar) only when Spotify data is insufficient.
- **Deployment:** Docker + Docker Compose for consistent local/dev/prod setup.

## 4. User Stories

- "As a developer, I want to select Focus for 2 hours and get a queue that matches my taste (e.g., Aphex Twin) while ensuring tracks are steady and instrumental (or low-vocal) enough for deep work."
- "As a user, I want the system to avoid 'Live' or 'Remastered' versions that might have applause or weird mixing, disrupting my flow."
- "As a user, I want to log in once and not be forced to re-auth every hour; playback should keep working via refresh tokens."
- "As a non-Premium user, I want Brain-Radio to still generate playlists even if it can’t play them in-browser."

## 5. Constraints

- **API Limits:** Agents must respect Spotify Rate Limits.
- **Latency:** Curation/verification takes time. The system should stream progress (queue tracks as they’re approved) rather than waiting to build the entire list.
- **Compliance:** No non-Spotify audio sources; no downloading/recording; Spotify attribution/branding when displaying Spotify content.
- **Identity correctness:** Avoid version mismatches (live/remaster/feat.) and ensure verified track identity is preserved end-to-end.
