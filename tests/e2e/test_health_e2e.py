"""End-to-end smoke test: the API is reachable over real HTTP.

Part of the always-on smoke set: tagged ``smoke`` so it is never deselected.
"""

import httpx
import pytest


@pytest.mark.e2e
@pytest.mark.smoke
def test_health_endpoint_is_reachable(live_server: str) -> None:
    response = httpx.get(f'{live_server}/health', timeout=5)

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
