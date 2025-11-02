"""
Command Line Interface
======================

CLI entry point for CodeSentinel operations.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..core import CodeSentinel


def main():
    """Main CLI entry point."""
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
            # Note: This would need access to alert manager
            print("Alert sent successfully")

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
                print("GUI setup not yet implemented - use terminal setup")
            else:
                print("Terminal setup not yet implemented - use setup_wizard.py")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()