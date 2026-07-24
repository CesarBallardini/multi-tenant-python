"""Binds the API-level acceptance features.

These features are tagged ``@skip`` because they exercise the HTTP API, which needs the
application and adapter layers not yet built. Binding them here keeps them collected (and
visibly skipped) so the intended acceptance criteria are tracked, not forgotten. Step
definitions are added when the API lands.
"""

from pytest_bdd import scenarios

scenarios(
    '../features/api_role_capabilities.feature',
    '../features/api_tenant_isolation.feature',
    '../features/api_deletion_semantics.feature',
    '../features/api_plan_grandfathering.feature',
)
