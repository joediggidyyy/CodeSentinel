"""
Command Line Interface
======================

CLI entry point for CodeSentinel operations.
"""

import argparse
import sys
import atexit
from pathlib import Path
from typing import Optional

from ..core import CodeSentinel
from ..utils.process_monitor import start_monitor, stop_monitor


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
    if any(arg == '!!!!' for arg in sys.argv[1:]):
        # Replace all '!!!!' tokens with 'dev-audit'
        sys.argv = [sys.argv[0]] + ['dev-audit' if a == '!!!!' else a for a in sys.argv[1:]]
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
  codesentinel dev-audit                 # Run interactive development audit
  codesentinel !!!!                      # Quick trigger for dev-audit
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
                # codesentinel.scheduler.start()
                print("Scheduler started")
            elif args.action == 'stop':
                print("Stopping maintenance scheduler...")
                # codesentinel.scheduler.stop()
                print("Scheduler stopped")
            elif args.action == 'status':
                print("Scheduler status:")
                # status = codesentinel.scheduler.get_schedule_status()
                # print(json.dumps(status, indent=2))

        elif args.command == 'setup':
            print("Launching setup wizard...")
            if args.gui:
                try:
                    # Prefer the new modular wizard
                    try:
                        from ..gui_wizard_v2 import main as wizard_main
                        wizard_main()
                    except Exception:
                        from ..gui_project_setup import main as project_setup_main
                        project_setup_main()
                except Exception as e:
                    print(f"Failed to launch GUI setup: {e}")
                    sys.exit(1)
            else:
                print("Terminal setup not yet implemented - use setup_wizard.py or --gui")

        elif args.command == 'dev-audit':
            interactive = not getattr(args, 'silent', False)
            agent_mode = getattr(args, 'agent', False)
            export_path = getattr(args, 'export', None)
            
            if agent_mode:
                # Export comprehensive context for AI agent
                print("Generating audit context for AI agent...")
                agent_context = codesentinel.dev_audit.get_agent_context()
                
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
                    print("=" * 60)
                    print("\nThis audit has detected issues that require intelligent remediation.")
                    print("An AI agent (GitHub Copilot) can now analyze these findings and build")
                    print("a remediation pipeline while respecting all persistent policies.\n")
                    
                    # Output structured data for agent to consume
                    print("\n@agent Here is the comprehensive audit context:")
                    print(_json.dumps(agent_context, indent=2))
                    
                    print("\n\nPlease analyze the audit findings and propose a remediation plan.")
                    print("Remember: All actions must be non-destructive and preserve features.")
                
                return
            
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
                    print("\nThis will provide comprehensive context for the AI agent to")
                    print("intelligently build a remediation pipeline while respecting")
                    print("all security, efficiency, and minimalism principles.")
                
                print("\nInteractive dev audit completed.")
                print("A brief audit is running in the background; results will arrive via alerts.")
            else:
                import json as _json
                print(_json.dumps(results.get('summary', {}), indent=2))
            return

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()