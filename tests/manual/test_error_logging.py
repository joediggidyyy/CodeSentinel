#!/usr/bin/env python
"""Test that errors are logged by metrics system."""

from codesentinel.utils.metrics_wrapper import track_cli_command
import time
import json

@track_cli_command('test_error')
def test_func():
    """Function that will raise an error."""
    time.sleep(0.05)
    raise ValueError('Test error for logging')

# Run test
try:
    test_func()
except ValueError:
    pass

# Check the log
print("Error logged. Verifying...")
with open('docs/metrics/agent_operations.jsonl') as f:
    lines = f.readlines()
    last_record = json.loads(lines[-1])
    print(f"\nLast command logged:")
    print(f"  Command: {last_record['command']}")
    print(f"  Success: {last_record['success']}")
    print(f"  Error: {last_record.get('error', 'None')}")
    print(f"  Duration: {last_record['duration_ms']:.2f}ms")
