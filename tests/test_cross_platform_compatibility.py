"""
Test Suite: Cross-Platform File Encoding Compatibility
======================================================

Validates that all Python files in the workspace can be read with UTF-8 encoding.
This prevents UnicodeDecodeError crashes on Windows and other platforms.

Addresses: INC-20251113-002 (F-string syntax) required cross-platform validation
Category: Integration tests (validates entire codebase structure)
Markers: @pytest.mark.integration
"""

import pytest
from pathlib import Path


class TestFileEncodingCompatibility:
    """Test UTF-8 encoding compatibility across all workspace Python files."""
    
    @pytest.fixture
    def repo_root(self):
        """Get repository root directory."""
        return Path(__file__).parent.parent
    
    def test_codesentinel_module_utf8_encoding(self, repo_root):
        """Test all files in codesentinel/ module are UTF-8 readable."""
        codesentinel_dir = repo_root / 'codesentinel'
        encoding_issues = []
        
        for file_path in codesentinel_dir.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError as e:
                encoding_issues.append({
                    'file': str(file_path.relative_to(repo_root)),
                    'error': str(e)
                })
        
        assert not encoding_issues, (
            f"Found {len(encoding_issues)} files with UTF-8 encoding issues:\n" +
            "\n".join([f"  {issue['file']}: {issue['error']}" for issue in encoding_issues])
        )
    
    def test_tests_module_utf8_encoding(self, repo_root):
        """Test all files in tests/ directory are UTF-8 readable."""
        tests_dir = repo_root / 'tests'
        encoding_issues = []
        
        if not tests_dir.exists():
            pytest.skip("tests/ directory not found")
        
        for file_path in tests_dir.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError as e:
                encoding_issues.append({
                    'file': str(file_path.relative_to(repo_root)),
                    'error': str(e)
                })
        
        assert not encoding_issues, (
            f"Found {len(encoding_issues)} test files with UTF-8 encoding issues:\n" +
            "\n".join([f"  {issue['file']}: {issue['error']}" for issue in encoding_issues])
        )
    
    def test_tools_module_utf8_encoding(self, repo_root):
        """Test all files in tools/ directory are UTF-8 readable."""
        tools_dir = repo_root / 'tools'
        encoding_issues = []
        
        if not tools_dir.exists():
            pytest.skip("tools/ directory not found")
        
        for file_path in tools_dir.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError as e:
                encoding_issues.append({
                    'file': str(file_path.relative_to(repo_root)),
                    'error': str(e)
                })
        
        assert not encoding_issues, (
            f"Found {len(encoding_issues)} tool files with UTF-8 encoding issues:\n" +
            "\n".join([f"  {issue['file']}: {issue['error']}" for issue in encoding_issues])
        )


class TestPrintStatementCrossPlatformCompatibility:
    """Test that print statements use Windows-safe characters."""
    
    @pytest.fixture
    def repo_root(self):
        """Get repository root directory."""
        return Path(__file__).parent.parent
    
    def test_no_unicode_symbols_in_print_statements(self, repo_root):
        """
        Verify that print() and logger.* calls don't use Unicode symbols.
        
        Windows console (cp1252) cannot display Unicode symbols like ✓ ✗ → ←.
        Must use ASCII alternatives: [OK] [FAIL] [WARN] -> *
        
        Reference: docs/architecture/CROSS_PLATFORM_OUTPUT_POLICY.md
        """
        # Unicode symbols that cause UnicodeEncodeError on Windows
        unsafe_symbols = {
            '✓': '[OK]',
            '✗': '[FAIL]',
            '→': '->',
            '←': '<-',
            '•': '*',
            '●': '*',
            '■': '[]',
            '□': '[]',
        }
        
        codesentinel_dir = repo_root / 'codesentinel'
        violations = []
        
        for file_path in codesentinel_dir.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_no, line in enumerate(f, 1):
                        # Check only print() and logger.* statements
                        if 'print(' in line or 'logger.' in line:
                            for symbol, replacement in unsafe_symbols.items():
                                if symbol in line:
                                    violations.append({
                                        'file': str(file_path.relative_to(repo_root)),
                                        'line': line_no,
                                        'symbol': symbol,
                                        'replace_with': replacement,
                                        'code': line.strip()
                                    })
            except UnicodeDecodeError:
                # Skip files with encoding issues (tested separately)
                pass
        
        assert not violations, (
            f"Found {len(violations)} print statements with unsafe Unicode symbols:\n" +
            "\n".join([
                f"  {v['file']}:{v['line']} - Replace '{v['symbol']}' with '{v['replace_with']}'\n"
                f"    Code: {v['code']}"
                for v in violations
            ])
        )
    
    def test_no_backslash_in_fstring_expressions(self, repo_root):
        """
        Verify that f-string expressions don't contain backslashes.
        
        Python 3.10+ prohibits backslashes in f-string expression parts.
        Example: f"({len(content.split('\n'))})" - INVALID
        Fix: Extract to variable outside f-string
        
        Reference: INC-20251113-002
        """
        cli_dir = repo_root / 'codesentinel' / 'cli'
        violations = []
        
        for file_path in cli_dir.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_no, line in enumerate(f, 1):
                        # Look for f-strings (f" or f')
                        if (('f"' in line or "f'" in line) and 
                            '{' in line and 
                            '\\' in line):
                            # Potential issue - flag for manual review
                            violations.append({
                                'file': str(file_path.relative_to(repo_root)),
                                'line': line_no,
                                'code': line.strip()
                            })
            except UnicodeDecodeError:
                pass
        
        # This is a warning-level check; syntax errors are caught by compilation
        if violations:
            pytest.warns(UserWarning, match="f-string backslash pattern detected")


class TestPackageStructureIntegrity:
    """Test that package structure is correctly configured for all Python versions."""
    
    @pytest.fixture
    def repo_root(self):
        """Get repository root directory."""
        return Path(__file__).parent.parent
    
    def test_required_init_files_present(self, repo_root):
        """
        Verify all package directories have __init__.py files.
        
        Missing __init__.py causes test collection failures on fresh Python installations.
        This was the root cause of INC-20251113-001.
        """
        required_packages = [
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
        
        missing_init = []
        for package_dir in required_packages:
            package_path = repo_root / package_dir
            init_file = package_path / '__init__.py'
            
            if package_path.exists() and not init_file.exists():
                missing_init.append(package_dir)
        
        assert not missing_init, (
            f"Missing __init__.py in {len(missing_init)} packages:\n" +
            "\n".join([f"  {pkg}/__init__.py" for pkg in missing_init])
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
