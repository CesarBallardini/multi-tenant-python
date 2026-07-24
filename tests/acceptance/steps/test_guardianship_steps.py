"""Step definitions for computed-on-read guardianship."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from pytest_bdd import given, parsers, scenarios, then, when

from academy.domain.guardianship.guardianship import Guardianship, SelfGuardianshipError
from academy.domain.people.age_of_majority import AgeOfMajority
from academy.domain.people.email import Email
from academy.domain.people.person import Person
from academy.domain.people.personal_data import PersonalData
from academy.domain.shared.errors import DomainError
from academy.domain.shared.ids import GuardianshipId, PersonId

scenarios('../features/guardianship.feature')

_GUARDIAN = PersonId(UUID(int=1))
_WARD = PersonId(UUID(int=2))
_GUARDIANSHIP = GuardianshipId(UUID(int=9))


@dataclass
class State:
    majority: AgeOfMajority
    today: date = date(2026, 1, 1)
    ward: Person | None = None
    guardianship: Guardianship | None = None
    error: DomainError | None = None


@given(parsers.parse('the age of majority is {years:d}'), target_fixture='state')
def the_age_of_majority(years: int) -> State:
    return State(majority=AgeOfMajority(years))


@given(parsers.parse('today is "{on}"'))
def today_is(state: State, on: str) -> None:
    state.today = date.fromisoformat(on)


@given(parsers.parse('a ward born on "{on}"'))
def a_ward(state: State, on: str) -> None:
    state.ward = Person(_WARD, Email('w@example.com'), PersonalData('W', date.fromisoformat(on)))
    state.guardianship = Guardianship(_GUARDIANSHIP, _GUARDIAN, _WARD)


@when('a guardianship links a person to themselves')
def self_guardianship(state: State) -> None:
    try:
        Guardianship(_GUARDIANSHIP, _GUARDIAN, _GUARDIAN)
    except DomainError as exc:
        state.error = exc


@then('the guardianship applies')
def guardianship_applies(state: State) -> None:
    assert state.guardianship is not None
    assert state.ward is not None
    assert state.guardianship.applies(state.ward, state.majority, state.today)


@then('the guardianship does not apply')
def guardianship_does_not_apply(state: State) -> None:
    assert state.guardianship is not None
    assert state.ward is not None
    assert not state.guardianship.applies(state.ward, state.majority, state.today)


@then('it is rejected as self-guardianship')
def rejected_self_guardianship(state: State) -> None:
    assert isinstance(state.error, SelfGuardianshipError)
