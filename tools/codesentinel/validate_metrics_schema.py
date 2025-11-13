#!/usr/bin/env python3
"""
Validate agent_operations.jsonl schema and data integrity.

Ensures all records conform to the expected schema:
{
  "timestamp": str (ISO 8601),
  "session_id": str,
  "event_type": str,
  "command": str,
  "args": dict,
  "success": bool,
  "duration_ms": float,
  "error": str | null,
  "metadata": dict
}
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Expected schema
REQUIRED_FIELDS = {
    'timestamp': str,
    'session_id': str,
    'event_type': str,
    'command': str,
    'args': dict,
    'success': bool,
    'duration_ms': (int, float),
    'error': (str, type(None)),
    'metadata': dict
}

def validate_timestamp(timestamp: str) -> Tuple[bool, str]:
    """Validate ISO 8601 timestamp format."""
    try:
        datetime.fromisoformat(timestamp)
        return True, "Valid"
    except ValueError as e:
        return False, f"Invalid timestamp format: {e}"

def validate_record(record: Dict[str, Any], line_num: int) -> List[str]:
    """Validate a single record against the schema."""
    errors = []
    
    # Check required fields
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in record:
            errors.append(f"Line {line_num}: Missing required field '{field}'")
            continue
        
        value = record[field]
        
        # Handle union types
        if isinstance(expected_type, tuple):
            if not isinstance(value, expected_type):
                errors.append(
                    f"Line {line_num}: Field '{field}' has wrong type. "
                    f"Expected {expected_type}, got {type(value).__name__}"
                )
        else:
            if not isinstance(value, expected_type):
                errors.append(
                    f"Line {line_num}: Field '{field}' has wrong type. "
                    f"Expected {expected_type.__name__}, got {type(value).__name__}"
                )
    
    # Validate timestamp format
    if 'timestamp' in record:
        valid, msg = validate_timestamp(record['timestamp'])
        if not valid:
            errors.append(f"Line {line_num}: {msg}")
    
    # Validate event_type
    if 'event_type' in record:
        valid_types = ['cli_command', 'security_event', 'agent_decision', 'oracl_query']
        if record['event_type'] not in valid_types:
            errors.append(
                f"Line {line_num}: Invalid event_type '{record['event_type']}'. "
                f"Expected one of: {', '.join(valid_types)}"
            )
    
    # Validate duration_ms is non-negative
    if 'duration_ms' in record:
        if record['duration_ms'] < 0:
            errors.append(f"Line {line_num}: duration_ms cannot be negative")
    
    # Validate success is boolean
    if 'success' in record:
        if not isinstance(record['success'], bool):
            errors.append(f"Line {line_num}: success must be boolean")
    
    # Check for unexpected fields (warnings, not errors)
    expected_fields = set(REQUIRED_FIELDS.keys())
    actual_fields = set(record.keys())
    extra_fields = actual_fields - expected_fields
    if extra_fields:
        # This is just informational, not an error
        pass
    
    return errors

def validate_jsonl(jsonl_path: Path) -> Tuple[int, List[str]]:
    """
    Validate entire JSONL file.
    
    Returns:
        (total_records, errors)
    """
    errors = []
    record_count = 0
    
    if not jsonl_path.exists():
        return 0, [f"File not found: {jsonl_path}"]
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            
            try:
                record = json.loads(line)
                record_count += 1
                
                # Validate record structure
                record_errors = validate_record(record, line_num)
                errors.extend(record_errors)
                
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Invalid JSON - {e}")
    
    return record_count, errors

def main():
    """Main entry point."""
    workspace_root = Path(__file__).resolve().parent.parent.parent
    metrics_file = workspace_root / "docs" / "metrics" / "agent_operations.jsonl"
    
    print("=" * 80)
    print("AGENT METRICS SCHEMA VALIDATOR")
    print("=" * 80)
    print()
    print(f"Validating: {metrics_file}")
    print()
    
    if not metrics_file.exists():
        print(f"[FAIL] File not found: {metrics_file}")
        return 1
    
    # Validate
    record_count, errors = validate_jsonl(metrics_file)
    
    # Report results
    print(f"[OK] Loaded {record_count} records")
    print()
    
    if errors:
        print(f"[FAIL] Found {len(errors)} validation error(s):")
        print("-" * 80)
        for error in errors:
            print(f"  {error}")
        print()
        return 1
    else:
        print("[OK] All records valid - schema compliance verified")
        print()
        print("SCHEMA SUMMARY:")
        print(f"  Records validated:  {record_count}")
        print(f"  Required fields:    {len(REQUIRED_FIELDS)}")
        print(f"  Validation errors:  0")
        print()
        print("=" * 80)
        return 0

if __name__ == "__main__":
    exit(main())
