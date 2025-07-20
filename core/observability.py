"""
Observability utilities for the application
"""
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

def get_opik_handler():
    """Get Opik handler for LLM observability"""
    try:
        from opik.integrations.langchain import OpikTracer
        return OpikTracer()
    except ImportError:
        logger.warning("Opik not available, using no-op handler")
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize Opik handler: {e}")
        return None