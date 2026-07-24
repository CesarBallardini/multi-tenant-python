"""FastAPI application factory (inbound API adapter)."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Build and return the FastAPI application.

    This is the composition seam for the inbound API: routers and dependencies are wired
    here. For now it exposes only a liveness probe.
    """
    app = FastAPI(title='academy', version='0.1.0')

    @app.get('/health')
    def health() -> dict[str, str]:
        """Liveness probe: return a static ok status."""
        return {'status': 'ok'}

    return app
