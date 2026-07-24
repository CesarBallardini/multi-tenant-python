# Architecture

Architecture decisions for the academy academic-records backend. The domain model itself
lives in [`domain.md`](./domain.md); the problem specification in
[`description.md`](./description.md). This document records the *structural* and
*technology* decisions and why they were made.

## 1. Overview

- A **Python backend** exposing a **JSON API** (FastAPI). Clients are thin: `curl` or
  simple Python scripts call the API; there is no server-rendered web UI.
- **Ports and adapters (hexagonal) architecture** with clean layering
  (domain -> application -> adapters) and a one-way dependency rule.
- **Domain-first delivery:** the current iteration implements only the pure domain layer.
  Persistence, API, and wiring are added in later iterations behind ports, without changing
  the domain.
- **Authorization is self-served** (relationship-based / ReBAC), decided in-process by our
  own policy against our own repositories -- no external authorization service.

## 2. Architectural style: ports and adapters

Layers, from inside out:

| Layer | Contains | May depend on |
|-------|----------|---------------|
| `domain` | entities, value objects, domain services, the `AccessPolicy` | nothing (pure) |
| `application` | use cases, DTOs, ports (`input` / `output`), `RelationshipResolver` | `domain` |
| `adapters` | FastAPI inbound API; SQLAlchemy outbound persistence | `application`, `domain` |
| `config` | composition root: builds engine/session, wires adapters into use cases | all layers |

**Dependency rule.** Source dependencies point only inward. The domain imports nothing
from outer layers; the application depends only on the domain and its own port interfaces;
adapters implement those ports. `config` is the single place allowed to know every layer.

**Enforcement.** The rule is made a CI-blocking check with **import-linter** (a layered
contract), mirroring the reference projects. A violation fails pre-commit and CI.

The domain is **pure**: no clock, no randomness, no I/O. Time-dependent rules (age,
guardianship) take an explicit `today: date`; identifier and clock generation are
**output ports** injected by the application, so behavior stays deterministic and testable.

## 3. Domain design

Tactical DDD: aggregate roots own their invariants, cross-aggregate references are by
typed id, value objects are immutable. Multi-aggregate rules live in domain services
(`CourseSectionFactory`, `EnrollmentService`, `GradingService`, `GraduationService`).
Full model and diagrams in [`domain.md`](./domain.md).

## 4. Authorization: self-served ReBAC

- **Relationship-based (ReBAC)** because each person is a tenant and almost every access
  crosses persons. Access flows along relations: *self*, *teacher-of-section*,
  *guardian-of*, *administrator*.
- **Self-served, centralized decision point.** `AccessPolicy` is a pure domain service --
  our own Policy Decision Point. Every access check funnels through it, instead of
  scattering `if role == ...` across API handlers. It decides from its inputs alone; the
  application's `RelationshipResolver` resolves which relations hold by reading the same
  repositories, then feeds the policy.
- **No third-party authorization engine.** We reuse only the generic *concepts* (PDP,
  resources, actions, relations, a `check`-style call) and reimplement them in-house, sized
  to this domain.
- Resources: `grades`, `academic_history`. Actions: `read`, `write`. Grants are
  record-level (a subset of records resolved by relation). Grant matrix in
  [`domain.md`](./domain.md#authorization-model-self-served).

## 5. Persistence: SQLAlchemy + Alembic on in-memory SQLite

- **Database: in-memory SQLite.** The engine uses SQLAlchemy's `StaticPool` with
  `check_same_thread=False` on a `sqlite://` URL, so a single in-memory database stays
  alive and shared across connections (otherwise each connection gets its own throwaway
  DB).
- **Schema via Alembic.** Migrations under `alembic/versions/` are the single source of
  truth for the schema and are applied to the in-memory engine at startup (and per test
  session), rather than `Base.metadata.create_all()`.
- **Imperative (classical) mapping.** Domain aggregates are plain classes that never
  inherit from a declarative `Base` or import SQLAlchemy. Tables are declared separately in
  `adapters/outbound/persistence/sqlalchemy/orm/`, and wired to the domain classes with
  `registry.map_imperatively()` in `mappers/`. The ORM lives only in the adapter; the
  domain stays persistence-ignorant.
- **Repositories** implement the application's output ports over a SQLAlchemy `Session`.
  These same repositories back the self-served `RelationshipResolver`.

## 6. Inbound API: FastAPI

- **FastAPI** is the only inbound adapter (`adapters/inbound/api/`): app factory, routers,
  request/response schemas (Pydantic), and dependency wiring. The API is the product
  surface; clients are `curl` / Python scripts.
- Use cases are invoked from routers through the application's input ports; routers hold no
  business logic.

## 7. Testing strategy

Test taxonomy follows the scaffold: `unit/`, `integration/`, `acceptance/` (BDD via
pytest-bdd), `e2e/`. Runner is pytest.

**Chosen:**

- **Unit tests** -- the pure domain (entities, value objects, services, `AccessPolicy`).
  Fast, no I/O, the bulk of the suite.
- **Integration tests (primary API tier)** -- **`httpx.AsyncClient` + `ASGITransport`**,
  in-process against the ASGI app. Native async, no socket, and it **shares the app's
  in-memory SQLite engine** (the DB-session dependency is overridden to the test's
  `StaticPool` engine, with the Alembic-migrated schema built per session). Fast and
  deterministic; same `httpx` API one would script against a real server.
- **End-to-end tests (thin tier)** -- **`httpx` against a live `uvicorn`** over real
  sockets, mirroring the real `curl` / Python-script clients. Kept small (smoke-level),
  since it is slower and manages server lifecycle.
- **Acceptance tests** -- pytest-bdd `.feature` scenarios for key business rules.

**Rejected / deferred alternatives (and why):**

| Option | Verdict | Why |
|--------|---------|-----|
| `fastapi.testclient.TestClient` (sync) | **Not chosen** (viable fallback) | Same in-process model as the async client, but a sync-only surface that hides real async code paths. Kept as the drop-in option if we ever want simpler, sync tests. |
| Live server only (`uvicorn` + `httpx`/`requests`) for *all* API tests | **Rejected as the primary tier** | True over-the-wire fidelity, but slow, flakier, and needs server + in-memory-DB lifecycle per test. Used only for the thin e2e smoke tier, not the main integration suite. |
| `requests` | **Rejected** | Sync and live-server-only; no async support. `httpx` covers both in-process and live use with one API. |
| **Schemathesis** (OpenAPI property/contract testing) | **Deferred** | Valuable for near-free contract/fuzz coverage, but complements rather than replaces scenario tests; revisit once the OpenAPI schema stabilizes. |
| **Tavern** (YAML API DSL) | **Rejected** | Declarative YAML struggles with the logic-rich authorization scenarios here; plain `httpx` in Python is clearer. |
| **Playwright `APIRequestContext`** (pytest-playwright, in scaffold) | **Rejected for API tests** | Browser-oriented and heavyweight for a pure JSON API; reserved for any future real browser e2e, not API integration. |

## 8. Tooling

Inherited from the scaffold (see the root `README.md`): **uv** (env/deps), **ruff**
(lint+format), **pyright + pyrefly** (types), **bandit + pip-audit + OSV-Scanner**
(security), **pre-commit**, and a **Makefile** as the single interface. Added for this
architecture: **import-linter** (dependency-rule contract). New runtime dependencies land
when their adapter is built: `sqlalchemy`, `alembic`, `fastapi`, `uvicorn`, and `httpx`
(test/dev).

## 9. References

The layout borrows deliberately from two in-house projects:

- **iqueue** -- strict layer separation (domain / application / infrastructure), ports
  split `input` / `output`, one file per entity / value object, typed-UUID id value
  objects, an in-memory persistence adapter, and an **import-linter** dependency contract.
- **bluedoter-tng** -- a single `src/<package>/` tree, **package-by-bounded-context** in
  `domain/` and `application/`, adapters split `inbound` / `outbound`, a `shared/` domain
  package, and a `config/` composition root.

## 10. Decision log

| # | Decision | Status |
|---|----------|--------|
| A-01 | Ports and adapters (hexagonal) with clean layering domain -> application -> adapters | Accepted |
| A-02 | Dependency rule enforced by import-linter (CI-blocking) | Accepted |
| A-03 | Domain-first delivery; current iteration is domain-only | Accepted |
| A-04 | Pure domain: no clock/randomness/I/O; time and ids via injected ports | Accepted |
| A-05 | Self-served ReBAC authorization via a pure `AccessPolicy` PDP; no third-party engine | Accepted |
| A-06 | Persistence: SQLAlchemy on in-memory SQLite (`StaticPool`) | Accepted |
| A-07 | Schema via Alembic migrations (not `create_all`) | Accepted |
| A-08 | SQLAlchemy imperative (classical) mapping; domain stays ORM-free | Accepted |
| A-09 | Inbound API: FastAPI, JSON only; clients are curl / Python scripts | Accepted |
| A-10 | Single package `src/academy/`, domain split by bounded context | Accepted |
| A-11 | Primary API integration tests: httpx AsyncClient + ASGITransport (in-process) | Accepted |
| A-12 | Thin e2e tier: httpx against live uvicorn | Accepted |
| A-13 | Schemathesis contract testing | Deferred |
| A-14 | Actor identity: Bearer token per person (`Authorization: Bearer <token>`); missing/invalid -> 401. Placeholder for real authN, isolated at the API edge | Accepted |
| A-15 | A thin `smoke` subset of e2e (health, auth happy path, one denial) runs on every `pytest` invocation (never deselected) | Accepted |

## 11. Out of scope (current iteration)

Application/use-case layer, FastAPI adapter, SQLAlchemy adapter + Alembic setup, `config`
composition root, and the import-linter contract file are specified here but implemented in
later iterations. This iteration ships the pure domain under `src/academy/domain/` with
unit tests.
