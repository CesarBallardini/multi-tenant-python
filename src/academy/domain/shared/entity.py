"""Base class for identity-based domain entities."""

from __future__ import annotations

from typing import Any


class Entity:
    """Base for entities: equality and hashing are based on identity, not attributes.

    Two entities are equal when they are of the same concrete type and share the same
    ``id``. Subclasses must assign ``id`` in their initializer.
    """

    id: Any

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` is the same entity (same concrete type and id)."""
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__(self) -> int:
        """Hash by concrete type and id, so entities work as set members and dict keys."""
        return hash((type(self), self.id))
