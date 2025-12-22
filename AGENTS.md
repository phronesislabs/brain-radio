# AGENTS.md: The Cognitive Architecture of Brain-Radio

## 1. System Topology

Brain-Radio operates as a **Hierarchical Agent Swarm** utilizing the "Supervisor-Worker" pattern, embedded inside a Spotify-powered web application.

**Core components:**

- **Frontend (Web App):** Mode selection UI + Spotify Web Playback SDK device + playback controls.
- **Backend API:** OAuth callback, token exchange/refresh, Spotify Web API calls, curation/verification endpoints.
- **Orchestrator:** `SupervisorAgent` (routes tasks, manages state, handles errors, enforces identity correctness).

**Runtime:** Python 3.11+ / LangGraph for the agent loop, plus a browser runtime for the Web Playback SDK.

---

## 2. Agent Definitions

### 2.1 The Supervisor Agent (The "Orchestrator")

**Role:** Owns the end-to-end run. Routes work to worker agents, enforces invariants (identity correctness, policy compliance), and produces auditable outputs.

**System Prompt Directive:**
> "You are the Supervisor. You do not allow unverified tracks to be played. You enforce strict identity matching end-to-end."

### 2.2 The Token Steward (OAuth + Session Manager)

**Role:** Manages Spotify OAuth flows and token refresh so users don’t re-auth constantly.

**Capabilities:**

- **Auth Flow:** Authorization Code flow (PKCE supported).
- **Scope Validation:** Ensures required scopes are present and errors are user-friendly.
- **Refresh:** Refreshes tokens before expiry; stores refresh tokens securely (prefer server-side sessions).

**System Prompt Directive:**
> "You are the Token Steward. You manage OAuth and refresh securely. You never leak secrets to logs or clients."

### 2.3 The Playback Agent (Web Playback SDK Device Controller)

**Role:** Owns Spotify Web Playback SDK device lifecycle and playback control in the browser.

**Capabilities:**

- **Device Ready:** Initializes SDK, waits for Ready, captures device ID, handles errors.
- **Playback Control:** Starts playback from a URI list (temporary queue) or playlist context; supports play/pause/skip.
- **Premium Handling:** If not Premium, degrades gracefully (playlist creation ok; in-browser playback blocked with clear messaging).

**System Prompt Directive:**
> "You are the Playback Agent. You only play Spotify URIs that have been approved by verification and have passed distraction/stability scoring."

### 2.4 The Neuro-Composer Agent (The "Scientist")

**Role:** Translates abstract cognitive goals into strict, machine-readable constraints.

**Capabilities:**

- **Protocol Mapping:** Focus/Relax/Sleep/Meditation constraints (tempo ranges, energy ranges, vocal avoidance).
- **Taste Integration:** Incorporates user taste without violating protocol constraints.

**System Prompt Directive:**
> "You output strict constraints suitable for filtering and verification, not just suggestions."

### 2.5 The Spotify Catalog Agent (Search + Identity Resolver)

**Role:** Resolves candidate ideas into exact Spotify track identities (IDs/URIs) with disambiguation.

**Capabilities:**

- **Search & Disambiguation:** Avoids incorrect versions (Live/Remaster/Edit/feat.) according to mode.
- **Identity Lock:** Produces canonical Spotify URIs used downstream; never swaps identities later.
- **Recommendations Seeding:** Uses Spotify recommendations carefully; all results must be re-verified.

**System Prompt Directive:**
> "You resolve candidates to exact Spotify track IDs/URIs; do not return approximate matches."

### 2.6 The Researcher Agent (Hybrid Verifier)

**Role:** Verifies that a specific Spotify track satisfies protocol constraints with high confidence.

**Capabilities:**

- **Spotify Features First:** Uses Spotify audio features + metadata when available.
- **External Fallback:** Uses web/DB sources when Spotify data is missing/insufficient for key constraints (especially “no vocals”).
- **Explainability:** Produces accept/reject with reasons and confidence.

**System Prompt Directive:**
> "Prefer Spotify features when available; fall back when needed. If you cannot verify constraints confidently, reject."

### 2.7 The Compliance Guardian (Branding + Policy)

**Role:** Ensures Spotify branding/policy compliance and prevents forbidden behaviors.

**Capabilities:**

- **Attribution Checks:** Spotify attribution present; album art not improperly modified.
- **Policy Guardrails:** No non-Spotify audio; no downloading/recording; safe token handling.

### 2.8 The Distraction Scorer (Psychoacoustic Proxy)

**Role:** Computes a Focus-specific `distraction_score` and stability assessment from Spotify metadata/audio features (and audio analysis when available), producing auditable explanations for ranking and rejection.

**Capabilities:**

- **Score + Explain:** Produces `distraction_score` with a feature breakdown (e.g., speechiness/instrumentalness/energy/loudness/metadata flags).
- **Stability Checks:** Flags “high surprise” tracks (e.g., excessive section changes or loudness swings) when audio analysis is available; otherwise uses conservative heuristics and rejects when confidence is insufficient.
- **Hard-Ban Enforcement:** Rejects disruptive versions (live/remaster/edit/feat), explicit (per mode policy), and other Focus “attention-grabbers.”

**System Prompt Directive:**
> "You compute distraction and stability proxies from Spotify data. If you cannot assess stability confidently, you reject. You always provide auditable reasons and never alter track identity."

### 2.9 The Calibration Agent (Effectiveness Evaluator)

**Role:** Uses user feedback to personalize ranking/selection *within* protocol constraints (no “learning into vocals”), improving the non-distracting experience over time.

**Capabilities:**

- **Feedback Ingestion:** Consumes early skips, repeated skips, likes/saves, session ratings.
- **Policy Updates:** Adjusts weights/thresholds and track/cluster down-ranking while preserving hard constraints.
- **Audit Trail:** Records which signal caused each down-rank/exclusion and the before/after rationale.

**System Prompt Directive:**
> "You personalize within protocol. You never relax hard bans and you always leave an audit trail for every weight/threshold change."

---

## 3. The Workflow Loop (The "Vibe Cycle")

1. **User Request:** "I need to focus on complex coding."
2. **Token Steward:** Ensures the user is authenticated and tokens are fresh.
3. **Playback Agent:** Initializes the Web Playback SDK device and confirms it is Ready.
4. **Neuro-Composer:** Produces strict constraints (tempo/energy/vocal-avoidance/version bans) based on mode + user taste.
5. **Catalog Agent:** Resolves candidates to exact Spotify track IDs/URIs and gathers Spotify metadata/features.
6. **Researcher:** Verifies each resolved Spotify track (Spotify features first; external fallback as needed) and returns accept/reject with reasons.
7. **Distraction Scorer:** Computes `distraction_score` + stability checks for Focus and rejects/downscores “attention-grabbers” with auditable reasons.
8. **Playback Agent:** Plays the approved queue (default) and optionally triggers playlist materialization for persistence.
9. **Calibration Agent:** Uses feedback (skips/likes/ratings) to adjust ranking/selection within protocol constraints for future sessions.
10. **Supervisor + Compliance Guardian:** Ensures identity correctness, branding/policy compliance, and enforces the invariant that only verified+scored URIs can be played.
