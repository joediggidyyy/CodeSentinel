# CodeSentinel Clean Installation Test Script
# ============================================
# Tests clean installation in isolated environment

param(
    [switch]$Verbose,
    [switch]$KeepEnvironment
)

$ErrorActionPreference = "Stop"
$TestStartTime = Get-Date
$Timestamp = $TestStartTime.ToString("yyyyMMdd_HHmmss")
$TestRoot = $PSScriptRoot
$ParentDir = Split-Path $TestRoot -Parent
$ResultsDir = Join-Path $TestRoot "test_results"

# Create results directory
New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null

$LogFile = Join-Path $ResultsDir "install_log_$Timestamp.txt"
$ReportFile = Join-Path $ResultsDir "test_report_$Timestamp.txt"

function Write-Log {
    param($Message, $Color = "White")
    $LogMessage = "[$((Get-Date).ToString('HH:mm:ss'))] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

function Write-TestSection {
    param($Title)
    $Separator = "=" * 60
    Write-Log ""
    Write-Log $Separator -Color Cyan
    Write-Log $Title -Color Cyan
    Write-Log $Separator -Color Cyan
}

function Test-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )
    
    Write-Log "Testing: $Name" -Color Yellow
    try {
        $result = & $Action
        Write-Log "✓ PASS: $Name" -Color Green
        return @{Success = $true; Result = $result}
    }
    catch {
        Write-Log "✗ FAIL: $Name - $($_.Exception.Message)" -Color Red
        return @{Success = $false; Error = $_.Exception.Message}
    }
}

# Start test report
@"
CodeSentinel Clean Installation Test Report
============================================
Test Date: $TestStartTime
Test Environment: test_install_env
Python Version: $(python --version 2>&1)

"@ | Set-Content $ReportFile

Write-TestSection "CLEAN INSTALLATION TEST STARTING"
Write-Log "Test directory: $TestRoot"
Write-Log "Parent directory: $ParentDir"
Write-Log "Results directory: $ResultsDir"

# Test results tracking
$TestResults = @{
    Total = 0
    Passed = 0
    Failed = 0
    Steps = @()
}

# Step 1: Clean existing environment
Write-TestSection "STEP 1: Clean Existing Environment"
$result = Test-Step "Remove old virtual environment" {
    $venvPath = Join-Path $TestRoot ".venv"
    if (Test-Path $venvPath) {
        Remove-Item -Path $venvPath -Recurse -Force
        Write-Log "Removed existing venv"
    } else {
        Write-Log "No existing venv found"
    }
}
$TestResults.Steps += $result
$TestResults.Total++
if ($result.Success) { $TestResults.Passed++ } else { $TestResults.Failed++ }

# Step 2: Create fresh virtual environment
Write-TestSection "STEP 2: Create Fresh Virtual Environment"
$result = Test-Step "Create new venv" {
    $output = python -m venv (Join-Path $TestRoot ".venv") 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "venv creation failed: $output"
    }
    Write-Log "Virtual environment created successfully"
}
$TestResults.Steps += $result
$TestResults.Total++
if ($result.Success) { $TestResults.Passed++ } else { $TestResults.Failed++ }

# Step 3: Activate virtual environment
Write-TestSection "STEP 3: Activate Virtual Environment"
$venvActivate = Join-Path $TestRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
    Write-Log "Virtual environment activated" -Color Green
} else {
    Write-Log "Failed to find activation script" -Color Red
    exit 1
}

# Step 4: Upgrade pip
Write-TestSection "STEP 4: Upgrade pip"
$result = Test-Step "Upgrade pip to latest version" {
    $output = python -m pip install --upgrade pip 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "pip upgrade failed: $output"
    }
    $pipVersion = python -m pip --version
    Write-Log "pip version: $pipVersion"
}
$TestResults.Steps += $result
$TestResults.Total++
if ($result.Success) { $TestResults.Passed++ } else { $TestResults.Failed++ }

# Step 5: Install CodeSentinel in editable mode
Write-TestSection "STEP 5: Install CodeSentinel"
$result = Test-Step "Install CodeSentinel from parent directory" {
    Write-Log "Installing from: $ParentDir"
    $output = python -m pip install -e $ParentDir 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Installation failed: $output"
    }
    Write-Log "Installation output saved to log"
    Add-Content -Path $LogFile -Value $output
}
$TestResults.Steps += $result
$TestResults.Total++
if ($result.Success) { $TestResults.Passed++ } else { $TestResults.Failed++ }

# Step 6: Verify package installation
Write-TestSection "STEP 6: Verify Package Installation"
$result = Test-Step "Check installed packages" {
    $packages = python -m pip list 2>&1
    Write-Log "Installed packages:"
    Add-Content -Path $LogFile -Value $packages
    
    # Check for CodeSentinel
    if ($packages -match "codesentinel") {
        Write-Log "✓ CodeSentinel package found"
    } else {
        throw "CodeSentinel package not found in pip list"
    }
}
$TestResults.Steps += $result
$TestResults.Total++
if ($result.Success) { $TestResults.Passed++ } else { $TestResults.Failed++ }

# Step 7: Verify CLI entry points
Write-TestSection "STEP 7: Verify CLI Entry Points"
$result = Test-Step "Check codesentinel command" {
    $output = codesentinel --help 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "codesentinel command not available: $output"
    }
    Write-Log "✓ codesentinel command works"
}
$TestResults.Steps += $result
$TestResults.Total++
if ($result.Success) { $TestResults.Passed++ } else { $TestResults.Failed++ }

$result = Test-Step "Check codesentinel-setup command" {
    # Just verify command exists, don't run interactively
    $command = Get-Command codesentinel-setup -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        throw "codesentinel-setup command not found"
    }
    Write-Log "✓ codesentinel-setup command available"
}
$TestResults.Steps += $result
$TestResults.Total++
if ($result.Success) { $TestResults.Passed++ } else { $TestResults.Failed++ }

# Step 8: Test module imports
Write-TestSection "STEP 8: Test Module Imports"
$result = Test-Step "Import codesentinel package" {
    $output = python -c "import codesentinel; print(f'Version: {codesentinel.__version__ if hasattr(codesentinel, '__version__') else 'unknown'}')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to import codesentinel: $output"
    }
    Write-Log "Import test output: $output"
}
$TestResults.Steps += $result
$TestResults.Total++
if ($result.Success) { $TestResults.Passed++ } else { $TestResults.Failed++ }

# Step 9: Check dependency installation
Write-TestSection "STEP 9: Check Dependencies"
$requiredDeps = @('tkinter', 'psutil', 'requests')
foreach ($dep in $requiredDeps) {
    $result = Test-Step "Check dependency: $dep" {
        if ($dep -eq 'tkinter') {
            $output = python -c "import tkinter; print('tkinter available')" 2>&1
        } else {
            $output = python -c "import $dep; print('$dep available')" 2>&1
        }
        if ($LASTEXITCODE -ne 0) {
            throw "Dependency $dep not available: $output"
        }
        Write-Log "✓ $dep is available"
    }
    $TestResults.Steps += $result
    $TestResults.Total++
    if ($result.Success) { $TestResults.Passed++ } else { $TestResults.Failed++ }
}

# Generate final report
Write-TestSection "TEST SUMMARY"
$TestEndTime = Get-Date
$Duration = $TestEndTime - $TestStartTime

$summary = @"

TEST RESULTS SUMMARY
====================
Total Tests: $($TestResults.Total)
Passed: $($TestResults.Passed)
Failed: $($TestResults.Failed)
Success Rate: $([math]::Round(($TestResults.Passed / $TestResults.Total) * 100, 2))%

Duration: $($Duration.TotalSeconds) seconds
Log File: $LogFile
Report File: $ReportFile

"@

Write-Log $summary
Add-Content -Path $ReportFile -Value $summary

if ($TestResults.Failed -eq 0) {
    Write-Log "✓ ALL TESTS PASSED - Installation successful!" -Color Green
    Write-Log ""
    Write-Log "Next steps:" -Color Yellow
    Write-Log "  1. Run: codesentinel-setup-gui" -Color Cyan
    Write-Log "  2. Complete the setup wizard" -Color Cyan
    Write-Log "  3. Test: codesentinel !!!!" -Color Cyan
    $exitCode = 0
} else {
    Write-Log "✗ SOME TESTS FAILED - Check logs for details" -Color Red
    $exitCode = 1
}

# Cleanup option
if (-not $KeepEnvironment) {
    Write-Log ""
    Write-Log "Note: To clean up test environment, run:" -Color Yellow
    Write-Log "  Remove-Item -Path '$TestRoot\.venv' -Recurse -Force" -Color Gray
}

Write-Log ""
Write-Log "Test complete. Results saved to: $ResultsDir" -Color Cyan

exit $exitCode
