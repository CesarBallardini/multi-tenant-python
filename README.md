# multi-tenant-python — academy

[![check](https://github.com/CesarBallardini/multi-tenant-python/actions/workflows/check.yml/badge.svg)](https://github.com/CesarBallardini/multi-tenant-python/actions/workflows/check.yml)
[![pytest](https://github.com/CesarBallardini/multi-tenant-python/actions/workflows/pytest.yml/badge.svg)](https://github.com/CesarBallardini/multi-tenant-python/actions/workflows/pytest.yml)
[![security](https://github.com/CesarBallardini/multi-tenant-python/actions/workflows/security.yml/badge.svg)](https://github.com/CesarBallardini/multi-tenant-python/actions/workflows/security.yml)

**academy** is an academic-records backend — students, teachers, guardians, and administrative staff, with degree programs, study plans, subjects, course sections, grades, and graduation. Its reason for being is to work through **multi-tenant authorization** in a real domain.

## Multi-tenant authorization

- **Each person is a tenant.** A person's own records — their grades and academic history — live in their own tenant.
- **Each person holds one or more roles at once**: administrative employee, teacher, student, guardian. One person can be a mother (guardian), a teacher, and a student simultaneously.
- Access to *other* people's records is granted through **relationships**, not through a role held inside a shared tenant — a relationship-based (**ReBAC**) model. The relations are *self*, *teacher-of-a-course-section*, *guardian-of-a-student*, and *administrator*.
- **Access is record-level**: a grant applies to a *subset of records* resolved by relationship — a student reads only their own grades; a teacher reads/writes only the grades of students in a section they teach; a guardian reads only their wards' grades.
- Authorization is **self-served**: every decision is made in-process by our own pure policy against our own repositories. There is no external authorization service.

The two protected resources are `grades` and `academic_history`, each with `read` and `write` actions; the full grant matrix is in [`docs/domain.md`](docs/domain.md#authorization-model-self-served).

## Architecture and domain

The project is built **domain-first** on a **ports and adapters (hexagonal)** architecture. This iteration ships **only the pure domain layer** — plain business objects with no database, no framework, and no I/O. The domain is deterministic: rules that depend on "now" (age, guardianship) take an explicit `today`, and identifier/clock generation are ports. Rules spanning more than one aggregate live in domain services.

The application, FastAPI inbound API, and SQLAlchemy persistence (imperative mapping + Alembic on in-memory SQLite) come next, each behind ports, without touching the domain.

```
src/academy/
  domain/                 # implemented — pure, no I/O
    shared/               # typed ids, the Entity base, DomainError
    people/               # Person, Email, PersonalData, Role, Credential, AgeOfMajority
    academics/            # DegreeProgram, Plan, Subject, Term, CourseSection, Enrollment
    grades/               # Grade, GradeEntry, AcademicHistory
    guardianship/         # Guardianship
    graduation/           # Graduation, GraduationStatus
    authorization/        # AccessPolicy (self-served), AccessRequest/Decision, enums
    services/             # CourseSectionFactory, EnrollmentService, GradingService, GraduationService
  # application/          # planned — use cases, ports (input/output), RelationshipResolver
  # adapters/             # planned — inbound/api (FastAPI), outbound/persistence (SQLAlchemy)
  # config/               # planned — composition root
tests/
  unit/                   # the pure domain (fast, no infrastructure)
  integration/            # in-process API tests via httpx (planned)
  acceptance/             # pytest-bdd scenarios (planned)
  e2e/                    # httpx against a live uvicorn (planned)
```

## Documentation

The design is written down before the code, under [`docs/`](docs/):

* [`docs/description.md`](docs/description.md) — the problem specification: entities, rules, and every design decision resolved during requirements analysis.
* [`docs/domain.md`](docs/domain.md) — the object-oriented domain model, with mermaid class diagrams per bounded context and the authorization grant matrix.
* [`docs/architecture.md`](docs/architecture.md) — the structural and technology decisions (hexagonal layering, self-served authorization, SQLAlchemy + Alembic on in-memory SQLite, FastAPI, testing strategy) with a decision log.
* [`docs/tooling.md`](docs/tooling.md) — how to build, test, and run the checks: uv, ruff, pyright/pyrefly, bandit, pytest, the Makefile, and dependency management.
* [`docs/best-practices-for-multi-tenant-authorization.md`](docs/best-practices-for-multi-tenant-authorization.md) — a local, illustrated copy of a background article on multi-tenant authorization (external reference material).

## Getting started

```bash
make install     # sync the environment and install pre-commit hooks
make lint types test security
```

Full tooling reference — prerequisites, every Makefile target, dependency updates, and building a wheel — is in [`docs/tooling.md`](docs/tooling.md).

## Status and what's next

* **Done** — the pure domain layer under `src/academy/domain/`, with unit tests. `make lint types test security` is green.
* **Next**, in order, each behind ports without touching the domain:
  * the **application** layer (use cases, input/output ports, the `RelationshipResolver` that feeds the self-served `AccessPolicy`);
  * the **SQLAlchemy** persistence adapter with **imperative mapping** and **Alembic** migrations on an **in-memory SQLite** database;
  * the **FastAPI** inbound API (clients are curl or simple Python scripts);
  * the **composition root** in `config/`, and an **import-linter** contract enforcing the dependency rule.

## License

MIT — see [LICENSE](LICENSE).
