# Agentic QA POC

An AI-first QA automation proof of concept: autonomous agents that plan, execute,
and **self-heal** end-to-end test suites, orchestrated with [LangGraph](https://github.com/langchain-ai/langgraph).

> **Status:** Proof of Concept — public repo, no production data or credentials
> should ever be present in this codebase.

---

## Security-First Approach

This project treats security as a prerequisite, not an afterthought. Before a
single line of application code was written, the following controls were put
in place:

| Control | Purpose |
|---|---|
| [`.gitignore`](.gitignore) | Blocks `.env` files, keys, virtual envs, and build artifacts from ever being tracked by git. |
| [`.cursorignore`](.cursorignore) | Prevents AI coding assistants (Cursor) from reading or indexing secrets and credential directories, even locally. |
| [`.pre-commit-config.yaml`](.pre-commit-config.yaml) | Runs [gitleaks](https://github.com/gitleaks/gitleaks) and companion hooks on every commit to catch hardcoded API keys, tokens, and private keys before they reach git history. |
| [`.env.example`](.env.example) | Documents every required environment variable **without** real values, so contributors never need to share secrets to get started. |

### Contributor setup

```bash
# 1. Install and enable pre-commit hooks (required before your first commit)
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push

# 2. Configure local secrets (never committed)
cp .env.example .env
# then fill in .env with your own keys
```

### Reporting a security issue

This is a public POC repository. If you discover a credential leak or
vulnerability, please do not open a public issue — report it privately to the
repository owner first.

---

## Architecture Overview

The system is built around [LangGraph](https://github.com/langchain-ai/langgraph),
which models QA execution as a stateful, directed graph of agent nodes rather
than a linear script. This gives the agent the ability to branch, retry, and
recover mid-run instead of failing hard on the first broken step.

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Planner    │────▶│   Executor    │────▶│   Validator     │
│  (LangGraph  │     │ (runs test    │     │ (asserts on     │
│   node)      │     │  step/action) │     │  expected state)│
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                    │
                                        fail ┌──────┴──────┐ pass
                                             ▼             ▼
                                    ┌─────────────┐   ┌─────────┐
                                    │ Self-Healing │   │  Report │
                                    │    Agent     │   │  Node   │
                                    └──────┬──────┘   └─────────┘
                                           │
                                    retry with
                                    healed locator/step
                                           │
                                           ▼
                                     back to Executor
```

**Core components:**

- **Planner** — decomposes a QA objective (e.g. "verify checkout flow") into
  discrete, executable test steps.
- **Executor** — carries out each step against the target application
  (browser automation, API calls, etc.).
- **Validator** — checks actual outcomes against expected assertions.
- **Self-Healing Agent** — see below; triggered only on validation failure.
- **Report Node** — aggregates run results into a structured QA report.

State is passed between nodes as a typed graph state object, and every
transition is checkpointed so a run can be inspected, replayed, or resumed.

---

## Self-Healing QA

Traditional automated tests break the moment a selector, endpoint, or UI
label changes — even when the underlying feature still works correctly.
This POC explores **self-healing test execution**: when a step fails
validation, control routes to a dedicated healing node instead of failing
the run outright.

The self-healing agent:

1. Inspects the failure (e.g. stale selector, changed DOM structure, shifted
   API response shape).
2. Re-derives an updated locator/step using the current state of the target
   application.
3. Retries the step with the healed action.
4. Logs both the original and healed step so drift is visible in the QA
   report, even when the test ultimately passes.

This keeps test suites resilient to minor, expected application changes
while still surfacing genuine regressions to the team.

---

## Project Status

This is an early-stage POC. Expect the graph topology, agent prompts, and
tooling to evolve quickly. Contributions and design feedback are welcome via
pull request.
