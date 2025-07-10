"""Lightweight Opik tracing utility.
Sends JSON events to a local Opik collector.
If the collector is unavailable, it logs a warning and continues.
"""
from __future__ import annotations

import json
import logging
import socket
import time
from typing import Any, Dict
from config.settings import settings
import requests

OPIK_ENDPOINT = settings.opik_endpoint  # default Opik listener
logger = logging.getLogger(__name__)

def _hostname() -> str:
    try:
        return socket.gethostname()
    except Exception:
        return "unknown-host"

def trace(event: str, details: Dict[str, Any] | None = None) -> None:
    """Send a trace event to Opik.

    Parameters
    ----------
    event : str
        A short name describing the event.
    details : dict | None
        Optional extra JSON-serialisable information.
    """
    payload = {
        "timestamp": time.time(),
        "event": event,
        "host": _hostname(),
        "details": details or {},
    }
    try:
        requests.post(OPIK_ENDPOINT, json=payload, timeout=0.5)
    except Exception as exc:
        # Fall back to log; we don't want instrumentation to break the app.
        logger.debug("Opik trace failed: %s", exc)
