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

OPIK_ENDPOINT = settings.opik_endpoint
logger = logging.getLogger(__name__)

# Global flag to track if Opik is available
_opik_available = None

def _check_opik_availability() -> bool:
    """Check if Opik endpoint is available."""
    global _opik_available
    if _opik_available is not None:
        return _opik_available
    
    try:
        response = requests.get(OPIK_ENDPOINT.replace('/trace', '/health'), timeout=1)
        _opik_available = response.status_code == 200
    except Exception:
        _opik_available = False
    
    return _opik_available

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
    if not _check_opik_availability():
        logger.debug(f"Opik not available, skipping trace: {event}")
        return
    
    payload = {
        "timestamp": time.time(),
        "event": event,
        "host": _hostname(),
        "details": details or {},
    }
    
    try:
        response = requests.post(OPIK_ENDPOINT, json=payload, timeout=1)
        if response.status_code != 200:
            logger.debug(f"Opik trace failed with status {response.status_code}")
    except Exception as exc:
        logger.debug(f"Opik trace failed: {exc}")
        # Mark as unavailable to avoid repeated failures
        global _opik_available
        _opik_available = False
