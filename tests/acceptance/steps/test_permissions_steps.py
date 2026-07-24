"""Step definitions for the roles-and-permissions features (against AccessPolicy)."""

from collections.abc import Set
from uuid import UUID

from pytest_bdd import given, parsers, scenarios, then, when

from academy.domain.authorization.models import (
    AccessDecision,
    AccessRequest,
    Action,
    Relation,
    ResourceType,
)
from academy.domain.authorization.policy import AccessPolicy
from academy.domain.shared.ids import PersonId

scenarios(
    '../features/grades_permissions.feature',
    '../features/academic_history_permissions.feature',
)

_ACTOR = PersonId(UUID(int=1))
_OWNER = PersonId(UUID(int=2))

_RELATIONS: dict[str, Relation] = {
    'self': Relation.SELF,
    'teacher_of_section': Relation.TEACHER_OF_SECTION,
    'guardian_of': Relation.GUARDIAN_OF,
    'administrator': Relation.ADMINISTRATOR,
}
_ACTIONS: dict[str, Action] = {'read': Action.READ, 'write': Action.WRITE}


def _decide(relations: Set[Relation], action: str, resource: ResourceType) -> AccessDecision:
    request = AccessRequest(_ACTOR, _ACTIONS[action], resource, _OWNER, relations=frozenset(relations))
    return AccessPolicy().decide(request)


@given(parsers.parse('an actor related to the record owner as "{relation_names}"'), target_fixture='relations')
def actor_with_relations(relation_names: str) -> set[Relation]:
    return {_RELATIONS[name.strip()] for name in relation_names.split(',')}


@given('an actor with no relationship to the record owner', target_fixture='relations')
def actor_with_no_relation() -> set[Relation]:
    return set()


@when(parsers.parse('the actor requests to "{action}" the grades'), target_fixture='decision')
def request_grades(relations: Set[Relation], action: str) -> AccessDecision:
    return _decide(relations, action, ResourceType.GRADES)


@when(parsers.parse('the actor requests to "{action}" the academic history'), target_fixture='decision')
def request_academic_history(relations: Set[Relation], action: str) -> AccessDecision:
    return _decide(relations, action, ResourceType.ACADEMIC_HISTORY)


@then(parsers.parse('access is "{outcome}"'))
def access_is(decision: AccessDecision, outcome: str) -> None:
    assert decision.allowed is (outcome == 'allowed')
