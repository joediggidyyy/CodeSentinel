"""
CodeSentinel Utilities Package

Core utility modules providing shared functionality for CodeSentinel:
- session_memory: Session-level caching and decision logging
- oracl_context_tier: Mid-term context aggregation (7-day rolling window)
- archive_decision_provider: Historical decision intelligence provider
- file_integrity: SHA-256 file verification and integrity monitoring
- alerts: Alert management and notification handling
- config: Configuration management and loading
- scheduler: Task scheduling and automation

Lazy imports to avoid circular dependencies during package initialization.
"""

__all__ = [
    'SessionMemory',
    'FileIntegrityValidator',
    'AlertManager',
    'ConfigManager',
]
