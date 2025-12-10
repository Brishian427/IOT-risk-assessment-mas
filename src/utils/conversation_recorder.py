"""
Conversation Recorder - Capture per-message prompts and responses for audit
Created: 2025-01-XX
"""

import contextvars
from datetime import datetime
from typing import Dict, Any, List

# Context variable to hold conversation log per run
_conversation_log: contextvars.ContextVar[List[Dict[str, Any]]] = contextvars.ContextVar(
    "conversation_log", default=[]
)


def start_run() -> None:
    """Initialize conversation log for a new run"""
    _conversation_log.set([])


def record(
    stage: str,
    role: str,
    model: str,
    prompt: str,
    response: str,
    revision: int = 0,
    extra: Dict[str, Any] = None,
) -> None:
    """Record a single prompt/response pair"""
    log = _conversation_log.get()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "role": role,
        "model": model,
        "revision": revision,
        "prompt": prompt,
        "response": response,
    }
    if extra:
        entry.update(extra)
    log.append(entry)
    _conversation_log.set(log)


def get_records() -> List[Dict[str, Any]]:
    """Get current conversation records"""
    return list(_conversation_log.get())


def end_run() -> List[Dict[str, Any]]:
    """End run and return all records"""
    records = list(_conversation_log.get())
    _conversation_log.set([])
    return records


