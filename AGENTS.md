# AGENTS.md

## Overview

This document outlines the autonomous agent architecture used to build and maintain the `brain-radio` application. The system is powered by ChatGPT Codex and operates within a Codez environment with full internet access. It leverages a multi-agent loop designed to plan, write, test, review, and iterate on the entire codebase end-to-end without human intervention.

## Architecture Summary

The agent system is composed of four primary roles operating in a deterministic loop:

### 1. Planner Agent (Architect)
- Parses the PRD and ACCEPTANCE_CRITERIA.md files.
- Defines a task roadmap and overall architecture.
- Outputs a sequenced plan of development milestones.
- Responsible for creating the initial `TODO.md` or updating it as the project evolves.

### 2. Coder Agent (Developer)
- Executes tasks from the Planner’s roadmap.
- Writes implementation code and corresponding tests following TDD.
- May initialize files, refactor existing logic, or add new modules.
- Ensures each code submission meets the specific acceptance criteria and test coverage requirements.

### 3. Reviewer Agent (QA + Critic)
- Evaluates code output from the Coder.
- Runs test suites, lint checks, static analysis, and code coverage tools.
- Returns structured feedback or initiates retry if failures or violations are found.
- Validates security practices and ensures >95% test coverage before approving work.

### 4. Orchestrator Agent (Manager)
- Manages task delegation and message-passing between agents.
- Initiates each round of Planner → Coder → Reviewer.
- Monitors loops for deadlocks, regressions, or convergence failures.
- Triggers self-healing routines or exits gracefully if blocked.

## Execution Model

The system runs as a continuous improvement loop with retry capability:

1. **Planner** defines a prioritized list of tasks.
2. **Coder** selects the next unblocked task and writes production code + test code.
3. **Reviewer** executes:
   - `pytest` or equivalent
   - code coverage (must be ≥95%)
   - linters (zero errors)
   - any static analysis (e.g., Bandit)
4. If any test fails or criteria are unmet:
   - Reviewer sends critique back to Coder.
   - Loop repeats for up to N retries (default 5).
5. Once a task passes review, Orchestrator moves to the next.

## Technical Stack

- **Environment:** Codez with Docker or Docker Compose containerization.
- **Orchestration Framework:** Preferably [AutoGen](https://github.com/microsoft/autogen) or [CrewAI](https://github.com/joaomdmoura/crewAI) for multi-agent coordination and code execution.
- **Code Execution:** Enabled and sandboxed per agent role.
- **Memory Strategy:** Context isolation per task + short-term summaries stored in `NOTES.md`.

## Agent Memory Design

- **Short-term:** Active prompt memory per task.
- **Mid-term:** Persistent logs and TODOs in repo.
- **Long-term:** Codebase itself + optional vector store integration for PRD/criteria recall.

## Security Safeguards

- Execution restricted to sandboxed environment.
- Secrets accessed via ENV vars; never hardcoded.
- Reviewer validates against insecure coding patterns and dependency risks.
- Reviewer checks for unintentional code exposure (e.g., credentials in logs).

## Quality Assurance Model

- Full TDD process.
- Unit, integration, and end-to-end tests included.
- Linting and code style enforcement.
- Self-healing behavior through iterative fix loops guided by Reviewer feedback.
- CI-integrated enforcement of all tests, lint, and coverage thresholds.

## Success Criteria

A task is considered complete only if:
- All automated and reviewer checks pass.
- Code adheres to PRD and ACCEPTANCE_CRITERIA.md.
- The CI pipeline is green.
- The repo maintains high-quality, modular, and maintainable structure.

---

This document governs the operation of the `brain-radio` agents and is the single source of truth for all autonomous behavior within this project.
