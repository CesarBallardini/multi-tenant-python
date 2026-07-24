"""Step definitions for enrollment rules."""

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from pytest_bdd import given, parsers, scenarios, then, when

from academy.domain.academics.course_section import CourseSection
from academy.domain.academics.plan import Plan
from academy.domain.academics.subject import Subject
from academy.domain.academics.term import Term
from academy.domain.people.email import Email
from academy.domain.people.person import Person
from academy.domain.people.personal_data import PersonalData
from academy.domain.people.role import Role
from academy.domain.services.enrollment_service import (
    DuplicateSubjectEnrollmentError,
    EnrollmentService,
    NotAStudentError,
    SubjectNotInPlanError,
    WrongTermError,
)
from academy.domain.shared.errors import DomainError
from academy.domain.shared.ids import PersonId, PlanId, SectionId, SubjectId

scenarios('../features/enrollment.feature')

_SUBJECTS = {'Maths': SubjectId(UUID(int=1)), 'Physics': SubjectId(UUID(int=2))}
_STUDENT = PersonId(UUID(int=200))
_TEACHER = PersonId(UUID(int=100))
_SECTION = SectionId(UUID(int=50))


@dataclass
class State:
    current_term: Term
    plan: Plan = field(default_factory=lambda: Plan(PlanId(UUID(int=10))))
    student: Person | None = None
    already: set[SubjectId] = field(default_factory=set)
    section: CourseSection | None = None
    error: DomainError | None = None


def _term(label: str) -> Term:
    year, number = label.split('-T')
    return Term(int(year), int(number))


def _person(roles: set[Role]) -> Person:
    return Person(_STUDENT, Email('s@example.com'), PersonalData('S', date(2000, 1, 1)), roles=roles)


@given(parsers.parse('the current term is "{label}"'), target_fixture='state')
def the_current_term(label: str) -> State:
    return State(current_term=_term(label))


@given(parsers.parse('a plan that contains "{subject}"'))
def plan_contains(state: State, subject: str) -> None:
    state.plan.add_subject(Subject(_SUBJECTS[subject], subject))


@given('a student')
def a_student(state: State) -> None:
    state.student = _person({Role.STUDENT})


@given(parsers.parse('a student already enrolled in "{subject}"'))
def student_already_enrolled(state: State, subject: str) -> None:
    state.student = _person({Role.STUDENT})
    state.already = {_SUBJECTS[subject]}


@given('a person who is not a student')
def not_a_student(state: State) -> None:
    state.student = _person(set())


@given(parsers.parse('a "{subject}" section in "{label}"'))
def a_section(state: State, subject: str, label: str) -> None:
    state.section = CourseSection(_SECTION, _SUBJECTS[subject], _term(label), _TEACHER)


@when('the student enrolls')
def the_student_enrolls(state: State) -> None:
    student = state.student
    section = state.section
    assert student is not None
    assert section is not None
    try:
        EnrollmentService().enroll(section, student, state.plan, state.current_term, state.already)
    except DomainError as exc:
        state.error = exc


@then('the student is enrolled')
def student_is_enrolled(state: State) -> None:
    assert state.error is None
    assert state.section is not None
    assert state.student is not None
    assert state.section.is_enrolled(state.student.id)


@then('enrollment is rejected because the subject is not in the plan')
def rejected_not_in_plan(state: State) -> None:
    assert isinstance(state.error, SubjectNotInPlanError)


@then('enrollment is rejected because the term is wrong')
def rejected_wrong_term(state: State) -> None:
    assert isinstance(state.error, WrongTermError)


@then('enrollment is rejected because they already have that subject')
def rejected_duplicate(state: State) -> None:
    assert isinstance(state.error, DuplicateSubjectEnrollmentError)


@then('enrollment is rejected because they are not a student')
def rejected_not_a_student(state: State) -> None:
    assert isinstance(state.error, NotAStudentError)
