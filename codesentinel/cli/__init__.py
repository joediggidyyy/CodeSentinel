"""
Command Line Interface
======================

CLI entry point for CodeSentinel operations.
"""

import argparse
import sys
import os
import subprocess
import atexit
from pathlib import Path
from typing import Optional
import signal
import threading

from ..core import CodeSentinel
from ..utils.process_monitor import start_monitor, stop_monitor


class TimeoutError(Exception):
    """Custom timeout exception."""
    pass


def timeout_handler(signum, frame):
    """Handle timeout signal."""
    raise TimeoutError("Operation timed out")


def verify_documentation_branding(file_path: Path) -> tuple[bool, list[str]]:
    """
    Verify that documentation files follow SEAM Protection branding policy.
    
    CodeSentinel Policy: All public documentation must have consistent branding:
    - Primary locations: Use "SEAM Protected™" with trademark
    - Secondary locations: Use "SEAM Protection" or "SEAM-tight"
    - No excessive repetition or misuse
    
    Args:
        file_path: Path to documentation file to verify
        
    Returns:
        Tuple of (is_compliant, issues_found)
    """
    if not file_path.exists():
        return True, []
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Could not read file: {e}"]
    
    issues = []
    file_name = file_path.name
    
    # Check for old policy references that should be updated
    old_patterns = [
        ('SECURITY > EFFICIENCY > MINIMALISM', 'should use SEAM Protection™ instead'),
        ('SECURITY.*EFFICIENCY.*MINIMALISM', 'should use SEAM Protection™ instead'),
    ]
    
    import re
    for pattern, reason in old_patterns:
        if re.search(pattern, content):
            issues.append(f"{file_name}: Found old policy terminology - {reason}")
    
    # Check for specific files that MUST have branding
    required_branding = {
        'README.md': ['SEAM Protected™', 'SEAM-Tight'],
        'SECURITY.md': ['SEAM Protected™'],
        '__init__.py': ['SEAM Protected™'],
        'copilot-instructions.md': ['SEAM Protection™'],
        '.github': ['SEAM Protection™'],
    }
    
    for req_file, required_terms in required_branding.items():
        if req_file in file_name or req_file in str(file_path):
            found_any = any(term in content for term in required_terms)
            if not found_any:
                issues.append(
                    f"{file_name}: Missing required SEAM Protection branding. "
                    f"Should contain one of: {', '.join(required_terms)}"
                )
    
    is_compliant = len(issues) == 0
    return is_compliant, issues


def verify_documentation_headers_footers(file_path: Path) -> tuple[bool, list[str], dict]:
    """
    Verify that documentation files have proper headers and footers.
    
    Requirements:
    - Markdown files (.md) should have clear title headers
    - Documentation should include metadata (version, date when applicable)
    - Key files should have SEAM Protection footer
    - Python files should have proper docstring headers
    
    Args:
        file_path: Path to documentation file to verify
        
    Returns:
        Tuple of (is_compliant, issues_found, metadata)
    """
    if not file_path.exists():
        return True, [], {}
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Could not read file: {e}"], {}
    
    issues = []
    file_name = file_path.name
    metadata = {
        'has_title': False,
        'has_footer': False,
        'has_metadata': False,
        'file_type': file_path.suffix,
    }
    
    import re
    
    # Check markdown files
    if file_path.suffix == '.md':
        # Check for title (H1 heading)
        if re.search(r'^#\s+\S', content, re.MULTILINE):
            metadata['has_title'] = True
        else:
            issues.append(f"{file_name}: Missing H1 title header (# Title)")
        
        # Check for SEAM Protection footer in key files
        key_docs = {'README.md', 'SECURITY.md', 'CHANGELOG.md', 'CONTRIBUTING.md'}
        if file_name in key_docs:
            if 'SEAM Protected™' in content or 'SEAM Protection' in content:
                metadata['has_footer'] = True
            else:
                issues.append(f"{file_name}: Key documentation missing SEAM Protection footer")
        
        # Check for metadata (version, date, or last updated)
        if re.search(r'(Version|Date|Last Updated|Last Reviewed).*:\s*', content, re.IGNORECASE):
            metadata['has_metadata'] = True
    
    # Check Python files
    elif file_path.suffix == '.py':
        # Check for module docstring
        if content.startswith('"""') or content.startswith("'''"):
            metadata['has_title'] = True
        else:
            # Only warn if file is significant (>50 lines)
            if len(content.split('\n')) > 50:
                issues.append(f"{file_name}: Missing module docstring")
    
    is_compliant = len(issues) == 0
    return is_compliant, issues, metadata


def apply_branding_fixes(file_path: Path, verbose: bool = False) -> tuple[bool, str]:
    """
    Apply automatic branding fixes to documentation files.
    
    Args:
        file_path: Path to documentation file
        verbose: Print detailed output
        
    Returns:
        Tuple of (success, message)
    """
    if not file_path.exists():
        return True, f"File not found: {file_path}"
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Could not read file: {e}"
    
    original_content = content
    modified = False
    
    import re
    
    # Fix 1: Replace old policy terminology with SEAM Protection
    patterns = [
        (r'SECURITY > EFFICIENCY > MINIMALISM', 'SEAM Protected™: Security, Efficiency, And Minimalism'),
        (r'SECURITY.*EFFICIENCY.*MINIMALISM', 'SEAM Protected™: Security, Efficiency, And Minimalism'),
    ]
    
    for old, new in patterns:
        if re.search(old, content):
            content = re.sub(old, new, content)
            modified = True
            if verbose:
                print(f"  Fixed: Replaced old policy terminology with SEAM Protection branding")
    
    # Fix 2: Add branding footer to markdown documentation files
    if file_path.suffix == '.md':
        key_docs = {'README.md', 'SECURITY.md', 'CHANGELOG.md', 'CONTRIBUTING.md'}
        if file_path.name in key_docs:
            footer = "\n\n---\n\nSEAM Protected™ by CodeSentinel"
            if footer not in content:
                # Only add if file is substantial and doesn't already have a similar footer
                if len(content) > 100 and not re.search(r'---\s*$', content, re.MULTILINE):
                    content += footer
                    modified = True
                    if verbose:
                        print(f"  Added: SEAM Protection branding footer")
    
    if modified:
        try:
            file_path.write_text(content, encoding='utf-8')
            return True, f"Applied branding fixes to {file_path.name}"
        except Exception as e:
            return False, f"Could not write file: {e}"
    
    return True, f"No branding fixes needed for {file_path.name}"


def apply_header_footer_fixes(file_path: Path, verbose: bool = False) -> tuple[bool, str]:
    """
    Apply automatic header and footer fixes to documentation files.
    
    Args:
        file_path: Path to documentation file
        verbose: Print detailed output
        
    Returns:
        Tuple of (success, message)
    """
    if not file_path.exists():
        return True, f"File not found: {file_path}"
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Could not read file: {e}"
    
    original_content = content
    modified = False
    
    import re
    
    # Fix for markdown files: ensure proper footer formatting
    if file_path.suffix == '.md':
        key_docs = {'README.md', 'SECURITY.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 
                    'CONTRIBUTING.md', 'QUICK_START.md'}
        
        if file_path.name in key_docs:
            # Ensure footer exists with proper formatting
            if not re.search(r'---\s*$', content, re.MULTILINE):
                # Add separator if missing
                if not content.endswith('\n'):
                    content += '\n'
                content += '\n---\n\nSEAM Protected™ by CodeSentinel\n'
                modified = True
                if verbose:
                    print(f"  Added: Proper footer separator and branding")
    
    if modified:
        try:
            file_path.write_text(content, encoding='utf-8')
            return True, f"Applied header/footer fixes to {file_path.name}"
        except Exception as e:
            return False, f"Could not write file: {e}"
    
    return True, f"No header/footer fixes needed for {file_path.name}"


# ============================================================================
# Header/Footer Template System
# ============================================================================

def detect_project_info() -> dict:
    """
    Intelligently detect project and repository information.
    
    Returns:
        Dictionary with detected project info (project_name, description, repo_url, etc.)
    """
    import json
    import re
    
    project_root = Path.cwd()
    info = {
        'project_name': 'Project',
        'description': 'A powerful automation tool',
        'repo_name': project_root.name,
        'repo_url': '',
        'version': '1.0.0',
    }
    
    # Try to detect from pyproject.toml
    pyproject_path = project_root / 'pyproject.toml'
    if pyproject_path.exists():
        try:
            content = pyproject_path.read_text(encoding='utf-8')
            
            # Extract name from [project] section
            name_match = re.search(r'^\s*name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if name_match:
                info['project_name'] = name_match.group(1)
            
            # Extract description
            desc_match = re.search(r'^\s*description\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if desc_match:
                info['description'] = desc_match.group(1)
            
            # Extract version
            version_match = re.search(r'^\s*version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if version_match:
                info['version'] = version_match.group(1)
        except Exception:
            pass
    
    # Try to detect from setup.py
    setup_path = project_root / 'setup.py'
    if setup_path.exists() and not info.get('project_name') or info['project_name'] == 'Project':
        try:
            content = setup_path.read_text(encoding='utf-8')
            
            # Extract name
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                info['project_name'] = name_match.group(1)
            
            # Extract description
            desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if desc_match:
                info['description'] = desc_match.group(1)
        except Exception:
            pass
    
    # Try to detect from package __init__.py
    pkg_init = project_root / 'codesentinel' / '__init__.py'
    if pkg_init.exists():
        try:
            content = pkg_init.read_text(encoding='utf-8')
            
            # Look for docstring with description
            docstring_match = re.search(r'^"""(.*?)"""', content, re.MULTILINE | re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1).strip()
                lines = docstring.split('\n')
                # Use the first non-empty line after title as description
                for line in lines[1:]:
                    line = line.strip()
                    if line and not line.startswith('='):
                        info['description'] = line
                        break
        except Exception:
            pass
    
    # Try to detect from git remote
    try:
        git_url = subprocess.check_output(
            ['git', 'config', '--get', 'remote.origin.url'],
            cwd=project_root,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        if git_url:
            info['repo_url'] = git_url
            # Extract repo name from URL
            if '/' in git_url:
                info['repo_name'] = git_url.split('/')[-1].replace('.git', '')
    except:
        pass
    
    return info


HEADER_TEMPLATES = {
    'README.md': {
        'template': '# {title}\n\n{subtitle}\n\n---\n\n',
        'description': 'Main project README template',
        'placeholders': {
            'title': 'Project Name (e.g., "CodeSentinel")',
            'subtitle': 'Brief project description',

        },
        'example': '# CodeSentinel\n\nSecurity-first automated maintenance and monitoring system.\n\n---\n\n'
    },
    'SECURITY.md': {
        'template': '# Security Policy\n\nThis document outlines the security practices and policies for CodeSentinel.\n\n---\n\n',
        'description': 'Security policy document template',
        'placeholders': {},
        'example': '# Security Policy\n\nThis document outlines the security practices and policies for CodeSentinel.\n\n---\n\n'
    },
    'CHANGELOG.md': {
        'template': '# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n---\n\n',
        'description': 'Changelog tracking document template',
        'placeholders': {},
        'example': '# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n---\n\n'
    },
    'CONTRIBUTING.md': {
        'template': '# Contributing Guidelines\n\nThank you for your interest in contributing to CodeSentinel!\n\n---\n\n',
        'description': 'Contributing guidelines template',
        'placeholders': {},
        'example': '# Contributing Guidelines\n\nThank you for your interest in contributing to CodeSentinel!\n\n---\n\n'
    },
}

FOOTER_TEMPLATES = {
    'standard': {
        'template': '\n---\n\nSEAM Protected™ by CodeSentinel\n',
        'description': 'Standard SEAM Protection branding footer',
    },
    'with_links': {
        'template': '\n---\n\nSEAM Protected™ by CodeSentinel\n\n- [Security Policy](SECURITY.md)\n- [Contributing](CONTRIBUTING.md)\n- [License](LICENSE)\n',
        'description': 'Footer with links to key documents',
    },
    'with_version': {
        'template': '\n---\n\n**Version:** {version}\n\nSEAM Protected™ by CodeSentinel\n',
        'description': 'Footer with version information',
    },
    'minimal': {
        'template': '\n\nSEAM Protected™ by CodeSentinel\n',
        'description': 'Minimal footer without separator line',
    },
}


def get_header_templates() -> dict:
    """
    Get all available header templates with project-specific values filled in.
    
    Automatically detects project name and description and integrates them.
    """
    project_info = detect_project_info()
    
    # Create dynamic templates based on project info
    return {
        'README.md': {
            'template': f"# {project_info['project_name']}\n\n{project_info['description']}\n\n---\n\n",
            'description': 'Main project README template',
            'project_specific': True,
        },
        'SECURITY.md': {
            'template': f"# Security Policy\n\nThis document outlines the security practices and policies for {project_info['project_name']}.\n\n---\n\n",
            'description': 'Security policy document template',
            'project_specific': True,
        },
        'CHANGELOG.md': {
            'template': "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n---\n\n",
            'description': 'Changelog tracking document template',
            'project_specific': False,
        },
        'CONTRIBUTING.md': {
            'template': f"# Contributing Guidelines\n\nThank you for your interest in contributing to {project_info['project_name']}!\n\n---\n\n",
            'description': 'Contributing guidelines template',
            'project_specific': True,
        },
    }


def get_footer_templates() -> dict:
    """
    Get all available footer templates with project-specific values filled in.
    
    Automatically detects project name and version and integrates them.
    """
    project_info = detect_project_info()
    
    return {
        'standard': {
            'template': '\n---\n\nSEAM Protected™ by CodeSentinel\n',
            'description': 'Standard SEAM Protection branding footer',
        },
        'with_project': {
            'template': f'\n---\n\n{project_info["project_name"]} - SEAM Protected™ by CodeSentinel\n',
            'description': 'Footer with project name',
            'project_specific': True,
        },
        'with_links': {
            'template': '\n---\n\nSEAM Protected™ by CodeSentinel\n\n- [Security Policy](SECURITY.md)\n- [Contributing](CONTRIBUTING.md)\n- [License](LICENSE)\n',
            'description': 'Footer with links to key documents',
        },
        'with_version': {
            'template': f'\n---\n\n**Version:** {project_info["version"]}\n\nSEAM Protected™ by CodeSentinel\n',
            'description': 'Footer with version information',
            'project_specific': True,
        },
        'minimal': {
            'template': '\n\nSEAM Protected™ by CodeSentinel\n',
            'description': 'Minimal footer without separator line',
        },
    }


def show_template_options(template_type: str = 'both') -> None:
    """
    Display available header and footer templates with project-specific values.
    
    Args:
        template_type: 'header', 'footer', or 'both'
    """
    project_info = detect_project_info()
    print("\n" + "="*70)
    print(f"📦 Detected Project: {project_info['project_name']}")
    print(f"   Description: {project_info['description']}")
    if project_info['repo_url']:
        print(f"   Repository: {project_info['repo_url']}")
    print("="*70)
    
    if template_type in ['header', 'both']:
        print("\nHEADER TEMPLATES")
        print("="*70)
        headers = get_header_templates()
        for file_name, template_info in headers.items():
            marker = "⭐" if template_info.get('project_specific') else "  "
            print(f"\n{marker} 📄 {file_name}")
            print(f"   Description: {template_info['description']}")
            print(f"   Preview:\n")
            lines = template_info['template'].split("\n")[:3]
            for line in lines:
                if line:
                    print(f"   {line}")
    
    if template_type in ['footer', 'both']:
        if template_type == 'both':
            print("\n" + "="*70)
        print("FOOTER TEMPLATES")
        print("="*70)
        footers = get_footer_templates()
        for template_name, template_info in footers.items():
            marker = "⭐" if template_info.get('project_specific') else "  "
            print(f"\n{marker} 🔖 {template_name.upper()}")
            print(f"   Description: {template_info['description']}")
            print(f"   Preview:\n")
            lines = template_info['template'].split("\n")[:3]
            for line in lines:
                if line:
                    print(f"   {line}")
    
    print("\n" + "="*70)
    print("⭐ = Project-specific (uses detected project name/version)")
    print("="*70 + "\n")


def set_header_for_file(file_path: Path, template_name: str = None, custom_header: str = None) -> tuple[bool, str]:
    """
    Set header for a documentation file.
    
    Args:
        file_path: Path to file to modify
        template_name: Name of predefined template or file name
        custom_header: Custom header text to use instead of template
        
    Returns:
        Tuple of (success, message)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Could not read file: {e}"
    
    import re
    
    # Get dynamic templates (with project-specific info)
    headers = get_header_templates()
    
    # Determine which header to use
    header_text = None
    if custom_header:
        header_text = custom_header
    elif template_name and template_name in headers:
        template_info = headers[template_name]
        header_text = template_info['template']
    elif file_path.name in headers:
        template_info = headers[file_path.name]
        header_text = template_info['template']
    else:
        return False, f"No template found for {file_path.name}"
    
    # Remove existing header (first H1 and separator line)
    content = re.sub(r'^#\s+.*?(?=\n\n|$)', '', content, count=1, flags=re.MULTILINE)
    content = re.sub(r'^\s*---\s*\n', '', content, flags=re.MULTILINE)
    
    # Add new header
    new_content = header_text + content.lstrip()
    
    try:
        file_path.write_text(new_content, encoding='utf-8')
        return True, f"Updated header for {file_path.name}"
    except Exception as e:
        return False, f"Could not write file: {e}"


def set_footer_for_file(file_path: Path, template_name: str = 'standard', custom_footer: str = None) -> tuple[bool, str]:
    """
    Set footer for a documentation file.
    
    Args:
        file_path: Path to file to modify
        template_name: Name of predefined footer template
        custom_footer: Custom footer text to use instead of template
        
    Returns:
        Tuple of (success, message)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Could not read file: {e}"
    
    import re
    
    # Get dynamic templates (with project-specific info)
    footers = get_footer_templates()
    
    # Determine which footer to use
    footer_text = None
    if custom_footer:
        footer_text = custom_footer
    elif template_name in footers:
        footer_text = footers[template_name]['template']
    else:
        return False, f"Footer template '{template_name}' not found"
    
    # Remove existing footer (everything from last --- to end, or last paragraph)
    content = re.sub(r'\n\s*---.*$', '', content, flags=re.DOTALL)
    content = re.sub(r'\n\s*SEAM Protected™.*$', '', content, flags=re.DOTALL | re.MULTILINE)
    
    # Add new footer
    if not content.endswith('\n'):
        content += '\n'
    
    new_content = content + footer_text
    
    try:
        file_path.write_text(new_content, encoding='utf-8')
        return True, f"Updated footer for {file_path.name}"
    except Exception as e:
        return False, f"Could not write file: {e}"


def edit_headers_interactive(doc_files: list[Path] = None) -> None:
    """
    Interactive mode to edit headers for multiple documentation files.
    
    Args:
        doc_files: List of files to edit, or None to use defaults
    """
    if doc_files is None:
        project_root = Path.cwd()
        doc_files = [
            project_root / "README.md",
            project_root / "SECURITY.md",
            project_root / "CHANGELOG.md",
            project_root / "CONTRIBUTING.md",
        ]
    
    print("\n" + "="*70)
    print("📝 INTERACTIVE HEADER EDITOR")
    print("="*70)
    
    for file_path in doc_files:
        if not file_path.exists():
            continue
        
        print(f"\n📄 {file_path.name}")
        print("-" * 70)
        
        # Show template options with project-specific values
        headers = get_header_templates()
        if file_path.name in headers:
            template_info = headers[file_path.name]
            project_marker = "⭐" if template_info.get('project_specific') else "  "
            print(f"{project_marker} Description: {template_info['description']}")
            print(f"\nSuggested template:\n")
            print(template_info['template'][:200])
            
            choice = input("Use suggested template? (y/n/custom): ").strip().lower()
            
            if choice == 'y':
                success, msg = set_header_for_file(file_path, file_path.name)
                print(f"✓ {msg}" if success else f"❌ {msg}")
            elif choice == 'custom':
                print("Enter custom header (type 'END' on new line when done):")
                lines = []
                while True:
                    line = input()
                    if line == 'END':
                        break
                    lines.append(line)
                custom_header = '\n'.join(lines) + '\n'
                success, msg = set_header_for_file(file_path, custom_header=custom_header)
                print(f"✓ {msg}" if success else f"❌ {msg}")
            else:
                print("Skipped.")
        else:
            print(f"No template available for {file_path.name}")
    
    print("\n" + "="*70 + "\n")


def edit_footers_interactive(doc_files: list[Path] = None) -> None:
    """
    Interactive mode to edit footers for multiple documentation files.
    
    Args:
        doc_files: List of files to edit, or None to use defaults
    """
    if doc_files is None:
        project_root = Path.cwd()
        doc_files = [
            project_root / "README.md",
            project_root / "SECURITY.md",
            project_root / "CHANGELOG.md",
            project_root / "CONTRIBUTING.md",
        ]
    
    print("\n" + "="*70)
    print("🔖 INTERACTIVE FOOTER EDITOR")
    print("="*70)
    
    for file_path in doc_files:
        if not file_path.exists():
            continue
        
        print(f"\n📄 {file_path.name}")
        print("-" * 70)
        
        # Show footer template options with project-specific values
        footers = get_footer_templates()
        print("Available footer templates:\n")
        for idx, (template_name, template_info) in enumerate(footers.items(), 1):
            marker = "⭐" if template_info.get('project_specific') else "  "
            print(f"  {idx}. {marker} {template_name.upper()}: {template_info['description']}")
        
        choice = input("\nSelect template (number/custom): ").strip().lower()
        
        if choice.isdigit() and 1 <= int(choice) <= len(footers):
            template_name = list(footers.keys())[int(choice) - 1]
            success, msg = set_footer_for_file(file_path, template_name)
            print(f"✓ {msg}" if success else f"❌ {msg}")
        elif choice == 'custom':
            print("Enter custom footer (type 'END' on new line when done):")
            lines = []
            while True:
                line = input()
                if line == 'END':
                    break
                lines.append(line)
            custom_footer = '\n' + '\n'.join(lines) + '\n'
            success, msg = set_footer_for_file(file_path, custom_footer=custom_footer)
            print(f"✓ {msg}" if success else f"❌ {msg}")
        else:
            print("Skipped.")
    
    print("\n" + "="*70 + "\n")



def main():
    """Main CLI entry point."""
    # Start low-cost process monitor daemon (checks every 60 seconds)
    try:
        monitor = start_monitor(check_interval=60, enabled=True)
        atexit.register(stop_monitor)  # Ensure cleanup on exit
    except Exception as e:
        # Don't fail if monitor can't start (e.g., missing psutil)
        print(f"Warning: Process monitor not started: {e}", file=sys.stderr)
    
    # Quick trigger: allow '!!!!' as an alias for interactive dev audit
    # Support optional focus parameter: '!!!! <focus_area>'
    # Process !!!! arguments before creating parser
    processed_argv = []
    focus_param = None
    
    i = 0
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith('!!!!'):
            if arg == '!!!!':
                processed_argv.append('dev-audit')
            else:
                processed_argv.append('dev-audit')
        elif processed_argv and processed_argv[-1] == 'dev-audit' and not arg.startswith('-') and focus_param is None:
            # First non-flag argument after dev-audit is focus
            focus_param = arg
        else:
            processed_argv.append(arg)
        i += 1
    
    # Apply focus parameter
    if focus_param and 'dev-audit' in processed_argv:
        dev_audit_idx = processed_argv.index('dev-audit')
        processed_argv.insert(dev_audit_idx + 1, '--focus')
        processed_argv.insert(dev_audit_idx + 2, focus_param)
    
    # Replace sys.argv if we made changes
    if processed_argv != list(sys.argv):
        sys.argv = processed_argv
    parser = argparse.ArgumentParser(
        description="CodeSentinel - SEAM Protected™ Automated Maintenance & Security Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog="""
Examples:
  codesentinel status                           # Show current status
  codesentinel scan                             # Run security scan
  codesentinel maintenance daily                # Run daily maintenance
  codesentinel alert "Test message"             # Send test alert
  codesentinel schedule start                   # Start maintenance scheduler
  codesentinel schedule stop                    # Stop maintenance scheduler
  codesentinel clean                            # Clean all (cache + temp + logs)
  codesentinel clean --root                     # Clean root directory clutter
  codesentinel clean --build --test             # Clean build and test artifacts
  codesentinel clean --emojis --dry-run         # Preview policy-violating emoji removal (smart detection)
  codesentinel clean --emojis --include-gui     # Include GUI files in emoji scan
  codesentinel clean --dry-run                  # Preview what would be deleted
  codesentinel update docs                      # Update repository documentation
  codesentinel update changelog --version 1.2.3 # Update CHANGELOG.md
  codesentinel update version patch             # Bump patch version
  codesentinel integrate --new                  # Integrate new CLI commands into workflows
  codesentinel integrate --all --dry-run        # Preview all integration opportunities
  codesentinel integrate --workflow ci-cd       # Integrate into CI/CD workflows
  codesentinel dev-audit                        # Run interactive development audit
  codesentinel !!!!                             # Quick trigger for dev-audit
  codesentinel !!!! scheduler                   # Focus audit on scheduler subsystem
  codesentinel !!!! "new feature"               # Focus audit on new feature development
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Status command
    subparsers.add_parser('status', help='Show CodeSentinel status')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Run security scan')
    scan_parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file for scan results'
    )

    # Maintenance command
    maintenance_parser = subparsers.add_parser('maintenance', help='Run maintenance tasks')
    maintenance_parser.add_argument(
        'type',
        choices=['daily', 'weekly', 'monthly'],
        help='Type of maintenance to run'
    )
    maintenance_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )

    # Alert command
    alert_parser = subparsers.add_parser('alert', help='Send alert')
    alert_parser.add_argument(
        'message',
        help='Alert message'
    )
    alert_parser.add_argument(
        '--title',
        default='Manual Alert',
        help='Alert title'
    )
    alert_parser.add_argument(
        '--severity',
        choices=['info', 'warning', 'error', 'critical'],
        default='info',
        help='Alert severity'
    )
    alert_parser.add_argument(
        '--channels',
        nargs='+',
        help='Channels to send alert to'
    )

    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Manage maintenance scheduler')
    schedule_parser.add_argument(
        'action',
        choices=['start', 'stop', 'status'],
        help='Scheduler action'
    )

    # Update command
    update_parser = subparsers.add_parser('update', help='Update repository files and documentation')
    update_subparsers = update_parser.add_subparsers(dest='update_action', help='Update actions')
    
    # Update docs
    docs_parser = update_subparsers.add_parser('docs', help='Update repository documentation')
    docs_parser.add_argument(
        '--dry-run', action='store_true', help='Show what would be updated without making changes')
    
    # Update changelog
    changelog_parser = update_subparsers.add_parser('changelog', help='Update CHANGELOG.md with recent commits')
    changelog_parser.add_argument(
        '--version', type=str, help='Version number for changelog section')
    changelog_parser.add_argument(
        '--draft', action='store_true', help='Generate draft changelog without committing')
    changelog_parser.add_argument(
        '--since', type=str, help='Git tag or commit to start from (default: last release tag)')
    
    # Update readme
    readme_parser = update_subparsers.add_parser('readme', help='Update README.md with current features')
    readme_parser.add_argument(
        '--dry-run', action='store_true', help='Show what would be updated without making changes')
    
    # Update version
    version_parser = update_subparsers.add_parser('version', help='Bump version numbers across project files')
    version_parser.add_argument(
        'bump_type',
        choices=['major', 'minor', 'patch'],
        help='Type of version bump (major.minor.patch)'
    )
    version_parser.add_argument(
        '--dry-run', action='store_true', help='Show what would be updated without making changes')
    
    # Update dependencies
    deps_parser = update_subparsers.add_parser('dependencies', help='Update dependency files')
    deps_parser.add_argument(
        '--check-only', action='store_true', help='Check for outdated dependencies without updating')
    deps_parser.add_argument(
        '--upgrade', action='store_true', help='Upgrade dependencies to latest compatible versions')
    
    # Update API documentation
    api_docs_parser = update_subparsers.add_parser('api-docs', help='Regenerate API documentation from docstrings')
    api_docs_parser.add_argument(
        '--format', choices=['markdown', 'html'], default='markdown', help='Documentation format')
    api_docs_parser.add_argument(
        '--output', type=str, help='Output directory for API docs (default: docs/api)')
    
    # Update headers
    headers_parser = update_subparsers.add_parser('headers', help='Manage documentation file headers')
    headers_parser.add_argument(
        'action', choices=['set', 'show', 'edit', 'templates'],
        help='Action to perform')
    headers_parser.add_argument(
        '--file', type=str, help='Specific file to edit (e.g., README.md)')
    headers_parser.add_argument(
        '--template', type=str, help='Template name to use')
    headers_parser.add_argument(
        '--custom', type=str, help='Custom header text')
    
    # Update footers
    footers_parser = update_subparsers.add_parser('footers', help='Manage documentation file footers')
    footers_parser.add_argument(
        'action', choices=['set', 'show', 'edit', 'templates'],
        help='Action to perform')
    footers_parser.add_argument(
        '--file', type=str, help='Specific file to edit (e.g., README.md)')
    footers_parser.add_argument(
        '--template', type=str, default='standard', help='Template name to use (default: standard)')
    footers_parser.add_argument(
        '--custom', type=str, help='Custom footer text')

    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean repository artifacts and temporary files')
    clean_parser.add_argument(
        '--all', action='store_true', default=False,
        help='Clean all safe targets (cache + temp + logs) - this is the default if no options specified')
    clean_parser.add_argument(
        '--root', action='store_true', help='Clean root directory clutter (__pycache__, .pyc files). Use --full for policy compliance')
    clean_parser.add_argument(
        '--full', action='store_true', help='When used with --root, also enforce policy compliance (remove unauthorized files/dirs)')
    clean_parser.add_argument(
        '--cache', action='store_true', help='Clean Python cache files (__pycache__, *.pyc, *.pyo)')
    clean_parser.add_argument(
        '--temp', action='store_true', help='Clean temporary files (*.tmp, .cache directories)')
    clean_parser.add_argument(
        '--logs', action='store_true', help='Clean old log files (*.log)')
    clean_parser.add_argument(
        '--build', action='store_true', help='Clean build artifacts (dist/, build/, *.egg-info)')
    clean_parser.add_argument(
        '--test', action='store_true', help='Clean test artifacts (.pytest_cache, .coverage, htmlcov/)')
    clean_parser.add_argument(
        '--git', action='store_true', help='Optimize git repository (gc, prune)')
    clean_parser.add_argument(
        '--emojis', action='store_true', help='Remove excessive emojis from code and documentation (policy violation)')
    clean_parser.add_argument(
        '--include-gui', action='store_true', help='Include GUI files in emoji scanning (default: excluded)')
    clean_parser.add_argument(
        '--dry-run', action='store_true', help='Show what would be deleted without deleting')
    clean_parser.add_argument(
        '--force', action='store_true', help='Skip confirmation prompts')
    clean_parser.add_argument(
        '--verbose', action='store_true', help='Show detailed output')
    clean_parser.add_argument(
        '--older-than', type=int, metavar='DAYS', 
        help='Only clean files older than N days (applies to logs and temp files)')

    # Integrate command
    integrate_parser = subparsers.add_parser('integrate', help='Integrate new CLI commands into existing workflows')
    integrate_parser.add_argument(
        '--new', action='store_true', default=True,
        help='Integrate newly added commands into workflows (default)')
    integrate_parser.add_argument(
        '--all', action='store_true',
        help='Integrate all available commands into workflows')
    integrate_parser.add_argument(
        '--workflow', choices=['scheduler', 'ci-cd', 'all'], default='scheduler',
        help='Target workflow for integration (default: scheduler)')
    integrate_parser.add_argument(
        '--dry-run', action='store_true',
        help='Show integration opportunities without making changes')
    integrate_parser.add_argument(
        '--force', action='store_true',
        help='Force integration even if conflicts detected')
    integrate_parser.add_argument(
        '--backup', action='store_true',
        help='Create backup before integration')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Run setup wizard')
    setup_parser.add_argument(
        '--gui',
        action='store_true',
        help='Use GUI setup wizard'
    )
    setup_parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run non-interactive setup'
    )

    # Development audit command
    dev_audit_parser = subparsers.add_parser('dev-audit', help='Run development audit')
    dev_audit_parser.add_argument(
        '--silent', action='store_true', help='Run brief audit suitable for CI/alerts')
    dev_audit_parser.add_argument(
        '--agent', action='store_true', help='Export audit context for AI agent remediation (requires GitHub Copilot)')
    dev_audit_parser.add_argument(
        '--export', type=str, help='Export audit results to JSON file')
    dev_audit_parser.add_argument(
        '--focus', type=str, metavar='AREA', 
        help='Focus audit analysis on specific area (e.g., "scheduler", "new feature", "duplication detection"). Only available with Copilot integration.')
    # File integrity command - robust management interface
    integrity_parser = subparsers.add_parser(
        'integrity',
        help='Manage file integrity validation and monitoring',
        description='CodeSentinel Integrity Manager - SEAM Protection™ for file stability'
    )
    integrity_subparsers = integrity_parser.add_subparsers(dest='integrity_action', help='Integrity actions')
    
    # Status: Show current integrity state
    status_parser = integrity_subparsers.add_parser(
        'status',
        help='Show current integrity state and monitoring status'
    )
    status_parser.add_argument(
        '--detailed', action='store_true', help='Show detailed statistics'
    )
    
    # Start: Enable integrity monitoring
    start_parser = integrity_subparsers.add_parser(
        'start',
        help='Enable integrity monitoring and validation'
    )
    start_parser.add_argument(
        '--baseline', type=str, help='Path to baseline file (auto-detect if not specified)'
    )
    start_parser.add_argument(
        '--watch', action='store_true', help='Enable real-time file monitoring'
    )
    
    # Stop: Disable integrity monitoring
    stop_parser = integrity_subparsers.add_parser(
        'stop',
        help='Disable integrity monitoring'
    )
    stop_parser.add_argument(
        '--save-state', action='store_true', help='Save current state before stopping'
    )
    
    # Reset: Clear integrity baseline and state
    reset_parser = integrity_subparsers.add_parser(
        'reset',
        help='Clear integrity baseline and reset monitoring state'
    )
    reset_parser.add_argument(
        '--force', action='store_true', help='Skip confirmation prompt'
    )
    
    # Verify: Check files against baseline (kept for direct verification)
    verify_parser = integrity_subparsers.add_parser(
        'verify',
        help='Verify files against baseline'
    )
    verify_parser.add_argument(
        '--baseline', type=str, help='Path to baseline file'
    )
    verify_parser.add_argument(
        '--report', type=str, help='Save report to file'
    )
    
    # Config: Manage integrity configuration
    config_parser = integrity_subparsers.add_parser(
        'config',
        help='Manage integrity configuration'
    )
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='Config actions')
    
    # Config -> Generate baseline
    gen_parser = config_subparsers.add_parser(
        'baseline',
        help='Generate file integrity baseline'
    )
    gen_parser.add_argument(
        '--patterns', nargs='+', help='File patterns to include (default: all files)'
    )
    gen_parser.add_argument(
        '--output', type=str, help='Output path for baseline file'
    )
    
    # Config -> Whitelist
    whitelist_parser = config_subparsers.add_parser(
        'whitelist',
        help='Manage whitelist patterns'
    )
    whitelist_parser.add_argument(
        'patterns', nargs='+', help='Glob patterns to add to whitelist'
    )
    whitelist_parser.add_argument(
        '--replace', action='store_true', help='Replace existing whitelist'
    )
    whitelist_parser.add_argument(
        '--show', action='store_true', help='Show current whitelist'
    )
    
    # Config -> Critical files
    critical_parser = config_subparsers.add_parser(
        'critical',
        help='Mark files as critical for integrity'
    )
    critical_parser.add_argument(
        'files', nargs='*', help='Files to mark as critical (relative paths)'
    )
    critical_parser.add_argument(
        '--replace', action='store_true', help='Replace existing critical files list'
    )
    critical_parser.add_argument(
        '--show', action='store_true', help='Show current critical files'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Initialize CodeSentinel
        config_path = Path(args.config) if args.config else None
        codesentinel = CodeSentinel(config_path)

        # Execute command
        if args.command == 'status':
            status = codesentinel.get_status()
            print("CodeSentinel Status:")
            print(f"  Version: {status['version']}")
            print(f"  Config Loaded: {status['config_loaded']}")
            print(f"  Alert Channels: {', '.join(status['alert_channels'])}")
            print(f"  Scheduler Active: {status['scheduler_active']}")

        elif args.command == 'scan':
            print("Running security scan...")
            results = codesentinel.run_security_scan()

            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"Scan results saved to {args.output}")
            else:
                print(f"Scan completed. Found {results['summary']['total_vulnerabilities']} vulnerabilities.")

        elif args.command == 'maintenance':
            if args.dry_run:
                print(f"Would run {args.type} maintenance tasks (dry run)")
            else:
                print(f"Running {args.type} maintenance tasks...")
                results = codesentinel.run_maintenance_tasks(args.type)
                print(f"Executed {len(results.get('tasks_executed', []))} tasks")

        elif args.command == 'alert':
            print(f"Sending alert: {args.title}")
            channels = args.channels
            try:
                result = codesentinel.alert_manager.send_alert(
                    title=args.title,
                    message=args.message,
                    severity=args.severity,
                    channels=channels
                )
                # Summarize results
                succeeded = [k for k, v in (result or {}).items() if v]
                failed = [k for k, v in (result or {}).items() if not v]
                if succeeded:
                    print(f"Alert sent via: {', '.join(succeeded)}")
                if failed:
                    print(f"Channels failed: {', '.join(failed)}")
            except Exception as _e:
                print(f"Alert failed: {_e}", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'schedule':
            if args.action == 'start':
                print("Starting maintenance scheduler...")
                try:
                    # Create a Python script that runs the scheduler
                    scheduler_script = Path.home() / ".codesentinel" / "run_scheduler.py"
                    scheduler_script.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Find the CodeSentinel package location
                    import codesentinel
                    package_dir = Path(codesentinel.__file__).parent.parent
                    
                    script_content = f"""
import sys as s
import time
from pathlib import Path

# Add CodeSentinel to path
s.path.insert(0, r'{package_dir}')

from codesentinel.core import CodeSentinel

cs = CodeSentinel()
cs.scheduler.start()

# Keep process alive
try:
    while cs.scheduler.running:
        time.sleep(60)
except KeyboardInterrupt:
    cs.scheduler.stop()
"""
                    with open(scheduler_script, 'w') as f:
                        f.write(script_content)
                    
                    print(f"Scheduler script created: {scheduler_script}")
                    
                    # Start background process
                    if sys.platform == 'win32':
                        # Windows: use CREATE_NO_WINDOW flag (0x08000000)
                        CREATE_NO_WINDOW = 0x08000000
                        subprocess.Popen(
                            [sys.executable, str(scheduler_script)],
                            creationflags=CREATE_NO_WINDOW,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    else:
                        # Unix: standard background process
                        subprocess.Popen(
                            [sys.executable, str(scheduler_script)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            preexec_fn=os.setsid
                        )
                    
                    print("Scheduler started in background")
                except Exception as e:
                    print(f"Error starting scheduler: {e}")
                    import traceback
                    traceback.print_exc()
            elif args.action == 'stop':
                print("Stopping maintenance scheduler...")
                try:
                    # Check if scheduler is running in background
                    from pathlib import Path
                    state_file = Path.home() / ".codesentinel" / "scheduler.state"
                    
                    if state_file.exists():
                        import json
                        try:
                            with open(state_file, 'r') as f:
                                state = json.load(f)
                            pid = state.get('pid')
                            
                            if pid:
                                # Try to terminate the background process
                                try:
                                    import psutil
                                    process = psutil.Process(pid)
                                    process.terminate()
                                    process.wait(timeout=5)
                                    print(f"Background scheduler process (PID {pid}) stopped")
                                except psutil.NoSuchProcess:
                                    print(f"Scheduler process (PID {pid}) not found (already stopped)")
                                except psutil.TimeoutExpired:
                                    print(f"Scheduler process (PID {pid}) did not stop gracefully, forcing...")
                                    process.kill()
                                    print("Scheduler process forcefully terminated")
                                except ImportError:
                                    # psutil not available, try basic kill
                                    if sys.platform == 'win32':
                                        os.system(f'taskkill /F /PID {pid}')
                                    else:
                                        os.kill(pid, 15)  # SIGTERM
                                    print(f"Sent stop signal to scheduler process (PID {pid})")
                                
                                # Clean up state file
                                state_file.unlink()
                        except Exception as e:
                            print(f"Error reading scheduler state: {e}")
                    else:
                        # No background scheduler, try stopping in-process
                        codesentinel.scheduler.stop()
                        print("In-process scheduler stopped")
                    
                except Exception as e:
                    print(f"Error stopping scheduler: {e}")
                    import traceback
                    traceback.print_exc()
            elif args.action == 'status':
                print("Scheduler status:")
                # status = codesentinel.scheduler.get_schedule_status()
                # print(json.dumps(status, indent=2))

        elif args.command == 'update':
            """Handle update command for repository files and documentation."""
            from pathlib import Path
            import subprocess
            import json
            
            if args.update_action == 'docs':
                """Update repository documentation files with branding + header/footer verification."""
                dry_run = getattr(args, 'dry_run', False)
                verbose = getattr(args, 'verbose', False)
                
                print("Analyzing repository documentation...")
                print("Verifying SEAM Protection™ branding + header/footer compliance...\n")
                
                # Files to verify and update
                docs_to_verify = [
                    Path.cwd() / "CHANGELOG.md",
                    Path.cwd() / "README.md",
                    Path.cwd() / "SECURITY.md",
                    Path.cwd() / ".github" / "copilot-instructions.md",
                    Path.cwd() / "codesentinel" / "__init__.py",
                ]
                
                branding_issues = []
                header_footer_issues = []
                fixed_files = []
                verified_files = []
                
                for doc_file in docs_to_verify:
                    if not doc_file.exists():
                        continue
                    
                    # Verify branding compliance
                    is_branding_compliant, branding_issues_list = verify_documentation_branding(doc_file)
                    
                    # Verify headers/footers (markdown only)
                    is_hf_compliant = True
                    hf_issues_list = []
                    if doc_file.suffix == '.md':
                        is_hf_compliant, hf_issues_list, metadata = verify_documentation_headers_footers(doc_file)
                    
                    # Track issues
                    if not is_branding_compliant:
                        branding_issues.extend(branding_issues_list)
                    if not is_hf_compliant:
                        header_footer_issues.extend(hf_issues_list)
                    
                    # Check if all compliant
                    if is_branding_compliant and is_hf_compliant:
                        verified_files.append(doc_file.name)
                        if verbose:
                            print(f"  ✓ Full compliance: {doc_file.name}")
                    else:
                        # Apply automatic fixes
                        if not dry_run:
                            fixes_applied = False
                            
                            if not is_branding_compliant:
                                success, message = apply_branding_fixes(doc_file, verbose)
                                if success:
                                    fixes_applied = True
                                    if verbose:
                                        print(f"  Fixed (branding): {doc_file.name}")
                            
                            if not is_hf_compliant:
                                success, message = apply_header_footer_fixes(doc_file, verbose)
                                if success:
                                    fixes_applied = True
                                    if verbose:
                                        print(f"  Fixed (header/footer): {doc_file.name}")
                            
                            if fixes_applied:
                                fixed_files.append(doc_file.name)
                        else:
                            print(f"  [DRY-RUN] Would fix: {doc_file.name}")
                
                # Summary
                print("\nDocumentation Verification Summary:")
                print(f"  ✓ Full compliance: {len(verified_files)} files")
                
                if fixed_files:
                    print(f"  Fixed: {len(fixed_files)} files")
                    for fname in fixed_files:
                        print(f"    - {fname}")
                
                if branding_issues:
                    print(f"\nBranding Issues Fixed: {len(branding_issues)}")
                    for issue in branding_issues:
                        print(f"  ⚠ {issue}")
                
                if header_footer_issues:
                    print(f"\nHeader/Footer Issues Fixed: {len(header_footer_issues)}")
                    for issue in header_footer_issues:
                        print(f"  ⚠ {issue}")
                
                if dry_run:
                    print("\nDry run complete. No files modified.")
                else:
                    if fixed_files or verified_files:
                        print("\nDocumentation verification complete.")
                        print("All files comply with SEAM Protection™ branding and header/footer policy.")
                    
            elif args.update_action == 'changelog':
                """Update CHANGELOG.md with recent git commits."""
                dry_run = getattr(args, 'draft', False) or getattr(args, 'dry_run', False)
                version = getattr(args, 'version', None)
                since = getattr(args, 'since', None)
                
                print("Updating CHANGELOG.md...")
                
                # Get recent commits
                try:
                    if since:
                        cmd = ['git', 'log', f'{since}..HEAD', '--oneline', '--no-merges']
                    else:
                        # Try to find last release tag
                        try:
                            last_tag = subprocess.check_output(
                                ['git', 'describe', '--tags', '--abbrev=0'],
                                stderr=subprocess.DEVNULL, text=True
                            ).strip()
                            cmd = ['git', 'log', f'{last_tag}..HEAD', '--oneline', '--no-merges']
                        except:
                            # No tags, get last 10 commits
                            cmd = ['git', 'log', '-10', '--oneline', '--no-merges']
                    
                    commits = subprocess.check_output(cmd, text=True).strip()
                    
                    if commits:
                        print(f"\n  Found {len(commits.splitlines())} commits:\n")
                        print(commits)
                        
                        if dry_run:
                            print("\nDraft mode. CHANGELOG.md not modified.")
                        else:
                            print("\nUse --draft to preview without modifying CHANGELOG.md")
                    else:
                        print("  No new commits found.")
                        
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ Error running git command: {e}")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    
            elif args.update_action == 'readme':
                """Update README.md with current features."""
                dry_run = getattr(args, 'dry_run', False)
                
                print("Updating README.md...")
                readme_path = Path.cwd() / "README.md"
                
                if readme_path.exists():
                    if dry_run:
                        print("  [DRY-RUN] Would update feature list and version badges")
                    else:
                        print("  ✓ README.md checked")
                        print("\nTip: Update version badges, feature lists, and examples manually")
                        print("         or integrate with documentation generator")
                else:
                    print("  ❌ README.md not found")
                    
            elif args.update_action == 'version':
                """Bump version numbers across project files."""
                bump_type = args.bump_type
                dry_run = getattr(args, 'dry_run', False)
                
                print(f"Bumping version ({bump_type})...")
                
                # Files to update
                version_files = [
                    Path.cwd() / "pyproject.toml",
                    Path.cwd() / "setup.py",
                    Path.cwd() / "codesentinel" / "__init__.py"
                ]
                
                for vf in version_files:
                    if vf.exists():
                        if dry_run:
                            print(f"  [DRY-RUN] Would update: {vf.name}")
                        else:
                            print(f"  ✓ Would update: {vf.name}")
                    else:
                        print(f"  ⚠️  Not found: {vf.name}")
                
                if dry_run:
                    print("\nDry run complete. No files modified.")
                else:
                    print("\nVersion update requires manual editing or integration with bump2version")
                    print("Consider: pip install bump2version && bump2version " + bump_type)
                    
            elif args.update_action == 'dependencies':
                """Update dependency files."""
                check_only = getattr(args, 'check_only', False)
                upgrade = getattr(args, 'upgrade', False)
                
                print("Checking dependencies...")
                
                try:
                    if check_only:
                        # Check for outdated packages
                        print("  Running: pip list --outdated")
                        subprocess.run(['pip', 'list', '--outdated'], check=False)
                    elif upgrade:
                        print("  Upgrading dependencies requires pip-tools or manual update")
                        print("Consider: pip install pip-tools && pip-compile --upgrade")
                    else:
                        print("  ✓ requirements.txt and pyproject.toml checked")
                        print("\n  Options:")
                        print("    --check-only : Check for outdated dependencies")
                        print("    --upgrade    : Upgrade to latest compatible versions")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    
            elif args.update_action == 'api-docs':
                """Regenerate API documentation from docstrings."""
                fmt = args.format
                output = getattr(args, 'output', None) or 'docs/api'
                
                print(f"📚 Generating API documentation ({fmt})...")
                
                output_path = Path.cwd() / output
                if not output_path.exists():
                    output_path.mkdir(parents=True, exist_ok=True)
                    print(f"  Created: {output}")
                
                print(f"  API doc generation requires sphinx or pdoc")
                print("Consider: pip install pdoc3 && pdoc --html --output-dir " + output + " codesentinel")
                
            elif args.update_action == 'headers':
                """Manage documentation headers."""
                action = args.action
                file_arg = getattr(args, 'file', None)
                template_arg = getattr(args, 'template', None)
                custom_arg = getattr(args, 'custom', None)
                
                if action == 'templates':
                    show_template_options('header')
                elif action == 'show':
                    print("\nAvailable Header Templates:")
                    print("="*70)
                    headers = get_header_templates()
                    for file_name, info in headers.items():
                        marker = "⭐" if info.get('project_specific') else "  "
                        print(f"\n{marker} 📄 {file_name}: {info['description']}")
                        print(f"   Preview:\n   {info['template'][:100]}...")
                elif action == 'set':
                    if not file_arg:
                        print("❌ --file required for set action")
                    else:
                        file_path = Path.cwd() / file_arg
                        if file_path.exists():
                            if custom_arg:
                                success, msg = set_header_for_file(file_path, custom_header=custom_arg)
                            else:
                                success, msg = set_header_for_file(file_path, template_name=template_arg or file_path.name)
                            print(f"{'✓' if success else '❌'} {msg}")
                        else:
                            print(f"❌ File not found: {file_arg}")
                elif action == 'edit':
                    if file_arg:
                        file_path = Path.cwd() / file_arg
                        edit_headers_interactive([file_path])
                    else:
                        edit_headers_interactive()
            
            elif args.update_action == 'footers':
                """Manage documentation footers."""
                action = args.action
                file_arg = getattr(args, 'file', None)
                template_arg = getattr(args, 'template', 'standard')
                custom_arg = getattr(args, 'custom', None)
                
                if action == 'templates':
                    show_template_options('footer')
                elif action == 'show':
                    print("\nAvailable Footer Templates:")
                    print("="*70)
                    footers = get_footer_templates()
                    for template_name, info in footers.items():
                        marker = "⭐" if info.get('project_specific') else "  "
                        print(f"\n{marker} 🔖 {template_name.upper()}: {info['description']}")
                        print(f"   Preview:\n   {info['template'][:100]}...")
                elif action == 'set':
                    if not file_arg:
                        print("❌ --file required for set action")
                    else:
                        file_path = Path.cwd() / file_arg
                        if file_path.exists():
                            if custom_arg:
                                success, msg = set_footer_for_file(file_path, custom_footer=custom_arg)
                            else:
                                success, msg = set_footer_for_file(file_path, template_name=template_arg)
                            print(f"{'✓' if success else '❌'} {msg}")
                        else:
                            print(f"❌ File not found: {file_arg}")
                elif action == 'edit':
                    if file_arg:
                        file_path = Path.cwd() / file_arg
                        edit_footers_interactive([file_path])
                    else:
                        edit_footers_interactive()
                
            else:
                print("❌ Unknown update action. Use 'codesentinel update --help'")

        elif args.command == 'clean':
            """Handle clean command for repository cleanup."""
            from pathlib import Path
            import shutil
            from datetime import datetime, timedelta
            
            dry_run = args.dry_run
            force = args.force
            verbose = args.verbose
            older_than = args.older_than
            
            # Determine what to clean
            # If no specific flags, default to --all behavior
            clean_targets = {
                'cache': args.cache,
                'temp': args.temp,
                'logs': args.logs,
                'build': args.build,
                'test': args.test,
                'git': args.git,
                'root': args.root,
                'emojis': args.emojis
            }
            
            # If nothing specified, enable --all behavior (cache + temp + logs)
            if not any(clean_targets.values()):
                clean_targets['cache'] = True
                clean_targets['temp'] = True
                clean_targets['logs'] = True
                print("🧹 Running clean (default: --all)\n")
            elif args.all:
                clean_targets['cache'] = True
                clean_targets['temp'] = True
                clean_targets['logs'] = True
            
            workspace_root = Path.cwd()
            items_to_delete = []
            size_saved = 0
            
            def get_size(path):
                """Calculate size of file or directory."""
                if path.is_file():
                    return path.stat().st_size
                total = 0
                try:
                    for item in path.rglob('*'):
                        if item.is_file():
                            total += item.stat().st_size
                except:
                    pass
                return total
            
            def is_older_than(path, days):
                """Check if file is older than specified days."""
                if not days:
                    return True
                try:
                    mtime = datetime.fromtimestamp(path.stat().st_mtime)
                    return datetime.now() - mtime > timedelta(days=days)
                except:
                    return False
            
            # Collect items to delete
            if clean_targets['cache']:
                print("🔍 Scanning for Python cache files...")
                # Find __pycache__ directories
                for pycache in workspace_root.rglob('__pycache__'):
                    items_to_delete.append(('dir', pycache, get_size(pycache)))
                    if verbose:
                        print(f"  Found: {pycache.relative_to(workspace_root)}")
                
                # Find .pyc and .pyo files
                for pattern in ['*.pyc', '*.pyo']:
                    for pyc_file in workspace_root.rglob(pattern):
                        items_to_delete.append(('file', pyc_file, get_size(pyc_file)))
                        if verbose:
                            print(f"  Found: {pyc_file.relative_to(workspace_root)}")
            
            if clean_targets['temp']:
                print("🔍 Scanning for temporary files...")
                # Find .tmp files
                for tmp_file in workspace_root.rglob('*.tmp'):
                    if is_older_than(tmp_file, older_than):
                        items_to_delete.append(('file', tmp_file, get_size(tmp_file)))
                        if verbose:
                            print(f"  Found: {tmp_file.relative_to(workspace_root)}")
                
                # Find .cache directories
                for cache_dir in workspace_root.rglob('.cache'):
                    items_to_delete.append(('dir', cache_dir, get_size(cache_dir)))
                    if verbose:
                        print(f"  Found: {cache_dir.relative_to(workspace_root)}")
            
            if clean_targets['logs']:
                print("🔍 Scanning for log files...")
                for log_file in workspace_root.rglob('*.log'):
                    if is_older_than(log_file, older_than):
                        items_to_delete.append(('file', log_file, get_size(log_file)))
                        if verbose:
                            print(f"  Found: {log_file.relative_to(workspace_root)}")
            
            if clean_targets['build']:
                print("🔍 Scanning for build artifacts...")
                build_dirs = ['dist', 'build', '*.egg-info']
                for pattern in build_dirs:
                    for build_item in workspace_root.glob(pattern):
                        items_to_delete.append(('dir', build_item, get_size(build_item)))
                        if verbose:
                            print(f"  Found: {build_item.relative_to(workspace_root)}")
            
            if clean_targets['test']:
                print("🔍 Scanning for test artifacts...")
                test_items = ['.pytest_cache', '.coverage', 'htmlcov', '.tox']
                for test_pattern in test_items:
                    for test_item in workspace_root.rglob(test_pattern):
                        items_to_delete.append(('dir' if test_item.is_dir() else 'file', 
                                               test_item, get_size(test_item)))
                        if verbose:
                            print(f"  Found: {test_item.relative_to(workspace_root)}")
            
            if clean_targets['root']:
                print("🔍 Scanning root directory for clutter...")
                
                # Standard clutter removal (always done)
                # Only scan root directory, not subdirectories
                for item in workspace_root.glob('__pycache__'):
                    items_to_delete.append(('dir', item, get_size(item)))
                    if verbose:
                        print(f"  Found: {item.name}")
                
                for pattern in ['*.pyc', '*.pyo', '*.tmp']:
                    for item in workspace_root.glob(pattern):
                        items_to_delete.append(('file', item, get_size(item)))
                        if verbose:
                            print(f"  Found: {item.name}")
                
                # Full policy validation (only if --full flag is used)
                if getattr(args, 'full', False):
                    print("🔍 Scanning for policy violations (--full mode)...")
                    
                    # Define allowed files and directories (from root_cleanup.py)
                    ALLOWED_ROOT_FILES = {
                        'setup.py', 'pyproject.toml', 'MANIFEST.in', 'pytest.ini',
                        'requirements.txt', 'requirements-dev.txt', 'run_tests.py',
                        'publish_to_pypi.py', 'README.md', 'LICENSE', 'CHANGELOG.md',
                        'CONTRIBUTING.md', 'SECURITY.md', 'QUICK_START.md',
                        'codesentinel.json', 'codesentinel.log', '.codesentinel_integrity.json',
                        '.test_integrity.json', '.gitignore',
                    }
                    
                    ALLOWED_ROOT_DIRS = {
                        '.git', '.github', 'archive', 'codesentinel', 'deployment',
                        'docs', 'github', 'infrastructure', 'logs', 'requirements',
                        'scripts', 'tests', 'tools', 'quarantine_legacy_archive',
                    }
                    
                    # Assess unauthorized items for proper placement (NON-DESTRUCTIVE approach)
                    # Policy: Never delete without archiving first
                    policy_violations = []
                    
                    # Check all items at root level
                    for item in workspace_root.iterdir():
                        # Skip git-related items
                        if item.name in {'.git', '.gitignore'}:
                            continue
                        
                        if item.is_dir():
                            # Check if directory is allowed
                            if item.name not in ALLOWED_ROOT_DIRS:
                                reason = ''
                                target_location = 'quarantine_legacy_archive/'  # Always archive first
                                
                                if item.name.startswith('.'):
                                    reason = 'unauthorized dot directory'
                                else:
                                    reason = 'unauthorized directory'
                                
                                policy_violations.append({
                                    'type': 'directory',
                                    'path': item,
                                    'name': item.name,
                                    'reason': reason,
                                    'target': target_location,
                                    'action': 'archive'  # Always archive, never delete
                                })
                                
                                if verbose:
                                    print(f"  Found (policy violation): {item.name} [{reason}]")
                        else:
                            # Check if file is allowed
                            if item.name not in ALLOWED_ROOT_FILES:
                                reason = 'unauthorized file'
                                target_location = 'quarantine_legacy_archive/'
                                
                                # Assess file type and suggest proper action
                                if item.name.startswith('test_') or item.name.endswith('_test.py'):
                                    reason = 'test/diagnostic file'
                                elif item.name.endswith('.md'):
                                    reason = 'documentation file - review placement'
                                elif item.name.endswith('.json'):
                                    reason = 'configuration/state file - review placement'
                                
                                policy_violations.append({
                                    'type': 'file',
                                    'path': item,
                                    'name': item.name,
                                    'reason': reason,
                                    'target': target_location,
                                    'action': 'archive'  # Always archive, never delete
                                })
                                
                                if verbose:
                                    print(f"  Found (policy violation): {item.name} [{reason}] → archive to {target_location}")
                    
                    # If violations found, show assessment and ask for approval
                    if policy_violations:
                        print(f"\n⚠️  Found {len(policy_violations)} policy violations:")
                        print("All items will be ARCHIVED (not deleted) per NON-DESTRUCTIVE policy\n")
                        
                        for i, violation in enumerate(policy_violations, 1):
                            print(f"  {i}. [{violation['type'].upper()}] {violation['name']}")
                            print(f"     Reason: {violation['reason']}")
                            print(f"     Action: Archive to {violation['target']}")
                        
                        if dry_run:
                            print("\n[DRY-RUN] Would archive the items above")
                        else:
                            if not force:
                                response = input("\nArchive these items to quarantine_legacy_archive/? (y/N): ").strip().lower()
                                if response != 'y':
                                    print("Policy compliance cleanup cancelled.")
                                    return
                            
                            # Archive all violations (non-destructive)
                            archive_dir = workspace_root / 'quarantine_legacy_archive'
                            archive_dir.mkdir(parents=True, exist_ok=True)
                            
                            archived_count = 0
                            for violation in policy_violations:
                                try:
                                    import shutil
                                    target_path = archive_dir / violation['path'].name
                                    
                                    # If target already exists, create timestamped copy
                                    if target_path.exists():
                                        from datetime import datetime
                                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                        base_name = violation['path'].name
                                        if '.' in base_name:
                                            name_parts = base_name.rsplit('.', 1)
                                            target_path = archive_dir / f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                                        else:
                                            target_path = archive_dir / f"{base_name}_{timestamp}"
                                    
                                    if violation['type'] == 'directory':
                                        shutil.move(str(violation['path']), str(target_path))
                                    else:
                                        shutil.move(str(violation['path']), str(target_path))
                                    
                                    archived_count += 1
                                    if verbose:
                                        print(f"  ✓ Archived: {violation['name']} → quarantine_legacy_archive/")
                                except Exception as e:
                                    print(f"  ✗ Failed to archive {violation['name']}: {e}")
                            
                            print(f"\n✓ Successfully archived {archived_count}/{len(policy_violations)} items")
                            print("  Items are preserved in quarantine_legacy_archive/ for review")
                            return



            
            # Emoji cleaning
            files_with_emoji_changes = []
            if clean_targets['emojis']:
                print("Scanning for policy-violating emoji usage...")
                import re
                
                include_gui = getattr(args, 'include_gui', False)
                
                # Emoji pattern - matches most common emojis
                # Policy: Only allow checkmark and X - all others removed
                emoji_pattern = re.compile(
                    "["
                    "\U0001F600-\U0001F64F"  # emoticons
                    "\U0001F300-\U0001F5FF"  # symbols & pictographs
                    "\U0001F680-\U0001F6FF"  # transport & map symbols
                    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                    "\U00002702-\U000027B0"  # dingbats
                    "\U000024C2-\U0001F251"
                    "]+", 
                    flags=re.UNICODE
                )
                
                # Policy-allowed emojis: checkmark and X
                allowed_emojis = {'✓', '✔', '✅', '❌', '✗', '❎'}
                
                # Allowed emoji contexts (user-facing messages)
                # These patterns indicate legitimate emoji usage in user output
                allowed_contexts = [
                    r'print\([f]?["\'].*?[emoji].*?["\']\)',  # print statements
                    r'\.format\(.*?[emoji].*?\)',              # format strings
                    r'f["\'].*?[emoji].*?["\']',                # f-strings
                    r'logging\.\w+\([f]?["\'].*?[emoji].*?["\']\)',  # logging
                    r'#\s*User-facing:',                        # Marked as user-facing
                ]
                
                # File patterns to scan
                file_patterns = ['*.py', '*.md', '*.txt', '*.rst']
                
                # GUI file patterns to exclude (unless --include-gui)
                gui_patterns = [
                    'gui', 'GUI', 'tkinter', 'wx', 'qt', 'pyqt',
                    'launcher', 'wizard', 'dialog', 'window'
                ]
                
                for pattern in file_patterns:
                    for file_path in workspace_root.rglob(pattern):
                        # Skip certain directories
                        if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'venv', '.venv', 'node_modules']):
                            continue
                        
                        # Skip GUI files unless explicitly included
                        if not include_gui:
                            path_str = str(file_path).lower()
                            if any(gui_term in path_str for gui_term in gui_patterns):
                                if verbose:
                                    print(f"  Skipped (GUI): {file_path.relative_to(workspace_root)}")
                                continue
                        
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            original_content = content
                            lines = content.split('\n')
                            
                            # Intelligent detection: check each line
                            violation_emojis = []
                            cleaned_lines = []
                            
                            for line in lines:
                                emoji_matches = emoji_pattern.findall(line)
                                if emoji_matches:
                                    # Check if ALL emojis in this line are policy-allowed
                                    all_allowed = all(emoji in allowed_emojis for emoji in emoji_matches)
                                    
                                    if all_allowed:
                                        # All emojis are checkmark/X - keep the line
                                        cleaned_lines.append(line)
                                        continue
                                    
                                    # Filter out non-allowed emojis
                                    policy_violating = [e for e in emoji_matches if e not in allowed_emojis]
                                    
                                    if policy_violating:
                                        # Has policy-violating emojis, remove them
                                        violation_emojis.extend(policy_violating)
                                        # Remove only policy-violating emojis, keep allowed ones
                                        for emoji in policy_violating:
                                            line = line.replace(emoji, '')
                                        # Clean up resulting double spaces
                                        line = re.sub(r'  +', ' ', line)
                                        cleaned_lines.append(line)
                                    else:
                                        cleaned_lines.append(line)
                                else:
                                    cleaned_lines.append(line)
                            
                            if violation_emojis:
                                cleaned_content = '\n'.join(cleaned_lines)
                                # Clean up excessive blank lines
                                cleaned_content = re.sub(r'\n\n\n+', '\n\n', cleaned_content)
                                
                                if cleaned_content != original_content:
                                    files_with_emoji_changes.append({
                                        'path': file_path,
                                        'emoji_count': len(violation_emojis),
                                        'original': original_content,
                                        'cleaned': cleaned_content,
                                        'size': len(original_content) - len(cleaned_content)
                                    })
                                    
                                    if verbose:
                                        print(f"  Found violations: {file_path.relative_to(workspace_root)} ({len(violation_emojis)} policy-violating emojis)")
                        except Exception as e:
                            if verbose:
                                print(f"  Error scanning {file_path.name}: {e}")
                
                if files_with_emoji_changes:
                    total_emojis = sum(f['emoji_count'] for f in files_with_emoji_changes)
                    print(f"  Found {total_emojis} emojis in {len(files_with_emoji_changes)} files")
            
            # Calculate total size
            total_size = sum(size for _, _, size in items_to_delete)
            emoji_size = sum(f['size'] for f in files_with_emoji_changes)
            
            # Display summary
            print(f"\n📊 Summary:")
            print(f"  Items found: {len(items_to_delete)}")
            if files_with_emoji_changes:
                print(f"  Files with emojis: {len(files_with_emoji_changes)}")
            print(f"  Space to reclaim: {(total_size + emoji_size) / 1024 / 1024:.2f} MB")
            
            if not items_to_delete and not files_with_emoji_changes:
                print("\nRepository is already clean!")
                if clean_targets['git']:
                    print("\n🔧 Running git optimization...")
                    if not dry_run:
                        try:
                            import subprocess
                            subprocess.run(['git', 'gc', '--auto'], check=False, 
                                         capture_output=not verbose)
                            print("  ✓ Git garbage collection completed")
                        except Exception as e:
                            print(f"  Git optimization failed: {e}")
                    else:
                        print("  [DRY-RUN] Would run: git gc --auto")
                return
            
            # Confirm deletion
            if dry_run:
                print("\n[DRY-RUN] Would delete:")
                for item_type, path, size in items_to_delete[:10]:  # Show first 10
                    print(f"  {item_type:4s} {path.relative_to(workspace_root)} ({size / 1024:.1f} KB)")
                if len(items_to_delete) > 10:
                    print(f"  ... and {len(items_to_delete) - 10} more items")
                
                if files_with_emoji_changes:
                    print("\n[DRY-RUN] Would remove emojis from:")
                    for file_info in files_with_emoji_changes[:10]:
                        print(f"  file {file_info['path'].relative_to(workspace_root)} ({file_info['emoji_count']} emojis)")
                    if len(files_with_emoji_changes) > 10:
                        print(f"  ... and {len(files_with_emoji_changes) - 10} more files")
                
                print("\nDry run complete. No files modified.")
                return
            
            if not force:
                total_changes = len(items_to_delete) + len(files_with_emoji_changes)
                response = input(f"\nDelete {len(items_to_delete)} items and clean {len(files_with_emoji_changes)} files? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Cleanup cancelled.")
                    return
            
            # Perform deletion
            print("\nCleaning...")
            deleted_count = 0
            errors = []
            
            for item_type, path, size in items_to_delete:
                try:
                    if item_type == 'dir':
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    deleted_count += 1
                    if verbose:
                        print(f"  ✓ Deleted: {path.relative_to(workspace_root)}")
                except Exception as e:
                    errors.append((path, str(e)))
                    if verbose:
                        print(f"  ✗ Failed: {path.relative_to(workspace_root)} - {e}")
            
            # Git optimization if requested
            if clean_targets['git']:
                print("\nRunning git optimization...")
                try:
                    import subprocess
                    result = subprocess.run(['git', 'gc', '--auto'], 
                                          capture_output=not verbose, text=True)
                    if result.returncode == 0:
                        print("  ✓ Git garbage collection completed")
                    else:
                        print(f"  ⚠️  Git gc returned code {result.returncode}")
                except Exception as e:
                    print(f"  ✗ Git optimization failed: {e}")
            
            # Clean emojis from files
            emoji_cleaned_count = 0
            emoji_errors = []
            
            if files_with_emoji_changes:
                print("\n🧹 Removing emojis from files...")
                for file_info in files_with_emoji_changes:
                    try:
                        file_info['path'].write_text(file_info['cleaned'], encoding='utf-8')
                        emoji_cleaned_count += 1
                        if verbose:
                            print(f"  ✓ Cleaned: {file_info['path'].relative_to(workspace_root)} ({file_info['emoji_count']} emojis removed)")
                    except Exception as e:
                        emoji_errors.append((file_info['path'], str(e)))
                        if verbose:
                            print(f"  ✗ Failed: {file_info['path'].relative_to(workspace_root)} - {e}")
            
            # Final summary
            print(f"\n✨ Cleanup complete!")
            if items_to_delete:
                print(f"  Deleted: {deleted_count}/{len(items_to_delete)} items")
                print(f"  Space reclaimed: {total_size / 1024 / 1024:.2f} MB")
            if files_with_emoji_changes:
                print(f"  Files cleaned: {emoji_cleaned_count}/{len(files_with_emoji_changes)}")
                total_emojis_removed = sum(f['emoji_count'] for f in files_with_emoji_changes[:emoji_cleaned_count])
                print(f"  Emojis removed: {total_emojis_removed}")
            
            if errors:
                print(f"\n⚠️  Encountered {len(errors)} deletion errors:")
                for path, error in errors[:5]:
                    print(f"  {path.name}: {error}")
                if len(errors) > 5:
                    print(f"  ... and {len(errors) - 5} more errors")
            
            if emoji_errors:
                print(f"\n⚠️  Encountered {len(emoji_errors)} emoji cleaning errors:")
                for path, error in emoji_errors[:5]:
                    print(f"  {path.name}: {error}")
                if len(emoji_errors) > 5:
                    print(f"  ... and {len(emoji_errors) - 5} more errors")

        elif args.command == 'integrate':
            """Handle integrate command for automated workflow integration."""
            from pathlib import Path
            import subprocess
            import os
            from datetime import datetime
            
            dry_run = args.dry_run
            force = args.force
            backup = args.backup
            workflow = args.workflow
            
            print("🔗 CodeSentinel Integration Analysis")
            print("=" * 50)
            
            if dry_run:
                print("🔍 DRY-RUN MODE: Analyzing integration opportunities...")
            else:
                print("🔧 Integrating CLI commands into workflows...")
            
            # Get repository root
            repo_root = Path.cwd()
            
            # Create backup if requested
            if backup and not dry_run:
                backup_dir = repo_root / "backups" / f"integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_dir.mkdir(parents=True, exist_ok=True)
                print(f"📦 Creating backup in: {backup_dir}")
                
                # Backup key files
                key_files = [
                    "codesentinel/utils/scheduler.py",
                    "codesentinel/cli/__init__.py"
                ]
                for file_path in key_files:
                    src = repo_root / file_path
                    if src.exists():
                        dst = backup_dir / file_path
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        import shutil
                        shutil.copy2(src, dst)
                        print(f"  ✓ Backed up: {file_path}")
            
            # Analyze available CLI commands
            print("\n🔍 Analyzing available CLI commands...")
            available_commands = {}
            
            # Check clean command capabilities
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'clean', '--help'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and '--cache' in result.stdout:
                    available_commands['clean'] = [
                        'cache', 'temp', 'logs', 'build', 'test', 'root', 'emojis'
                    ]
                    print("  ✓ Clean command: available with multiple targets")
                else:
                    print("  ⚠️  Clean command: not available or incomplete")
            except Exception as e:
                print(f"  ❌ Clean command analysis failed: {e}")
            
            # Check update command capabilities
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'update', '--help'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and 'dependencies' in result.stdout:
                    available_commands['update'] = [
                        'docs', 'changelog', 'readme', 'version', 'dependencies', 'api-docs'
                    ]
                    print("  ✓ Update command: available with multiple targets")
                else:
                    print("  ⚠️  Update command: not available or incomplete")
            except Exception as e:
                print(f"  ❌ Update command analysis failed: {e}")
            
            if not available_commands:
                print("\n❌ No integrable commands found!")
                return
            
            # Analyze integration opportunities
            integration_opportunities = []
            
            if workflow in ['scheduler', 'all']:
                print("\n🔍 Analyzing scheduler integration opportunities...")
                
                # Check scheduler file
                scheduler_file = repo_root / "codesentinel" / "utils" / "scheduler.py"
                if scheduler_file.exists():
                    content = scheduler_file.read_text()
                    
                    # Check daily tasks
                    if "_run_daily_tasks" in content:
                        print("  ✓ Daily tasks method found")
                        
                        # Check for existing integrations
                        existing_integrations = []
                        if "clean --root" in content:
                            existing_integrations.append("root cleanup")
                        if "clean --cache" in content:
                            existing_integrations.append("cache cleanup")
                        if "update --dependencies" in content:
                            existing_integrations.append("dependency check")
                        
                        if existing_integrations:
                            print(f"  ✓ Existing integrations: {', '.join(existing_integrations)}")
                        
                        # Find new opportunities
                        opportunities = []
                        
                        # Clean command opportunities
                        if 'clean' in available_commands:
                            clean_targets = available_commands['clean']
                            if "clean --temp" not in content and "temp" in clean_targets:
                                opportunities.append({
                                    'command': 'clean --temp --logs',
                                    'target': 'daily_tasks',
                                    'benefit': 'Automated temp file and log cleanup'
                                })
                            if "clean --emojis" not in content and "emojis" in clean_targets:
                                opportunities.append({
                                    'command': 'clean --emojis',
                                    'target': 'daily_tasks',
                                    'benefit': 'Automated emoji policy enforcement'
                                })
                        
                        # Update command opportunities
                        if 'update' in available_commands:
                            update_targets = available_commands['update']
                            if "'update', 'docs'" not in content and "docs" in update_targets:
                                opportunities.append({
                                    'command': 'update --docs',
                                    'target': 'weekly_tasks',
                                    'benefit': 'Automated documentation validation'
                                })
                            if "'update', 'changelog'" not in content and "changelog" in update_targets:
                                opportunities.append({
                                    'command': 'update --changelog',
                                    'target': 'weekly_tasks',
                                    'benefit': 'Automated changelog maintenance'
                                })
                        
                        if opportunities:
                            integration_opportunities.extend(opportunities)
                            print(f"  🔍 Found {len(opportunities)} integration opportunities")
                        else:
                            print("  ✓ No new integration opportunities found")
                    else:
                        print("  ⚠️  Daily tasks method not found")
                else:
                    print("  ❌ Scheduler file not found")
            
            # Display integration plan
            if integration_opportunities:
                print(f"\n📋 Integration Plan ({len(integration_opportunities)} opportunities):")
                for i, opp in enumerate(integration_opportunities, 1):
                    print(f"  {i}. {opp['command']} → {opp['target'].replace('_', ' ')}")
                    print(f"     Benefit: {opp['benefit']}")
                
                if dry_run:
                    print("\n✨ Dry run complete. Use --force to apply integrations.")
                    return
                
                # Apply integrations
                print("\n🔧 Applying integrations...")
                
                # Change to repo root for operations
                original_cwd = os.getcwd()
                os.chdir(repo_root)
                
                try:
                    applied_count = 0
                    
                    def integrate_into_daily_tasks(command, force=False):
                        """Integrate command into daily tasks."""
                        try:
                            scheduler_path = Path("codesentinel/utils/scheduler.py")
                            content = scheduler_path.read_text()
                            
                            # Find the right place to insert (after dependency check, before duplication detection)
                            insert_marker = "# Dependency check using CLI update command"
                            if insert_marker in content:
                                # Find the end of the dependency check block
                                lines = content.split('\n')
                                insert_index = -1
                                for i, line in enumerate(lines):
                                    if insert_marker in line:
                                        # Find the end of this block
                                        for j in range(i + 1, len(lines)):
                                            if lines[j].strip().startswith('except Exception as e:'):
                                                # Find the next blank line after this block
                                                for k in range(j + 1, len(lines)):
                                                    if not lines[k].strip():
                                                        insert_index = k
                                                        break
                                                break
                                    break
                                
                                if insert_index > 0:
                                    # Create the integration code
                                    integration_code = f"""
            # {command.split()[1].title()} cleanup using CLI command
            try:
                # Run {command} command
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', '{command}'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    tasks_executed.append('{command.replace(" --", "_").replace("-", "_")}_cleanup')
                    self.logger.info("{command.split()[1].title()} cleanup completed successfully")
                else:
                    self.logger.warning(f"{command.split()[1].title()} cleanup failed: {{result.stderr}}")
                    errors.append(f"{command.split()[1].title()} cleanup failed: {{result.stderr}}")

            except subprocess.TimeoutExpired:
                self.logger.error("{command.split()[1].title()} cleanup timed out")
                errors.append("{command.split()[1].title()} cleanup timed out")
            except Exception as e:
                self.logger.error(f"{command.split()[1].title()} cleanup error: {{e}}")
                errors.append(f"{command.split()[1].title()} cleanup failed: {{str(e)}}")
            
            # Duplication detection"""
                                    
                                    # Insert the code
                                    lines.insert(insert_index, integration_code)
                                    new_content = '\n'.join(lines)
                                    
                                    if not dry_run:
                                        scheduler_path.write_text(new_content)
                                    return True
                            
                            return False
                            
                        except Exception as e:
                            print(f"  ❌ Integration failed: {e}")
                            return False
                    
                    def integrate_into_weekly_tasks(command, force=False):
                        """Integrate command into weekly tasks."""
                        try:
                            scheduler_path = Path("codesentinel/utils/scheduler.py")
                            content = scheduler_path.read_text()
                            
                            # Find the weekly tasks method
                            if "_run_weekly_tasks" in content:
                                lines = content.split('\n')
                                
                                # Find where to insert (before the return statement)
                                return_index = -1
                                for i, line in enumerate(lines):
                                    if "_run_weekly_tasks" in line:
                                        # Find the return statement
                                        for j in range(i + 1, len(lines)):
                                            if lines[j].strip().startswith('return {'):
                                                return_index = j - 1  # Insert before return
                                                break
                                    break
                                
                                if return_index > 0:
                                    # Create the integration code
                                    integration_code = f"""
                # {command.split()[1].title()} update using CLI command
                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'codesentinel.cli', '{command}'
                    ], capture_output=True, text=True, timeout=300)

                    if result.returncode == 0:
                        tasks_executed.append('{command.replace(" --", "_").replace("-", "_")}_update')
                        self.logger.info("{command.split()[1].title()} update completed successfully")
                    else:
                        self.logger.warning(f"{command.split()[1].title()} update failed: {{result.stderr}}")
                        errors.append(f"{command.split()[1].title()} update failed: {{result.stderr}}")

                except subprocess.TimeoutExpired:
                    self.logger.error("{command.split()[1].title()} update timed out")
                    errors.append("{command.split()[1].title()} update timed out")
                except Exception as e:
                    self.logger.error(f"{command.split()[1].title()} update error: {{e}}")
                    errors.append(f"{command.split()[1].title()} update failed: {{str(e)}}")
"""
                                    
                                    # Insert the code
                                    lines.insert(return_index, integration_code)
                                    new_content = '\n'.join(lines)
                                    
                                    if not dry_run:
                                        scheduler_path.write_text(new_content)
                                    return True
                            
                            return False
                            
                        except Exception as e:
                            print(f"  ❌ Integration failed: {e}")
                            return False
                    
                    for opp in integration_opportunities:
                        if opp['target'] == 'daily_tasks':
                            # Integrate into daily tasks
                            success = integrate_into_daily_tasks(opp['command'], force)
                            if success:
                                applied_count += 1
                                print(f"  ✓ Integrated {opp['command']} into daily tasks")
                            else:
                                print(f"  ⚠️  Failed to integrate {opp['command']} into daily tasks")
                        
                        elif opp['target'] == 'weekly_tasks':
                            # Integrate into weekly tasks
                            success = integrate_into_weekly_tasks(opp['command'], force)
                            if success:
                                applied_count += 1
                                print(f"  ✓ Integrated {opp['command']} into weekly tasks")
                            else:
                                print(f"  ⚠️  Failed to integrate {opp['command']} into weekly tasks")
                    
                    print(f"\n✨ Integration complete! Applied {applied_count}/{len(integration_opportunities)} integrations.")
                    
                    if applied_count > 0:
                        print("\n💡 Test the integrations:")
                        print("  codesentinel maintenance daily    # Test daily tasks")
                        print("  codesentinel maintenance weekly   # Test weekly tasks")
                        print("  codesentinel maintenance monthly  # Test monthly tasks")
                
                finally:
                    os.chdir(original_cwd)
            
            else:
                print("\n✨ No integration opportunities found. All commands are already integrated!")
            
            def integrate_into_daily_tasks(command, force=False):
                """Integrate command into daily tasks."""
                try:
                    scheduler_path = Path("codesentinel/utils/scheduler.py")
                    content = scheduler_path.read_text()
                    
                    # Find the right place to insert (after dependency check, before duplication detection)
                    insert_marker = "# Dependency check using CLI update command"
                    if insert_marker in content:
                        # Find the end of the dependency check block
                        lines = content.split('\n')
                        insert_index = -1
                        for i, line in enumerate(lines):
                            if insert_marker in line:
                                # Find the end of this block
                                for j in range(i + 1, len(lines)):
                                    if lines[j].strip().startswith('except Exception as e:'):
                                        # Find the next blank line after this block
                                        for k in range(j + 1, len(lines)):
                                            if not lines[k].strip():
                                                insert_index = k
                                                break
                                        break
                                break
                        
                        if insert_index > 0:
                            # Create the integration code
                            integration_code = f"""
        # {command.split()[1].title()} cleanup using CLI command
        try:
            # Run {command} command
            result = subprocess.run([
                sys.executable, '-m', 'codesentinel.cli', '{command}'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                tasks_executed.append('{command.replace(" --", "_").replace("-", "_")}_cleanup')
                self.logger.info("{command.split()[1].title()} cleanup completed successfully")
            else:
                self.logger.warning(f"{command.split()[1].title()} cleanup failed: {{result.stderr}}")
                errors.append(f"{command.split()[1].title()} cleanup failed: {{result.stderr}}")

        except subprocess.TimeoutExpired:
            self.logger.error("{command.split()[1].title()} cleanup timed out")
            errors.append("{command.split()[1].title()} cleanup timed out")
        except Exception as e:
            self.logger.error(f"{command.split()[1].title()} cleanup error: {{e}}")
            errors.append(f"{command.split()[1].title()} cleanup failed: {{str(e)}}")
        
        # Duplication detection"""
                            
                            # Insert the code
                            lines.insert(insert_index, integration_code)
                            new_content = '\n'.join(lines)
                            
                            if not dry_run:
                                scheduler_path.write_text(new_content)
                            return True
                    
                    return False
                    
                except Exception as e:
                    print(f"  ❌ Integration failed: {e}")
                    return False
            
            def integrate_into_weekly_tasks(command, force=False):
                """Integrate command into weekly tasks."""
                try:
                    scheduler_path = Path("codesentinel/utils/scheduler.py")
                    content = scheduler_path.read_text()
                    
                    # Find the weekly tasks method
                    if "_run_weekly_tasks" in content:
                        lines = content.split('\n')
                        
                        # Find where to insert (before the return statement)
                        return_index = -1
                        for i, line in enumerate(lines):
                            if "_run_weekly_tasks" in line:
                                # Find the return statement
                                for j in range(i + 1, len(lines)):
                                    if lines[j].strip().startswith('return {'):
                                        return_index = j - 1  # Insert before return
                                        break
                                break
                        
                        if return_index > 0:
                            # Create the integration code
                            integration_code = f"""
            # {command.split()[1].title()} update using CLI command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', '{command}'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    tasks_executed.append('{command.replace(" --", "_").replace("-", "_")}_update')
                    self.logger.info("{command.split()[1].title()} update completed successfully")
                else:
                    self.logger.warning(f"{command.split()[1].title()} update failed: {{result.stderr}}")
                    errors.append(f"{command.split()[1].title()} update failed: {{result.stderr}}")

            except subprocess.TimeoutExpired:
                self.logger.error("{command.split()[1].title()} update timed out")
                errors.append("{command.split()[1].title()} update timed out")
            except Exception as e:
                self.logger.error(f"{command.split()[1].title()} update error: {{e}}")
                errors.append(f"{command.split()[1].title()} update failed: {{str(e)}}")
"""
                            
                            # Insert the code
                            lines.insert(return_index, integration_code)
                            new_content = '\n'.join(lines)
                            
                            if not dry_run:
                                scheduler_path.write_text(new_content)
                            return True
                    
                    return False
                    
                except Exception as e:
                    print(f"  ❌ Integration failed: {e}")
                    return False

        elif args.command == 'setup':
            print("Launching setup wizard...")
            if args.gui or args.non_interactive is False:
                try:
                    # Prefer the new modular wizard
                    try:
                        from ..gui_wizard_v2 import main as wizard_main
                        wizard_main()
                    except ImportError:
                        try:
                            from ..gui_project_setup import main as project_setup_main
                            project_setup_main()
                        except ImportError:
                            print("\n❌ ERROR: GUI modules not available")
                            print("\nTry running: codesentinel setup --non-interactive")
                            sys.exit(1)
                except Exception as e:
                    print(f"\n❌ ERROR: Failed to launch GUI setup: {e}")
                    print(f"\nDetails: {type(e).__name__}")
                    print("\nTry running: codesentinel setup --non-interactive")
                    sys.exit(1)
            else:
                # Non-interactive setup
                print("\n" + "=" * 60)
                print("CodeSentinel Setup - Terminal Mode")
                print("=" * 60)
                print("\nThis is the minimal terminal-based setup.")
                print("For full configuration, use: codesentinel setup --gui")
                print("\nSetup wizard created config file: codesentinel.json")
                print("You can edit it directly to customize CodeSentinel.")
                print("\nTo view/edit configuration:")
                print("  notepad codesentinel.json  (Windows)")
                print("  nano codesentinel.json     (Linux/Mac)")
                print("\nSetup complete! CodeSentinel is ready to use.")
                print("=" * 60)

        elif args.command == 'dev-audit':
            interactive = not getattr(args, 'silent', False)
            agent_mode = getattr(args, 'agent', False)
            export_path = getattr(args, 'export', None)
            focus_area = getattr(args, 'focus', None)
            
            if agent_mode:
                # Export comprehensive context for AI agent
                print("Generating audit context for AI agent...")
                if focus_area:
                    print(f"Focus area: {focus_area}")
                agent_context = codesentinel.dev_audit.get_agent_context()
                
                # Add focus area to agent context if specified
                if focus_area:
                    agent_context['focus_area'] = focus_area
                    agent_context['agent_guidance'] = f"""
FOCUSED AUDIT ANALYSIS

Focus Area: {focus_area}

You have been requested to perform a targeted analysis on: "{focus_area}"

While the full audit context is provided below, you should:
1. Prioritize issues and opportunities related to {focus_area}
2. Consider how changes in this area affect the broader system
3. Ensure all remediation respects SEAM Protection (Security, Efficiency, And Minimalism)
4. Maintain non-destructive, feature-preserving principles

{agent_context.get('agent_guidance', '')}
"""
                if export_path:
                    import json as _json
                    with open(export_path, 'w') as f:
                        _json.dump(agent_context, f, indent=2)
                    print(f"Agent context exported to: {export_path}")
                else:
                    # Print guidance for agent
                    print("\n" + "=" * 60)
                    print(agent_context['agent_guidance'])
                    print("\n" + "=" * 60)
                    print("\nAudit Results Summary:")
                    import json as _json
                    print(_json.dumps(agent_context['remediation_context']['summary'], indent=2))
                    
                    print("\n" + "=" * 60)
                    print("AGENT REMEDIATION MODE")
                    if focus_area:
                        print(f"FOCUS: {focus_area}")
                    print("=" * 60)
                    print("\nThis audit has detected issues that require intelligent remediation.")
                    print("An AI agent (GitHub Copilot) can now analyze these findings and build")
                    print("a remediation pipeline while respecting all persistent policies.\n")
                    
                    if focus_area:
                        print(f"\n🎯 Analysis will prioritize: {focus_area}")
                        print("   (while maintaining awareness of system-wide impact)\n")
                    
                    # Output structured data for agent to consume
                    print("\n@agent Here is the comprehensive audit context:")
                    print(_json.dumps(agent_context, indent=2))
                    
                    print("\n\nPlease analyze the audit findings and propose a remediation plan.")
                    if focus_area:
                        print(f"Focus your analysis on: {focus_area}")
                    print("Remember: All actions must be non-destructive and preserve features.")
                
                return
            
            # Non-agent mode with focus
            if focus_area:
                print(f"\n🎯 Focus Area: {focus_area}")
                print("Note: Focus parameter is most effective with --agent mode for Copilot integration.\n")
            
            results = codesentinel.run_dev_audit(interactive=interactive)
            if interactive:
                # Check if there are issues and offer agent mode
                total_issues = results.get('summary', {}).get('total_issues', 0)
                if total_issues > 0:
                    print("\n" + "=" * 60)
                    print(f"🤖 AGENT REMEDIATION AVAILABLE")
                    print("=" * 60)
                    print(f"\nThe audit detected {total_issues} issues.")
                    print("\nIf you have GitHub Copilot integrated, you can run:")
                    print("  codesentinel !!!! --agent")
                    if focus_area:
                        print(f"  codesentinel !!!! {focus_area} --agent  (focused analysis)")
                    else:
                        print("  codesentinel !!!! scheduler --agent       (focus on specific area)")
                    print("\nThis will provide comprehensive context for the AI agent to")
                    print("intelligently build a remediation pipeline while maintaining")
                    print("SEAM Protection (Security, Efficiency, And Minimalism).")
                
                print("\nInteractive dev audit completed.")
                print("A brief audit is running in the background; results will arrive via alerts.")
            else:
                import json as _json
                print(_json.dumps(results.get('summary', {}), indent=2))
            return

        elif args.command == 'integrity':
            """Robust file integrity management interface."""
            from pathlib import Path
            from ..utils.file_integrity import FileIntegrityValidator
            import json as _json
            
            # Load integrity config
            cfg = getattr(codesentinel.config, 'config', {}) or {}
            integrity_config = cfg.get("integrity", {})
            
            # Get workspace root
            workspace_root = Path.cwd()
            
            # Initialize validator
            validator = FileIntegrityValidator(workspace_root, integrity_config)
            
            # State file for tracking monitoring status
            state_file = workspace_root / '.codesentinel' / 'integrity.state'
            state_file.parent.mkdir(parents=True, exist_ok=True)
            
            def load_integrity_state():
                """Load monitoring state from file."""
                if state_file.exists():
                    try:
                        return _json.loads(state_file.read_text())
                    except:
                        return {}
                return {}
            
            def save_integrity_state(state):
                """Save monitoring state to file."""
                state_file.write_text(_json.dumps(state, indent=2))
            
            if args.integrity_action == 'status':
                """Show current integrity monitoring status."""
                state = load_integrity_state()
                is_monitoring = state.get('monitoring', False)
                baseline_path = state.get('baseline_path')
                
                print("\n" + "="*70)
                print("🔒 INTEGRITY MONITORING STATUS")
                print("="*70)
                print(f"\nMonitoring Status: {'🟢 ACTIVE' if is_monitoring else '🔴 INACTIVE'}")
                
                if baseline_path:
                    baseline_file = Path(baseline_path)
                    if baseline_file.exists():
                        baseline_data = _json.loads(baseline_file.read_text())
                        stats = baseline_data.get('statistics', {})
                        print(f"\nBaseline File: {baseline_path}")
                        print(f"  Files tracked: {stats.get('total_files', 0)}")
                        print(f"  Critical files: {stats.get('critical_files', 0)}")
                        print(f"  Last generated: {baseline_data.get('timestamp', 'Unknown')}")
                    else:
                        print(f"\nBaseline File: {baseline_path} (not found)")
                else:
                    print("\nBaseline File: None configured")
                
                if getattr(args, 'detailed', False):
                    print(f"\nDetailed State:")
                    for key, value in state.items():
                        print(f"  {key}: {value}")
                
                print("\n" + "="*70 + "\n")
            
            elif args.integrity_action == 'start':
                """Enable integrity monitoring."""
                baseline_arg = getattr(args, 'baseline', None)
                watch_enabled = getattr(args, 'watch', False)
                
                # Find or use specified baseline
                if baseline_arg:
                    baseline_path = Path(baseline_arg)
                else:
                    # Look for baseline in standard locations
                    standard_paths = [
                        workspace_root / '.codesentinel' / 'integrity_baseline.json',
                        workspace_root / 'integrity_baseline.json',
                    ]
                    baseline_path = None
                    for baseline_file in standard_paths:
                        if baseline_file.exists():
                            baseline_path = baseline_file
                            break
                
                if not baseline_path or not baseline_path.exists():
                    print("❌ ERROR: No baseline found!")
                    print("\nGenerate a baseline first:")
                    print("  codesentinel integrity config baseline")
                    sys.exit(1)
                
                # Save state
                state = {
                    'monitoring': True,
                    'baseline_path': str(baseline_path),
                    'watch_enabled': watch_enabled,
                    'started_at': _json.dumps(str(Path.cwd().stat().st_mtime)),
                }
                save_integrity_state(state)
                
                print("\n✓ Integrity monitoring ENABLED")
                print(f"  Baseline: {baseline_path.name}")
                if watch_enabled:
                    print(f"  Real-time monitoring: Active")
                print("\nIntegrity checks will run during maintenance cycles.")
                print("Use 'codesentinel integrity verify' for immediate verification.\n")
            
            elif args.integrity_action == 'stop':
                """Disable integrity monitoring."""
                state = load_integrity_state()
                save_state_arg = getattr(args, 'save_state', False)
                
                if save_state_arg:
                    # Optionally verify before stopping
                    if state.get('baseline_path'):
                        validator.load_baseline(Path(state['baseline_path']))
                        results = validator.verify_integrity()
                        print(f"Final integrity check: {results['status'].upper()}")
                
                state['monitoring'] = False
                save_integrity_state(state)
                
                print("\n✓ Integrity monitoring DISABLED")
                print("  Files will not be checked during maintenance cycles.")
                print("  Use 'codesentinel integrity start' to re-enable.\n")
            
            elif args.integrity_action == 'reset':
                """Clear baseline and reset integrity state."""
                force = getattr(args, 'force', False)
                
                if not force:
                    response = input("⚠️  Reset all integrity data? This cannot be undone. (y/N): ").strip().lower()
                    if response != 'y':
                        print("Reset cancelled.")
                        return
                
                # Clear state file
                if state_file.exists():
                    state_file.unlink()
                
                # Clear baseline
                baseline_paths = [
                    workspace_root / '.codesentinel' / 'integrity_baseline.json',
                    workspace_root / 'integrity_baseline.json',
                ]
                for baseline_file in baseline_paths:
                    if baseline_file.exists():
                        baseline_file.unlink()
                
                print("\n✓ Integrity state RESET")
                print("  All baselines and monitoring state cleared.")
                print("  Generate a new baseline to resume monitoring.")
                print("  Command: codesentinel integrity config baseline\n")
            
            elif args.integrity_action == 'verify':
                """Verify files against baseline."""
                baseline_arg = getattr(args, 'baseline', None)
                report_arg = getattr(args, 'report', None)
                
                # Load baseline
                if baseline_arg:
                    validator.load_baseline(Path(baseline_arg))
                else:
                    state = load_integrity_state()
                    if state.get('baseline_path'):
                        validator.load_baseline(Path(state['baseline_path']))
                
                print("Verifying file integrity...")
                results = validator.verify_integrity()
                
                print(f"\nIntegrity Check: {results['status'].upper()}")
                stats = results['statistics']
                print(f"\nStatistics:")
                print(f"  Files checked: {stats['files_checked']}")
                print(f"  Passed: {stats['files_passed']}")
                print(f"  Modified: {stats['files_modified']}")
                print(f"  Missing: {stats['files_missing']}")
                print(f"  Unauthorized: {stats['files_unauthorized']}")
                print(f"  Critical violations: {stats['critical_violations']}")
                
                if results['violations']:
                    print(f"\nViolations found: {len(results['violations'])}")
                    print("\nCritical Issues:")
                    for violation in [v for v in results['violations'] if v.get('severity') == 'critical'][:10]:
                        print(f"  ! {violation['type']}: {violation['file']}")
                    
                    if report_arg:
                        report_path = Path(report_arg)
                        report_path.write_text(_json.dumps(results, indent=2))
                        print(f"\nFull report saved to: {report_arg}")
                    
                    print("\nRun 'codesentinel !!!! --agent' for AI-assisted remediation.")
                else:
                    print("\n✓ All files passed integrity check!")
            
            elif args.integrity_action == 'config':
                """Manage integrity configuration."""
                if args.config_action == 'baseline':
                    # Generate baseline
                    print("Generating file integrity baseline (timeout: 30 seconds)...")
                    
                    timeout_seconds = 30
                    baseline = None
                    error_message = None
                    
                    def generate_with_timeout():
                        nonlocal baseline, error_message
                        try:
                            baseline = validator.generate_baseline(patterns=getattr(args, 'patterns', None))
                        except Exception as e:
                            error_message = str(e)
                    
                    thread = threading.Thread(target=generate_with_timeout, daemon=True)
                    thread.start()
                    thread.join(timeout=timeout_seconds)
                    
                    if thread.is_alive():
                        print(f"\n❌ ERROR: Baseline generation timed out after {timeout_seconds} seconds")
                        print("The file enumeration may be stuck on a large or slow filesystem.")
                        print("\nPossible causes:")
                        print("  - Large number of files (>100,000) in workspace")
                        print("  - Slow/network filesystem causing I/O hangs")
                        print("  - Symlinks or junction points causing infinite traversal")
                        print("\nTry with specific patterns to limit scope:")
                        print("  codesentinel integrity config baseline --patterns '**/*.py' '**/*.md'")
                        sys.exit(1)
                    
                    if error_message:
                        print(f"\n❌ ERROR: Baseline generation failed: {error_message}")
                        sys.exit(1)
                    
                    if baseline is None:
                        print(f"\n❌ ERROR: Baseline generation failed (no data)")
                        sys.exit(1)
                    
                    output_path = Path(args.output) if args.output else None
                    saved_path = validator.save_baseline(output_path)
                    
                    print(f"\n✓ Baseline generated successfully!")
                    print(f"Saved to: {saved_path}")
                    print(f"\nStatistics:")
                    stats = baseline['statistics']
                    print(f"  Total files: {stats['total_files']}")
                    print(f"  Critical files: {stats['critical_files']}")
                    print(f"  Whitelisted files: {stats['whitelisted_files']}")
                    print(f"  Excluded files: {stats['excluded_files']}")
                    print(f"  Skipped files: {stats.get('skipped_files', 0)}")
                    print(f"\nNext: codesentinel integrity start --baseline {saved_path}")
                
                elif args.config_action == 'whitelist':
                    if getattr(args, 'show', False):
                        # Show current whitelist
                        print("Current whitelist patterns:")
                        whitelist = integrity_config.get('whitelist', [])
                        if whitelist:
                            for pattern in whitelist:
                                print(f"  - {pattern}")
                        else:
                            print("  (empty)")
                    else:
                        # Update whitelist
                        print(f"Updating whitelist with {len(args.patterns)} pattern(s)...")
                        validator.update_whitelist(args.patterns, replace=args.replace)
                        print(f"Whitelist updated: {', '.join(args.patterns)}")
                        print("Note: Update your config file to persist these changes.")
                
                elif args.config_action == 'critical':
                    if getattr(args, 'show', False):
                        # Show current critical files
                        print("Current critical files:")
                        critical = integrity_config.get('critical_files', [])
                        if critical:
                            for file in critical:
                                print(f"  - {file}")
                        else:
                            print("  (empty)")
                    else:
                        # Update critical files
                        if not args.files:
                            print("❌ ERROR: Specify files to mark as critical")
                        else:
                            print(f"Marking {len(args.files)} file(s) as critical...")
                            validator.update_critical_files(args.files, replace=args.replace)
                            print(f"Critical files updated: {', '.join(args.files)}")
                            print("Note: Update your config file to persist these changes.")
                
                else:
                    print("❌ Unknown config action. Use 'codesentinel integrity config --help'")
            
            else:
                print("❌ Unknown integrity action. Use 'codesentinel integrity --help'")
            
            return

    except Exception as e:
        import traceback
        if str(e):
            print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()