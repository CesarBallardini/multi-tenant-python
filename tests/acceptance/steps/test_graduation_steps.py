"""Step definitions for conferring graduation."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from pytest_bdd import given, parsers, scenarios, then, when

from academy.domain.academics.plan import Plan
from academy.domain.academics.subject import Subject
from academy.domain.academics.term import Term
from academy.domain.grades.academic_history import AcademicHistory
from academy.domain.grades.grade import Grade
from academy.domain.grades.grade_entry import GradeEntry
from academy.domain.graduation.graduation import Graduation
from academy.domain.people.email import Email
from academy.domain.people.person import Person
from academy.domain.people.personal_data import PersonalData
from academy.domain.people.role import Role
from academy.domain.services.graduation_service import (
    GraduationService,
    NotEligibleForGraduationError,
)
from academy.domain.shared.errors import DomainError
from academy.domain.shared.ids import (
    CredentialId,
    GraduationId,
    PersonId,
    PlanId,
    ProgramId,
    SubjectId,
)

scenarios('../features/graduation.feature')

_SUBJECTS = {'Maths': SubjectId(UUID(int=1)), 'Physics': SubjectId(UUID(int=2))}
_TERM = Term(2026, 1)
_STUDENT = PersonId(UUID(int=200))
_PROGRAM = ProgramId(UUID(int=1))
_CREDENTIAL = CredentialId(UUID(int=5))
_GRADUATION = GraduationId(UUID(int=9))


@dataclass
class State:
    plan: Plan
    student: Person | None = None
    history: AcademicHistory | None = None
    graduation: Graduation | None = None
    error: DomainError | None = None


def _subjects(names: str) -> list[str]:
    return [name.strip() for name in names.split(',')]


@given(parsers.parse('a plan with subjects "{names}"'), target_fixture='state')
def a_plan(names: str) -> State:
    plan = Plan(PlanId(UUID(int=10)), [Subject(_SUBJECTS[name], name) for name in _subjects(names)])
    return State(plan=plan)


@given('a student')
def a_student(state: State) -> None:
    state.student = Person(_STUDENT, Email('s@example.com'), PersonalData('S', date(2000, 1, 1)), roles={Role.STUDENT})
    state.history = AcademicHistory(_STUDENT)


@given(parsers.parse('the student has passed "{names}"'))
def student_has_passed(state: State, names: str) -> None:
    assert state.history is not None
    for name in _subjects(names):
        state.history.record(GradeEntry(_SUBJECTS[name], _TERM, Grade(9)))


def _confer(state: State) -> None:
    assert state.student is not None
    assert state.history is not None
    state.graduation = GraduationService().confer(
        _GRADUATION, state.student, _PROGRAM, _CREDENTIAL, state.history, state.plan, date(2026, 3, 1)
    )


@given('graduation has been conferred')
def graduation_conferred(state: State) -> None:
    _confer(state)


@when('graduation is conferred')
def confer_graduation(state: State) -> None:
    try:
        _confer(state)
    except DomainError as exc:
        state.error = exc


@when('the graduation is revoked')
def revoke_graduation(state: State) -> None:
    assert state.graduation is not None
    state.graduation.revoke()


@when(parsers.parse('the graduation is reissued on "{on}"'))
def reissue_graduation(state: State, on: str) -> None:
    assert state.graduation is not None
    state.graduation.reissue(date.fromisoformat(on))


@then('the graduation is active')
def graduation_is_active(state: State) -> None:
    assert state.graduation is not None
    assert state.graduation.is_active()


@then('the graduation is not active')
def graduation_is_not_active(state: State) -> None:
    assert state.graduation is not None
    assert not state.graduation.is_active()


@then("it issues the program's credential")
def issues_credential(state: State) -> None:
    assert state.graduation is not None
    assert state.graduation.credential_id == _CREDENTIAL


@then('conferral is rejected because the student is not eligible')
def rejected_not_eligible(state: State) -> None:
    assert isinstance(state.error, NotEligibleForGraduationError)
