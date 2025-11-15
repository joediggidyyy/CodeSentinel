"""Abstractions for syncing ORACall events into external incident trackers."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class IncidentSyncPayload:
    """Structured payload describing an ORACall event destined for an external tracker."""

    event_id: str
    severity: str
    event_type: str
    summary: str
    metadata: Dict[str, Any]


class IncidentSyncAdapter(abc.ABC):
    """Base class for outbound integrations (Jira, ServiceNow, etc.)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abc.abstractmethod
    def prepare_payload(self, event: Dict[str, Any]) -> IncidentSyncPayload:
        """Convert an ORACall event dict into a structured payload ready for transmission."""

    @abc.abstractmethod
    def push_event(self, payload: IncidentSyncPayload) -> Dict[str, Any]:
        """Send the payload to the target system and return a response dictionary."""

    @abc.abstractmethod
    def audit_log(self, response: Dict[str, Any]) -> None:
        """Persist a lightweight audit trail for compliance (console/log for now)."""

    def is_enabled(self) -> bool:
        """Adapters may override to embed custom enablement logic based on config."""
        return bool(self.config.get('enabled'))
