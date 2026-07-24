"""Step definitions for recording grades."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from pytest_bdd import given, parsers, scenarios, then, when

from academy.domain.academics.course_section import CourseSection
from academy.domain.academics.term import Term
from academy.domain.grades.academic_history import AcademicHistory
from academy.domain.grades.grade import Grade
from academy.domain.grades.grade_entry import GradeEntry
from academy.domain.people.email import Email
from academy.domain.people.person import Person
from academy.domain.people.personal_data import PersonalData
from academy.domain.people.role import Role
from academy.domain.services.grading_service import (
    GradingService,
    NotTeacherOfSectionError,
    StudentNotEnrolledError,
)
from academy.domain.shared.errors import DomainError
from academy.domain.shared.ids import PersonId, SectionId, SubjectId

scenarios('../features/grading.feature')

_SUBJECTS = {'Maths': SubjectId(UUID(int=1))}
_TEACHERS = {'T': PersonId(UUID(int=100)), 'OTHER': PersonId(UUID(int=101))}
_SECTION = SectionId(UUID(int=50))


@dataclass
class State:
    section: CourseSection
    student: Person
    history: AcademicHistory
    other: Person | None = None
    other_history: AcademicHistory | None = None
    entry: GradeEntry | None = None
    error: DomainError | None = None


def _term(label: str) -> Term:
    year, number = label.split('-T')
    return Term(int(year), int(number))


def _person(person_id: PersonId, roles: set[Role]) -> Person:
    return Person(
        person_id, Email(f'{person_id.value.int}@example.com'), PersonalData('P', date(2000, 1, 1)), roles=roles
    )


@given(parsers.parse('a "{subject}" section taught by teacher "{name}" in "{label}"'), target_fixture='state')
def a_section(subject: str, name: str, label: str) -> State:
    section = CourseSection(_SECTION, _SUBJECTS[subject], _term(label), _TEACHERS[name])
    student = _person(PersonId(UUID(int=200)), {Role.STUDENT})
    return State(section=section, student=student, history=AcademicHistory(student.id))


@given('a student enrolled in the section')
def enroll_student(state: State) -> None:
    state.section.enroll(state.student.id)


@given('another student who is not enrolled')
def another_student(state: State) -> None:
    other = _person(PersonId(UUID(int=201)), {Role.STUDENT})
    state.other = other
    state.other_history = AcademicHistory(other.id)


@when(parsers.parse('teacher "{name}" records a grade of {value:d} for the student'))
def grade_the_student(state: State, name: str, value: int) -> None:
    teacher = _person(_TEACHERS[name], {Role.TEACHER})
    try:
        state.entry = GradingService().record_grade(
            state.section, teacher, state.student.id, Grade(value), state.history
        )
    except DomainError as exc:
        state.error = exc


@when(parsers.parse('teacher "{name}" records a grade of {value:d} for the other student'))
def grade_the_other_student(state: State, name: str, value: int) -> None:
    teacher = _person(_TEACHERS[name], {Role.TEACHER})
    other = state.other
    history = state.other_history
    assert other is not None
    assert history is not None
    try:
        state.entry = GradingService().record_grade(state.section, teacher, other.id, Grade(value), history)
    except DomainError as exc:
        state.error = exc


@then("the grade is recorded in the student's history")
def grade_recorded(state: State) -> None:
    assert state.error is None
    assert state.entry is not None
    assert state.entry in state.history.entries


@then(parsers.parse('the best grade for "{subject}" is {value:d}'))
def best_grade_is(state: State, subject: str, value: int) -> None:
    assert state.history.best_grade(_SUBJECTS[subject]) == Grade(value)


@then('grading is rejected because they do not teach the section')
def rejected_not_teacher_of_section(state: State) -> None:
    assert isinstance(state.error, NotTeacherOfSectionError)


@then('grading is rejected because the student is not enrolled')
def rejected_not_enrolled(state: State) -> None:
    assert isinstance(state.error, StudentNotEnrolledError)
