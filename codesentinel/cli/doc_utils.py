"""
Documentation utilities for verification and fixing.

This module contains shared functions for documentation branding,
header/footer management, and integrity verification.
"""
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import re


def _normalize_markdown_whitespace(content: str) -> str:
    """
    Normalizes whitespace in markdown content.
    - Replaces multiple blank lines with a single blank line.
    - Removes trailing whitespace from lines (except intentional Markdown line breaks).
    - Ensures content ends with a single newline.
    
    Note: Preserves intentional Markdown line breaks (exactly two spaces at end of line)
    but removes all other trailing whitespace.
    """
    lines = content.split('\n')
    normalized_lines = []
    
    for line in lines:
        # Check if line ends with exactly 2 spaces (Markdown line break)
        # Must check for exactly 2, not 2+
        if len(line) >= 2 and line[-2:] == '  ' and (len(line) == 2 or line[-3] != ' '):
            # Keep exactly 2 trailing spaces (intentional line break)
            normalized_lines.append(line)
        else:
            # Strip all trailing whitespace
            normalized_lines.append(line.rstrip())
    
    # Rejoin lines
    content = '\n'.join(normalized_lines)
    
    # Replace 3 or more newlines with just two (one blank line)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Ensure the file ends with a single newline
    content = content.strip() + '\n'
    
    return content


def verify_documentation_branding(file_path: Path) -> Tuple[bool, List[str]]:
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


def verify_documentation_headers_footers(file_path: Path) -> Tuple[bool, List[str], Dict[str, Any]]:
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


def apply_branding_fixes(file_path: Path, verbose: bool = False) -> Tuple[bool, str]:
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


def apply_header_footer_fixes(file_path: Path, verbose: bool = False) -> Tuple[bool, str]:
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


def verify_and_fix_documentation_pipeline(file_paths: List[Path], dry_run: bool = False,
                                          verbose: bool = False, file_type_label: str = "") -> Dict[str, List[str]]:
    """
    Consolidated documentation verification and fix pipeline.
    
    This unified function maximizes efficiency and minimalism by:
    1. Verifying branding compliance (SEAM Protection™)
    2. Verifying header/footer structure
    3. Checking for encoding corruption
    4. Checking for excessive blank lines
    5. Applying automatic fixes if needed
    
    Security: All file operations use proper encoding validation.
    Efficiency: Single reusable pipeline eliminates duplicate code across all update subcommands.
    Minimalism: Replaces separate verification code in docs, readme, changelog, etc.
    
    Args:
        file_paths: List of Path objects to verify
        dry_run: If True, report issues without fixing
        verbose: Print detailed output
        file_type_label: Label for this verification pass (e.g., "README", "Documentation")
        
    Returns:
        Dictionary with results:
        {
            'verified': [files_that_passed],
            'fixed': [files_that_were_fixed],
            'errors': [files_with_errors],
            'branding_issues': [...],
            'header_footer_issues': [...],
            'encoding_issues': [...],
            'whitespace_issues': [...]
        }
    """
    results: Dict[str, List[str]] = {
        'verified': [],
        'fixed': [],
        'errors': [],
        'branding_issues': [],
        'header_footer_issues': [],
        'encoding_issues': [],
        'whitespace_issues': [],
    }
    
    for doc_file in file_paths:
        if not doc_file.exists():
            continue
        
        file_issues = []
        fixes_applied = False
        
        # 1. Check for encoding corruption
        try:
            content = doc_file.read_text(encoding='utf-8')
            # Verify encoding integrity
            content.encode('utf-8').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            results['encoding_issues'].append(f"{doc_file.name}: {e}")
            results['errors'].append(doc_file.name)
            if verbose:
                print(f"   Encoding error: {doc_file.name}")
            continue
        except Exception as e:
            results['errors'].append(doc_file.name)
            if verbose:
                print(f"   Error reading: {doc_file.name}")
            continue
        
        # 2. Check for excessive blank lines
        if doc_file.suffix == '.md':
            line_count = len(content.split('\n'))
            # Heuristic: if more than 25% are blank, flag it
            non_empty_lines = len([l for l in content.split('\n') if l.strip()])
            blank_percentage = ((1 - non_empty_lines/line_count)*100) if line_count > 0 else 0
            if blank_percentage > 25:
                results['whitespace_issues'].append(
                    f"{doc_file.name}: {blank_percentage:.1f}% blank lines (threshold: 25%)"
                )
                file_issues.append("excessive_blanks")
                
                # Fix excessive blanks
                if not dry_run:
                    try:
                        normalized = _normalize_markdown_whitespace(content)
                        doc_file.write_text(normalized, encoding='utf-8')
                        fixes_applied = True
                        if verbose:
                            print(f"  ✓ Fixed (whitespace): {doc_file.name}")
                    except Exception as e:
                        results['errors'].append(f"{doc_file.name}: Could not fix whitespace")
                        continue
        
        # 3. Verify branding compliance
        is_branding_compliant, branding_issues_list = verify_documentation_branding(doc_file)
        if not is_branding_compliant:
            results['branding_issues'].extend(branding_issues_list)
            file_issues.append("branding")
            
            # Fix branding
            if not dry_run:
                success, message = apply_branding_fixes(doc_file, verbose)
                if success:
                    fixes_applied = True
                    if verbose:
                        print(f"  ✓ Fixed (branding): {doc_file.name}")
        
        # 4. Verify headers/footers (markdown only)
        is_hf_compliant = True
        hf_issues_list = []
        if doc_file.suffix == '.md':
            is_hf_compliant, hf_issues_list, metadata = verify_documentation_headers_footers(doc_file)
            if not is_hf_compliant:
                results['header_footer_issues'].extend(hf_issues_list)
                file_issues.append("header_footer")
                
                # Fix header/footer
                if not dry_run:
                    success, message = apply_header_footer_fixes(doc_file, verbose)
                    if success:
                        fixes_applied = True
                        if verbose:
                            print(f"  ✓ Fixed (header/footer): {doc_file.name}")
        
        # Summary for this file
        if not file_issues:
            results['verified'].append(doc_file.name)
            if verbose:
                print(f"  ✓ Full compliance: {doc_file.name}")
        elif fixes_applied:
            results['fixed'].append(doc_file.name)
        elif dry_run and file_issues:
            if verbose:
                print(f"  [DRY-RUN] Would fix: {doc_file.name} ({', '.join(file_issues)})")
    
    return results


def detect_project_info() -> dict:
    """
    Intelligently detect project and repository information.
    
    Returns:
        Dictionary with detected project info (project_name, description, repo_url, etc.)
    """
    import json
    import re
    import subprocess
    
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
    print(f"[PROJECT] Detected Project: {project_info['project_name']}")
    print(f"   Description: {project_info['description']}")
    if project_info['repo_url']:
        print(f"   Repository: {project_info['repo_url']}")
    print("="*70)
    
    if template_type in ['header', 'both']:
        print("\nHEADER TEMPLATES")
        print("="*70)
        headers = get_header_templates()
        for file_name, template_info in headers.items():
            marker = "[PROJECT]" if template_info.get('project_specific') else "        "
            print(f"\n{marker} [FILE] {file_name}")
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
            marker = "[PROJECT]" if template_info.get('project_specific') else "        "
            print(f"\n{marker} [TEMPLATE] {template_name.upper()}")
            print(f"   Description: {template_info['description']}")
            print(f"   Preview:\n")
            lines = template_info['template'].split("\n")[:3]
            for line in lines:
                if line:
                    print(f"   {line}")
    
    print("\n" + "="*70)
    print("[PROJECT] = Project-specific (uses detected project name/version)")
    print("="*70 + "\n")


def set_header_for_file(file_path: Path, template_name: Optional[str] = None, custom_header: Optional[str] = None) -> Tuple[bool, str]:
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


def set_footer_for_file(file_path: Path, template_name: str = 'standard', custom_footer: Optional[str] = None) -> Tuple[bool, str]:
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


def edit_headers_interactive(doc_files: Optional[List[Path]] = None) -> None:
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
    print("[EDITOR] INTERACTIVE HEADER EDITOR")
    print("="*70)
    
    for file_path in doc_files:
        if not file_path.exists():
            continue
        
        print(f"\n[FILE] {file_path.name}")
        print("-" * 70)
        
        # Show template options with project-specific values
        headers = get_header_templates()
        if file_path.name in headers:
            template_info = headers[file_path.name]
            project_marker = "[PROJECT]" if template_info.get('project_specific') else "        "
            print(f"{project_marker} Description: {template_info['description']}")
            print(f"\nSuggested template:\n")
            print(template_info['template'][:200])
            
            choice = input("Use suggested template? (y/n/custom): ")

            if choice == 'y':
                success, msg = set_header_for_file(file_path, file_path.name)
                print(f"[OK] {msg}" if success else f"[FAIL] {msg}")
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
                print(f"[OK] {msg}" if success else f"[FAIL] {msg}")
            else:
                print("Skipped.")
        else:
            print(f"No template available for {file_path.name}")
    
    print("\n" + "="*70 + "\n")


def edit_footers_interactive(doc_files: Optional[List[Path]] = None) -> None:
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
    print("[EDITOR] INTERACTIVE FOOTER EDITOR")
    print("="*70)
    
    for file_path in doc_files:
        if not file_path.exists():
            continue
        
        print(f"\n[FILE] {file_path.name}")
        print("-" * 70)
        
        # Show footer template options with project-specific values
        footers = get_footer_templates()
        print("Available footer templates:\n")
        for idx, (template_name, template_info) in enumerate(footers.items(), 1):
            marker = "[PROJECT]" if template_info.get('project_specific') else "        "
            print(f"  {idx}. {marker} {template_name.upper()}: {template_info['description']}")
        
        choice = input("\nSelect template (number/custom): ").strip().lower()
        
        if choice.isdigit() and 1 <= int(choice) <= len(footers):
            template_name = list(footers.keys())[int(choice) - 1]
            success, msg = set_footer_for_file(file_path, template_name)
            print(f"[OK] {msg}" if success else f"[FAIL] {msg}")
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
            print(f"[OK] {msg}" if success else f"[FAIL] {msg}")
        else:
            print("Skipped.")
    
    print("\n" + "="*70 + "\n")
