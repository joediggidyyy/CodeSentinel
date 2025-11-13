"""
Agent Metrics & Performance Tracking
=====================================

Comprehensive tracking of agent operations, CLI commands, errors, and learning curve.
All metrics feed into ORACL intelligence and enable performance gain reporting.

Tracks:
- CLI command execution (success/failure, duration, errors)
- Agent decisions and remediation outcomes
- ORACL confidence evolution over time
- Error patterns and recovery strategies
- Security events (logged but not elevated based on threshold)
- Performance metrics (cache hits, query latency, efficiency gains)

Data Storage:
- docs/metrics/agent_operations.jsonl (append-only)
- docs/metrics/performance_summary.json (daily rollup)
- docs/metrics/security_events.jsonl (elevated + noted)
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class AgentMetrics:
    """
    Tracks all agent operations and performance metrics.
    
    Design Principles:
    - Zero data loss (everything logged)
    - Security events tagged but always logged
    - Append-only for audit trail
    - Aggregation for reporting
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize agent metrics tracker."""
        self.workspace_root = workspace_root or Path.cwd()
        self.metrics_dir = self.workspace_root / "docs" / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Metrics files
        self.operations_log = self.metrics_dir / "agent_operations.jsonl"
        self.performance_summary = self.metrics_dir / "performance_summary.json"
        self.security_events_log = self.metrics_dir / "security_events.jsonl"
        self.error_patterns_log = self.metrics_dir / "error_patterns.jsonl"
        
        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.session_start = time.time()
        
    def log_cli_command(
        self,
        command: str,
        args: Dict[str, Any],
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log CLI command execution.
        
        Args:
            command: Command name (e.g., 'clean', 'update', 'memory')
            args: Command arguments and flags
            success: Whether command succeeded
            duration_ms: Execution time in milliseconds
            error: Error message if failed
            metadata: Additional context (files processed, items found, etc.)
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'event_type': 'cli_command',
            'command': command,
            'args': args,
            'success': success,
            'duration_ms': round(duration_ms, 2),
            'error': error,
            'metadata': metadata or {}
        }
        
        self._append_to_log(self.operations_log, record)
        
        # If error, also log to error patterns
        if not success and error:
            self.log_error_pattern(
                error_type='cli_command_failure',
                command=command,
                error_message=error,
                context=args
            )
    
    def log_agent_decision(
        self,
        decision_type: str,
        recommendation: str,
        user_action: str,
        confidence: float,
        outcome: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log agent decision and outcome.
        
        Args:
            decision_type: Type of decision (cleanup, remediation, optimization)
            recommendation: What agent recommended
            user_action: What user did (accepted, rejected, modified)
            confidence: ORACL confidence score (0.0-1.0)
            outcome: Result (success, failure, deferred)
            metadata: Additional context
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'event_type': 'agent_decision',
            'decision_type': decision_type,
            'recommendation': recommendation,
            'user_action': user_action,
            'confidence': round(confidence, 3),
            'outcome': outcome,
            'metadata': metadata or {}
        }
        
        self._append_to_log(self.operations_log, record)
    
    def log_oracl_query(
        self,
        query_type: str,
        confidence: float,
        cache_hit: bool,
        latency_ms: float,
        result_count: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log ORACL intelligence query.
        
        Args:
            query_type: Type of query (domain_guidance, search_history, decision_context)
            confidence: Returned confidence score
            cache_hit: Whether result was cached
            latency_ms: Query execution time
            result_count: Number of results returned
            metadata: Additional context
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'event_type': 'oracl_query',
            'query_type': query_type,
            'confidence': round(confidence, 3),
            'cache_hit': cache_hit,
            'latency_ms': round(latency_ms, 2),
            'result_count': result_count,
            'metadata': metadata or {}
        }
        
        self._append_to_log(self.operations_log, record)
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        elevated: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log security event.
        
        CRITICAL: All security events are logged, regardless of severity threshold.
        Events below threshold are tagged as 'noted' but not elevated to user.
        
        Args:
            event_type: Type of event (policy_violation, credential_leak, vulnerability)
            severity: low, medium, high, critical
            description: Human-readable description
            elevated: Whether event was shown to user (based on threshold)
            metadata: Additional context (file paths, patterns, etc.)
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'event_type': 'security_event',
            'security_event_type': event_type,
            'severity': severity,
            'description': description,
            'elevated': elevated,  # True if shown to user, False if only logged
            'status': 'elevated' if elevated else 'noted',  # Annotation for filtering
            'metadata': metadata or {}
        }
        
        self._append_to_log(self.security_events_log, record)
        
        # Also log to main operations log
        self._append_to_log(self.operations_log, record)
    
    def log_error_pattern(
        self,
        error_type: str,
        command: Optional[str],
        error_message: str,
        context: Dict[str, Any],
        recovery_attempted: bool = False,
        recovery_success: bool = False
    ) -> None:
        """
        Log error pattern for analysis.
        
        Args:
            error_type: Category of error
            command: Command that failed (if CLI)
            error_message: Full error message
            context: Context when error occurred
            recovery_attempted: Whether recovery was attempted
            recovery_success: Whether recovery succeeded
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'event_type': 'error_pattern',
            'error_type': error_type,
            'command': command,
            'error_message': error_message,
            'context': context,
            'recovery_attempted': recovery_attempted,
            'recovery_success': recovery_success
        }
        
        self._append_to_log(self.error_patterns_log, record)
    
    def log_performance_metric(
        self,
        metric_type: str,
        value: float,
        unit: str,
        baseline: Optional[float] = None,
        improvement_pct: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log performance metric.
        
        Args:
            metric_type: Type of metric (cache_hit_rate, query_latency, etc.)
            value: Measured value
            unit: Unit of measurement (%, ms, MB, etc.)
            baseline: Baseline value for comparison
            improvement_pct: Percentage improvement over baseline
            metadata: Additional context
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'event_type': 'performance_metric',
            'metric_type': metric_type,
            'value': value,
            'unit': unit,
            'baseline': baseline,
            'improvement_pct': improvement_pct,
            'metadata': metadata or {}
        }
        
        self._append_to_log(self.operations_log, record)
    
    def _append_to_log(self, log_file: Path, record: Dict[str, Any]) -> None:
        """Append record to JSONL log file."""
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record) + '\n')
        except IOError as e:
            logger.error(f"Failed to write to {log_file}: {e}")
    
    def generate_performance_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate performance report from metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict containing performance summary
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Counters
        cli_commands = Counter()
        cli_success = 0
        cli_failure = 0
        oracl_queries = 0
        oracl_cache_hits = 0
        agent_decisions = []
        security_events_elevated = 0
        security_events_noted = 0
        error_patterns = Counter()
        
        # Performance metrics
        durations = []
        latencies = []
        
        # Read operations log
        if self.operations_log.exists():
            with open(self.operations_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(record['timestamp'])
                        
                        if timestamp < cutoff_date:
                            continue
                        
                        event_type = record.get('event_type')
                        
                        if event_type == 'cli_command':
                            cli_commands[record['command']] += 1
                            if record['success']:
                                cli_success += 1
                            else:
                                cli_failure += 1
                            durations.append(record.get('duration_ms', 0))
                        
                        elif event_type == 'oracl_query':
                            oracl_queries += 1
                            if record.get('cache_hit'):
                                oracl_cache_hits += 1
                            latencies.append(record.get('latency_ms', 0))
                        
                        elif event_type == 'agent_decision':
                            agent_decisions.append(record)
                        
                        elif event_type == 'security_event':
                            if record.get('elevated'):
                                security_events_elevated += 1
                            else:
                                security_events_noted += 1
                    
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        # Read error patterns
        if self.error_patterns_log.exists():
            with open(self.error_patterns_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(record['timestamp'])
                        
                        if timestamp < cutoff_date:
                            continue
                        
                        error_patterns[record.get('error_type', 'unknown')] += 1
                    
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        # Calculate metrics
        cli_total = cli_success + cli_failure
        cli_success_rate = (cli_success / cli_total) if cli_total > 0 else 0.0
        oracl_cache_hit_rate = (oracl_cache_hits / oracl_queries) if oracl_queries > 0 else 0.0
        avg_command_duration = (sum(durations) / len(durations)) if durations else 0.0
        avg_oracl_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
        
        # ORACL learning curve (confidence over time)
        confidence_trend = [d['confidence'] for d in agent_decisions if 'confidence' in d]
        avg_confidence = (sum(confidence_trend) / len(confidence_trend)) if confidence_trend else 0.0
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'time_window_days': days,
            'cli_metrics': {
                'total_commands': cli_total,
                'success_count': cli_success,
                'failure_count': cli_failure,
                'success_rate': round(cli_success_rate, 3),
                'avg_duration_ms': round(avg_command_duration, 2),
                'command_breakdown': dict(cli_commands.most_common())
            },
            'oracl_metrics': {
                'total_queries': oracl_queries,
                'cache_hits': oracl_cache_hits,
                'cache_hit_rate': round(oracl_cache_hit_rate, 3),
                'avg_latency_ms': round(avg_oracl_latency, 2),
                'avg_confidence': round(avg_confidence, 3),
                'confidence_trend': confidence_trend[-10:]  # Last 10 decisions
            },
            'agent_metrics': {
                'total_decisions': len(agent_decisions),
                'accepted_decisions': sum(1 for d in agent_decisions if d.get('user_action') == 'accepted'),
                'rejected_decisions': sum(1 for d in agent_decisions if d.get('user_action') == 'rejected')
            },
            'security_metrics': {
                'events_elevated': security_events_elevated,
                'events_noted': security_events_noted,
                'total_events': security_events_elevated + security_events_noted
            },
            'error_metrics': {
                'total_errors': sum(error_patterns.values()),
                'error_breakdown': dict(error_patterns.most_common())
            }
        }
        
        # Write summary
        try:
            with open(self.performance_summary, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to write performance summary: {e}")
        
        return report
    
    def get_oracl_learning_curve(self, days: int = 30) -> List[Tuple[str, float]]:
        """
        Get ORACL confidence scores over time (learning curve).
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of (date, avg_confidence) tuples
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        daily_confidences = defaultdict(list)
        
        if self.operations_log.exists():
            with open(self.operations_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(record['timestamp'])
                        
                        if timestamp < cutoff_date:
                            continue
                        
                        if record.get('event_type') == 'agent_decision':
                            date_key = timestamp.strftime('%Y-%m-%d')
                            confidence = record.get('confidence', 0.0)
                            daily_confidences[date_key].append(confidence)
                    
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        # Calculate daily averages
        learning_curve = [
            (date, sum(scores) / len(scores))
            for date, scores in sorted(daily_confidences.items())
        ]
        
        return learning_curve
    
    def print_performance_summary(self, days: int = 7) -> None:
        """Print human-readable performance summary."""
        report = self.generate_performance_report(days)
        
        print("\n" + "="*80)
        print(f"AGENT PERFORMANCE SUMMARY ({days} days)")
        print("="*80)
        
        # CLI Metrics
        cli = report['cli_metrics']
        print(f"\nCLI Commands:")
        print(f"  Total: {cli['total_commands']}")
        print(f"  Success Rate: {cli['success_rate']*100:.1f}%")
        print(f"  Avg Duration: {cli['avg_duration_ms']:.2f}ms")
        
        # ORACL Metrics
        oracl = report['oracl_metrics']
        print(f"\nORACL Intelligence:")
        print(f"  Total Queries: {oracl['total_queries']}")
        print(f"  Cache Hit Rate: {oracl['cache_hit_rate']*100:.1f}%")
        print(f"  Avg Confidence: {oracl['avg_confidence']*100:.0f}%")
        print(f"  Avg Latency: {oracl['avg_latency_ms']:.2f}ms")
        
        # Agent Decisions
        agent = report['agent_metrics']
        print(f"\nAgent Decisions:")
        print(f"  Total: {agent['total_decisions']}")
        print(f"  Accepted: {agent['accepted_decisions']}")
        print(f"  Rejected: {agent['rejected_decisions']}")
        
        # Security Events
        security = report['security_metrics']
        print(f"\nSecurity Events:")
        print(f"  Elevated (shown to user): {security['events_elevated']}")
        print(f"  Noted (logged only): {security['events_noted']}")
        print(f"  Total Tracked: {security['total_events']}")
        
        # Errors
        errors = report['error_metrics']
        print(f"\nErrors:")
        print(f"  Total: {errors['total_errors']}")
        if errors['error_breakdown']:
            print("  Top Patterns:")
            for error_type, count in list(errors['error_breakdown'].items())[:5]:
                print(f"    - {error_type}: {count}")
        
        print("\n" + "="*80 + "\n")


# Global instance for easy access
_metrics_instance = None

def get_metrics() -> AgentMetrics:
    """Get global metrics instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = AgentMetrics()
    return _metrics_instance


if __name__ == '__main__':
    """CLI for generating performance reports."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent Metrics Reporter')
    parser.add_argument('--days', type=int, default=7, help='Days to analyze')
    parser.add_argument('--learning-curve', action='store_true', help='Show ORACL learning curve')
    
    args = parser.parse_args()
    
    metrics = AgentMetrics()
    
    if args.learning_curve:
        curve = metrics.get_oracl_learning_curve(args.days)
        print("\nORACL Learning Curve:")
        print("="*60)
        print(f"{'Date':<12} {'Avg Confidence':<15} {'Trend':<30}")
        print("-"*60)
        for date, confidence in curve:
            bar = '█' * int(confidence * 30)
            print(f"{date:<12} {confidence*100:>6.1f}% {bar:<30}")
        print("="*60 + "\n")
    else:
        metrics.print_performance_summary(args.days)
