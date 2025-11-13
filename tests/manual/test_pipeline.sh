#!/bin/bash
# Comprehensive Pipeline Test Suite
# Tests all major CLI commands and features

echo "=========================================="
echo "CodeSentinel Comprehensive Pipeline Test"
echo "=========================================="
echo ""

# Test 1: Memory commands
echo "[TEST 1] Memory Commands"
echo "  - Testing: codesentinel memory show"
time codesentinel memory show > /dev/null 2>&1 && echo "  [PASS] memory show" || echo "  [FAIL] memory show"

echo "  - Testing: codesentinel memory stats"
time codesentinel memory stats > /dev/null 2>&1 && echo "  [PASS] memory stats" || echo "  [FAIL] memory stats"

echo "  - Testing: codesentinel memory tasks"
time codesentinel memory tasks > /dev/null 2>&1 && echo "  [PASS] memory tasks" || echo "  [FAIL] memory tasks"

# Test 2: Process Monitor Commands
echo ""
echo "[TEST 2] Process Monitor Commands"
echo "  - Testing: codesentinel memory process status"
time codesentinel memory process status > /dev/null 2>&1 && echo "  [PASS] process status" || echo "  [FAIL] process status"

echo "  - Testing: codesentinel memory process history"
time codesentinel memory process history --limit 3 > /dev/null 2>&1 && echo "  [PASS] process history" || echo "  [FAIL] process history"

# Test 3: Metrics Verification
echo ""
echo "[TEST 3] Metrics Tracking"
echo "  - Checking agent_operations.jsonl..."
if [ -f docs/metrics/agent_operations.jsonl ]; then
    count=$(wc -l < docs/metrics/agent_operations.jsonl)
    echo "  [PASS] Found $count tracked operations"
else
    echo "  [FAIL] agent_operations.jsonl not found"
fi

echo "  - Checking security_events.jsonl..."
if [ -f docs/metrics/security_events.jsonl ]; then
    count=$(wc -l < docs/metrics/security_events.jsonl)
    echo "  [PASS] Found $count security events"
else
    echo "  [FAIL] security_events.jsonl not found"
fi

# Test 4: File Integrity
echo ""
echo "[TEST 4] File Integrity"
echo "  - Checking baseline file..."
if [ -f .codesentinel_integrity.json ]; then
    size=$(stat -f%z .codesentinel_integrity.json 2>/dev/null || stat -c%s .codesentinel_integrity.json 2>/dev/null || echo "unknown")
    echo "  [PASS] Baseline file exists ($size bytes)"
else
    echo "  [FAIL] Baseline file not found"
fi

echo ""
echo "=========================================="
echo "Pipeline Test Complete"
echo "=========================================="
