#!/usr/bin/env python3
"""
CodeSentinel Dependency Checker
===============================

Comprehensive dependency checking tool for CodeSentinel installation.
Checks all required and optional dependencies and provides installation guidance.
"""

import sys
import importlib
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Optional


class DependencyChecker:
    """Comprehensive dependency checker for CodeSentinel."""

    def __init__(self):
        self.results = {
            'python_version': None,
            'pip_available': False,
            'core_modules': {},
            'required_packages': {},
            'optional_packages': {},
            'build_tools': {},
            'system_tools': {},
        }

    def check_python_version(self) -> bool:
        """Check Python version requirements."""
        version = sys.version_info
        self.results['python_version'] = {
            'version': f"{version.major}.{version.minor}.{version.micro}",
            'meets_requirement': version >= (3, 13),
            'required': '>=3.13'
        }
        return version >= (3, 13)

    def check_pip(self) -> bool:
        """Check if pip is available."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', '--version'
            ], capture_output=True, text=True, check=True)
            
            self.results['pip_available'] = {
                'available': True,
                'version': result.stdout.strip(),
                'location': 'built-in'
            }
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.results['pip_available'] = {
                'available': False,
                'error': 'pip module not found',
                'location': None
            }
            return False

    def check_core_modules(self) -> bool:
        """Check core Python standard library modules."""
        core_modules = [
            'pathlib', 'json', 'os', 'sys', 'platform', 'subprocess',
            'urllib.request', 'urllib.error', 'smtplib', 'email.mime.text',
            'logging', 'datetime', 'argparse', 'shutil', 'getpass',
            'threading', 'queue', 'typing', 're', 'sysconfig'
        ]
        
        all_available = True
        for module in core_modules:
            try:
                importlib.import_module(module)
                self.results['core_modules'][module] = {
                    'available': True,
                    'version': getattr(importlib.import_module(module), '__version__', 'built-in')
                }
            except ImportError as e:
                self.results['core_modules'][module] = {
                    'available': False,
                    'error': str(e)
                }
                all_available = False
        
        return all_available

    def check_required_packages(self) -> bool:
        """Check required external packages."""
        required_packages = [
            ('requests', '>=2.25.0'),
            ('schedule', '>=1.1.0'),
        ]
        
        all_available = True
        for package, version_req in required_packages:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown')
                self.results['required_packages'][package] = {
                    'available': True,
                    'version': version,
                    'requirement': version_req
                }
            except ImportError as e:
                self.results['required_packages'][package] = {
                    'available': False,
                    'error': str(e),
                    'requirement': version_req
                }
                all_available = False
        
        return all_available

    def check_optional_packages(self) -> dict:
        """Check optional packages."""
        optional_packages = [
            ('tkinter', 'GUI functionality'),
            ('pytest', 'Testing framework'),
            ('black', 'Code formatting'),
            ('flake8', 'Linting'),
            ('mypy', 'Type checking'),
        ]
        
        for package, description in optional_packages:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'built-in')
                self.results['optional_packages'][package] = {
                    'available': True,
                    'version': version,
                    'description': description
                }
            except ImportError as e:
                self.results['optional_packages'][package] = {
                    'available': False,
                    'error': str(e),
                    'description': description
                }
        
        return self.results['optional_packages']

    def check_build_tools(self) -> dict:
        """Check build tools availability."""
        build_tools = [
            ('setuptools', 'Package building'),
            ('wheel', 'Wheel format support'),
        ]
        
        for tool, description in build_tools:
            try:
                module = importlib.import_module(tool)
                version = getattr(module, '__version__', 'unknown')
                self.results['build_tools'][tool] = {
                    'available': True,
                    'version': version,
                    'description': description
                }
            except ImportError as e:
                self.results['build_tools'][tool] = {
                    'available': False,
                    'error': str(e),
                    'description': description
                }
        
        return self.results['build_tools']

    def check_system_tools(self) -> dict:
        """Check system tools availability."""
        system_tools = [
            ('git', 'Version control'),
            ('python', 'Python interpreter'),
        ]
        
        for tool, description in system_tools:
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, check=True)
                self.results['system_tools'][tool] = {
                    'available': True,
                    'version': result.stdout.strip().split('\n')[0],
                    'description': description
                }
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.results['system_tools'][tool] = {
                    'available': False,
                    'error': 'command not found',
                    'description': description
                }
        
        return self.results['system_tools']

    def run_full_check(self) -> Dict:
        """Run comprehensive dependency check."""
        print("Running comprehensive dependency check...")
        print("=" * 50)
        
        # Check Python version
        print("\n1. Python Version:")
        if self.check_python_version():
            print(f"   ✓ Python {self.results['python_version']['version']} (meets requirement)")
        else:
            print(f"   ✗ Python {self.results['python_version']['version']} (requires >=3.13)")
        
        # Check pip
        print("\n2. Pip Availability:")
        if self.check_pip():
            print(f"   ✓ pip available: {self.results['pip_available']['version']}")
        else:
            print(f"   ✗ pip not available: {self.results['pip_available']['error']}")
        
        # Check core modules
        print("\n3. Core Modules:")
        if self.check_core_modules():
            print(f"   ✓ All {len(self.results['core_modules'])} core modules available")
        else:
            missing = [m for m, r in self.results['core_modules'].items() if not r['available']]
            print(f"   ✗ Missing core modules: {', '.join(missing)}")
        
        # Check required packages
        print("\n4. Required Packages:")
        if self.check_required_packages():
            print(f"   ✓ All required packages available")
        else:
            missing = [p for p, r in self.results['required_packages'].items() if not r['available']]
            print(f"   ✗ Missing required packages: {', '.join(missing)}")
        
        # Check optional packages
        print("\n5. Optional Packages:")
        self.check_optional_packages()
        available = [p for p, r in self.results['optional_packages'].items() if r['available']]
        missing = [p for p, r in self.results['optional_packages'].items() if not r['available']]
        
        if available:
            print(f"   ✓ Available: {', '.join(available)}")
        if missing:
            print(f"   - Missing (optional): {', '.join(missing)}")
        
        # Check build tools
        print("\n6. Build Tools:")
        self.check_build_tools()
        available = [t for t, r in self.results['build_tools'].items() if r['available']]
        missing = [t for t, r in self.results['build_tools'].items() if not r['available']]
        
        if available:
            print(f"   ✓ Available: {', '.join(available)}")
        if missing:
            print(f"   - Missing: {', '.join(missing)}")
        
        # Check system tools
        print("\n7. System Tools:")
        self.check_system_tools()
        available = [t for t, r in self.results['system_tools'].items() if r['available']]
        missing = [t for t, r in self.results['system_tools'].items() if not r['available']]
        
        if available:
            print(f"   ✓ Available: {', '.join(available)}")
        if missing:
            print(f"   - Missing: {', '.join(missing)}")
        
        return self.results

    def get_installation_status(self) -> str:
        """Get overall installation readiness status."""
        if not self.results['python_version']['meets_requirement']:
            return "BLOCKED: Python version too old"
        
        if not self.results['pip_available']['available']:
            return "BLOCKED: pip not available"
        
        missing_core = [m for m, r in self.results['core_modules'].items() if not r['available']]
        if missing_core:
            return f"BLOCKED: Missing core modules: {', '.join(missing_core)}"
        
        missing_required = [p for p, r in self.results['required_packages'].items() if not r['available']]
        if missing_required:
            return f"READY: Will install missing packages: {', '.join(missing_required)}"
        
        return "READY: All dependencies satisfied"

    def provide_installation_guidance(self):
        """Provide specific installation guidance based on check results."""
        print("\n" + "=" * 50)
        print("INSTALLATION GUIDANCE")
        print("=" * 50)
        
        status = self.get_installation_status()
        print(f"\nStatus: {status}")
        
        if "BLOCKED" in status:
            print("\n❌ Installation is BLOCKED. Please fix the following issues:")
            
            if not self.results['python_version']['meets_requirement']:
                print("\n1. Upgrade Python:")
                print("   - Download Python 3.13+ from https://python.org")
                print("   - Or use a package manager (e.g., conda, homebrew)")
            
            if not self.results['pip_available']['available']:
                print("\n2. Install pip:")
                print("   - Download get-pip.py from https://bootstrap.pypa.io/get-pip.py")
                print("   - Run: python get-pip.py")
                print("   - Or install Python from python.org (includes pip)")
            
            missing_core = [m for m, r in self.results['core_modules'].items() if not r['available']]
            if missing_core:
                print(f"\n3. Fix Python installation - missing core modules: {', '.join(missing_core)}")
                print("   - Reinstall Python from python.org")
                print("   - These modules should be included with Python")
        
        else:
            print("\n✅ Installation can proceed!")
            
            missing_required = [p for p, r in self.results['required_packages'].items() if not r['available']]
            if missing_required:
                print(f"\nRequired packages will be installed automatically:")
                for package in missing_required:
                    req = self.results['required_packages'][package]['requirement']
                    print(f"   - {package} {req}")
            
            missing_optional = [p for p, r in self.results['optional_packages'].items() if not r['available']]
            if missing_optional:
                print(f"\nOptional packages (install manually if needed):")
                for package in missing_optional:
                    desc = self.results['optional_packages'][package]['description']
                    print(f"   - pip install {package}  # {desc}")
        
        print(f"\nTo run the installer:")
        print(f"   python install.py")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check CodeSentinel dependencies"
    )
    parser.add_argument(
        '--json', action='store_true',
        help='Output results in JSON format'
    )
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Only show status, not detailed output'
    )
    
    args = parser.parse_args()
    
    checker = DependencyChecker()
    
    if args.quiet:
        # Quick check mode
        checker.check_python_version()
        checker.check_pip()
        checker.check_core_modules()
        checker.check_required_packages()
        
        status = checker.get_installation_status()
        print(status)
        
        if "BLOCKED" in status:
            sys.exit(1)
        else:
            sys.exit(0)
    
    elif args.json:
        # JSON output mode
        import json
        results = checker.run_full_check()
        print(json.dumps(results, indent=2))
    
    else:
        # Full interactive mode
        results = checker.run_full_check()
        checker.provide_installation_guidance()


if __name__ == "__main__":
    main()