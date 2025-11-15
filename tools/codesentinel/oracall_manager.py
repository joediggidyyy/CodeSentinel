"""ORACall event scaffolding, SLA enforcement, and feed generation utilities."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from codesentinel.utils.alerts import AlertManager
from codesentinel.utils.config import ConfigManager
from codesentinel.utils.integrations import IncidentSyncAdapter, NullIncidentSyncAdapter
from codesentinel.utils.session_memory import SessionMemory

SEVERITY_WINDOWS = {
    'critical': {'analytic_hours': 2, 'action_hours': 4},
    'high': {'analytic_hours': 6, 'action_hours': 12},
    'medium': {'analytic_hours': 24, 'action_hours': 48},
    'low': {'analytic_hours': 72, 'action_hours': 120},
}

CACHE_EXPIRY_HOURS = {
    'critical': 24,
    'high': 72,
    'medium': 168,
    'low': 336,
}

SEVERITY_ORDER = ['low', 'medium', 'high', 'critical']

PLACEHOLDER_MANIFEST = Path('docs/planning/placeholder_manifest.json')

NAV_LINKS = [
    {
        'title': 'Placeholder Registry (PL-001–PL-006)',
        'path': Path('docs/planning/PLACEHOLDER_REGISTRY.md'),
        'description': 'Authoritative list of inactive scaffolding and activation criteria.'
    },
    {
        'title': 'ORACall Implementation Proposal',
        'path': Path('docs/planning/ORACALL_IMPLEMENTATION_PROPOSAL.md'),
        'description': 'Execution blueprint for scaffolding, SLA enforcement, and feeds.'
    },
    {
        'title': 'ORACall Investment & Equity Brief',
        'path': Path('docs/planning/ORACALL_INVESTMENT_EQUITY_BRIEF.md'),
        'description': 'Financial context and placeholder PL-006 owner actions.'
    },
    {
        'title': 'ORACall Checkpoint (Merge Ready)',
        'path': Path('docs/checkpoints/.checkpoint_oracl_integration_complete.md'),
        'description': 'Latest merge-ready snapshot tying all placeholders to validation steps.'
    },
    {
        'title': 'ORACall Templates README',
        'path': Path('docs/reports/README.md'),
        'description': 'Explains metadata headers, feed locations, and report flows.'
    },
    {
        'title': 'Placeholder Manifest (automation)',
        'path': Path('docs/planning/placeholder_manifest.json'),
        'description': 'Machine-readable placeholder metadata mirrored from the registry.'
    }
]


class OracallManager:
    """Coordinates ORACall scaffolding, SLA tracking, and feeds."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.logger = logging.getLogger('ORACallManager')
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[2]
        self.config_manager = ConfigManager(config_path=self.workspace_root / 'codesentinel.json')
        self.config_manager.load_config()
        self.alert_manager = AlertManager(self.config_manager)
        self.session_memory = SessionMemory(workspace_root=self.workspace_root)

        self.events_dir = self.workspace_root / 'docs' / 'reports' / 'oracall' / 'events'
        self.feed_path = self.workspace_root / 'docs' / 'reports' / 'feeds' / 'oracall_feed.jsonl'
        self.incident_template = self.workspace_root / 'docs' / 'reports' / 'templates' / 'oracl_incident_report.md'
        self.job_template = self.workspace_root / 'docs' / 'reports' / 'templates' / 'oracl_job_completion.md'
        self.incident_dir = self.workspace_root / 'docs' / 'reports' / 'INCIDENT_REPORTS'
        self.job_dir = self.workspace_root / 'docs' / 'reports' / 'PHASE_REPORTS'

        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.feed_path.parent.mkdir(parents=True, exist_ok=True)
        self.incident_dir.mkdir(parents=True, exist_ok=True)
        self.job_dir.mkdir(parents=True, exist_ok=True)

        self.adapter: IncidentSyncAdapter = self._build_adapter()
        self.navigation_links = self._build_navigation_links()
        self.placeholder_manifest: Dict[str, Any] = self._load_placeholder_manifest()

    def _build_navigation_links(self) -> List[Dict[str, Any]]:
        links: List[Dict[str, Any]] = []
        for entry in NAV_LINKS:
            rel_path = entry['path']
            abs_path = self.workspace_root / rel_path
            exists = abs_path.exists()
            links.append({
                'title': entry['title'],
                'path': self._relative_path(abs_path) if exists else rel_path.as_posix(),
                'description': entry['description'],
                'exists': exists
            })
        return links

    def _build_adapter(self) -> IncidentSyncAdapter:
        integrations = self.config_manager.get('integrations', {}) or {}
        jira_cfg = integrations.get('jira', {})
        servicenow_cfg = integrations.get('servicenow', {})

        # Placeholder: Return Null adapter until concrete connectors are implemented
        if jira_cfg.get('enabled') or servicenow_cfg.get('enabled'):
            self.logger.info("External integration requested but not yet implemented; using Null adapter.")
        return NullIncidentSyncAdapter()

    # ------------------------------------------------------------------
    # Scaffold Command
    # ------------------------------------------------------------------
    def scaffold(self, args: argparse.Namespace) -> Dict[str, Any]:
        severity = args.severity.lower()
        if severity not in SEVERITY_WINDOWS:
            raise ValueError(f"Unsupported severity: {args.severity}")

        now = datetime.now(timezone.utc)
        date_str = now.strftime('%Y%m%d')
        sequence = self._next_sequence(date_str)
        base_id = f"ORACALL-{date_str}-{sequence:03d}"
        incident_id = f"INC-{date_str}-{sequence:03d}"
        job_id = f"JOB-{date_str}-{sequence:03d}"

        windows = SEVERITY_WINDOWS[severity]
        analytic_due = now + timedelta(hours=windows['analytic_hours'])
        action_due = now + timedelta(hours=windows['action_hours'])

        replacements = self._build_replacements(
            args=args,
            incident_id=incident_id,
            job_id=job_id,
            now=now,
            severity=severity,
            analytic_due=analytic_due,
            action_due=action_due
        )

        incident_path = self._render_report(
            template_path=self.incident_template,
            output_dir=self.incident_dir,
            file_name=f"{incident_id}.md",
            replacements=replacements,
            feed_id=base_id,
            severity=severity,
            analytic_due=analytic_due,
            action_due=action_due
        )

        job_path = self._render_report(
            template_path=self.job_template,
            output_dir=self.job_dir,
            file_name=f"{job_id}.md",
            replacements=replacements,
            feed_id=base_id,
            severity=severity,
            analytic_due=analytic_due,
            action_due=action_due
        )

        metadata = {
            'event_id': base_id,
            'incident_id': incident_id,
            'job_id': job_id,
            'severity': severity,
            'event_type': args.event_type,
            'title': args.title,
            'engineer': args.engineer,
            'created_at': self._to_iso(now),
            'analytic_due': self._to_iso(analytic_due),
            'action_due': self._to_iso(action_due),
            'status': {'analytic': 'pending', 'action': 'pending'},
            'reports': {
                'analytic': self._relative_path(incident_path),
                'action': self._relative_path(job_path)
            },
            'distribution_level': 'tier-2',
        }

        metadata_path = self.events_dir / f"{base_id}.json"
        with open(metadata_path, 'w', encoding='utf-8') as handle:
            json.dump(metadata, handle, indent=2)

        self._append_feed_entry(metadata)
        self._maybe_sync_external(metadata)
        self._log_navigation_reference(context='scaffold', placeholder_ids=['PL-001', 'PL-002', 'PL-003', 'PL-004', 'PL-005'])

        self.logger.info("ORACall event scaffolded: %s", base_id)
        return metadata

    # ------------------------------------------------------------------
    # SLA Monitoring
    # ------------------------------------------------------------------
    def check_slas(self, warn_only: bool = False) -> List[Dict[str, Any]]:
        events = self._load_events()
        now = datetime.now(timezone.utc)
        findings: List[Dict[str, Any]] = []

        for event in events:
            created = self._parse_iso(event.get('created_at'))
            for report_key in ['analytic', 'action']:
                status = (event.get('status') or {}).get(report_key, 'pending')
                if status == 'completed':
                    continue
                due = self._parse_iso(event.get(f'{report_key}_due'))
                if not created or not due:
                    continue
                total = (due - created).total_seconds()
                if total <= 0:
                    continue
                elapsed = (now - created).total_seconds()
                ratio = max(0.0, elapsed / total)
                finding = {
                    'event_id': event['event_id'],
                    'report': report_key,
                    'severity': event.get('severity', 'low'),
                    'ratio': ratio,
                    'time_remaining_seconds': (due - now).total_seconds()
                }
                if ratio >= 0.9:
                    findings.append({**finding, 'level': 'critical'})
                    if not warn_only:
                        self._send_sla_alert(event, report_key, ratio, critical=True)
                elif ratio >= 0.75:
                    findings.append({**finding, 'level': 'warning'})
                    if not warn_only:
                        self._send_sla_alert(event, report_key, ratio, critical=False)
        if events:
            self._log_navigation_reference(context='sla-check', placeholder_ids=['PL-001', 'PL-002', 'PL-003', 'PL-004', 'PL-005'])
        return findings

    def mark_complete(self, event_id: str, report: str) -> Dict[str, Any]:
        event_path = self.events_dir / f"{event_id}.json"
        if not event_path.exists():
            raise FileNotFoundError(f"Missing ORACall metadata for {event_id}")
        with open(event_path, 'r', encoding='utf-8') as handle:
            metadata = json.load(handle)

        now = self._to_iso(datetime.now(timezone.utc))
        status = metadata.setdefault('status', {})
        status[report] = 'completed'
        completed_map = metadata.setdefault('completed_at', {})
        completed_map[report] = now

        with open(event_path, 'w', encoding='utf-8') as handle:
            json.dump(metadata, handle, indent=2)

        self._append_feed_entry(metadata, event_type='update')
        self._log_navigation_reference(context=f'mark-complete:{event_id}', placeholder_ids=['PL-001', 'PL-002', 'PL-003', 'PL-004', 'PL-005'])
        self.logger.info("Marked %s for %s as completed", report, event_id)
        return metadata

    # ------------------------------------------------------------------
    # Partner Feed Helpers
    # ------------------------------------------------------------------
    def _append_feed_entry(self, metadata: Dict[str, Any], event_type: str = 'create') -> None:
        feed_payload = {
            'feed_id': metadata['event_id'],
            'event_type': event_type,
            'severity': metadata.get('severity'),
            'timestamp': self._to_iso(datetime.now(timezone.utc)),
            'reports': metadata.get('reports', {}),
            'status': metadata.get('status', {}),
            'analytic_due': metadata.get('analytic_due'),
            'action_due': metadata.get('action_due'),
            'distribution_level': metadata.get('distribution_level', 'tier-2')
        }
        serialized = json.dumps(metadata, sort_keys=True).encode('utf-8')
        feed_payload['content_hash'] = hashlib.sha256(serialized).hexdigest()
        feed_payload['signature'] = 'pending-ed25519'

        with open(self.feed_path, 'a', encoding='utf-8') as handle:
            handle.write(json.dumps(feed_payload) + '\n')
        self._log_navigation_reference(context=f'feed-entry:{metadata.get("event_id", "unknown")}', placeholder_ids=['PL-004', 'PL-005'])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_replacements(self, *, args: argparse.Namespace, incident_id: str, job_id: str,
                             now: datetime, severity: str, analytic_due: datetime, action_due: datetime) -> Dict[str, Any]:
        timestamp_str = now.strftime('%Y-%m-%d %H:%M')
        return {
            'timestamp': self._to_iso(now),
            'incident_id': incident_id,
            'job_id': job_id,
            'time_range': f"{timestamp_str} to TBD",
            'timeframe': f"{timestamp_str} -> TBD",
            'primary_engineer': args.engineer,
            'engineers': args.engineer,
            'severity': severity.upper(),
            'analytic_due': self._to_iso(analytic_due),
            'action_due': self._to_iso(action_due),
            'deliverable_notes': 'Pending engineer input.',
            'decision_summary': 'Ledger entries pending.',
            'reports_updated': 'Pending updates',
            'tests_run': 'Pending tests',
            'seam_status': 'Security > Efficiency > Minimalism maintained.',
            'follow_on_tasks': 'Pending assignments'
        }

    def _render_report(self, template_path: Path, output_dir: Path, file_name: str,
                        replacements: Dict[str, Any], feed_id: str, severity: str,
                        analytic_due: datetime, action_due: datetime) -> Path:
        if not template_path.exists():
            raise FileNotFoundError(f"Missing template: {template_path}")
        content = template_path.read_text(encoding='utf-8')
        for key, value in replacements.items():
            placeholder = f"{{{{ {key} }}}}"
            content = content.replace(placeholder, str(value))

        metadata_header = '\n'.join([
            '<!-- distribution_level: tier-2 -->',
            f"<!-- cache_expiry_hours: {CACHE_EXPIRY_HOURS.get(severity, 168)} -->",
            f"<!-- feed_id: {feed_id} -->",
            f"<!-- severity: {severity} -->",
            f"<!-- analytic_due: {self._to_iso(analytic_due)} -->",
            f"<!-- action_due: {self._to_iso(action_due)} -->"
        ])

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / file_name
        with open(output_path, 'w', encoding='utf-8') as handle:
            handle.write(metadata_header + '\n\n' + content)
        return output_path

    def _next_sequence(self, date_str: str) -> int:
        pattern = f"ORACALL-{date_str}-"
        existing = [p for p in self.events_dir.glob('ORACALL-*.json') if pattern in p.name]
        return len(existing) + 1

    def _relative_path(self, path: Path) -> str:
        return str(path.relative_to(self.workspace_root).as_posix())

    def _to_iso(self, dt: datetime) -> str:
        return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')

    def _parse_iso(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        value = value.replace('Z', '+00:00')
        return datetime.fromisoformat(value)

    def _load_events(self) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        for path in sorted(self.events_dir.glob('ORACALL-*.json')):
            try:
                with open(path, 'r', encoding='utf-8') as handle:
                    events.append(json.load(handle))
            except Exception as exc:
                self.logger.error("Failed to load metadata %s: %s", path, exc)
        return events

    def _send_sla_alert(self, metadata: Dict[str, Any], report_key: str, ratio: float, critical: bool) -> None:
        severity = 'critical' if critical else 'warning'
        title = f"ORACall SLA nearing breach ({metadata['event_id']} / {report_key})"
        percent = int(ratio * 100)
        due_time = metadata.get(f'{report_key}_due', 'unknown')
        message = (
            f"Event {metadata['event_id']} ({metadata.get('severity')}) is {percent}% through the allowed window.\n"
            f"Report type: {report_key}. Due at {due_time}."
        )
        self.alert_manager.send_alert(title=title, message=message, severity=severity)

    def _maybe_sync_external(self, metadata: Dict[str, Any]) -> None:
        integrations = self.config_manager.get('integrations', {}) or {}
        threshold = (integrations.get('severity_sync_threshold') or 'high').lower()
        severity = (metadata.get('severity') or 'low').lower()
        if isinstance(self.adapter, NullIncidentSyncAdapter):
            return
        if self._severity_gte(severity, threshold):
            payload = self.adapter.prepare_payload(metadata)
            response = self.adapter.push_event(payload)
            self.adapter.audit_log(response)

    def _severity_gte(self, severity: str, threshold: str) -> bool:
        try:
            return SEVERITY_ORDER.index(severity) >= SEVERITY_ORDER.index(threshold)
        except ValueError:
            return False

    def _load_placeholder_manifest(self) -> Dict[str, Any]:
        manifest_path = self.workspace_root / PLACEHOLDER_MANIFEST
        if not manifest_path.exists():
            return {'placeholders': []}
        try:
            with open(manifest_path, 'r', encoding='utf-8') as handle:
                return json.load(handle)
        except Exception as exc:
            self.logger.error("Failed to load placeholder manifest: %s", exc)
            return {'placeholders': []}

    def placeholder_entries(self, placeholder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        entries = self.placeholder_manifest.get('placeholders', [])
        if placeholder_id:
            needle = placeholder_id.lower()
            return [entry for entry in entries if entry.get('id', '').lower() == needle]
        return entries

    def navigation_map(self) -> List[Dict[str, Any]]:
        """Return navigation metadata for agents and docs."""
        # Refresh to capture newly created files without reinstantiating the manager
        self.navigation_links = self._build_navigation_links()
        return self.navigation_links

    def render_navigation_text(self, placeholder_id: Optional[str] = None) -> str:
        lines = ["ORACall Navigation Map", "", "General References:"]
        for link in self.navigation_map():
            status = 'available' if link['exists'] else 'missing'
            lines.append(f"- {link['title']} ({status}): {link['path']}\n  {link['description']}")

        entries = self.placeholder_entries(placeholder_id)
        lines.append("")
        header = "Placeholder Entries" if not placeholder_id else f"Placeholder Entries ({placeholder_id.upper()})"
        lines.append(header + ":")
        if not entries:
            lines.append("- No placeholder entries found for the provided filter.")
        else:
            for entry in entries:
                lines.append(f"- {entry['id']} {entry.get('name', '')}")
                lines.append(f"  Status: {entry.get('status', 'unknown')}")
                lines.append(f"  Description: {entry.get('description', 'n/a')}")
                files = entry.get('files', [])
                if files:
                    lines.append("  Files:")
                    for file_entry in files:
                        lines.append(f"    - {file_entry.get('path')}: {file_entry.get('summary', '')}")
                checkpoint = entry.get('checkpoint') or {}
                if checkpoint:
                    anchor = checkpoint.get('anchor')
                    path = checkpoint.get('path')
                    suffix = f"#{anchor}" if anchor else ''
                    lines.append(f"  Checkpoint: {path}{suffix}")
        return '\n'.join(lines)

    def _resolve_placeholder_links(self, placeholder_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if placeholder_ids:
            ids = {pid.lower() for pid in placeholder_ids}
            return [entry for entry in self.placeholder_entries() if entry.get('id', '').lower() in ids]
        return self.placeholder_entries()

    def _log_navigation_reference(self, context: str, placeholder_ids: Optional[List[str]] = None) -> None:
        try:
            entries = self._resolve_placeholder_links(placeholder_ids)
            payload = {
                'context': context,
                'placeholder_ids': [entry.get('id') for entry in entries],
                'links': entries,
                'documents': self.navigation_map()
            }
            self.session_memory.log_decision(
                decision=f"ORACall navigation context: {context}",
                rationale=json.dumps(payload, indent=2)
            )
        except Exception as exc:
            self.logger.warning("Failed to log navigation context: %s", exc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='ORACall management utilities')
    subparsers = parser.add_subparsers(dest='command', required=True)

    scaffold = subparsers.add_parser('scaffold', help='Generate dual-report stubs for a new event')
    scaffold.add_argument('--title', required=True, help='Short event title')
    scaffold.add_argument('--engineer', required=True, help='Primary engineer or operator')
    scaffold.add_argument('--severity', required=True, choices=SEVERITY_ORDER,
                         help='Severity level to apply')
    scaffold.add_argument('--event-type', default='pei', help='Event classification (pei, security, etc.)')

    sla = subparsers.add_parser('sla-check', help='Evaluate SLA timers and emit alerts when needed')
    sla.add_argument('--warn-only', action='store_true', help='Print warnings without sending alerts')

    complete = subparsers.add_parser('complete', help='Mark analytic or action report as completed')
    complete.add_argument('event_id', help='ORACall event identifier (e.g., ORACALL-20251114-001)')
    complete.add_argument('--report', choices=['analytic', 'action'], required=True,
                          help='Which report to mark complete')

    feed = subparsers.add_parser('feed', help='Inspect the ORACall JSONL feed')
    feed.add_argument('--tail', type=int, default=5, help='Number of entries to display from the end')

    guide = subparsers.add_parser('guide', help='Show navigation references for ORACall artifacts')
    guide.add_argument('--format', choices=['text', 'json'], default='text',
                      help='Output format for navigation map')
    guide.add_argument('--placeholder', help='Filter to a specific placeholder ID (e.g., PL-004)')

    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
    parser = build_parser()
    args = parser.parse_args()

    manager = OracallManager()

    if args.command == 'scaffold':
        metadata = manager.scaffold(args)
        print(json.dumps(metadata, indent=2))
    elif args.command == 'sla-check':
        findings = manager.check_slas(warn_only=args.warn_only)
        if findings:
            print(json.dumps(findings, indent=2))
        else:
            print('All tracked ORACall reports are within SLA windows.')
    elif args.command == 'complete':
        metadata = manager.mark_complete(args.event_id, args.report)
        print(json.dumps(metadata, indent=2))
    elif args.command == 'feed':
        tail = args.tail
        entries = []
        if manager.feed_path.exists():
            with open(manager.feed_path, 'r', encoding='utf-8') as handle:
                entries = [json.loads(line) for line in handle if line.strip()]
        print(json.dumps(entries[-tail:], indent=2))
        manager._log_navigation_reference(context='feed-view', placeholder_ids=['PL-004', 'PL-005'])
    elif args.command == 'guide':
        placeholder = args.placeholder
        if args.format == 'json':
            payload = {
                'documents': manager.navigation_map(),
                'placeholders': manager.placeholder_entries(placeholder)
            }
            print(json.dumps(payload, indent=2))
        else:
            print(manager.render_navigation_text(placeholder_id=placeholder))

        if placeholder:
            manager._log_navigation_reference(context=f'guide:{placeholder}', placeholder_ids=[placeholder])
        else:
            manager._log_navigation_reference(context='guide:all', placeholder_ids=None)
    elif args.command == 'guide':
        if args.format == 'json':
            print(json.dumps(manager.navigation_map(), indent=2))
        else:
            print(manager.render_navigation_text())


if __name__ == '__main__':
    main()
