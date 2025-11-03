#!/usr/bin/env python3
"""
UNC Dependency Update Suggester
===============================

SECURITY > EFFICIENCY > MINIMALISM

Analyzes current dependencies and suggests updates for security and performance.
Integrates with the maintenance workflow to provide actionable update recommendations.

Usage: python tools/monitoring/dependency_suggester.py
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class DependencySuggester:
    """Analyzes and suggests dependency updates."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.pyproject_file = repo_root / "pyproject.toml"
        self.requirements_file = repo_root / "requirements.txt"
        self.venv_dir = self._find_venv_dir()

    def _find_venv_dir(self) -> Optional[Path]:
        """Find the active virtual environment directory."""
        # Check common venv locations
        candidates = [
            self.repo_root / ".venv",
            self.repo_root / ".venv_py314",
            self.repo_root / ".venv_313",
            self.repo_root / "venv"
        ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate

        return None

    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze current dependencies and suggest updates."""
        results = {
            "timestamp": "2024-12-01T00:00:00",  # Will be set by caller
            "python_packages": {},
            "security_updates": [],
            "performance_updates": [],
            "deprecated_packages": [],
            "recommendations": []
        }

        # Analyze Python dependencies
        if self.pyproject_file.exists():
            pyproject_analysis = self._analyze_pyproject()
            results["python_packages"].update(pyproject_analysis)

        if self.requirements_file.exists():
            req_analysis = self._analyze_requirements()
            results["python_packages"].update(req_analysis)

        # Check for outdated packages
        outdated = self._check_outdated_packages()
        results["python_packages"].update(outdated)

        # Generate security recommendations
        security_recs = self._generate_security_recommendations(results["python_packages"])
        results["security_updates"] = security_recs

        # Generate performance recommendations
        perf_recs = self._generate_performance_recommendations(results["python_packages"])
        results["performance_updates"] = perf_recs

        # Check for deprecated packages
        deprecated = self._check_deprecated_packages(results["python_packages"])
        results["deprecated_packages"] = deprecated

        # Generate actionable recommendations
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _analyze_pyproject(self) -> Dict[str, Any]:
        """Analyze pyproject.toml dependencies."""
        packages = {}

        try:
            with open(self.pyproject_file, 'r') as f:
                content = f.read()

            # Extract dependencies from [tool.poetry.dependencies] or [project.dependencies]
            dep_patterns = [
                r'\[tool\.poetry\.dependencies\](.*?)(?=\[|$)',
                r'\[project\.dependencies\](.*?)(?=\[|$)'
            ]

            for pattern in dep_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    deps_section = match.group(1)
                    # Extract package specifications
                    pkg_pattern = r'(\w[\w\-]*)\s*=\s*["\']([^"\']+)["\']'
                    for pkg_match in re.finditer(pkg_pattern, deps_section):
                        name, version = pkg_match.groups()
                        packages[name.lower()] = {
                            "current": version,
                            "source": "pyproject.toml",
                            "type": "python"
                        }

        except Exception as e:
            print(f"Warning: Failed to analyze pyproject.toml: {e}")

        return packages

    def _analyze_requirements(self) -> Dict[str, Any]:
        """Analyze requirements.txt dependencies."""
        packages = {}

        try:
            with open(self.requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package==version format
                        if '==' in line:
                            name, version = line.split('==', 1)
                            packages[name.lower()] = {
                                "current": version,
                                "source": "requirements.txt",
                                "type": "python"
                            }
                        else:
                            # Package without version specification
                            packages[line.lower()] = {
                                "current": "unspecified",
                                "source": "requirements.txt",
                                "type": "python"
                            }

        except Exception as e:
            print(f"Warning: Failed to analyze requirements.txt: {e}")

        return packages

    def _check_outdated_packages(self) -> Dict[str, Any]:
        """Check for outdated packages using pip."""
        outdated_info = {}

        try:
            # Run pip list --outdated
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode == 0:
                outdated_packages = json.loads(result.stdout)
                for pkg in outdated_packages:
                    name = pkg["name"].lower()
                    outdated_info[name] = {
                        "current": pkg["version"],
                        "latest": pkg["latest_version"],
                        "outdated": True,
                        "type": "python"
                    }

        except Exception as e:
            print(f"Warning: Failed to check outdated packages: {e}")

        return outdated_info

    def _generate_security_recommendations(self, packages: Dict) -> List[Dict]:
        """Generate security update recommendations."""
        recommendations = []

        # Known security issues (this would be expanded with a real vulnerability database)
        security_concerns = {
            "requests": {"max_safe": "2.25.1", "issue": "CVE-2023-XXXX"},
            "urllib3": {"max_safe": "1.26.0", "issue": "CVE-2023-XXXX"},
            "cryptography": {"min_safe": "3.4.0", "issue": "Legacy algorithm support"}
        }

        for name, info in packages.items():
            if name in security_concerns:
                concern = security_concerns[name]
                current = info.get("current", "")

                if "max_safe" in concern and current and current <= concern["max_safe"]:
                    recommendations.append({
                        "package": name,
                        "current_version": current,
                        "issue": concern["issue"],
                        "recommendation": f"Update to version > {concern['max_safe']}",
                        "severity": "HIGH"
                    })
                elif "min_safe" in concern and current and current < concern["min_safe"]:
                    recommendations.append({
                        "package": name,
                        "current_version": current,
                        "issue": concern["issue"],
                        "recommendation": f"Update to version >= {concern['min_safe']}",
                        "severity": "MEDIUM"
                    })

        return recommendations

    def _generate_performance_recommendations(self, packages: Dict) -> List[Dict]:
        """Generate performance update recommendations."""
        recommendations = []

        # Performance improvement suggestions
        perf_suggestions = {
            "pandas": {"min_recommended": "1.5.0", "benefit": "Improved performance with PyArrow"},
            "numpy": {"min_recommended": "1.24.0", "benefit": "Better memory efficiency"},
            "scikit-learn": {"min_recommended": "1.3.0", "benefit": "Faster training algorithms"}
        }

        for name, info in packages.items():
            if name in perf_suggestions:
                suggestion = perf_suggestions[name]
                current = info.get("current", "")

                if current and current < suggestion["min_recommended"]:
                    recommendations.append({
                        "package": name,
                        "current_version": current,
                        "recommended_version": f">= {suggestion['min_recommended']}",
                        "benefit": suggestion["benefit"],
                        "impact": "MEDIUM"
                    })

        return recommendations

    def _check_deprecated_packages(self, packages: Dict) -> List[Dict]:
        """Check for deprecated packages."""
        deprecated = []

        # Known deprecated packages
        deprecated_packages = {
            "distutils": {"replacement": "setuptools", "reason": "Removed in Python 3.12"},
            "imp": {"replacement": "importlib", "reason": "Deprecated since Python 3.4"}
        }

        for name in packages:
            if name in deprecated_packages:
                dep_info = deprecated_packages[name]
                deprecated.append({
                    "package": name,
                    "replacement": dep_info["replacement"],
                    "reason": dep_info["reason"]
                })

        return deprecated

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Security recommendations
        if results["security_updates"]:
            recommendations.append("🔴 SECURITY: Update packages with known vulnerabilities immediately")
            for update in results["security_updates"]:
                recommendations.append(f"  - {update['package']}: {update['recommendation']}")

        # Performance recommendations
        if results["performance_updates"]:
            recommendations.append("🟡 PERFORMANCE: Consider updating for better performance")
            for update in results["performance_updates"]:
                recommendations.append(f"  - {update['package']}: {update['benefit']}")

        # Outdated packages
        outdated_count = sum(1 for pkg in results["python_packages"].values() if pkg.get("outdated"))
        if outdated_count > 0:
            recommendations.append(f"📦 DEPENDENCIES: {outdated_count} packages have newer versions available")
            recommendations.append("  Run 'pip list --outdated' for details")

        # Deprecated packages
        if results["deprecated_packages"]:
            recommendations.append("⚠️  DEPRECATED: Remove or replace deprecated packages")
            for dep in results["deprecated_packages"]:
                recommendations.append(f"  - {dep['package']} → {dep['replacement']}: {dep['reason']}")

        if not recommendations:
            recommendations.append("✅ All dependencies appear up to date")

        return recommendations


def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent.parent

    suggester = DependencySuggester(repo_root)
    results = suggester.analyze_dependencies()

    # Print results
    print("UNC Dependency Analysis Results")
    print("=" * 40)

    if results["security_updates"]:
        print(f"\n🔴 SECURITY UPDATES NEEDED ({len(results['security_updates'])})")
        for update in results["security_updates"]:
            print(f"  {update['package']} {update['current_version']} - {update['recommendation']}")

    if results["performance_updates"]:
        print(f"\n🟡 PERFORMANCE IMPROVEMENTS ({len(results['performance_updates'])})")
        for update in results["performance_updates"]:
            print(f"  {update['package']} {update['current_version']} - {update['benefit']}")

    if results["deprecated_packages"]:
        print(f"\n⚠️  DEPRECATED PACKAGES ({len(results['deprecated_packages'])})")
        for dep in results["deprecated_packages"]:
            print(f"  {dep['package']} - Replace with {dep['replacement']}")

    print("\n📋 RECOMMENDATIONS")
    for rec in results["recommendations"]:
        print(f"  {rec}")

    # Save detailed results
    output_file = repo_root / "tools" / "monitoring" / "dependency_analysis.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()