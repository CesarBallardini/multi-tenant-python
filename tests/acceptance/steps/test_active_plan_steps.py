"""Step definitions for the one-active-plan-per-program invariant."""

from dataclasses import dataclass
from uuid import UUID

from pytest_bdd import given, parsers, scenarios, then, when

from academy.domain.academics.degree_program import DegreeProgram
from academy.domain.academics.plan import Plan
from academy.domain.shared.ids import PlanId, ProgramId

scenarios('../features/active_plan.feature')

_PLANS = {'A': PlanId(UUID(int=10)), 'B': PlanId(UUID(int=11))}


@dataclass
class State:
    program: DegreeProgram


@given(parsers.parse('a program with plans "{a}" and "{b}"'), target_fixture='state')
def program_with_plans(a: str, b: str) -> State:
    program = DegreeProgram(ProgramId(UUID(int=1)), 'Engineering')
    program.add_plan(Plan(_PLANS[a]))
    program.add_plan(Plan(_PLANS[b]))
    return State(program=program)


@given(parsers.parse('a program with an active plan "{name}"'), target_fixture='state')
def program_with_active_plan(name: str) -> State:
    program = DegreeProgram(ProgramId(UUID(int=1)), 'Engineering')
    program.add_plan(Plan(_PLANS[name], active=True))
    return State(program=program)


@when(parsers.parse('plan "{name}" is activated'))
def activate_plan(state: State, name: str) -> None:
    state.program.activate_plan(_PLANS[name])


@when(parsers.parse('an active plan "{name}" is added'))
def add_active_plan(state: State, name: str) -> None:
    state.program.add_plan(Plan(_PLANS[name], active=True))


@then(parsers.parse('plan "{name}" is the active plan'))
def is_the_active_plan(state: State, name: str) -> None:
    active = state.program.active_plan()
    assert active is not None
    assert active.id == _PLANS[name]


@then(parsers.parse('plan "{name}" is not active'))
def is_not_active(state: State, name: str) -> None:
    assert not state.program.plan(_PLANS[name]).active
