#!/bin/bash
# CodeSentinel Clean Installation Test Script (Linux/macOS)
# ===========================================================

set -e

TEST_START=$(date +%s)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_ROOT="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$TEST_ROOT")"
RESULTS_DIR="$TEST_ROOT/test_results"

mkdir -p "$RESULTS_DIR"

LOG_FILE="$RESULTS_DIR/install_log_$TIMESTAMP.txt"
REPORT_FILE="$RESULTS_DIR/test_report_$TIMESTAMP.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() {
    local message="[$(date +%H:%M:%S)] $1"
    echo -e "$message" | tee -a "$LOG_FILE"
}

log_color() {
    local color=$1
    shift
    local message="[$(date +%H:%M:%S)] $*"
    echo -e "${color}${message}${NC}" | tee -a "$LOG_FILE"
}

test_section() {
    local title=$1
    echo "" | tee -a "$LOG_FILE"
    log_color "$CYAN" "============================================================"
    log_color "$CYAN" "$title"
    log_color "$CYAN" "============================================================"
}

test_step() {
    local name=$1
    local command=$2
    
    log_color "$YELLOW" "Testing: $name"
    
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        log_color "$GREEN" "✓ PASS: $name"
        return 0
    else
        log_color "$RED" "✗ FAIL: $name"
        return 1
    fi
}

# Start report
cat > "$REPORT_FILE" <<EOF
CodeSentinel Clean Installation Test Report
============================================
Test Date: $(date)
Test Environment: test_install_env
Python Version: $(python3 --version)

EOF

test_section "CLEAN INSTALLATION TEST STARTING"
log "Test directory: $TEST_ROOT"
log "Parent directory: $PARENT_DIR"
log "Results directory: $RESULTS_DIR"

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Step 1: Clean existing environment
test_section "STEP 1: Clean Existing Environment"
((TOTAL_TESTS++))
if test_step "Remove old virtual environment" "rm -rf $TEST_ROOT/.venv"; then
    ((PASSED_TESTS++))
else
    ((FAILED_TESTS++))
fi

# Step 2: Create fresh virtual environment  
test_section "STEP 2: Create Fresh Virtual Environment"
((TOTAL_TESTS++))
if test_step "Create new venv" "python3 -m venv $TEST_ROOT/.venv"; then
    ((PASSED_TESTS++))
else
    ((FAILED_TESTS++))
    exit 1
fi

# Step 3: Activate virtual environment
test_section "STEP 3: Activate Virtual Environment"
source "$TEST_ROOT/.venv/bin/activate"
log_color "$GREEN" "Virtual environment activated"

# Step 4: Upgrade pip
test_section "STEP 4: Upgrade pip"
((TOTAL_TESTS++))
if test_step "Upgrade pip to latest version" "python -m pip install --upgrade pip"; then
    ((PASSED_TESTS++))
    log "pip version: $(python -m pip --version)"
else
    ((FAILED_TESTS++))
fi

# Step 5: Install CodeSentinel
test_section "STEP 5: Install CodeSentinel"
((TOTAL_TESTS++))
log "Installing from: $PARENT_DIR"
if test_step "Install CodeSentinel from parent directory" "python -m pip install -e $PARENT_DIR"; then
    ((PASSED_TESTS++))
else
    ((FAILED_TESTS++))
fi

# Step 6: Verify package installation
test_section "STEP 6: Verify Package Installation"
((TOTAL_TESTS++))
if test_step "Check installed packages" "python -m pip list | grep -i codesentinel"; then
    ((PASSED_TESTS++))
else
    ((FAILED_TESTS++))
fi

# Step 7: Verify CLI entry points
test_section "STEP 7: Verify CLI Entry Points"
((TOTAL_TESTS++))
if test_step "Check codesentinel command" "codesentinel --help"; then
    ((PASSED_TESTS++))
else
    ((FAILED_TESTS++))
fi

((TOTAL_TESTS++))
if test_step "Check codesentinel-setup command" "command -v codesentinel-setup"; then
    ((PASSED_TESTS++))
else
    ((FAILED_TESTS++))
fi

# Step 8: Test module imports
test_section "STEP 8: Test Module Imports"
((TOTAL_TESTS++))
if test_step "Import codesentinel package" "python -c 'import codesentinel; print(\"Import successful\")'"; then
    ((PASSED_TESTS++))
else
    ((FAILED_TESTS++))
fi

# Step 9: Check dependencies
test_section "STEP 9: Check Dependencies"
for dep in "psutil" "requests"; do
    ((TOTAL_TESTS++))
    if test_step "Check dependency: $dep" "python -c 'import $dep'"; then
        ((PASSED_TESTS++))
    else
        ((FAILED_TESTS++))
    fi
done

# Generate final report
test_section "TEST SUMMARY"
TEST_END=$(date +%s)
DURATION=$((TEST_END - TEST_START))
SUCCESS_RATE=$(awk "BEGIN {printf \"%.2f\", ($PASSED_TESTS / $TOTAL_TESTS) * 100}")

SUMMARY="
TEST RESULTS SUMMARY
====================
Total Tests: $TOTAL_TESTS
Passed: $PASSED_TESTS
Failed: $FAILED_TESTS
Success Rate: $SUCCESS_RATE%

Duration: $DURATION seconds
Log File: $LOG_FILE
Report File: $REPORT_FILE
"

echo "$SUMMARY" | tee -a "$LOG_FILE" "$REPORT_FILE"

if [ $FAILED_TESTS -eq 0 ]; then
    log_color "$GREEN" "✓ ALL TESTS PASSED - Installation successful!"
    echo ""
    log_color "$YELLOW" "Next steps:"
    log_color "$CYAN" "  1. Run: codesentinel-setup-gui"
    log_color "$CYAN" "  2. Complete the setup wizard"
    log_color "$CYAN" "  3. Test: codesentinel !!!!"
    EXIT_CODE=0
else
    log_color "$RED" "✗ SOME TESTS FAILED - Check logs for details"
    EXIT_CODE=1
fi

echo ""
log_color "$YELLOW" "Note: To clean up test environment, run:"
log_color "$NC" "  rm -rf '$TEST_ROOT/.venv'"

echo ""
log_color "$CYAN" "Test complete. Results saved to: $RESULTS_DIR"

exit $EXIT_CODE
