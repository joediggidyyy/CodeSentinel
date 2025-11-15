"""
CLI Metrics Wrapper
===================

Wraps CLI command execution to automatically track metrics.
Integrates with agent_metrics.py for comprehensive tracking.
"""

import time
import functools
from typing import Any, Callable, Dict, Optional
from .agent_metrics import get_metrics


def track_cli_command(command_name: str):
    """
    Decorator to track CLI command execution.
    
    Usage:
        @track_cli_command('clean')
        def handle_clean_command(args, codesentinel):
            # command implementation
            return result
    
    Automatically logs:
    - Command name and arguments
    - Success/failure status
    - Execution duration
    - Errors (if any)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            metrics = get_metrics()
            success = False
            error = None
            result = None
            
            # Extract args for logging
            arg_dict = {}
            if args:
                # First arg is typically argparse.Namespace
                arg_obj = args[0] if len(args) > 0 else None
                if hasattr(arg_obj, '__dict__'):
                    arg_dict = {k: v for k, v in vars(arg_obj).items() if not k.startswith('_')}
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            
            except Exception as e:
                success = False
                error = str(e)
                raise
            
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                # Extract metadata from result if available
                metadata = {}
                if isinstance(result, dict):
                    metadata = {k: v for k, v in result.items() if k in ['files_processed', 'items_found', 'changes_made']}
                
                # Log to metrics
                metrics.log_cli_command(
                    command=command_name,
                    args=arg_dict,
                    success=success,
                    duration_ms=duration_ms,
                    error=error,
                    metadata=metadata
                )
                
                # Flush buffer to ensure data is written before command exits
                metrics._flush_buffer()
        
        return wrapper
    return decorator


def track_security_event(
    event_type: str,
    severity: str,
    description: str,
    threshold: str = 'medium',
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Log security event with automatic elevation logic.
    
    Args:
        event_type: Type of security event
        severity: low, medium, high, critical
        description: Human-readable description
        threshold: Minimum severity to elevate to user
        metadata: Additional context
        
    Returns:
        True if elevated to user, False if only noted
    """
    metrics = get_metrics()
    
    # Severity ranking
    severity_rank = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    threshold_rank = severity_rank.get(threshold, 2)
    event_rank = severity_rank.get(severity, 1)
    
    # Determine if elevated
    elevated = event_rank >= threshold_rank
    
    # Always log (both elevated and noted)
    metrics.log_security_event(
        event_type=event_type,
        severity=severity,
        description=description,
        elevated=elevated,
        metadata=metadata
    )
    
    return elevated


def track_agent_decision(
    decision_type: str,
    recommendation: str,
    user_action: str,
    confidence: float = 0.0,
    outcome: str = 'pending',
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log agent decision for ORACL learning curve tracking.
    
    Args:
        decision_type: Type of decision
        recommendation: What agent recommended
        user_action: accepted, rejected, modified, deferred
        confidence: ORACL confidence score
        outcome: success, failure, pending
        metadata: Additional context
    """
    metrics = get_metrics()
    metrics.log_agent_decision(
        decision_type=decision_type,
        recommendation=recommendation,
        user_action=user_action,
        confidence=confidence,
        outcome=outcome,
        metadata=metadata
    )


def track_oracl_query(
    query_type: str,
    confidence: float,
    cache_hit: bool,
    latency_ms: float,
    result_count: int = 0,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log ORACL query for performance tracking.
    
    Args:
        query_type: Type of query
        confidence: Returned confidence score
        cache_hit: Whether cached
        latency_ms: Query latency
        result_count: Number of results
        metadata: Additional context
    """
    metrics = get_metrics()
    metrics.log_oracl_query(
        query_type=query_type,
        confidence=confidence,
        cache_hit=cache_hit,
        latency_ms=latency_ms,
        result_count=result_count,
        metadata=metadata
    )


def track_performance_metric(
    metric_type: str,
    value: float,
    unit: str,
    baseline: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log performance metric.
    
    Args:
        metric_type: Type of metric
        value: Measured value
        unit: Unit of measurement
        baseline: Baseline for comparison
        metadata: Additional context
    """
    metrics = get_metrics()
    
    improvement_pct = None
    if baseline is not None and baseline > 0:
        improvement_pct = ((baseline - value) / baseline) * 100
    
    metrics.log_performance_metric(
        metric_type=metric_type,
        value=value,
        unit=unit,
        baseline=baseline,
        improvement_pct=improvement_pct,
        metadata=metadata
    )


def log_engineer_feedback(
    feedback_type: str,
    message: str,
    intensity: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Record engineer feedback and propagate collaboration boosts."""
    metrics = get_metrics()
    metrics.log_engineer_feedback(
        feedback_type=feedback_type,
        message=message,
        intensity=intensity,
        metadata=metadata
    )
