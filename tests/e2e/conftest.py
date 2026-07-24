"""Fixtures for end-to-end tests: a real uvicorn server hit over real HTTP.

This is the thin e2e tier: it boots the actual ASGI app on a live socket, exactly as a
curl or a Python-script client would reach it. Kept small and smoke-level on purpose.
"""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator

import httpx
import pytest
import uvicorn

from academy.adapters.inbound.api.app import create_app


class _ThreadedServer(uvicorn.Server):
    """A uvicorn server that can run off the main thread (no signal handlers)."""

    def install_signal_handlers(self) -> None:
        return


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        return probe.getsockname()[1]


def _wait_until_ready(base_url: str, attempts: int = 100) -> None:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            if httpx.get(f'{base_url}/health', timeout=0.5).status_code == 200:
                return
        except httpx.HTTPError as error:
            last_error = error
        time.sleep(0.05)
    raise RuntimeError(f'server did not become ready in time: {last_error}')


@pytest.fixture
def live_server() -> Iterator[str]:
    port = _free_port()
    config = uvicorn.Config(create_app(), host='127.0.0.1', port=port, log_level='warning')
    server = _ThreadedServer(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{port}'
    try:
        _wait_until_ready(url)
        yield url
    finally:
        server.should_exit = True
        thread.join(timeout=5)
