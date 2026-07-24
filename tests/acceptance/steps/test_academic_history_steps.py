"""Step definitions for the best-attempt-counts rule in the academic history."""

from dataclasses import dataclass
from uuid import UUID

from pytest_bdd import given, parsers, scenarios, then, when

from academy.domain.academics.term import Term
from academy.domain.grades.academic_history import AcademicHistory
from academy.domain.grades.grade import Grade
from academy.domain.grades.grade_entry import GradeEntry
from academy.domain.shared.ids import PersonId, SubjectId

scenarios('../features/academic_history.feature')

_SUBJECTS = {'Maths': SubjectId(UUID(int=1))}
_TERM = Term(2026, 1)


@dataclass
class State:
    history: AcademicHistory


@given('an empty academic history', target_fixture='state')
def empty_history() -> State:
    return State(history=AcademicHistory(PersonId(UUID(int=200))))


@when(parsers.parse('a grade of {value:d} is recorded for "{subject}"'))
def record_grade(state: State, value: int, subject: str) -> None:
    state.history.record(GradeEntry(_SUBJECTS[subject], _TERM, Grade(value)))


@then(parsers.parse('the best grade for "{subject}" is {value:d}'))
def best_grade_is(state: State, subject: str, value: int) -> None:
    assert state.history.best_grade(_SUBJECTS[subject]) == Grade(value)


@then(parsers.parse('"{subject}" is passed'))
def subject_is_passed(state: State, subject: str) -> None:
    assert state.history.has_passed(_SUBJECTS[subject])


@then(parsers.parse('"{subject}" is not passed'))
def subject_is_not_passed(state: State, subject: str) -> None:
    assert not state.history.has_passed(_SUBJECTS[subject])
