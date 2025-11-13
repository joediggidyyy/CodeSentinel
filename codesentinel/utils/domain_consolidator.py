"""
Domain History Consolidator
============================

DHIS Layer 2: Consolidation and Pattern Analysis

Reads domain history.jsonl files, analyzes patterns, and generates
INDEX.json with aggregated intelligence and confidence scores.

This module feeds ORACL Tier 2 (Context) and Tier 3 (Intelligence).
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter


class DomainConsolidator:
    """
    Consolidates domain history into actionable intelligence.
    
    DHIS Layer 2: Transforms raw activity logs into patterns and insights.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize domain consolidator.
        
        Args:
            workspace_root: Root directory of workspace. Auto-detected if None.
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.domains_dir = self.workspace_root / "docs" / "domains"
        
    def read_domain_history(self, domain: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Read and parse domain history.jsonl file.
        
        Args:
            domain: Domain name (cli, core, utils, process, root, policy)
            days: Number of days of history to read (default: 7)
            
        Returns:
            List of activity records within time window
        """
        history_file = self.domains_dir / domain / "history.jsonl"
        
        if not history_file.exists():
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        records = []
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    record = json.loads(line)
                    
                    # Parse timestamp
                    timestamp_str = record.get('timestamp', '')
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        if timestamp >= cutoff_date:
                            records.append(record)
                    except (ValueError, TypeError):
                        # Skip records with invalid timestamps
                        continue
                        
        except (IOError, json.JSONDecodeError) as e:
            print(f"[WARN] Could not read {history_file}: {e}")
            return []
        
        return records
    
    def analyze_patterns(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in domain activity records.
        
        Args:
            records: List of activity records from domain history
            
        Returns:
            Dict containing pattern analysis:
            - action_frequency: Counter of action types
            - success_rate: Overall success rate
            - avg_duration_ms: Average operation duration
            - files_modified: Set of files touched
            - peak_hours: Most active hours
            - confidence_score: Confidence in pattern reliability (0.0-1.0)
        """
        if not records:
            return {
                'action_frequency': {},
                'success_rate': 0.0,
                'avg_duration_ms': 0,
                'files_modified': [],
                'peak_hours': [],
                'confidence_score': 0.0,
                'total_operations': 0
            }
        
        # Counters
        action_counter = Counter()
        success_count = 0
        total_duration = 0
        files_set = set()
        hour_counter = Counter()
        
        for record in records:
            activity = record.get('activity', {})
            
            # Action frequency
            action = activity.get('action', 'unknown')
            action_counter[action] += 1
            
            # Success tracking
            if activity.get('success', False):
                success_count += 1
            
            # Duration tracking
            duration = activity.get('duration_ms', 0)
            total_duration += duration
            
            # Files modified
            files = activity.get('files_modified', [])
            files_set.update(files)
            
            # Peak hours
            timestamp_str = record.get('timestamp', '')
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                hour_counter[timestamp.hour] += 1
            except (ValueError, TypeError):
                pass
        
        total_ops = len(records)
        success_rate = (success_count / total_ops) if total_ops > 0 else 0.0
        avg_duration = (total_duration / total_ops) if total_ops > 0 else 0
        
        # Peak hours (top 3)
        peak_hours = [hour for hour, _ in hour_counter.most_common(3)]
        
        # Confidence score calculation
        # Factors: sample size, success rate, consistency
        confidence = self._calculate_confidence(
            sample_size=total_ops,
            success_rate=success_rate,
            action_diversity=len(action_counter)
        )
        
        return {
            'action_frequency': dict(action_counter.most_common()),
            'success_rate': round(success_rate, 3),
            'avg_duration_ms': round(avg_duration, 2),
            'files_modified': sorted(list(files_set)),
            'peak_hours': peak_hours,
            'confidence_score': round(confidence, 3),
            'total_operations': total_ops
        }
    
    def _calculate_confidence(
        self, 
        sample_size: int, 
        success_rate: float, 
        action_diversity: int
    ) -> float:
        """
        Calculate confidence score for pattern reliability.
        
        Confidence factors:
        - Sample size: More data = higher confidence (log scale)
        - Success rate: Higher success = higher confidence
        - Action diversity: More action types = more representative
        
        Args:
            sample_size: Number of records analyzed
            success_rate: Success rate (0.0-1.0)
            action_diversity: Number of unique action types
            
        Returns:
            Confidence score (0.0-1.0)
        """
        import math
        
        # Sample size component (0.0-0.4)
        # 10 records = 0.2, 100 records = 0.35, 1000+ records = 0.4
        size_score = min(0.4, math.log10(sample_size + 1) / 10)
        
        # Success rate component (0.0-0.4)
        success_score = success_rate * 0.4
        
        # Diversity component (0.0-0.2)
        # 1-2 actions = 0.05, 3-5 actions = 0.15, 6+ actions = 0.2
        diversity_score = min(0.2, (action_diversity / 30))
        
        total_confidence = size_score + success_score + diversity_score
        return min(1.0, total_confidence)
    
    def generate_index(self, domain: str, days: int = 7) -> Dict[str, Any]:
        """
        Generate INDEX.json for a domain.
        
        Reads domain history, analyzes patterns, and creates consolidated index.
        
        Args:
            domain: Domain name (cli, core, utils, process, root, policy)
            days: Number of days of history to analyze (default: 7)
            
        Returns:
            Dict containing INDEX.json structure
        """
        records = self.read_domain_history(domain, days)
        patterns = self.analyze_patterns(records)
        
        index = {
            'domain': domain,
            'last_updated': datetime.now().isoformat(),
            'time_window_days': days,
            'patterns': patterns,
            'metadata': {
                'total_records_analyzed': len(records),
                'oldest_record': records[0]['timestamp'] if records else None,
                'newest_record': records[-1]['timestamp'] if records else None,
            }
        }
        
        return index
    
    def consolidate_all_domains(self, days: int = 7) -> Dict[str, Dict[str, Any]]:
        """
        Consolidate all domains and generate INDEX.json for each.
        
        Args:
            days: Number of days of history to analyze (default: 7)
            
        Returns:
            Dict mapping domain names to their INDEX.json content
        """
        domains = ['cli', 'core', 'utils', 'process', 'root', 'policy']
        indices = {}
        
        for domain in domains:
            index = self.generate_index(domain, days)
            indices[domain] = index
            
            # Write INDEX.json
            index_file = self.domains_dir / domain / "INDEX.json"
            try:
                with open(index_file, 'w', encoding='utf-8') as f:
                    json.dump(index, f, indent=2)
                print(f"[OK] Generated INDEX.json for domain '{domain}'")
            except IOError as e:
                print(f"[FAIL] Could not write {index_file}: {e}")
        
        return indices
    
    def get_domain_summary(self, domain: str, days: int = 7) -> str:
        """
        Get human-readable summary of domain activity.
        
        Args:
            domain: Domain name
            days: Number of days to summarize
            
        Returns:
            Formatted summary string
        """
        index = self.generate_index(domain, days)
        patterns = index['patterns']
        
        summary_lines = [
            f"Domain: {domain.upper()}",
            f"Time Window: {days} days",
            f"Total Operations: {patterns['total_operations']}",
            f"Success Rate: {patterns['success_rate'] * 100:.1f}%",
            f"Avg Duration: {patterns['avg_duration_ms']:.2f}ms",
            f"Confidence: {patterns['confidence_score'] * 100:.0f}%",
            "",
            "Top Actions:"
        ]
        
        for action, count in list(patterns['action_frequency'].items())[:5]:
            summary_lines.append(f"  - {action}: {count} times")
        
        if patterns['peak_hours']:
            hours_str = ', '.join(f"{h:02d}:00" for h in patterns['peak_hours'])
            summary_lines.append(f"\nPeak Hours: {hours_str}")
        
        return '\n'.join(summary_lines)


def consolidate_domains_cli(days: int = 7, verbose: bool = False) -> None:
    """
    CLI entry point for domain consolidation.
    
    Args:
        days: Number of days to analyze
        verbose: Show detailed summaries
    """
    print("\n[DHIS] Domain History Consolidation")
    print("="*80)
    
    consolidator = DomainConsolidator()
    indices = consolidator.consolidate_all_domains(days)
    
    print(f"\nConsolidated {len(indices)} domains")
    
    if verbose:
        print("\n" + "="*80)
        print("Domain Summaries:")
        print("="*80 + "\n")
        
        for domain in indices.keys():
            print(consolidator.get_domain_summary(domain, days))
            print("\n" + "-"*80 + "\n")
    
    print("="*80 + "\n")


if __name__ == '__main__':
    """Command-line execution for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='DHIS Domain Consolidator')
    parser.add_argument('--days', type=int, default=7, help='Days of history to analyze')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed summaries')
    
    args = parser.parse_args()
    consolidate_domains_cli(args.days, args.verbose)
