#!/usr/bin/env python3
"""
Generate comprehensive metrics report from agent_operations.jsonl.

This script analyzes metrics data and produces a detailed report showing:
- Command execution statistics
- Success/failure rates
- Performance metrics (duration)
- Error patterns
- Most common operations
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Any

def load_metrics(jsonl_path: Path) -> List[Dict[str, Any]]:
    """Load all metrics records from JSONL file."""
    records = []
    if not jsonl_path.exists():
        return records
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                records.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    return records

def analyze_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze metrics records and produce summary statistics."""
    
    # Counters
    command_counts = Counter()
    command_success = defaultdict(int)
    command_failure = defaultdict(int)
    command_durations = defaultdict(list)
    error_patterns = Counter()
    session_ids = set()
    
    # Date range
    timestamps = []
    
    for record in records:
        cmd = record.get('command', 'unknown')
        success = record.get('success', False)
        duration = record.get('duration_ms', 0)
        error = record.get('error')
        session_id = record.get('session_id')
        timestamp = record.get('timestamp')
        
        command_counts[cmd] += 1
        
        if success:
            command_success[cmd] += 1
        else:
            command_failure[cmd] += 1
            if error:
                error_patterns[error] += 1
        
        if duration > 0:
            command_durations[cmd].append(duration)
        
        if session_id:
            session_ids.add(session_id)
        
        if timestamp:
            timestamps.append(timestamp)
    
    # Calculate aggregates
    total_commands = sum(command_counts.values())
    total_success = sum(command_success.values())
    total_failure = sum(command_failure.values())
    success_rate = (total_success / total_commands * 100) if total_commands > 0 else 0
    
    # Average durations
    avg_durations = {}
    for cmd, durations in command_durations.items():
        if durations:
            avg_durations[cmd] = sum(durations) / len(durations)
    
    # Date range
    date_range = None
    if timestamps:
        timestamps.sort()
        date_range = {
            'start': timestamps[0],
            'end': timestamps[-1]
        }
    
    return {
        'total_records': len(records),
        'total_commands': total_commands,
        'total_success': total_success,
        'total_failure': total_failure,
        'success_rate': success_rate,
        'unique_sessions': len(session_ids),
        'command_counts': dict(command_counts.most_common()),
        'command_success': dict(command_success),
        'command_failure': dict(command_failure),
        'avg_durations': avg_durations,
        'error_patterns': dict(error_patterns.most_common(10)),
        'date_range': date_range
    }

def format_report(analysis: Dict[str, Any]) -> str:
    """Format analysis results as a readable report."""
    
    report_lines = [
        "=" * 80,
        "CODESENTINEL METRICS REPORT",
        "=" * 80,
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    # Date range
    if analysis['date_range']:
        report_lines.extend([
            "DATA RANGE:",
            f"  Start: {analysis['date_range']['start']}",
            f"  End:   {analysis['date_range']['end']}",
            ""
        ])
    
    # Summary statistics
    report_lines.extend([
        "SUMMARY STATISTICS:",
        f"  Total records:      {analysis['total_records']:>6}",
        f"  Total commands:     {analysis['total_commands']:>6}",
        f"  Successful:         {analysis['total_success']:>6}",
        f"  Failed:             {analysis['total_failure']:>6}",
        f"  Success rate:       {analysis['success_rate']:>6.1f}%",
        f"  Unique sessions:    {analysis['unique_sessions']:>6}",
        ""
    ])
    
    # Command frequency
    report_lines.extend([
        "COMMAND FREQUENCY:",
        "-" * 80
    ])
    
    for cmd, count in analysis['command_counts'].items():
        success = analysis['command_success'].get(cmd, 0)
        failure = analysis['command_failure'].get(cmd, 0)
        rate = (success / count * 100) if count > 0 else 0
        
        avg_duration = analysis['avg_durations'].get(cmd, 0)
        duration_str = f"{avg_duration:>6.1f}ms" if avg_duration > 0 else "    N/A"
        
        report_lines.append(
            f"  {cmd:<25} {count:>4}x  "
            f"[OK] {success:>3}  [FAIL] {failure:>3}  "
            f"({rate:>5.1f}%)  Avg: {duration_str}"
        )
    
    report_lines.append("")
    
    # Performance metrics
    if analysis['avg_durations']:
        report_lines.extend([
            "PERFORMANCE METRICS:",
            "-" * 80
        ])
        
        sorted_durations = sorted(
            analysis['avg_durations'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for cmd, avg_ms in sorted_durations:
            report_lines.append(f"  {cmd:<25} {avg_ms:>8.2f} ms")
        
        report_lines.append("")
    
    # Error patterns
    if analysis['error_patterns']:
        report_lines.extend([
            "TOP ERROR PATTERNS:",
            "-" * 80
        ])
        
        for error, count in list(analysis['error_patterns'].items())[:10]:
            # Truncate long error messages
            error_short = error[:70] + "..." if len(error) > 70 else error
            report_lines.append(f"  [{count}x] {error_short}")
        
        report_lines.append("")
    
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)

def main():
    """Main entry point."""
    workspace_root = Path(__file__).resolve().parent.parent.parent
    metrics_file = workspace_root / "docs" / "metrics" / "agent_operations.jsonl"
    
    print(f"Loading metrics from: {metrics_file}")
    
    if not metrics_file.exists():
        print(f"[FAIL] Metrics file not found: {metrics_file}")
        return 1
    
    # Load and analyze
    records = load_metrics(metrics_file)
    print(f"[OK] Loaded {len(records)} records")
    
    analysis = analyze_metrics(records)
    print(f"[OK] Analysis complete")
    print()
    
    # Generate and display report
    report = format_report(analysis)
    print(report)
    
    # Save report
    report_file = workspace_root / "docs" / "metrics" / "metrics_report.txt"
    report_file.write_text(report, encoding='utf-8')
    print(f"\n[OK] Report saved to: {report_file}")
    
    return 0

if __name__ == "__main__":
    exit(main())
