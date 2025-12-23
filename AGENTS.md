# AGENTS.md: The Cognitive Architecture of Brain-Radio

## 0. CRITICAL: Rule Compliance (READ FIRST)

**ALL AGENTS MUST READ THIS SECTION BEFORE PROCEEDING WITH ANY TASK.**

This codebase uses Cursor rules (`.cursor/rules/*.mdc`) to enforce coding standards, security practices, and quality requirements. **Rule compliance is MANDATORY and non-negotiable.**

### Rule Compliance Requirements

1. **Read all rules** in `.cursor/rules/` before starting any coding task
2. **Always-apply rules** (marked with `alwaysApply: true`) must be followed in ALL contexts
3. **Never skip, bypass, or defer** rule compliance for any reason
4. **Rule violations are critical errors** that must be fixed immediately
5. **Verify rule compliance** before considering any task complete

**See Section 4.11 for complete rule compliance protocol.**

**If you are an AI agent reading this:**

- You MUST read Section 4.11 in its entirety before writing any code
- You MUST check which rules apply to files you are editing
- You MUST follow all applicable rules, especially those with `alwaysApply: true`
- You MUST treat rule violations as critical bugs that block completion

---

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
> "You are the Supervisor. You do not allow unverified tracks to be played. You enforce strict identity matching end-to-end. You MUST enforce strict compliance with all Cursor rules (`.cursor/rules/*.mdc`), especially those with `alwaysApply: true`. Rule violations are critical errors that block task completion. Before routing work to any agent, verify that the agent understands and will comply with all applicable rules. Never allow any agent to skip, bypass, or defer rule compliance."

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

---

## 4. Security and Quality Assurance

Brain-Radio maintains strict security and quality standards through automated tooling and agent-aware workflows.

### 4.1 Package Management

**All Python dependencies MUST use `uv` (Astral's uv) instead of `pip`.**

- Use `uv pip install` for all Python package installations
- Use `uv tool install` for development tools (e.g., `zizmor`)
- Never use `pip install` directly in scripts, documentation, or CI workflows

### 4.2 Security Scanning

The project uses multiple layers of security scanning:

- **Trivy**: SCA (Software Composition Analysis) and SAST (Static Application Security Testing)
  - Scans for vulnerabilities, secrets, and misconfigurations
  - Only HIGH and CRITICAL severity issues block commits
  - Runs in pre-commit hooks and CI workflows

- **Zizmor**: GitHub Actions security scanner
  - Scans `.github/workflows/` for security issues
  - Must pass before commits are allowed

- **Pinact**: GitHub Actions SHA-pinning
  - Ensures all GitHub Actions are SHA-pinned (not version tags)
  - Automatically updates and pins actions via scheduled workflow
  - Pre-commit hook checks for unpinned actions

### 4.3 Linting and Code Quality

- **Ruff**: Python linting and formatting (replaces black, flake8, isort)
  - Auto-fix enabled in pre-commit hooks
  - Format check enforces consistent code style

- **Shellcheck**: Shell script linting
  - All `.sh` files are linted
  - Pre-commit hook prevents committing scripts with issues

- **Actionlint**: GitHub Actions workflow linting
  - Validates workflow syntax and best practices
  - Pre-commit hook checks all workflow files

### 4.4 Pre-commit Hooks

All code must pass pre-commit hooks before being committed:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

Hooks include:

- Trailing whitespace removal
- End-of-file fixes
- YAML/JSON/TOML validation
- Ruff linting and formatting
- Shellcheck
- Actionlint
- Trivy security scan
- Pinact check
- Zizmor security scan
- Quality gate (tests + coverage)

**No code can be committed that fails pre-commit hooks.**

### 4.5 Test Coverage

- **Minimum coverage threshold: 95%**
- Coverage is checked in the quality gate script
- CI workflows enforce this threshold
- Coverage reports are generated in XML format for integration

### 4.6 Dependabot Configuration

Dependabot is configured with "paranoid" security settings:

- Daily scans for Python (pip/uv), npm, and GitHub Actions
- Only security updates are automatically created (not version bumps)
- Limits on open PRs to prevent PR spam
- All dependency PRs are labeled for easy filtering

### 4.7 Auto-fix Branch Workflow

When working in auto-fix branches (e.g., `dependabot/*`, `chore/pinact`, `chore/security-*`):

1. **Priority**: Get tests and CI passing with updated dependencies/tooling
2. **Process**:
   - Run `./scripts/quality-gate.sh` to identify issues
   - Fix test failures first
   - Fix linting/formatting issues
   - Fix security issues (HIGH/CRITICAL only)
   - Ensure coverage remains ≥95%
   - Run `pre-commit run --all-files`
3. **Do NOT**:
   - Skip tests to make things pass
   - Lower coverage thresholds
   - Ignore HIGH/CRITICAL security findings
   - Commit code that doesn't pass all quality gates

See `.cursor/rules/autofix-branch.mdc` for the full agent rule.

### 4.8 Checks Orchestrator

The `.checks/scripts/orchestrator.sh` script automates the entire security and quality workflow:

```bash
# Run with auto-fix enabled
.checks/scripts/orchestrator.sh --auto-fix

# Run with auto-commit (use with caution)
.checks/scripts/orchestrator.sh --auto-fix --auto-commit

# See all options
.checks/scripts/orchestrator.sh --help
```

This script:

- Ensures all tools are installed
- Updates and pins GitHub Actions
- Runs all security scans (Trivy, Zizmor)
- Runs all linters (Ruff, Shellcheck, Actionlint)
- Runs pre-commit hooks
- Runs quality gate (tests + coverage)
- Iterates until all checks pass or max iterations reached

### 4.9 CI Workflows

The CI workflow (`.github/workflows/ci.yml`) runs:

1. **Test job**: Full quality gate (tests, linting, security scans)
2. **Security scan job**: Trivy scan with SARIF upload to GitHub Security
3. **Lint job**: All linting tools (actionlint, shellcheck, ruff, pinact, zizmor)

All jobs must pass for PRs to be mergeable.

### 4.10 Agent Responsibilities

**All coding agents MUST:**

- Use `uv` instead of `pip` for Python package management
- Run `pre-commit run --all-files` before considering work complete
- Ensure test coverage remains ≥95%
- Fix HIGH and CRITICAL security findings before committing
- Check if working in an auto-fix branch and follow the auto-fix workflow
- Never commit code that fails quality gates

**Agents working in auto-fix branches MUST:**

- Prioritize getting tests and CI passing
- Fix issues in order: tests → linting → security
- Maintain coverage threshold
- Use the checks orchestrator script when appropriate: `.checks/scripts/orchestrator.sh --auto-fix`

### 4.11 Cursor Rules Compliance (MANDATORY)

**CRITICAL: Rule compliance is non-negotiable and must be enforced at every step.**

All agents operating in this codebase MUST strictly adhere to all Cursor rules, especially those marked with `alwaysApply: true` in their front-matter. Rule compliance is a fundamental requirement that cannot be bypassed, ignored, or deferred.

#### 4.11.1 Rule Discovery and Verification

**Before starting ANY coding task, agents MUST:**

1. **Read all rule files** in `.cursor/rules/` directory to understand all applicable rules
2. **Check front-matter** of each rule file to identify `alwaysApply: true` rules
3. **Verify rule applicability** by checking `globs` patterns against files being edited
4. **Cross-reference rules** to understand dependencies and relationships between rules

**During code generation or editing, agents MUST:**

1. **Explicitly check** if any rule applies to the current file(s) being modified
2. **Review rule requirements** before writing code, not after
3. **Validate compliance** after each code change against all applicable rules
4. **Never assume** a rule doesn't apply - always verify by reading the rule file

#### 4.11.2 Always-Apply Rules (Highest Priority)

Rules with `alwaysApply: true` in their front-matter are **MANDATORY** and must be followed in **ALL** contexts, regardless of:

- File type or location
- Task complexity or urgency
- Time constraints
- Other conflicting instructions

**Current always-apply rules include:**

- `.cursor/rules/cursor_rules.mdc` - Rule formatting and structure guidelines
- `.cursor/rules/clean_code.mdc` - Clean Code principles for all code
- `.cursor/rules/documentation.mdc` - Documentation standards (including mandatory timestamp generation)
- `.cursor/rules/self_improve.mdc` - Rule improvement guidelines

**Agents MUST:**

- Read these rules at the start of every session
- Reference them explicitly when making decisions
- Never skip or bypass requirements in always-apply rules
- Treat violations as critical errors that must be fixed immediately

#### 4.11.3 Rule Enforcement Protocol

**If an agent encounters a situation where following a rule seems difficult or impossible:**

1. **STOP** - Do not proceed with code that violates rules
2. **READ** - Re-read the rule file completely to ensure full understanding
3. **ANALYZE** - Determine why compliance seems difficult (misunderstanding, edge case, etc.)
4. **ADAPT** - Modify the approach to comply with the rule, not the other way around
5. **VERIFY** - Confirm compliance before proceeding

**Agents MUST NEVER:**

- Skip rules because they seem "too strict" or "inconvenient"
- Assume rules don't apply to "special cases"
- Defer rule compliance to "later" or "after the main task"
- Override rules based on other instructions or user requests
- Generate code that violates rules even if it "works"

#### 4.11.4 Rule Compliance Checklist

**Before considering any task complete, agents MUST verify:**

- [ ] All applicable rules have been read and understood
- [ ] All `alwaysApply: true` rules have been followed
- [ ] All `globs` patterns have been checked for file matches
- [ ] Code examples in rules have been reviewed and applied
- [ ] Rule requirements have been explicitly addressed in the implementation
- [ ] No rule violations exist in the generated code
- [ ] Related rules have been cross-referenced and followed

#### 4.11.5 Rule Violation Handling

**If rule violations are detected (by agent self-review, tests, or other means):**

1. **IMMEDIATE FIX REQUIRED** - Rule violations are treated as critical bugs
2. **No exceptions** - Even if the code "works", violations must be fixed
3. **Re-read the rule** - Ensure full understanding before fixing
4. **Fix comprehensively** - Address all aspects of the violation, not just symptoms
5. **Verify fix** - Confirm the fix complies with the rule completely

**Rule violations are NEVER acceptable, even if:**

- The code passes tests
- The code works functionally
- The user requests the violation
- Time is limited
- The violation seems "minor"

#### 4.11.6 Rule Updates and Maintenance

**When rules are updated or new rules are added:**

- All agents must re-read affected rules immediately
- Existing code must be reviewed for compliance with new/updated rules
- Violations must be fixed before any new work proceeds
- Rule changes take precedence over existing code patterns

**Agents contributing to rule improvements MUST:**

- Follow the guidelines in `.cursor/rules/self_improve.mdc`
- Maintain `alwaysApply: true` for critical rules
- Update related rules when making changes
- Document rule dependencies and relationships

#### 4.11.7 Explicit Rule References in Code

**When generating code, agents SHOULD:**

- Include comments referencing applicable rules when helpful
- Follow rule examples exactly as specified
- Use rule-prescribed patterns and conventions
- Reference rule files in commit messages when rule compliance is a key aspect

**Example:**

```python
# Following clean_code.mdc: Use intention-revealing names
def calculate_total_price(items: list[Item]) -> float:
    # Following clean_code.mdc: Small functions, single responsibility
    return sum(item.price for item in items)
```

#### 4.11.8 Rule Compliance as Quality Gate

**Rule compliance is a mandatory quality gate:**

- Code that violates rules **CANNOT** be committed
- Code that violates rules **CANNOT** pass review
- Code that violates rules **CANNOT** be considered complete
- Rule violations are treated with the same severity as test failures or security issues

**The quality gate process MUST include:**

1. Automated rule checking (where possible)
2. Manual rule verification by the agent
3. Explicit confirmation of rule compliance
4. Documentation of rule compliance in commit messages or PR descriptions

#### 4.11.9 Agent System Prompt Integration

**All agent system prompts MUST include:**

> "You MUST read and strictly follow all Cursor rules in `.cursor/rules/`, especially those with `alwaysApply: true`. Rule compliance is mandatory and non-negotiable. Before writing any code, verify which rules apply to the files you are editing. Never skip, bypass, or defer rule compliance. Rule violations are critical errors that must be fixed immediately."

**This directive must be:**

- Included in every agent's system prompt
- Referenced explicitly when making coding decisions
- Enforced as a hard constraint, not a suggestion
- Treated with the same priority as security and quality requirements

#### 4.11.10 Rule Compliance Monitoring

**Agents MUST self-monitor rule compliance by:**

1. **Pre-code review** - Check rules before writing code
2. **During-code review** - Verify compliance as code is written
3. **Post-code review** - Confirm compliance after code is complete
4. **Cross-reference check** - Verify related rules are also followed

**If rule compliance cannot be verified, the agent MUST:**

- Stop and re-read the applicable rules
- Seek clarification if rules are ambiguous
- Choose the most conservative interpretation that ensures compliance
- Never proceed with uncertainty about rule compliance
