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
    if any(arg.startswith('!!!!') for arg in sys.argv[1:]):
        # Extract focus parameter if present
        focus_param = None
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg.startswith('!!!!'):
                if arg == '!!!!':
                    # Simple '!!!!' without focus
                    sys.argv[i] = 'dev-audit'
                else:
                    # '!!!!<space><focus>' format - extract focus
                    # This shouldn't happen as shell splits arguments
                    sys.argv[i] = 'dev-audit'
            elif i > 1 and sys.argv[i-1] == 'dev-audit' and not arg.startswith('-'):
                # First non-flag argument after dev-audit is focus
                focus_param = arg
                break
        
        # If we have a focus parameter, add it as --focus flag
        if focus_param:
            # Find position of dev-audit command
            dev_audit_idx = sys.argv.index('dev-audit')
            # Insert --focus flag after dev-audit
            sys.argv.insert(dev_audit_idx + 1, '--focus')
            sys.argv.insert(dev_audit_idx + 2, focus_param)
    parser = argparse.ArgumentParser(
        description="CodeSentinel - Automated Maintenance & Security Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog="""
Examples:
  codesentinel status                    # Show current status
  codesentinel scan                      # Run security scan
  codesentinel maintenance daily         # Run daily maintenance
  codesentinel alert "Test message"      # Send test alert
  codesentinel schedule start            # Start maintenance scheduler
  codesentinel schedule stop             # Stop maintenance scheduler
  codesentinel dev-audit                 # Run interactive development audit
  codesentinel !!!!                      # Quick trigger for dev-audit
  codesentinel !!!! scheduler            # Focus audit on scheduler subsystem
  codesentinel !!!! "new feature"        # Focus audit on new feature development
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

    # File integrity command
    integrity_parser = subparsers.add_parser('integrity', help='Manage file integrity validation')
    integrity_subparsers = integrity_parser.add_subparsers(dest='integrity_action', help='Integrity actions')
    
    # Generate baseline
    generate_parser = integrity_subparsers.add_parser('generate', help='Generate integrity baseline')
    generate_parser.add_argument(
        '--patterns', nargs='+', help='File patterns to include (default: all files)')
    generate_parser.add_argument(
        '--output', type=str, help='Output path for baseline file')
    
    # Verify integrity
    verify_parser = integrity_subparsers.add_parser('verify', help='Verify files against baseline')
    verify_parser.add_argument(
        '--baseline', type=str, help='Path to baseline file')
    
    # Update whitelist
    whitelist_parser = integrity_subparsers.add_parser('whitelist', help='Manage whitelist patterns')
    whitelist_parser.add_argument(
        'patterns', nargs='+', help='Glob patterns to add to whitelist')
    whitelist_parser.add_argument(
        '--replace', action='store_true', help='Replace existing whitelist')
    
    # Mark critical files
    critical_parser = integrity_subparsers.add_parser('critical', help='Mark files as critical')
    critical_parser.add_argument(
        'files', nargs='+', help='Files to mark as critical (relative paths)')
    critical_parser.add_argument(
        '--replace', action='store_true', help='Replace existing critical files list')

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
import sys
import time
from pathlib import Path

# Add CodeSentinel to path
sys.path.insert(0, r'{package_dir}')

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
3. Ensure all remediation respects SECURITY > EFFICIENCY > MINIMALISM
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
                    print("intelligently build a remediation pipeline while respecting")
                    print("all security, efficiency, and minimalism principles.")
                
                print("\nInteractive dev audit completed.")
                print("A brief audit is running in the background; results will arrive via alerts.")
            else:
                import json as _json
                print(_json.dumps(results.get('summary', {}), indent=2))
            return

        elif args.command == 'integrity':
            from ..utils.file_integrity import FileIntegrityValidator
            import json as _json
            
            # Load integrity config
            cfg = getattr(codesentinel.config, 'config', {}) or {}
            integrity_config = cfg.get("integrity", {})
            
            # Get workspace root
            workspace_root = Path.cwd()
            
            # Initialize validator
            validator = FileIntegrityValidator(workspace_root, integrity_config)
            
            if args.integrity_action == 'generate':
                print("Generating file integrity baseline (timeout: 30 seconds)...")
                
                # Set timeout to prevent indefinite hangs
                timeout_seconds = 30
                baseline = None
                error_message = None
                
                def generate_with_timeout():
                    nonlocal baseline, error_message
                    try:
                        baseline = validator.generate_baseline(patterns=args.patterns)
                    except Exception as e:
                        error_message = str(e)
                
                # Run generation in thread with timeout
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
                    print("  codesentinel integrity generate --patterns '**/*.py' '**/*.md'")
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
                print(f"\nEnable integrity checking in config to use during audits.")
                
            elif args.integrity_action == 'verify':
                print("Verifying file integrity...")
                if args.baseline:
                    validator.load_baseline(Path(args.baseline))
                
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
                    
                    print("\nRun 'codesentinel !!!! --agent' for AI-assisted remediation.")
                else:
                    print("\n✓ All files passed integrity check!")
                
            elif args.integrity_action == 'whitelist':
                print(f"Updating whitelist with {len(args.patterns)} pattern(s)...")
                validator.update_whitelist(args.patterns, replace=args.replace)
                
                # Save updated config (would need to persist this properly)
                print(f"Whitelist updated: {', '.join(args.patterns)}")
                print("Note: Update your config file to persist these changes.")
                
            elif args.integrity_action == 'critical':
                print(f"Marking {len(args.files)} file(s) as critical...")
                validator.update_critical_files(args.files, replace=args.replace)
                
                print(f"Critical files updated: {', '.join(args.files)}")
                print("Note: Update your config file to persist these changes.")
                
            else:
                integrity_parser.print_help()
            
            return

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()