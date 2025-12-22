# Agent Rules: Autofix Branch Hygiene

These rules apply to automated update branches such as:

- `chore/pinact`
- `dependabot/*`
- `chore/autofix/*`

If you are operating on one of these branches:

1. Run `scripts/tooling/run-quality-suite.sh --check` and capture failures.
2. Apply fixes as needed to restore a clean run.
3. Re-run `scripts/tooling/run-quality-suite.sh --check` until it is clean.
4. Ensure CI parity by keeping the workflow `scripts/quality-gate.sh` aligned with the
   quality suite script.

If additional tooling updates land (e.g., pinact, dependabot, or other automated PRs),
repeat the loop until all checks pass.
