# AGENTS.md - Engineering Workflow for Diligencia Reforzada EDD

## Project Overview

Panama AML/CFT compliance application (FastAPI + React + PostgreSQL). System for "Diligencia Reforzada" (Enhanced Due Diligence) based on Ley 23/2015 and Ley 254/2021.

## Skill-Driven Development

Before any action, check if a skill applies. Skills MUST be used when they do.

### Lifecycle Mapping

| Phase | Skill | Trigger |
|-------|-------|---------|
| DEFINE | spec-driven-development | New features, changes |
| PLAN | planning-and-task-breakdown | After spec is approved |
| BUILD | incremental-implementation | Implementing any change |
| VERIFY | test-driven-development | Logic, bugs, behavior |
| DEBUG | debugging-and-error-recovery | Tests fail, builds break |
| REVIEW | code-review-and-quality | Before merging |
| SIMPLIFY | code-simplification | Code works but is complex |
| SECURITY | security-and-hardening | Auth, input, data, integrations |
| SHIP | shipping-and-launch | Preparing to deploy |
| UI | frontend-ui-engineering | Building user interfaces |

## Rules

1. Always check if a skill applies before acting
2. If a skill applies, it MUST be loaded and followed
3. Never skip spec, plan, test, or review phases
4. Small, atomic, verifiable tasks
5. Tests are proof - "seems right" is never sufficient
6. Commit often with meaningful commit messages

## Code Style

- Backend: FastAPI + SQLAlchemy + Pydantic v2
- Frontend: React 18 + TypeScript + TailwindCSS + Zustand
- Python: flake8, type hints
- TypeScript: strict mode, no `any` types

## Verification

Before calling a task complete:
- Backend: `uvicorn app.main:app` starts without errors
- Frontend: `npm run build` succeeds
- Tests pass (backend: pytest, frontend: vitest)
