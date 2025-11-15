"""Integration adapter utilities for external incident trackers."""

from .incident_sync_adapter import IncidentSyncAdapter, IncidentSyncPayload
from .null_incident_adapter import NullIncidentSyncAdapter

__all__ = [
    'IncidentSyncAdapter',
    'IncidentSyncPayload',
    'NullIncidentSyncAdapter',
]
