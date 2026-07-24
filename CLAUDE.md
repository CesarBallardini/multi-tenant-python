# Project guidance for academy

academy is a multi-tenant academic-records backend, built **domain-first** on **ports and
adapters**. See `docs/` for the specification, domain model, and architecture decisions.

## Development workflow

Build in phases, inside-out: **domain -> ports -> use cases -> adapters**. After each
phase, apply the two standing reviews below, and keep the quality gate green.

### Rule 1 - Per-phase test hunt

At the end of every phase, deliberately look for new tests to add across **all three
tiers** — unit, integration, and e2e — not only the tier the phase was about. Write the
ones that carry their weight.

### Rule 2 - Post-test typing review

After adding tests, review the phase's code for **typing opportunities**. Prefer precise,
named types over loose structures: named types / `NewType`, dataclasses and classes,
mixins, `NamedTuple`, `TypedDict`, enums, and `Protocol`s.

**`Any` and `object` as annotations are a red flag** — every occurrence must be justified
or replaced with a precise type.

### Rule 3 - Smoke tests always run

The `smoke`-tagged tests are a thin, always-on subset of e2e and are **never deselected**
(the default pytest marker expression is `(not e2e and not snapshot) or smoke`). Keep them
passing at all times. The smoke set is: liveness/health, the auth happy path, and one
authorization-denial test.

### Rule 4 - Quality gate per phase

`make lint types test security` must be green before a phase is done: ruff (lint +
format), pyright + pyrefly, the full test suite, and bandit.

## Conventions

- **Dependency rule:** source dependencies point inward only —
  `adapters -> application -> domain`. The domain imports nothing from outer layers.
- **Pure domain:** no clock, randomness, or I/O in `domain/`; time comes in as an explicit
  argument, ids/clock via ports.
- **Authorization is self-served:** decided in-process by the pure `AccessPolicy`, fed by
  the application's `RelationshipResolver`; no external authorization service.
- **No quoted / deferred imports.** Use normal top-level imports (the `flake8-type-checking`
  rule is intentionally disabled).
- **Do not reference non-repository files from committed code or docs** (e.g. dated
  working notes like `YYYY-MM-DD-*.md`). Committed files reference only committed files.
