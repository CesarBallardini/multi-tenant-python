"""Self-served, relationship-based access policy (the domain's decision point)."""

from __future__ import annotations

from academy.domain.authorization.models import (
    AccessDecision,
    AccessRequest,
    Action,
    Relation,
    ResourceType,
)

_R = ResourceType
_A = Action

# The grant matrix: for each relation, the (resource, action) pairs it permits.
_GRANTS: dict[Relation, frozenset[tuple[ResourceType, Action]]] = {
    Relation.SELF: frozenset({(_R.GRADES, _A.READ), (_R.ACADEMIC_HISTORY, _A.READ)}),
    Relation.TEACHER_OF_SECTION: frozenset({(_R.GRADES, _A.READ), (_R.GRADES, _A.WRITE)}),
    Relation.GUARDIAN_OF: frozenset({(_R.GRADES, _A.READ), (_R.ACADEMIC_HISTORY, _A.READ)}),
    Relation.ADMINISTRATOR: frozenset({(_R.GRADES, _A.READ), (_R.ACADEMIC_HISTORY, _A.READ)}),
}


class AccessPolicy:
    """Pure authorization policy: decides allow/deny from a resolved access request.

    The policy is a pure function of its inputs (actor's resolved relations plus the
    requested resource and action). Resolving which relations hold is the application's
    job; this class contains no I/O and never reads a repository.
    """

    def decide(self, request: AccessRequest) -> AccessDecision:
        """Decide whether ``request`` is allowed under the grant matrix."""
        wanted = (request.resource, request.action)
        for relation in request.relations:
            if wanted in _GRANTS.get(relation, frozenset()):
                return AccessDecision.allow(f'granted by {relation.value}')
        return AccessDecision.deny('no relation grants this action on this resource')
