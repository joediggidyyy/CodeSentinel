"""Null implementation of IncidentSyncAdapter for environments without outbound connectors."""

from __future__ import annotations

import logging
from typing import Dict, Any

from .incident_sync_adapter import IncidentSyncAdapter, IncidentSyncPayload


class NullIncidentSyncAdapter(IncidentSyncAdapter):
    """No-op adapter that keeps call sites stable while integrations are disabled."""

    def __init__(self):
        super().__init__(config={"enabled": False})
        self.logger = logging.getLogger('NullIncidentSyncAdapter')

    def prepare_payload(self, event: Dict[str, Any]) -> IncidentSyncPayload:
        summary = event.get('title') or event.get('event_id', 'unknown')
        payload = IncidentSyncPayload(
            event_id=event.get('event_id', 'UNKNOWN'),
            severity=event.get('severity', 'low').lower(),
            event_type=event.get('event_type', 'incident'),
            summary=summary,
            metadata=event
        )
        self.logger.debug("Prepared placeholder payload for %s", payload.event_id)
        return payload

    def push_event(self, payload: IncidentSyncPayload) -> Dict[str, Any]:
        self.logger.info(
            "[NullAdapter] Skipping outbound sync for %s (severity=%s)",
            payload.event_id,
            payload.severity
        )
        return {"status": "skipped", "provider": "null", "event_id": payload.event_id}

    def audit_log(self, response: Dict[str, Any]) -> None:
        self.logger.debug("[NullAdapter] audit info: %s", response)

    def is_enabled(self) -> bool:
        return False
