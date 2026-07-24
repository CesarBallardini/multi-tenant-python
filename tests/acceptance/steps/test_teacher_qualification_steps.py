"""Step definitions for teacher qualification."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from pytest_bdd import given, parsers, scenarios, then, when

from academy.domain.academics.course_section import CourseSection
from academy.domain.academics.term import Term
from academy.domain.people.credential import Credential
from academy.domain.people.email import Email
from academy.domain.people.person import Person
from academy.domain.people.personal_data import PersonalData
from academy.domain.people.role import Role
from academy.domain.services.course_section_factory import (
    CourseSectionFactory,
    NotATeacherError,
    TeacherNotQualifiedError,
)
from academy.domain.shared.errors import DomainError
from academy.domain.shared.ids import CredentialId, PersonId, SectionId, SubjectId

scenarios('../features/teacher_qualification.feature')

_SUBJECTS = {'Maths': SubjectId(UUID(int=1)), 'History': SubjectId(UUID(int=2))}
_CREDENTIAL = CredentialId(UUID(int=10))
_TERM = Term(2026, 1)
_SECTION = SectionId(UUID(int=50))


@dataclass
class State:
    teacher: Person
    credentials: list[Credential]
    section: CourseSection | None = None
    error: DomainError | None = None


def _teacher(roles: set[Role]) -> Person:
    return Person(PersonId(UUID(int=100)), Email('t@example.com'), PersonalData('T', date(2000, 1, 1)), roles=roles)


@given(parsers.parse('a teacher credentialed to teach "{subject}"'), target_fixture='state')
def teacher_credentialed(subject: str) -> State:
    teacher = _teacher({Role.TEACHER})
    teacher.hold_credential(_CREDENTIAL)
    return State(teacher=teacher, credentials=[Credential(_CREDENTIAL, subject, {_SUBJECTS[subject]})])


@given('a person who is not a teacher', target_fixture='state')
def not_a_teacher() -> State:
    return State(teacher=_teacher(set()), credentials=[])


@when(parsers.parse('a "{subject}" section is created for the teacher'))
@when(parsers.parse('a "{subject}" section is created for that person'))
def create_section(state: State, subject: str) -> None:
    try:
        state.section = CourseSectionFactory().create(
            _SECTION, _SUBJECTS[subject], _TERM, state.teacher, state.credentials
        )
    except DomainError as exc:
        state.error = exc


@then('the section is created')
def section_created(state: State) -> None:
    assert state.error is None
    assert state.section is not None


@then('the assignment is rejected because the teacher is not qualified')
def rejected_not_qualified(state: State) -> None:
    assert isinstance(state.error, TeacherNotQualifiedError)


@then('the assignment is rejected because they are not a teacher')
def rejected_not_a_teacher(state: State) -> None:
    assert isinstance(state.error, NotATeacherError)
