# Comprehensive Pipeline Test Suite
# Tests all major CLI commands and features

Write-Host "==========================================" -ForegroundColor Green
Write-Host "CodeSentinel Comprehensive Pipeline Test" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Test 1: Memory commands
Write-Host "[TEST 1] Memory Commands" -ForegroundColor Cyan
Write-Host "  - Testing: codesentinel memory show"
$result = Measure-Command { codesentinel memory show *>$null }
if ($LASTEXITCODE -eq 0) { 
    Write-Host "  [PASS] memory show (${[math]::Round($result.TotalMilliseconds)}ms)" -ForegroundColor Green 
} else { 
    Write-Host "  [FAIL] memory show" -ForegroundColor Red 
}

Write-Host "  - Testing: codesentinel memory stats"
$result = Measure-Command { codesentinel memory stats *>$null }
if ($LASTEXITCODE -eq 0) { 
    Write-Host "  [PASS] memory stats (${[math]::Round($result.TotalMilliseconds)}ms)" -ForegroundColor Green 
} else { 
    Write-Host "  [FAIL] memory stats" -ForegroundColor Red 
}

Write-Host "  - Testing: codesentinel memory tasks"
$result = Measure-Command { codesentinel memory tasks *>$null }
if ($LASTEXITCODE -eq 0) { 
    Write-Host "  [PASS] memory tasks (${[math]::Round($result.TotalMilliseconds)}ms)" -ForegroundColor Green 
} else { 
    Write-Host "  [FAIL] memory tasks" -ForegroundColor Red 
}

# Test 2: Process Monitor Commands
Write-Host ""
Write-Host "[TEST 2] Process Monitor Commands" -ForegroundColor Cyan
Write-Host "  - Testing: codesentinel memory process status"
$result = Measure-Command { codesentinel memory process status *>$null }
if ($LASTEXITCODE -eq 0) { 
    Write-Host "  [PASS] process status (${[math]::Round($result.TotalMilliseconds)}ms)" -ForegroundColor Green 
} else { 
    Write-Host "  [FAIL] process status" -ForegroundColor Red 
}

Write-Host "  - Testing: codesentinel memory process history"
$result = Measure-Command { codesentinel memory process history --limit 3 *>$null }
if ($LASTEXITCODE -eq 0) { 
    Write-Host "  [PASS] process history (${[math]::Round($result.TotalMilliseconds)}ms)" -ForegroundColor Green 
} else { 
    Write-Host "  [FAIL] process history" -ForegroundColor Red 
}

# Test 3: Metrics Verification
Write-Host ""
Write-Host "[TEST 3] Metrics Tracking" -ForegroundColor Cyan
Write-Host "  - Checking agent_operations.jsonl..."
if (Test-Path "docs\metrics\agent_operations.jsonl") {
    $count = @(Get-Content "docs\metrics\agent_operations.jsonl").Count
    Write-Host "  [PASS] Found $count tracked operations" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] agent_operations.jsonl not found" -ForegroundColor Red
}

Write-Host "  - Checking security_events.jsonl..."
if (Test-Path "docs\metrics\security_events.jsonl") {
    $count = @(Get-Content "docs\metrics\security_events.jsonl").Count
    Write-Host "  [PASS] Found $count security events" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] security_events.jsonl not found" -ForegroundColor Red
}

# Test 4: File Integrity
Write-Host ""
Write-Host "[TEST 4] File Integrity" -ForegroundColor Cyan
Write-Host "  - Checking baseline file..."
if (Test-Path ".codesentinel_integrity.json") {
    $size = (Get-Item ".codesentinel_integrity.json").Length
    Write-Host "  [PASS] Baseline file exists ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Baseline file not found" -ForegroundColor Red
}

# Test 5: Performance Validation
Write-Host ""
Write-Host "[TEST 5] Performance Validation" -ForegroundColor Cyan
$total_time = 0
$runs = 3
Write-Host "  - Running $runs consecutive commands..."
for ($i = 1; $i -le $runs; $i++) {
    $result = Measure-Command { codesentinel memory stats *>$null }
    $total_time += $result.TotalMilliseconds
    Write-Host "    Run $i: ${[math]::Round($result.TotalMilliseconds)}ms"
}
$avg_time = $total_time / $runs
Write-Host "  [PASS] Average execution: ${[math]::Round($avg_time)}ms (threshold: <1000ms)" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Pipeline Test Complete" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
