"""
CodeSentinel Beta Testing Suite
===============================

Provides a command-line interface for managing isolated beta testing environments.
"""

import json
import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import argparse
import uuid


class BetaTestingManager:
    """Manages isolated beta testing environments for CodeSentinel."""

    def __init__(self, version: str, session_id: str | None = None):
        """
        Initialize the beta testing manager.

        Args:
            version: The version being tested (e.g., "v1.1.0-beta.1").
            session_id: Optional existing session ID to resume a previous session.
        """
        self.version = version
        self.workspace_root = Path(__file__).parent.parent.parent
        self.test_root = self.workspace_root / 'tests' / 'beta_testing' / self.version
        self.session_id = session_id or str(uuid.uuid4())
        self.iteration_count = 0
        self.tester_name = None
        self.python_executable = None
        self.wheel_file = None
        self.venv_path = None

        # Ensure directories exist
        self.env_dir = self.test_root / 'environment'
        self.logs_dir = self.test_root / 'logs'
        self.iterations_dir = self.test_root / 'iterations'
        self.consolidated_dir = self.test_root / 'consolidated'
        self.templates_dir = self.test_root / 'templates'
        self.sessions_dir = self.test_root / 'sessions'

        for d in [self.env_dir, self.logs_dir, self.iterations_dir, self.consolidated_dir, self.templates_dir, self.sessions_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def create_isolated_env(self, python_executable: str = 'python'):
        """
        Create an isolated virtual environment for testing.

        Args:
            python_executable: Path to the Python executable to use.
        """
        venv_path = self.env_dir / f"venv_{self.session_id}"
        print(f"Creating isolated environment at: {venv_path}")

        try:
            subprocess.run([python_executable, '-m', 'venv', str(venv_path)], check=True)
            print("Virtual environment created successfully.")
            return str(venv_path)
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            return None

    def install_beta_version(self, venv_path: str, wheel_path: str):
        """
        Install the beta version of CodeSentinel into the isolated environment.

        Args:
            venv_path: Path to the virtual environment.
            wheel_path: Path to the CodeSentinel wheel file.
        """
        if sys.platform == "win32":
            pip_executable = Path(venv_path) / 'Scripts' / 'pip.exe'
        else:
            pip_executable = Path(venv_path) / 'bin' / 'pip'

        print(f"Installing CodeSentinel from {wheel_path}...")
        try:
            subprocess.run([str(pip_executable), 'install', wheel_path], check=True)
            print("CodeSentinel installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing CodeSentinel: {e}")

    def start_test_iteration(self, tester_name: str):
        """
        Start a new test iteration.

        Returns:
            Path to the new iteration report.
        """
        self.iteration_count += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"iteration_{self.iteration_count}_{timestamp}.md"
        report_path = self.iterations_dir / report_filename

        template_path = self.templates_dir / 'iteration_report_template.md'
        if not template_path.exists():
            print(f"Error: Iteration report template not found at {template_path}")
            return None

        with open(template_path, 'r') as f:
            template = f.read()

        # Pre-fill some fields
        content = template.replace('{{ session_id }}', self.session_id)
        content = content.replace('{{ iteration_number }}', str(self.iteration_count))
        content = content.replace('{{ tester_name }}', tester_name)
        content = content.replace('{{ timestamp }}', datetime.now().isoformat())

        with open(report_path, 'w') as f:
            f.write(content)

        print(f"Started new test iteration. Report at: {report_path}")
        return str(report_path)

    def consolidate_reports(self, lead_tester: str):
        """
        Consolidate all iteration reports into a single report.
        """
        consolidated_report_path = self.consolidated_dir / f"consolidated_report_{self.session_id}.md"
        template_path = self.templates_dir / 'consolidated_report_template.md'

        if not template_path.exists():
            print(f"Error: Consolidated report template not found at {template_path}")
            return

        with open(template_path, 'r') as f:
            template = f.read()

        # Collect data from iteration reports
        iteration_reports = list(self.iterations_dir.glob('*.md'))
        iteration_summary = []
        for report in iteration_reports:
            # This is a simplified consolidation. A real implementation would parse the markdown.
            iteration_summary.append(f"- {report.name}")

        content = template.replace('{{ session_id }}', self.session_id)
        content = content.replace('{{ lead_tester }}', lead_tester)
        content = content.replace('{{ total_iterations }}', str(len(iteration_reports)))
        content = content.replace('{{ iteration_summary_table }}', "\n".join(iteration_summary))
        content = content.replace('{{ report_timestamp }}', datetime.now().isoformat())

        with open(consolidated_report_path, 'w') as f:
            f.write(content)

        print(f"Consolidated report created at: {consolidated_report_path}")

    def save_session_state(self, test_results: dict | None = None):
        """
        Save the current session state to enable resume capability.
        
        Args:
            test_results: Dictionary of test results (test_id -> {completed, failed, etc.})
        """
        session_file = self.sessions_dir / f"session_{self.session_id}.json"
        
        state = {
            'session_id': self.session_id,
            'version': self.version,
            'tester_name': self.tester_name,
            'python_executable': str(self.python_executable) if self.python_executable else None,
            'wheel_file': str(self.wheel_file) if self.wheel_file else None,
            'venv_path': str(self.venv_path) if self.venv_path else None,
            'iteration_count': self.iteration_count,
            'test_results': test_results or {},
            'last_updated': datetime.now().isoformat()
        }
        
        with open(session_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"✓ Session state saved: {session_file}")
        return session_file
    
    def load_session_state(self):
        """
        Load a previously saved session state.
        
        Returns:
            Dictionary containing session state, or None if not found.
        """
        session_file = self.sessions_dir / f"session_{self.session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                state = json.load(f)
            
            # Restore manager state
            self.tester_name = state.get('tester_name')
            self.python_executable = state.get('python_executable')
            self.wheel_file = state.get('wheel_file')
            self.venv_path = state.get('venv_path')
            self.iteration_count = state.get('iteration_count', 0)
            
            print(f"✓ Session state loaded from: {session_file}")
            return state
        except Exception as e:
            print(f"⚠️  Error loading session state: {e}")
            return None
    
    @staticmethod
    def find_active_sessions(version: str):
        """
        Find all active (saved) sessions for a given version.
        
        Args:
            version: Version to search for sessions.
            
        Returns:
            List of tuples: (session_id, session_file_path, last_updated)
        """
        workspace_root = Path(__file__).parent.parent.parent
        sessions_dir = workspace_root / 'tests' / 'beta_testing' / version / 'sessions'
        
        if not sessions_dir.exists():
            return []
        
        sessions = []
        for session_file in sessions_dir.glob('session_*.json'):
            try:
                with open(session_file, 'r') as f:
                    state = json.load(f)
                sessions.append((
                    state['session_id'],
                    session_file,
                    state.get('last_updated', 'Unknown')
                ))
            except Exception:
                continue
        
        return sessions

    def cleanup_session(self):
        """
        Clean up the testing environment for the current session.
        """
        venv_path = self.env_dir / f"venv_{self.session_id}"
        if venv_path.exists():
            print(f"Removing virtual environment: {venv_path}")
            shutil.rmtree(venv_path)

        # Optionally, archive iteration reports
        print("Archiving iteration reports...")
        for report in self.iterations_dir.glob('*.md'):
            # For now, we just print. A real implementation might move them.
            print(f"  - {report.name}")

        print("Test session cleanup complete.")


def main():
    """Main entry point for the beta testing suite."""
    parser = argparse.ArgumentParser(description='CodeSentinel Beta Testing Suite')
    parser.add_argument('action', choices=['create-env', 'install', 'start-iteration', 'consolidate', 'cleanup'],
                        help='Action to perform')
    parser.add_argument('--version', required=True, help='Version to test (e.g., "v1.1.0-beta.1")')
    parser.add_argument('--python', default='python', help='Python executable for venv creation')
    parser.add_argument('--wheel', help='Path to the CodeSentinel wheel file for installation')
    parser.add_argument('--tester', default='Anonymous', help='Name of the tester for iteration reports')
    parser.add_argument('--lead-tester', default='Anonymous', help='Name of the lead tester for consolidation')

    args = parser.parse_args()

    manager = BetaTestingManager(args.version)

    if args.action == 'create-env':
        manager.create_isolated_env(args.python)
    elif args.action == 'install':
        if not args.wheel:
            print("Error: --wheel parameter is required for install action.")
            sys.exit(1)
        # This assumes a session is active, a real CLI would manage session state
        venv_path = manager.env_dir / f"venv_{manager.session_id}"
        manager.install_beta_version(str(venv_path), args.wheel)
    elif args.action == 'start-iteration':
        manager.start_test_iteration(args.tester)
    elif args.action == 'consolidate':
        manager.consolidate_reports(args.lead_tester)
    elif args.action == 'cleanup':
        manager.cleanup_session()


if __name__ == '__main__':
    main()
