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

        summary = self._summarize(security, efficiency, minimalism)

        return {
            "repository": repo_name,
            "root": str(prj),
            "detail_level": detail_level,
            "policy": self.policy,
            "metrics": metrics,
            "security": security,
            "efficiency": efficiency,
            "minimalism": minimalism,
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
                        findings.append({
                            "file": str(p.relative_to(root)),
                            "pattern": pat.pattern[:40] + ("..." if len(pat.pattern) > 40 else ""),
                        })
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
            suggestions.append("Repository large; consider excluding artifacts from repo")
        if len(metrics.get("big_files", [])) > 0:
            suggestions.append("Large files detected; consider Git LFS or pruning")
        return {
            "suggestions": suggestions,
            "issues": len(suggestions),
        }

    def _minimalism_checks(self, root: Path, metrics: Dict[str, Any]) -> Dict[str, Any]:
        violations: List[str] = []
        # Check for duplicate installers (defensive)
        installer_names = {"install.py", "install_deps.py", "setup_wizard.py", "install_codesentinel.py"}
        present_installers = []
        for name in installer_names:
            if (root / name).exists():
                present_installers.append(name)
        if len(present_installers) > 2:
            violations.append(f"Too many installers present: {', '.join(present_installers)}")

        # Check for legacy quarantine still present
        if (root / "quarantine").exists():
            violations.append("Legacy quarantine directory present; archive recommended")

        return {
            "violations": violations,
            "issues": len(violations),
        }

    # -------------------- Reporting --------------------
    def _summarize(self, security: Dict[str, Any], efficiency: Dict[str, Any], minimalism: Dict[str, Any]) -> Dict[str, Any]:
        total_issues = security.get("issues", 0) + efficiency.get("issues", 0) + minimalism.get("issues", 0)
        level = "info"
        if total_issues >= 8 or security.get("issues", 0) >= 5:
            level = "critical"
        elif total_issues >= 4 or security.get("issues", 0) >= 3:
            level = "warning"
        return {
            "total_issues": total_issues,
            "severity": level,
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
