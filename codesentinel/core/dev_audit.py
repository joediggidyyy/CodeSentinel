"""
Development Audit System
========================

Implements interactive and silent development audits focused on:

> SECURITY - EFFICIENCY - MINIMALISM <

The interactive audit prints a detailed report. Immediately after it
finishes, a brief silent audit runs in the background and reports its
outcome via the configured alert channels.
"""

from __future__ import annotations

import os
import re
import json
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional


class DevAudit:
    """Runs development audits with interactive and silent modes."""

    def __init__(self, project_root: Optional[Path], alert_manager, config_manager):
        self.project_root = project_root or Path.cwd()
        self.alert_manager = alert_manager
        self.config_manager = config_manager
        # Persisted policy: '!!!!' must be non-destructive and feature-preserving
        cfg = getattr(self.config_manager, "config", {}) or {}
        self.policy = cfg.get("policy") or {
            "non_destructive": True,
            "feature_preservation": True,
            "conflict_resolution": "merge-prefer-existing",
        }

    # -------------------- Public API --------------------
    def run_interactive(self) -> Dict[str, Any]:
        """Run a full interactive audit and print results to console."""
        results = self._run_audit(detail_level="full")
        self._print_report(results)

        # Kick off a brief audit in background and alert
        bg_thread = threading.Thread(target=self._run_brief_and_alert, daemon=True)
        bg_thread.start()
        return results

    def run_brief(self) -> Dict[str, Any]:
        """Run a brief audit suitable for background/alerts."""
        return self._run_audit(detail_level="brief")

    def get_agent_context(self) -> Dict[str, Any]:
        """
        Export audit results with remediation context for AI agent.

        This provides comprehensive information for GitHub Copilot to
        intelligently decide remediation actions while respecting
        persistent policies (non-destructive, feature preservation).
        """
        results = self._run_audit(detail_level="full")

        # Build remediation hints for each category
        remediation_context = {
            "policy": self.policy,
            "principles": ["SECURITY", "EFFICIENCY", "MINIMALISM"],
            "constraints": [
                "All actions must be non-destructive",
                "Feature preservation is mandatory",
                "Style must be preserved (no forced formatting)",
                "Conflict resolution: merge-prefer-existing",
            ],
            "security_issues": self._build_security_remediation_hints(
                results["security"]
            ),
            "efficiency_issues": self._build_efficiency_remediation_hints(
                results["efficiency"]
            ),
            "minimalism_issues": self._build_minimalism_remediation_hints(
                results["minimalism"]
            ),
            "summary": results["summary"],
        }

        return {
            "audit_results": results,
            "remediation_context": remediation_context,
            "agent_guidance": self._generate_agent_guidance(remediation_context),
        }

    def _build_security_remediation_hints(
        self, security: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build actionable hints for security issues."""
        hints = []
        for finding in security.get("secrets_findings", []):
            hints.append(
                {
                    "file": finding["file"],
                    "issue": "Potential secret/credential detected",
                    "pattern": finding["pattern"],
                    "suggested_actions": [
                        "Review file to confirm if this is a real credential",
                        "If real: move to environment variables or secure vault",
                        "If false positive: add exception to audit config",
                        "Consider adding file to .gitignore if contains secrets",
                    ],
                    "priority": "critical",
                }
            )
        return hints

    def _build_efficiency_remediation_hints(
        self, efficiency: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build actionable hints for efficiency issues."""
        hints = []
        for suggestion in efficiency.get("suggestions", []):
            if "wizard implementations" in suggestion:
                hints.append(
                    {
                        "issue": "Multiple wizard implementations detected",
                        "suggestion": suggestion,
                        "suggested_actions": [
                            "Identify the canonical wizard (likely codesentinel/gui_wizard_v2.py)",
                            "Verify other wizards are truly redundant (not different use cases)",
                            "Move deprecated wizards to quarantine_legacy_archive/",
                            "Update any references to point to canonical implementation",
                        ],
                        "priority": "medium",
                        "agent_decision_required": True,
                    }
                )
            elif "__pycache__" in suggestion:
                hints.append(
                    {
                        "issue": "__pycache__ in root directory",
                        "suggestion": suggestion,
                        "suggested_actions": [
                            "Add __pycache__/ to .gitignore",
                            "Remove from git: git rm -r --cached __pycache__/",
                            "Delete directory: rm -rf __pycache__/",
                        ],
                        "priority": "low",
                        "safe_to_automate": True,
                    }
                )
            elif "Large files" in suggestion:
                hints.append(
                    {
                        "issue": "Large files detected",
                        "suggestion": suggestion,
                        "suggested_actions": [
                            "Review large files to determine if they belong in repo",
                            "Consider Git LFS for large binary files",
                            "Move test data/assets to separate location",
                            "Add large files to .gitignore if not needed",
                        ],
                        "priority": "medium",
                        "agent_decision_required": True,
                    }
                )
            else:
                hints.append(
                    {
                        "issue": "General efficiency concern",
                        "suggestion": suggestion,
                        "suggested_actions": [
                            "Review and determine appropriate action"
                        ],
                        "priority": "low",
                        "agent_decision_required": True,
                    }
                )
        return hints

    def _build_minimalism_remediation_hints(
        self, minimalism: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build actionable hints for minimalism violations."""
        hints = []
        for violation in minimalism.get("violations", []):
            if "Orphaned test files" in violation:
                hints.append(
                    {
                        "issue": "Test files in wrong location",
                        "violation": violation,
                        "suggested_actions": [
                            "Move test_*.py files from root to tests/ directory",
                            "Update any references or imports",
                            "Verify tests still run after move: pytest tests/",
                        ],
                        "priority": "high",
                        "safe_to_automate": True,
                    }
                )
            elif "Duplicate launcher files" in violation:
                hints.append(
                    {
                        "issue": "Duplicate launcher implementations",
                        "violation": violation,
                        "suggested_actions": [
                            "Identify canonical launcher (codesentinel/launcher.py for package)",
                            "Verify launch.py is only used as root entry point",
                            "If truly duplicate: archive one to quarantine_legacy_archive/",
                            "Update references and entry points",
                        ],
                        "priority": "medium",
                        "agent_decision_required": True,
                    }
                )
            elif "Redundant packaging" in violation:
                hints.append(
                    {
                        "issue": "Both setup.py and pyproject.toml present",
                        "violation": violation,
                        "suggested_actions": [
                            "Modern Python uses pyproject.toml only (PEP 517/518)",
                            "Verify all setup.py config is in pyproject.toml",
                            "Archive setup.py to quarantine_legacy_archive/",
                            "Test installation still works: pip install -e .",
                        ],
                        "priority": "high",
                        "agent_decision_required": True,
                        "note": "This may be causing console script generation issues",
                    }
                )
            elif "Incomplete src/codesentinel/" in violation:
                hints.append(
                    {
                        "issue": "Abandoned src/ directory structure",
                        "violation": violation,
                        "suggested_actions": [
                            "Review src/codesentinel/ contents",
                            "If truly abandoned: archive to quarantine_legacy_archive/",
                            "If needed: integrate into main codesentinel/ package",
                            "Update imports and references",
                        ],
                        "priority": "medium",
                        "agent_decision_required": True,
                    }
                )
            elif "Legacy archive directory" in violation:
                hints.append(
                    {
                        "issue": "Legacy archive taking up space",
                        "violation": violation,
                        "suggested_actions": [
                            "Verify all needed features have been ported",
                            "Consider creating archive tarball: tar -czf legacy_v0.tar.gz quarantine_legacy_archive/",
                            "Move tarball to docs/ or external storage",
                            "Remove directory after verification period",
                        ],
                        "priority": "low",
                        "agent_decision_required": True,
                        "note": "Keep until v2 feature parity confirmed",
                    }
                )
            elif "Too many installers" in violation:
                hints.append(
                    {
                        "issue": "Multiple installer scripts",
                        "violation": violation,
                        "suggested_actions": [
                            "Identify canonical installer for the project",
                            "Archive redundant installers",
                            "Update documentation to reference single installer",
                        ],
                        "priority": "medium",
                        "agent_decision_required": True,
                    }
                )
            else:
                hints.append(
                    {
                        "issue": "Minimalism violation",
                        "violation": violation,
                        "suggested_actions": [
                            "Review and determine appropriate action"
                        ],
                        "priority": "medium",
                        "agent_decision_required": True,
                    }
                )
        return hints

    def _generate_agent_guidance(self, context: Dict[str, Any]) -> str:
        """Generate high-level guidance for AI agent."""
        total_issues = context["summary"]["total_issues"]
        severity = context["summary"]["severity"]

        guidance = f"""
CodeSentinel Development Audit - Agent Guidance
================================================

Total Issues: {total_issues} (Severity: {severity})

CORE PRINCIPLES:
- SECURITY > EFFICIENCY > MINIMALISM
- All actions must be NON-DESTRUCTIVE
- Feature preservation is MANDATORY
- Style preservation is MANDATORY

AGENT ROLE:
You are tasked with intelligently reviewing the audit findings and building
a remediation pipeline. You should:

1. ANALYZE: Review each issue with context
2. PRIORITIZE: Focus on critical/high priority items first
3. DECIDE: Determine safe vs. requires-review actions
4. PLAN: Build step-by-step remediation plan
5. EXECUTE: Only perform safe, non-destructive operations
6. REPORT: Document all actions and decisions

SAFE ACTIONS (can automate):
- Moving test files to proper directories
- Adding entries to .gitignore
- Removing __pycache__ directories
- Archiving confirmed-redundant files to quarantine_legacy_archive/

REQUIRES REVIEW (agent decision needed):
- Deleting or archiving potentially-used code
- Consolidating multiple implementations
- Removing packaging configurations
- Modifying imports or entry points

FORBIDDEN ACTIONS:
- Deleting files without archiving
- Forcing code style changes
- Removing features without verification
- Modifying core functionality

RECOMMENDED APPROACH:
1. Start with safe, low-priority cleanup (__pycache__, .gitignore)
2. Move orphaned test files to proper locations
3. For duplicates: analyze usage, archive unused, update references
4. For each action: explain reasoning and confirm non-destructive
5. Create archive snapshots before any structural changes
"""
        return guidance.strip()

    # -------------------- Internal --------------------
    def _run_brief_and_alert(self) -> None:
        results = self.run_brief()
        title = "Dev Audit Summary"
        severity = self._severity_from_results(results)
        message = self._format_alert_message(results)
        try:
            self.alert_manager.send_alert(
                title=title, message=message, severity=severity
            )
        except Exception:
            # Alerts should never crash the process
            pass

    def _run_audit(self, detail_level: str = "full") -> Dict[str, Any]:
        prj = self.project_root
        repo_name = prj.name

        # Collect metrics
        metrics = self._collect_repo_metrics(prj, limit_scan=(detail_level == "brief"))
        security = self._security_checks(prj, limit_scan=(detail_level == "brief"))
        efficiency = self._efficiency_checks(metrics)
        minimalism = self._minimalism_checks(prj, metrics)
        style = self._style_preservation_checks(prj)

        summary = self._summarize(security, efficiency, minimalism, style)

        return {
            "repository": repo_name,
            "root": str(prj),
            "detail_level": detail_level,
            "policy": self.policy,
            "metrics": metrics,
            "security": security,
            "efficiency": efficiency,
            "minimalism": minimalism,
            "style_preservation": style,
            "summary": summary,
        }

    # -------------------- Checks --------------------
    def _collect_repo_metrics(self, root: Path, limit_scan: bool) -> Dict[str, Any]:
        file_count = 0
        py_count = 0
        big_files: List[str] = []
        unsafe_exts = {".pem", ".key", ".pfx", ".p12"}
        unsafe_files: List[str] = []

        max_files = 3000 if not limit_scan else 800
        max_big_file_size = 5 * 1024 * 1024  # 5 MiB

        for dirpath, dirnames, filenames in os.walk(root):
            # Skip typical build/venv/artifacts
            skip_dirs = {
                ".git",
                "__pycache__",
                ".venv",
                "venv",
                "dist",
                "build",
                "node_modules",
            }
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]

            for fname in filenames:
                file_count += 1
                if file_count > max_files:
                    break

                p = Path(dirpath) / fname
                if p.suffix == ".py":
                    py_count += 1
                if p.suffix.lower() in unsafe_exts:
                    unsafe_files.append(str(p.relative_to(root)))
                try:
                    if p.stat().st_size > max_big_file_size:
                        big_files.append(str(p.relative_to(root)))
                except OSError:
                    continue

            if file_count > max_files:
                break

        return {
            "total_files_scanned": file_count,
            "python_files": py_count,
            "big_files": big_files[:10],
            "unsafe_files": unsafe_files[:10],
            "scan_limited": file_count >= max_files,
        }

    def _security_checks(self, root: Path, limit_scan: bool) -> Dict[str, Any]:
        secrets_patterns = [
            re.compile(
                r"aws_?(access|secret)[_\- ]?key\s*[:=]\s*['\"][A-Za-z0-9/+=]{16,}['\"]",
                re.I,
            ),
            re.compile(r"(?i)secret\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
            re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
            re.compile(r"-----BEGIN (RSA|DSA|EC) PRIVATE KEY-----"),
        ]
        findings: List[Dict[str, Any]] = []
        max_hits = 25 if not limit_scan else 8

        scanned = 0
        for dirpath, dirnames, filenames in os.walk(root):
            skip_dirs = {
                ".git",
                "__pycache__",
                ".venv",
                "venv",
                "dist",
                "build",
                "node_modules",
                "quarantine_legacy_archive",
            }
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]

            for fname in filenames:
                # Only scan text-like files
                if not any(
                    fname.endswith(ext)
                    for ext in (".py", ".json", ".md", ".yml", ".yaml", ".ini", ".txt")
                ):
                    continue
                p = Path(dirpath) / fname
                try:
                    content = p.read_text(errors="ignore")
                except Exception:
                    continue

                for pat in secrets_patterns:
                    if pat.search(content):
                        findings.append(
                            {
                                "file": str(p.relative_to(root)),
                                "pattern": pat.pattern[:40]
                                + ("..." if len(pat.pattern) > 40 else ""),
                            }
                        )
                        if len(findings) >= max_hits:
                            break
                if len(findings) >= max_hits:
                    break

            scanned += 1
            if len(findings) >= max_hits:
                break

        return {
            "secrets_findings": findings,
            "issues": len(findings),
        }

    def _efficiency_checks(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        suggestions: List[str] = []

        if metrics.get("scan_limited"):
            suggestions.append(
                "Repository large; consider excluding artifacts from repo"
            )

        if len(metrics.get("big_files", [])) > 0:
            suggestions.append("Large files detected; consider Git LFS or pruning")

        # Check for redundant wizard implementations
        root = self.project_root
        wizard_files = []
        if (root / "setup_wizard.py").exists():
            wizard_files.append("setup_wizard.py")
        if (root / "codesentinel" / "gui_wizard_v2.py").exists():
            wizard_files.append("codesentinel/gui_wizard_v2.py")
        if (root / "src" / "codesentinel" / "ui" / "setup" / "wizard.py").exists():
            wizard_files.append("src/codesentinel/ui/setup/wizard.py")
        if len(wizard_files) > 1:
            suggestions.append(
                f"Multiple wizard implementations detected: {', '.join(wizard_files)} (consolidate to one)"
            )

        # Check for __pycache__ in root
        if (root / "__pycache__").exists():
            suggestions.append(
                "__pycache__ in root directory (add to .gitignore and clean up)"
            )

        return {
            "suggestions": suggestions,
            "issues": len(suggestions),
        }

    def _minimalism_checks(self, root: Path, metrics: Dict[str, Any]) -> Dict[str, Any]:
        violations: List[str] = []

        # Check for duplicate installers (defensive)
        installer_names = {
            "install.py",
            "install_deps.py",
            "setup_wizard.py",
            "install_codesentinel.py",
        }
        present_installers = []
        for name in installer_names:
            if (root / name).exists():
                present_installers.append(name)
        if len(present_installers) > 2:
            violations.append(
                f"Too many installers present: {', '.join(present_installers)}"
            )

        # Check for orphaned test files in root (should be in tests/)
        orphaned_tests = []
        for item in root.iterdir():
            if (
                item.is_file()
                and item.name.startswith("test_")
                and item.suffix == ".py"
            ):
                orphaned_tests.append(item.name)
        if orphaned_tests:
            violations.append(
                f"Orphaned test files in root (move to tests/): {', '.join(orphaned_tests)}"
            )

        # Check for duplicate launcher/wizard files
        launchers = []
        if (root / "launch.py").exists():
            launchers.append("launch.py")
        if (root / "codesentinel" / "launcher.py").exists():
            launchers.append("codesentinel/launcher.py")
        if len(launchers) > 1:
            violations.append(f"Duplicate launcher files: {', '.join(launchers)}")

        # Check for duplicate setup configurations (setup.py + pyproject.toml)
        if (root / "setup.py").exists() and (root / "pyproject.toml").exists():
            violations.append(
                "Redundant packaging: both setup.py and pyproject.toml (prefer pyproject.toml only)"
            )

        # Check for incomplete/abandoned directories
        src_dir = root / "src"
        if src_dir.exists():
            # Check if src/ contains incomplete/abandoned code
            src_codesentinel = src_dir / "codesentinel"
            if src_codesentinel.exists():
                violations.append(
                    "Incomplete src/codesentinel/ directory detected (may contain abandoned code)"
                )

        # Check for legacy quarantine directories
        if (root / "quarantine").exists():
            violations.append(
                "Legacy quarantine directory present; archive recommended"
            )
        if (root / "quarantine_legacy_archive").exists():
            violations.append(
                "Legacy archive directory still present (cleanup recommended after verification)"
            )

        return {
            "violations": violations,
            "issues": len(violations),
        }

    def _style_preservation_checks(self, root: Path) -> Dict[str, Any]:
        """Check that audit respects existing style and doesn't force changes."""
        notes: List[str] = []

        # Verify we're not forcing style changes
        notes.append("Audit is non-destructive; no style enforcement")

        # Check for style consistency indicators
        if (root / ".editorconfig").exists():
            notes.append("EditorConfig detected; style defined")
        if (root / "pyproject.toml").exists():
            notes.append("pyproject.toml detected; may contain style config")
        if (root / ".pre-commit-config.yaml").exists():
            notes.append("Pre-commit hooks detected; automated style checks active")

        return {
            "notes": notes,
            "style_preserved": True,
        }

    # -------------------- Reporting --------------------
    def _summarize(
        self,
        security: Dict[str, Any],
        efficiency: Dict[str, Any],
        minimalism: Dict[str, Any],
        style: Dict[str, Any],
    ) -> Dict[str, Any]:
        total_issues = (
            security.get("issues", 0)
            + efficiency.get("issues", 0)
            + minimalism.get("issues", 0)
        )
        level = "info"
        if total_issues >= 8 or security.get("issues", 0) >= 5:
            level = "critical"
        elif total_issues >= 4 or security.get("issues", 0) >= 3:
            level = "warning"
        return {
            "total_issues": total_issues,
            "severity": level,
            "style_preserved": style.get("style_preserved", True),
        }

    def _print_report(self, results: Dict[str, Any]) -> None:
        print("\nCodeSentinel Development Audit")
        print("=" * 40)
        print(f"Repository: {results['repository']}")
        print(f"Detail: {results['detail_level']}")
        print(
            "Policy: non_destructive=%s, feature_preservation=%s"
            % (
                str(results.get("policy", {}).get("non_destructive", True)),
                str(results.get("policy", {}).get("feature_preservation", True)),
            )
        )
        print("\nSecurity Findings:")
        for f in results["security"]["secrets_findings"][:5]:
            print(f"  - {f['file']} (pattern: {f['pattern']})")
        if not results["security"]["secrets_findings"]:
            print("  - No obvious secrets detected")
        print("\nEfficiency Suggestions:")
        for s in results["efficiency"]["suggestions"]:
            print(f"  - {s}")
        if not results["efficiency"]["suggestions"]:
            print("  - No suggestions")
        print("\nMinimalism Violations:")
        for v in results["minimalism"]["violations"]:
            print(f"  - {v}")
        if not results["minimalism"]["violations"]:
            print("  - None detected")
        print("\nStyle Preservation:")
        style_notes = results.get("style_preservation", {}).get("notes", [])
        for note in style_notes:
            print(f"  - {note}")
        if not style_notes:
            print("  - No style information available")
        print("\nSummary:")
        print(json.dumps(results["summary"], indent=2))

    def _severity_from_results(self, results: Dict[str, Any]) -> str:
        return results.get("summary", {}).get("severity", "info")

    def _format_alert_message(self, results: Dict[str, Any]) -> str:
        total = results["summary"]["total_issues"]
        sec = results["security"]["issues"]
        eff = results["efficiency"]["issues"]
        minv = results["minimalism"]["issues"]
        return (
            f"Repo: {results['repository']}\n"
            f"Issues: {total} (security: {sec}, efficiency: {eff}, minimalism: {minv})\n"
            f"Detail: {results['detail_level']}\n"
        )


__all__ = ["DevAudit"]
