#!/usr/bin/env python3
"""
CI Failure Diagnostics Framework
=================================

Automated investigation and remediation playbooks for common CI failures.
Pre-built to run immediately if GitHub Actions reports issues.

Handles:
1. Test collection failures (KeyError, ImportError, SyntaxError)
2. Python version-specific issues (3.10 f-string, 3.8 type annotations)
3. Environment parity problems (cached vs fresh environments)
4. Dependency resolution issues

Usage:
    python tools/ci_failure_diagnostics.py --python-version 3.10 --failure-type syntax
    python tools/ci_failure_diagnostics.py --investigate-all
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CIFailureDiagnostics:
    """Diagnose and investigate CI failures automatically."""
    
    # Failure patterns and their investigation procedures
    FAILURE_PATTERNS = {
        'syntax': {
            'keywords': ['SyntaxError', 'f-string expression', 'backslash'],
            'investigation': 'investigate_syntax_errors',
            'common_causes': [
                'F-string with backslash in expression (Python 3.10+)',
                'Type annotation using lowercase generics (Python 3.8 incompatible)',
                'Unicode characters in print statements (Windows encoding)',
            ],
        },
        'import': {
            'keywords': ['ImportError', 'ModuleNotFoundError', 'KeyError'],
            'investigation': 'investigate_import_errors',
            'common_causes': [
                'Missing __init__.py in package directory',
                'Circular imports or missing dependencies',
                'Fresh environment missing cached modules',
            ],
        },
        'collection': {
            'keywords': ['cannot collect', 'test collection failed', 'error during collection'],
            'investigation': 'investigate_collection_failures',
            'common_causes': [
                'Syntax error preventing module load',
                'Missing package markers (__init__.py)',
                'Import errors in test files',
            ],
        },
    }
    
    def __init__(self, python_version: Optional[str] = None):
        """Initialize diagnostics."""
        self.python_version = python_version or sys.version.split()[0]
        self.repo_root = Path(__file__).parent.parent
        self.findings: List[str] = []
    
    def investigate_syntax_errors(self) -> Dict:
        """Investigate syntax errors in Python files."""
        findings = {
            'status': 'investigating',
            'python_version': self.python_version,
            'checks': [],
        }
        
        # Check 1: F-string compatibility
        findings['checks'].append(self._check_fstring_compatibility())
        
        # Check 2: Type annotation compatibility
        findings['checks'].append(self._check_type_annotations())
        
        # Check 3: Print statement encoding
        findings['checks'].append(self._check_print_statements())
        
        return findings
    
    def investigate_import_errors(self) -> Dict:
        """Investigate import and module loading errors."""
        findings = {
            'status': 'investigating',
            'python_version': self.python_version,
            'checks': [],
        }
        
        # Check 1: Package markers
        findings['checks'].append(self._check_package_markers())
        
        # Check 2: Module structure
        findings['checks'].append(self._check_module_structure())
        
        # Check 3: Dependency resolution
        findings['checks'].append(self._check_dependencies())
        
        return findings
    
    def investigate_collection_failures(self) -> Dict:
        """Investigate test collection failures."""
        findings = {
            'status': 'investigating',
            'python_version': self.python_version,
            'checks': [],
        }
        
        # Check 1: Test file syntax
        findings['checks'].append(self._check_test_file_syntax())
        
        # Check 2: Import paths
        findings['checks'].append(self._check_import_paths())
        
        # Check 3: Pytest configuration
        findings['checks'].append(self._check_pytest_config())
        
        return findings
    
    def _check_fstring_compatibility(self) -> Dict:
        """Check for f-string syntax issues."""
        result = {
            'check': 'F-string compatibility',
            'status': 'OK',
            'details': [],
        }
        
        # Python 3.10+ restricts backslashes in f-string expressions
        if self.python_version >= '3.10':
            result['details'].append('Python 3.10+: Checking for backslashes in f-string expressions')
            
            # Search for problematic patterns
            pattern_files = [
                'codesentinel/cli/test_utils.py',
                'codesentinel/cli/__init__.py',
                'tests/test_ci_environment_parity.py',
            ]
            
            for file_path in pattern_files:
                full_path = self.repo_root / file_path
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8') as f:
                        for line_no, line in enumerate(f, 1):
                            # Look for f-strings with backslashes
                            if 'f"' in line or "f'" in line:
                                if '\\' in line and '{' in line:
                                    result['status'] = 'ISSUE_FOUND'
                                    result['details'].append(
                                        f"{file_path}:{line_no} - Potential f-string backslash issue"
                                    )
        
        return result
    
    def _check_type_annotations(self) -> Dict:
        """Check for Python 3.8 incompatible type annotations."""
        result = {
            'check': 'Type annotation compatibility (Python 3.8)',
            'status': 'OK',
            'details': [],
        }
        
        if self.python_version <= '3.8':
            result['details'].append('Python 3.8: Checking for PEP 585 lowercase generic syntax')
            
            # PEP 585 (lowercase generics) requires Python 3.9+
            # Look for: list[...], dict[...], tuple[...], set[...]
            suspicious_patterns = ['list[', 'dict[', 'tuple[', 'set[']
            
            for file_path in (self.repo_root / 'codesentinel').rglob('*.py'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_no, line in enumerate(f, 1):
                        for pattern in suspicious_patterns:
                            if pattern in line and '->' in line:  # Type annotation context
                                result['status'] = 'ISSUE_FOUND'
                                rel_path = file_path.relative_to(self.repo_root)
                                result['details'].append(
                                    f"{rel_path}:{line_no} - Incompatible type annotation: {pattern}"
                                )
        
        return result
    
    def _check_print_statements(self) -> Dict:
        """Check for Unicode encoding issues in print statements."""
        result = {
            'check': 'Print statement encoding (Windows compatibility)',
            'status': 'OK',
            'details': [],
        }
        
        # Windows uses cp1252, not UTF-8; Unicode symbols cause UnicodeEncodeError
        unicode_symbols = ['✓', '✗', '→', '←', '•', '●', '■', '□']
        
        for file_path in (self.repo_root / 'codesentinel').rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_no, line in enumerate(f, 1):
                        if 'print(' in line or 'logger.' in line:
                            for symbol in unicode_symbols:
                                if symbol in line:
                                    result['status'] = 'ISSUE_FOUND'
                                    rel_path = file_path.relative_to(self.repo_root)
                                    result['details'].append(
                                        f"{rel_path}:{line_no} - Unicode symbol '{symbol}' in output"
                                    )
            except UnicodeDecodeError:
                # File encoding issue - skip
                pass
        
        return result
    
    def _check_package_markers(self) -> Dict:
        """Check for missing __init__.py files."""
        result = {
            'check': 'Package markers (__init__.py)',
            'status': 'OK',
            'details': [],
        }
        
        # Critical package directories
        package_dirs = [
            'codesentinel',
            'codesentinel/cli',
            'codesentinel/core',
            'codesentinel/gui',
            'codesentinel/utils',
            'tools',
            'tools/codesentinel',
            'tools/config',
            'tests',
        ]
        
        for dir_name in package_dirs:
            dir_path = self.repo_root / dir_name
            init_file = dir_path / '__init__.py'
            
            if dir_path.exists() and not init_file.exists():
                result['status'] = 'ISSUE_FOUND'
                result['details'].append(f"Missing: {dir_name}/__init__.py")
        
        return result
    
    def _check_module_structure(self) -> Dict:
        """Check module import structure."""
        result = {
            'check': 'Module structure and imports',
            'status': 'OK',
            'details': [],
        }
        
        # Try importing main package
        try:
            sys.path.insert(0, str(self.repo_root))
            import codesentinel
            result['details'].append('[OK] codesentinel imports successfully')
        except Exception as e:
            result['status'] = 'ISSUE_FOUND'
            result['details'].append(f"[FAIL] Failed to import codesentinel: {e}")
        finally:
            if str(self.repo_root) in sys.path:
                sys.path.remove(str(self.repo_root))
        
        return result
    
    def _check_dependencies(self) -> Dict:
        """Check dependency resolution."""
        result = {
            'check': 'Dependency resolution',
            'status': 'OK',
            'details': [],
        }
        
        # Check requirements files
        req_files = [
            'requirements.txt',
            'requirements-dev.txt',
        ]
        
        for req_file in req_files:
            req_path = self.repo_root / req_file
            if req_path.exists():
                result['details'].append(f"[OK] Found: {req_file}")
            else:
                result['details'].append(f"[FAIL] Missing: {req_file}")
        
        return result
    
    def _check_test_file_syntax(self) -> Dict:
        """Check test file syntax."""
        result = {
            'check': 'Test file syntax',
            'status': 'OK',
            'details': [],
        }
        
        # Compile test files to check syntax
        test_files = list((self.repo_root / 'tests').glob('test_*.py'))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(test_file), 'exec')
                result['details'].append(f"[OK] {test_file.name}")
            except SyntaxError as e:
                result['status'] = 'ISSUE_FOUND'
                result['details'].append(f"[FAIL] {test_file.name}: {e.msg} (line {e.lineno})")
        
        return result
    
    def _check_import_paths(self) -> Dict:
        """Check import path resolution."""
        result = {
            'check': 'Import path resolution',
            'status': 'OK',
            'details': [],
        }
        
        result['details'].append(f"Python sys.path length: {len(sys.path)}")
        result['details'].append(f"Repo root in path: {str(self.repo_root) in sys.path}")
        
        return result
    
    def _check_pytest_config(self) -> Dict:
        """Check pytest configuration."""
        result = {
            'check': 'Pytest configuration',
            'status': 'OK',
            'details': [],
        }
        
        pytest_config = self.repo_root / 'pytest.ini'
        if pytest_config.exists():
            result['details'].append('[OK] pytest.ini found')
            with open(pytest_config, 'r', encoding='utf-8') as f:
                result['details'].append(f"Config:\n{f.read()}")
        else:
            result['details'].append('[FAIL] pytest.ini not found')
        
        return result
    
    def run_full_investigation(self) -> Dict:
        """Run all investigations and return findings."""
        findings = {
            'python_version': self.python_version,
            'syntax_check': self.investigate_syntax_errors(),
            'import_check': self.investigate_import_errors(),
            'collection_check': self.investigate_collection_failures(),
        }
        
        return findings
    
    def print_findings(self, findings: Dict) -> None:
        """Print findings in readable format."""
        print(f"\n{'='*70}")
        print(f"CI Failure Diagnostics Report")
        print(f"Python Version: {findings['python_version']}")
        print(f"{'='*70}\n")
        
        for check_category, check_findings in findings.items():
            if isinstance(check_findings, dict) and 'checks' in check_findings:
                print(f"\n{check_category.upper()}")
                print(f"{'-'*70}")
                for check in check_findings['checks']:
                    status_marker = '[OK]' if check['status'] == 'OK' else '[ISSUE]'
                    print(f"{status_marker} {check['check']}")
                    for detail in check.get('details', []):
                        print(f"    {detail}")


def main():
    """Run diagnostics."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CI Failure Diagnostics')
    parser.add_argument('--python-version', help='Python version to check against')
    parser.add_argument('--investigate-all', action='store_true', help='Run all investigations')
    parser.add_argument('--failure-type', choices=['syntax', 'import', 'collection'],
                       help='Specific failure type to investigate')
    
    args = parser.parse_args()
    
    diagnostics = CIFailureDiagnostics(python_version=args.python_version)
    
    if args.investigate_all:
        findings = diagnostics.run_full_investigation()
        diagnostics.print_findings(findings)
    elif args.failure_type:
        investigation_method = getattr(diagnostics, f'investigate_{args.failure_type}_errors')
        findings = investigation_method()
        print(f"\nInvestigation: {args.failure_type} errors")
        for check in findings.get('checks', []):
            print(f"  {check}")
    else:
        # Default: run full investigation
        findings = diagnostics.run_full_investigation()
        diagnostics.print_findings(findings)


if __name__ == '__main__':
    main()
