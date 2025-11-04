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
from typing import Dict, Any, List, Optional, Tuple

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for older interpreters
    tomllib = None  # type: ignore


class DevAudit:
    """Runs development audits with interactive and silent modes."""

    def __init__(self, project_root: Optional[Path], alert_manager, config_manager):
        self.project_root = project_root or Path.cwd()
        self.alert_manager = alert_manager
        self.config_manager = config_manager
        # Persisted policy: '!!!!' must be non-destructive and feature-preserving
        cfg = getattr(self.config_manager, 'config', {}) or {}
        self.policy = (cfg.get('policy') or {
            'non_destructive': True,
            'feature_preservation': True,
            'conflict_resolution': 'merge-prefer-existing'
        })

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
                "Conflict resolution: merge-prefer-existing"
            ],
            "security_issues": self._build_security_remediation_hints(results["security"]),
            "efficiency_issues": self._build_efficiency_remediation_hints(results["efficiency"]),
            "minimalism_issues": self._build_minimalism_remediation_hints(results["minimalism"]),
            "summary": results["summary"]
        }
        
        return {
            "audit_results": results,
            "remediation_context": remediation_context,
            "agent_guidance": self._generate_agent_guidance(remediation_context)
        }

    def _build_security_remediation_hints(self, security: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build actionable hints for security issues."""
        hints = []
        for finding in security.get("secrets_findings", []):
            hints.append({
                "file": finding["file"],
                "issue": "Potential secret/credential detected",
                "pattern": finding["pattern"],
                "suggested_actions": [
                    "Review file to confirm if this is a real credential",
                    "If real: move to environment variables or secure vault",
                    "If false positive: add exception to audit config",
                    "Consider adding file to .gitignore if contains secrets"
                ],
                "priority": "critical"
            })
        for finding in security.get("attack_surface_findings", []):
            description = finding["issue"]
            hints.append({
                "file": finding["file"],
                "issue": description,
                "line": finding.get("line"),
                "suggested_actions": [
                    finding.get("recommendation", "Review implementation for hardening opportunities"),
                    "Assess user-provided inputs for sanitization",
                    "Document mitigation or refactor to safer alternative"
                ],
                "priority": "high"
            })
        for alert in security.get("dependency_alerts", []):
            hints.append({
                "file": alert["file"],
                "issue": alert["issue"],
                "suggested_actions": [
                    alert.get("recommendation", "Review dependency security posture"),
                    "Pin versions to known-good releases",
                    "Schedule dependency vulnerability scans (pip-audit, osv-scanner)"
                ],
                "priority": "medium"
            })
        return hints

    def _build_efficiency_remediation_hints(self, efficiency: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build actionable hints for efficiency issues."""
        hints = []
        for suggestion in efficiency.get("suggestions", []):
            if "wizard implementations" in suggestion:
                hints.append({
                    "issue": "Multiple wizard implementations detected",
                    "suggestion": suggestion,
                    "suggested_actions": [
                        "Identify the canonical wizard (likely codesentinel/gui_wizard_v2.py)",
                        "Verify other wizards are truly redundant (not different use cases)",
                        "Move deprecated wizards to quarantine_legacy_archive/",
                        "Update any references to point to canonical implementation"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            elif "__pycache__" in suggestion:
                hints.append({
                    "issue": "__pycache__ in root directory",
                    "suggestion": suggestion,
                    "suggested_actions": [
                        "Add __pycache__/ to .gitignore",
                        "Remove from git: git rm -r --cached __pycache__/",
                        "Delete directory: rm -rf __pycache__/"
                    ],
                    "priority": "low",
                    "safe_to_automate": True
                })
            elif "Large files" in suggestion:
                hints.append({
                    "issue": "Large files detected",
                    "suggestion": suggestion,
                    "suggested_actions": [
                        "Review large files to determine if they belong in repo",
                        "Consider Git LFS for large binary files",
                        "Move test data/assets to separate location",
                        "Add large files to .gitignore if not needed"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            else:
                hints.append({
                    "issue": "General efficiency concern",
                    "suggestion": suggestion,
                    "suggested_actions": ["Review and determine appropriate action"],
                    "priority": "low",
                    "agent_decision_required": True
                })
        return hints

    def _build_minimalism_remediation_hints(self, minimalism: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build actionable hints for minimalism violations."""
        hints = []
        for violation in minimalism.get("violations", []):
            if "Orphaned test files" in violation:
                hints.append({
                    "issue": "Test files in wrong location",
                    "violation": violation,
                    "suggested_actions": [
                        "Move test_*.py files from root to tests/ directory",
                        "Update any references or imports",
                        "Verify tests still run after move: pytest tests/"
                    ],
                    "priority": "high",
                    "safe_to_automate": True
                })
            elif "Duplicate launcher files" in violation:
                hints.append({
                    "issue": "Duplicate launcher implementations",
                    "violation": violation,
                    "suggested_actions": [
                        "Identify canonical launcher (codesentinel/launcher.py for package)",
                        "Verify launch.py is only used as root entry point",
                        "If truly duplicate: archive one to quarantine_legacy_archive/",
                        "Update references and entry points"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            elif "Redundant packaging" in violation:
                hints.append({
                    "issue": "Both setup.py and pyproject.toml present",
                    "violation": violation,
                    "suggested_actions": [
                        "Modern Python uses pyproject.toml only (PEP 517/518)",
                        "Verify all setup.py config is in pyproject.toml",
                        "Archive setup.py to quarantine_legacy_archive/",
                        "Test installation still works: pip install -e ."
                    ],
                    "priority": "high",
                    "agent_decision_required": True,
                    "note": "This may be causing console script generation issues"
                })
            elif "Incomplete src/codesentinel/" in violation:
                hints.append({
                    "issue": "Abandoned src/ directory structure",
                    "violation": violation,
                    "suggested_actions": [
                        "Review src/codesentinel/ contents",
                        "If truly abandoned: archive to quarantine_legacy_archive/",
                        "If needed: integrate into main codesentinel/ package",
                        "Update imports and references"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            elif "Legacy archive directory" in violation:
                hints.append({
                    "issue": "Legacy archive taking up space",
                    "violation": violation,
                    "suggested_actions": [
                        "Verify all needed features have been ported",
                        "Consider creating archive tarball: tar -czf legacy_v0.tar.gz quarantine_legacy_archive/",
                        "Move tarball to docs/ or external storage",
                        "Remove directory after verification period"
                    ],
                    "priority": "low",
                    "agent_decision_required": True,
                    "note": "Keep until v2 feature parity confirmed"
                })
            elif "Too many installers" in violation:
                hints.append({
                    "issue": "Multiple installer scripts",
                    "violation": violation,
                    "suggested_actions": [
                        "Identify canonical installer for the project",
                        "Archive redundant installers",
                        "Update documentation to reference single installer"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            else:
                hints.append({
                    "issue": "Minimalism violation",
                    "violation": violation,
                    "suggested_actions": ["Review and determine appropriate action"],
                    "priority": "medium",
                    "agent_decision_required": True
                })
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
            self.alert_manager.send_alert(title=title, message=message, severity=severity)
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
            skip_dirs = {".git", "__pycache__", ".venv", "venv", "dist", "build", "node_modules"}
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
            re.compile(r"aws_?(access|secret)[_\- ]?key\s*[:=]\s*['\"][A-Za-z0-9/+=]{16,}['\"]", re.I),
            re.compile(r"(?i)secret\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
            re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
            re.compile(r"-----BEGIN (RSA|DSA|EC) PRIVATE KEY-----"),
        ]
        findings: List[Dict[str, Any]] = []
        verified_false_positives: List[Dict[str, Any]] = []
        max_hits = 25 if not limit_scan else 8

        scanned = 0
        for dirpath, dirnames, filenames in os.walk(root):
            skip_dirs = {".git", "__pycache__", ".venv", "venv", "dist", "build", "node_modules", "quarantine_legacy_archive"}
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]

            for fname in filenames:
                # Only scan text-like files
                if not any(fname.endswith(ext) for ext in (".py", ".json", ".md", ".yml", ".yaml", ".ini", ".txt")):
                    continue
                p = Path(dirpath) / fname
                try:
                    content = p.read_text(errors="ignore")
                except Exception:
                    continue

                for pat in secrets_patterns:
                    if pat.search(content):
                        finding = {
                            "file": str(p.relative_to(root)),
                            "pattern": pat.pattern[:40] + ("..." if len(pat.pattern) > 40 else ""),
                        }
                        
                        # Verify if this is a false positive
                        fp_result = self._verify_false_positive_security(p, content, pat)
                        if fp_result["is_false_positive"]:
                            verified_false_positives.append({
                                **finding,
                                "verified_false_positive": True,
                                "reason": fp_result["reason"]
                            })
                        else:
                            findings.append(finding)
                        
                        if len(findings) + len(verified_false_positives) >= max_hits:
                            break
                if len(findings) + len(verified_false_positives) >= max_hits:
                    break

            scanned += 1
            if len(findings) + len(verified_false_positives) >= max_hits:
                break

        attack_surface_findings = self._scan_attack_surfaces(root, limit_scan)
        dependency_alerts = self._analyze_dependency_security(root)

        return {
            "secrets_findings": findings,
            "verified_false_positives": verified_false_positives,
            "attack_surface_findings": attack_surface_findings,
            "dependency_alerts": dependency_alerts,
            "issues": len(findings) + len(attack_surface_findings) + len(dependency_alerts),
        }

    def _verify_false_positive_security(self, file_path: Path, content: str, pattern: re.Pattern) -> Dict[str, Any]:
        """
        Verify if a security finding is a false positive through contextual analysis.
        Does NOT whitelist - still reports the finding but marks it as verified FP.
        """
        file_name = file_path.name
        rel_path = str(file_path)
        
        # Check for documentation/example contexts
        if file_name in ("SECURITY.md", "README.md", "CONTRIBUTING.md", "EXAMPLE.md"):
            # Look for documentation indicators around matches
            doc_indicators = [
                r"example[:\s]",
                r"for example",
                r"sample",
                r"placeholder",
                r"demo",
                r"illustration",
                r"```",  # code blocks
                r"#\s*Example",
                r">\s*",  # markdown quotes
            ]
            for indicator in doc_indicators:
                if re.search(indicator, content, re.IGNORECASE):
                    return {
                        "is_false_positive": True,
                        "reason": f"Documentation file ({file_name}) with example/demo context"
                    }
        
        # Check for GUI wizard placeholder/demo password fields
        if "gui_wizard" in rel_path or "setup_wizard" in rel_path:
            # Look for GUI context - Entry widgets, placeholder text, validation
            gui_indicators = [
                r"Entry\s*\(",
                r"placeholder",
                r"Label\s*\(",
                r"\.insert\s*\(",
                r"show\s*=\s*['\"][\*\•]",  # password masking
                r"entry\.get\(\)",
                r"validate",
                r"# Example:",
                r"# Demo",
            ]
            match = pattern.search(content)
            if match:
                # Get context around the match (500 chars before/after)
                start = max(0, match.start() - 500)
                end = min(len(content), match.end() + 500)
                context = content[start:end]
                
                for indicator in gui_indicators:
                    if re.search(indicator, context):
                        return {
                            "is_false_positive": True,
                            "reason": f"GUI wizard file with placeholder/demo password field context"
                        }
        
        # Not a verified false positive
        return {"is_false_positive": False, "reason": None}

    def _scan_attack_surfaces(self, root: Path, limit_scan: bool) -> List[Dict[str, Any]]:
        """Scan repository for potential attack surface indicators."""
        findings: List[Dict[str, Any]] = []
        max_files = 160 if not limit_scan else 60
        max_findings = 50 if not limit_scan else 15

        high_risk_patterns: List[Tuple[re.Pattern, str, str]] = [
            (re.compile(r"subprocess\.(run|Popen)\([^)]*shell\s*=\s*True", re.IGNORECASE),
             "Subprocess shell execution detected",
             "Avoid shell=True to reduce command injection risk"),
            (re.compile(r"os\.system\(", re.IGNORECASE),
             "os.system usage detected",
             "Replace with subprocess.run without shell or dedicated APIs"),
            (re.compile(r"eval\(", re.IGNORECASE),
             "eval usage detected",
             "Avoid eval; use safer parsing or explicit dispatch"),
            (re.compile(r"exec\(", re.IGNORECASE),
             "exec usage detected",
             "exec executes arbitrary code; review necessity"),
            (re.compile(r"requests\.(get|post|put|delete|patch|head)\(\s*['\"]http://", re.IGNORECASE),
             "HTTP request without TLS",
             "Prefer HTTPS endpoints or explicitly document non-TLS usage"),
            (re.compile(r"pickle\.(load|loads)\(", re.IGNORECASE),
             "Insecure pickle deserialization",
             "Validate sources or switch to safer serialization (json, msgpack)"),
            (re.compile(r"yaml\.load\(", re.IGNORECASE),
             "yaml.load without SafeLoader",
             "Use yaml.safe_load to prevent arbitrary object construction"),
            (re.compile(r"tempfile\.mktemp\(", re.IGNORECASE),
             "Insecure temporary file pattern",
             "Use NamedTemporaryFile or mkstemp for safer temp files"),
        ]

        files_scanned = 0
        for py_file in root.rglob("*.py"):
            if files_scanned >= max_files:
                break
            if any(skip in py_file.parts for skip in [".venv", "venv", "__pycache__", "build", "dist", "quarantine_legacy_archive", "test_install_env", "quarantine"]):
                continue

            try:
                content = py_file.read_text(errors="ignore")
            except Exception:
                continue

            files_scanned += 1
            for pattern, issue, recommendation in high_risk_patterns:
                for match in pattern.finditer(content):
                    line_no = content.count("\n", 0, match.start()) + 1
                    findings.append({
                        "file": str(py_file.relative_to(root)),
                        "line": line_no,
                        "issue": issue,
                        "recommendation": recommendation,
                    })
                    if len(findings) >= max_findings:
                        return findings

        return findings

    def _analyze_dependency_security(self, root: Path) -> List[Dict[str, Any]]:
        """Analyze dependency definitions for potential security risks."""
        alerts: List[Dict[str, Any]] = []
        requirement_files = ["requirements.txt", "requirements-dev.txt"]
        specifiers = {"==", "<=", ">=", "~=", "!=", "<", ">"}

        for req_name in requirement_files:
            req_path = root / req_name
            if not req_path.exists():
                continue

            unpinned: List[str] = []
            insecure_sources: List[str] = []
            try:
                for raw_line in req_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    lowered = line.lower()
                    if lowered.startswith("git+") and "http://" in lowered:
                        insecure_sources.append(line)
                    if not any(spec in line for spec in specifiers):
                        unpinned.append(line)
            except Exception:
                continue

            if unpinned or insecure_sources:
                alert: Dict[str, Any] = {
                    "file": str(req_path.relative_to(root)),
                    "issue": "Dependency hygiene warning",
                    "details": {},
                    "recommendation": "Pin versions and prefer secure sources (https or PyPI releases)",
                }
                if unpinned:
                    alert["details"]["unpinned"] = unpinned[:10]
                if insecure_sources:
                    alert["details"]["insecure_sources"] = insecure_sources[:10]
                alerts.append(alert)

        # Inspect pyproject dependencies for unpinned entries
        pyproject = root / "pyproject.toml"
        if pyproject.exists():
            try:
                content_bytes = pyproject.read_bytes()
                content_text = content_bytes.decode("utf-8", errors="ignore")
                if tomllib:
                    data = tomllib.loads(content_text)
                    project_block = data.get("project", {}) if isinstance(data, dict) else {}
                    dependency_sets: List[Tuple[str, List[Any]]] = []
                    deps = project_block.get("dependencies", []) if isinstance(project_block, dict) else []
                    if deps:
                        dependency_sets.append(("project.dependencies", deps))
                    opt_deps = project_block.get("optional-dependencies", {}) if isinstance(project_block, dict) else {}
                    if isinstance(opt_deps, dict):
                        for group, entries in opt_deps.items():
                            if entries:
                                dependency_sets.append((f"project.optional-dependencies.{group}", entries))

                    for section_name, entries in dependency_sets:
                        if not isinstance(entries, list):
                            continue
                        unpinned_entries: List[str] = []
                        insecure_entries: List[str] = []
                        for entry in entries:
                            if isinstance(entry, str):
                                lowered = entry.lower()
                                if lowered.startswith("git+") and "http://" in lowered:
                                    insecure_entries.append(entry)
                                if not any(spec in entry for spec in specifiers):
                                    unpinned_entries.append(entry)
                            elif isinstance(entry, dict):
                                name = entry.get("name")
                                version = entry.get("version", "")
                                if isinstance(name, str):
                                    lowered_name = name.lower()
                                    if lowered_name.startswith("git+") and "http://" in lowered_name:
                                        insecure_entries.append(name)
                                version_str = str(version) if version is not None else ""
                                if not version_str or not any(spec in version_str for spec in specifiers):
                                    display = f"{name or 'dependency'} ({version_str or 'unconstrained'})"
                                    unpinned_entries.append(display)

                        if unpinned_entries or insecure_entries:
                            alert_details: Dict[str, Any] = {}
                            if unpinned_entries:
                                alert_details["unpinned"] = unpinned_entries[:10]
                            if insecure_entries:
                                alert_details["insecure_sources"] = insecure_entries[:10]
                            alerts.append({
                                "file": "pyproject.toml",
                                "section": section_name,
                                "issue": "Unpinned dependencies in pyproject",
                                "details": alert_details,
                                "recommendation": "Provide version constraints or document rationale for floating dependencies",
                            })
                else:
                    for match in re.finditer(r"dependencies\s*=\s*\[(.*?)\]", content_text, re.DOTALL):
                        block = match.group(1)
                        entries = re.findall(r"\"([^\"\n]+)\"", block)
                        unpinned_entries = [entry for entry in entries if not any(spec in entry for spec in specifiers)]
                        if unpinned_entries:
                            alerts.append({
                                "file": "pyproject.toml",
                                "issue": "Unpinned dependencies in pyproject",
                                "details": {"unpinned": unpinned_entries[:10]},
                                "recommendation": "Provide version constraints or document rationale for floating dependencies",
                            })
                            break
            except Exception:
                pass

        return alerts

    def _efficiency_checks(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        suggestions: List[str] = []
        verified_false_positives: List[Dict[str, Any]] = []
        root = self.project_root
        
        # Repository size efficiency
        if metrics.get("scan_limited"):
            suggestions.append("Repository large; consider excluding artifacts from repo")
        
        if len(metrics.get("big_files", [])) > 0:
            suggestions.append("Large files detected; consider Git LFS or pruning")
        
        # Check for redundant wizard implementations
        wizard_files = []
        if (root / "setup_wizard.py").exists():
            wizard_files.append("setup_wizard.py")
        if (root / "codesentinel" / "gui_wizard_v2.py").exists():
            wizard_files.append("codesentinel/gui_wizard_v2.py")
        if (root / "src" / "codesentinel" / "ui" / "setup" / "wizard.py").exists():
            wizard_files.append("src/codesentinel/ui/setup/wizard.py")
        if len(wizard_files) > 1:
            suggestion = f"Multiple wizard implementations detected: {', '.join(wizard_files)} (consolidate to one)"
            fp_result = self._verify_false_positive_efficiency(root, "multiple_wizards", wizard_files)
            if fp_result["is_false_positive"]:
                verified_false_positives.append({
                    "suggestion": suggestion,
                    "reason": fp_result["reason"]
                })
            else:
                suggestions.append(suggestion)

        # Check for __pycache__ in root
        if (root / "__pycache__").exists():
            suggestions.append("__pycache__ in root directory (add to .gitignore and clean up)")

        # Check for duplicate implementations (core efficiency concern)
        self._check_duplicate_implementations(root, suggestions, verified_false_positives)
        
        # Check for unused imports and dead code indicators
        self._check_code_efficiency(root, suggestions, metrics)
        
        # Check for performance anti-patterns
        self._check_performance_patterns(root, suggestions, metrics)
        
        # Check for import optimization opportunities
        self._check_import_efficiency(root, suggestions, verified_false_positives)

        return {
            "suggestions": suggestions,
            "verified_false_positives": verified_false_positives,
            "issues": len(suggestions),
        }

    def _check_duplicate_implementations(self, root: Path, suggestions: List[str], verified_fps: List[Dict[str, Any]]) -> None:
        """Check for duplicate/redundant code implementations."""
        # Check for duplicate launcher files
        launchers = []
        if (root / "launcher.py").exists():
            launchers.append("launcher.py")
        if (root / "codesentinel" / "launcher.py").exists():
            launchers.append("codesentinel/launcher.py")
        if (root / "codesentinel" / "gui_launcher.py").exists():
            launchers.append("codesentinel/gui_launcher.py")
        
        if len(launchers) > 1:
            # Verify if these serve different purposes
            try:
                purposes_differ = False
                if "launcher.py" in launchers and "gui_launcher.py" in launchers:
                    # CLI vs GUI launchers - different purposes
                    purposes_differ = True
                
                if purposes_differ:
                    verified_fps.append({
                        "suggestion": f"Multiple launcher files: {', '.join(launchers)}",
                        "reason": "Different launcher types serve distinct purposes (CLI vs GUI)"
                    })
                else:
                    suggestions.append(f"Duplicate launcher implementations: {', '.join(launchers)} (consolidate)")
            except Exception:
                suggestions.append(f"Multiple launcher files detected: {', '.join(launchers)}")
        
        # Check for duplicate config/setup files
        config_files = []
        for name in ["config.py", "configuration.py", "settings.py"]:
            if (root / name).exists():
                config_files.append(name)
            if (root / "codesentinel" / name).exists():
                config_files.append(f"codesentinel/{name}")
        
        if len(config_files) > 1:
            suggestions.append(f"Multiple config implementations: {', '.join(config_files)} (consolidate)")

    def _check_code_efficiency(self, root: Path, suggestions: List[str], metrics: Dict[str, Any]) -> None:
        """Check for code efficiency issues."""
        # Look for common inefficiency patterns in Python files
        py_files_checked = 0
        max_check = 50
        
        long_functions = []
        complex_files = []
        
        for py_file in root.rglob("*.py"):
            if any(skip in py_file.parts for skip in [".venv", "venv", "__pycache__", "quarantine_legacy_archive"]):
                continue
            
            if py_files_checked >= max_check:
                break
            
            try:
                content = py_file.read_text(errors="ignore")
                lines = content.split('\n')
                
                # Check for very long functions (> 150 lines)
                in_function = False
                func_start = 0
                func_name = ""
                for i, line in enumerate(lines):
                    if re.match(r'^\s*def\s+\w+', line):
                        if in_function and (i - func_start > 150):
                            long_functions.append(f"{py_file.relative_to(root)}:{func_name} ({i - func_start} lines)")
                        in_function = True
                        func_start = i
                        match = re.search(r'def\s+(\w+)', line)
                        func_name = match.group(1) if match else "unknown"
                    elif in_function and re.match(r'^\S', line) and line.strip() and not line.strip().startswith('#'):
                        in_function = False
                
                # Check for files with high complexity indicators
                if len(lines) > 500:
                    # Count nested blocks
                    max_indent = max((len(line) - len(line.lstrip())) // 4 for line in lines if line.strip())
                    if max_indent > 5:
                        complex_files.append(f"{py_file.relative_to(root)} ({len(lines)} lines, nesting: {max_indent})")
                
                py_files_checked += 1
            except Exception:
                continue
        
        if long_functions:
            suggestions.append(f"Long functions detected (consider refactoring): {', '.join(long_functions[:3])}")
        
        if complex_files:
            suggestions.append(f"High complexity files detected: {', '.join(complex_files[:3])}")

    def _check_performance_patterns(self, root: Path, suggestions: List[str], metrics: Dict[str, Any]) -> None:
        """Check for performance anti-patterns."""
        # Check for synchronous code in async contexts, blocking I/O, etc.
        perf_issues = []
        
        for py_file in list(root.rglob("*.py"))[:30]:  # Sample first 30 files
            if any(skip in py_file.parts for skip in [".venv", "venv", "__pycache__", "quarantine_legacy_archive"]):
                continue
            
            try:
                content = py_file.read_text(errors="ignore")
                
                # Check for N+1 query patterns in loops
                if re.search(r'for\s+\w+\s+in\s+.*:\s*\n\s+.*\.(get|query|fetch|read)\(', content):
                    perf_issues.append(f"{py_file.relative_to(root)}: Potential N+1 pattern")
                
                # Check for inefficient string concatenation in loops
                if re.search(r'for\s+.*:\s*\n\s+\w+\s*\+=\s*["\']', content):
                    perf_issues.append(f"{py_file.relative_to(root)}: String concatenation in loop")
                
            except Exception:
                continue
        
        if perf_issues:
            suggestions.append(f"Performance patterns to review: {', '.join(perf_issues[:2])}")

    def _check_import_efficiency(self, root: Path, suggestions: List[str], verified_fps: List[Dict[str, Any]]) -> None:
        """Check for import efficiency issues."""
        # Check for circular import risks
        import_graph: Dict[str, List[str]] = {}
        
        for py_file in list(root.rglob("*.py"))[:50]:
            if any(skip in py_file.parts for skip in [".venv", "venv", "__pycache__", "quarantine_legacy_archive"]):
                continue
            
            try:
                content = py_file.read_text(errors="ignore")
                imports = re.findall(r'from\s+([\w.]+)\s+import', content)
                imports.extend(re.findall(r'import\s+([\w.]+)', content))
                
                module_name = str(py_file.relative_to(root)).replace('\\', '.').replace('/', '.').replace('.py', '')
                import_graph[module_name] = imports
            except Exception:
                continue
        
        # Basic circular dependency detection
        circular_risks = []
        for module, imports in list(import_graph.items())[:20]:
            for imp in imports:
                if imp in import_graph and module.split('.')[0] in str(import_graph.get(imp, [])):
                    circular_risks.append(f"{module} <-> {imp}")
        
        if circular_risks:
            suggestions.append(f"Potential circular import risks: {', '.join(circular_risks[:2])}")

    def _verify_false_positive_efficiency(self, root: Path, check_type: str, context: Any = None) -> Dict[str, Any]:
        """
        Verify if an efficiency suggestion is a false positive through contextual analysis.
        Does NOT whitelist - still reports the finding but marks it as verified FP.
        """
        if check_type == "multiple_wizards" and context:
            wizard_files = context
            # Check if wizards serve different purposes (CLI vs GUI)
            has_cli_wizard = any("setup_wizard" in f for f in wizard_files)
            has_gui_wizard = any("gui_wizard" in f for f in wizard_files)
            
            if has_cli_wizard and has_gui_wizard:
                return {
                    "is_false_positive": True,
                    "reason": "Separate CLI and GUI wizards serve different user interaction patterns"
                }
        
        return {"is_false_positive": False, "reason": None}

    def _minimalism_checks(self, root: Path, metrics: Dict[str, Any]) -> Dict[str, Any]:
        violations: List[str] = []
        verified_false_positives: List[Dict[str, Any]] = []
        
        # Check for duplicate installers (defensive)
        installer_names = {"install.py", "install_deps.py", "setup_wizard.py", "install_codesentinel.py"}
        present_installers = []
        for name in installer_names:
            if (root / name).exists():
                present_installers.append(name)
        if len(present_installers) > 2:
            violations.append(f"Too many installers present: {', '.join(present_installers)}")

        # Check for orphaned test files in root (should be in tests/)
        orphaned_tests = []
        for item in root.iterdir():
            if item.is_file() and item.name.startswith("test_") and item.suffix == ".py":
                orphaned_tests.append(item.name)
        if orphaned_tests:
            violations.append(f"Orphaned test files in root (move to tests/): {', '.join(orphaned_tests)}")

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
            violation = "Redundant packaging: both setup.py and pyproject.toml (prefer pyproject.toml only)"
            fp_result = self._verify_false_positive_minimalism(root, "redundant_packaging")
            if fp_result["is_false_positive"]:
                verified_false_positives.append({
                    "violation": violation,
                    "reason": fp_result["reason"]
                })
            else:
                violations.append(violation)

        # Check for incomplete/abandoned directories
        src_dir = root / "src"
        if src_dir.exists():
            # Check if src/ contains incomplete/abandoned code
            src_codesentinel = src_dir / "codesentinel"
            if src_codesentinel.exists():
                violations.append("Incomplete src/codesentinel/ directory detected (may contain abandoned code)")

        # Check for legacy quarantine directories
        if (root / "quarantine").exists():
            violations.append("Legacy quarantine directory present; archive recommended")
        if (root / "quarantine_legacy_archive").exists():
            violations.append("Legacy archive directory still present (cleanup recommended after verification)")

        return {
            "violations": violations,
            "verified_false_positives": verified_false_positives,
            "issues": len(violations),
        }

    def _verify_false_positive_minimalism(self, root: Path, check_type: str) -> Dict[str, Any]:
        """
        Verify if a minimalism violation is a false positive through contextual analysis.
        Does NOT whitelist - still reports the finding but marks it as verified FP.
        """
        if check_type == "redundant_packaging":
            setup_py = root / "setup.py"
            pyproject_toml = root / "pyproject.toml"
            
            if not setup_py.exists() or not pyproject_toml.exists():
                return {"is_false_positive": False, "reason": None}
            
            try:
                setup_content = setup_py.read_text(errors="ignore")
                pyproject_content = pyproject_toml.read_text(errors="ignore")
                
                # Modern Python packaging best practice: pyproject.toml is primary,
                # but setup.py can be kept for backward compatibility with:
                # - pip < 19.0
                # - older build tools
                # - editable installs in some environments
                
                # Check if pyproject.toml has complete PEP 517/518 build system
                has_build_system = "[build-system]" in pyproject_content
                has_project_section = "[project]" in pyproject_content
                uses_setuptools_backend = "setuptools.build_meta" in pyproject_content
                
                # If pyproject.toml is complete and uses setuptools backend,
                # having setup.py is intentional for compatibility
                if has_build_system and has_project_section and uses_setuptools_backend:
                    return {
                        "is_false_positive": True,
                        "reason": "Valid dual-config: pyproject.toml (PEP 517/518) primary with setup.py for backward compatibility"
                    }
            except Exception:
                pass
        
        return {"is_false_positive": False, "reason": None}

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
    def _summarize(self, security: Dict[str, Any], efficiency: Dict[str, Any], minimalism: Dict[str, Any], style: Dict[str, Any]) -> Dict[str, Any]:
        total_issues = security.get("issues", 0) + efficiency.get("issues", 0) + minimalism.get("issues", 0)
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
        print("Policy: non_destructive=%s, feature_preservation=%s" % (
            str(results.get('policy', {}).get('non_destructive', True)),
            str(results.get('policy', {}).get('feature_preservation', True))
        ))
        
        print("\nSecurity Findings:")
        for f in results["security"]["secrets_findings"][:5]:
            print(f"  - {f['file']} (pattern: {f['pattern']})")
        if not results["security"]["secrets_findings"]:
            print("  - No obvious secrets detected")
        
        # Report verified false positives separately
        verified_fps = results["security"].get("verified_false_positives", [])
        if verified_fps:
            print("\nSecurity - Verified False Positives:")
            for fp in verified_fps[:5]:
                print(f"  ✓ {fp['file']} (pattern: {fp['pattern']})")
                print(f"    Reason: {fp['reason']}")

        attack_findings = results["security"].get("attack_surface_findings", [])
        if attack_findings:
            print("\nSecurity - Attack Surface Findings:")
            for finding in attack_findings[:5]:
                location = f"{finding['file']}:{finding.get('line', '?')}"
                print(f"  ! {location} - {finding['issue']}")
                print(f"    Recommendation: {finding['recommendation']}")

        dependency_alerts = results["security"].get("dependency_alerts", [])
        if dependency_alerts:
            print("\nSecurity - Dependency Alerts:")
            for alert in dependency_alerts[:5]:
                print(f"  ! {alert['file']} - {alert['issue']}")
                details = alert.get("details", {})
                for key, values in details.items():
                    if values:
                        preview = ", ".join(values[:3])
                        remainder = len(values) - 3
                        extra = f" (+{remainder} more)" if remainder > 0 else ""
                        print(f"    {key}: {preview}{extra}")
                print(f"    Recommendation: {alert['recommendation']}")
        
        print("\nEfficiency Suggestions:")
        for s in results["efficiency"]["suggestions"]:
            print(f"  - {s}")
        if not results["efficiency"]["suggestions"]:
            print("  - No suggestions")
        
        # Report verified false positives for efficiency
        eff_fps = results["efficiency"].get("verified_false_positives", [])
        if eff_fps:
            print("\nEfficiency - Verified False Positives:")
            for fp in eff_fps:
                print(f"  ✓ {fp['suggestion']}")
                print(f"    Reason: {fp['reason']}")
        
        print("\nMinimalism Violations:")
        for v in results["minimalism"]["violations"]:
            print(f"  - {v}")
        if not results["minimalism"]["violations"]:
            print("  - None detected")
        
        # Report verified false positives for minimalism
        min_fps = results["minimalism"].get("verified_false_positives", [])
        if min_fps:
            print("\nMinimalism - Verified False Positives:")
            for fp in min_fps:
                print(f"  ✓ {fp['violation']}")
                print(f"    Reason: {fp['reason']}")
        
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
