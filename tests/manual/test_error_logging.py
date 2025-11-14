#!/usr/bin/env python
"""Test that errors are logged by metrics system."""

from codesentinel.utils.metrics_wrapper import track_cli_command
import time
import json


@track_cli_command('test_error')
def _test_error_function():
    """Function that will raise an error for metrics logging."""
    time.sleep(0.05)
    raise ValueError('Test error for logging')


def test_error_is_logged():
    """Verify that a failing command is still logged by the metrics system.

    This is a pytest-style test function so that failures are reported
    through pytest instead of raising at import time.
    """

    # Run the instrumented function and swallow the expected error
    try:
        _test_error_function()
    except ValueError:
        pass

    # Check the last metrics record
    with open('docs/metrics/agent_operations.jsonl') as f:
        lines = f.readlines()

    assert lines, "Expected at least one metrics record to be present"

    last_record = json.loads(lines[-1])
    assert last_record['command'] == 'test_error'
    assert last_record['success'] is False
    # Error field may vary, but it should be present for failing command
    assert 'error' in last_record
