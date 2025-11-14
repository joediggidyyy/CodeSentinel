"""
Utilities for the 'memory process' CLI command.
Handles displaying and managing CodeSentinel processes and instances.
"""

from typing import List, Dict, Any
import os
import json
from pathlib import Path
import psutil
from datetime import datetime
import time

from ..utils.process_monitor import get_monitor
from ..utils.instance_manager import find_instances, get_registered_instances
from ..utils.session_memory import SessionMemory

def _format_bytes(byte_count: float) -> str:
    """Formats bytes into a human-readable string (KB, MB, GB)."""
    if byte_count is None:
        return "N/A"
    power = 1024
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while byte_count >= power and n < len(power_labels) -1 :
        byte_count /= power
        n += 1
    return f"{byte_count:.1f} {power_labels[n]}"


def _format_duration(seconds: float) -> str:
    """Return human-readable duration string."""
    if seconds is None or seconds < 0:
        return "N/A"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _safe_cmdline(proc: psutil.Process) -> str:
    try:
        return " ".join(proc.cmdline())
    except (psutil.AccessDenied, psutil.ZombieProcess):
        return "Access denied"
    except Exception:
        return "Unavailable"


def _safe_name(proc: psutil.Process) -> str:
    try:
        return proc.name()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        return 'unknown'
    except Exception:
        return 'unavailable'

def _get_process_details(pid: int) -> Dict[str, Any]:
    """Safely get details for a given PID."""
    try:
        proc = psutil.Process(pid)
        mem_info = proc.memory_info()
        return {
            "pid": pid,
            "name": proc.name(),
            "status": proc.status(),
            "cpu_percent": proc.cpu_percent(interval=0.01),
            "memory": mem_info.rss,
            "create_time": datetime.fromtimestamp(proc.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "cmdline": " ".join(proc.cmdline())
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return {
            "pid": pid,
            "name": "N/A (process terminated or access denied)",
            "status": "terminated",
            "cpu_percent": 0,
            "memory": 0,
            "create_time": "N/A",
            "cmdline": "N/A"
        }

def handle_lifecycle_status(args):
    """Handler for `codesentinel memory process status` - Show tracked processes."""
    start_time = time.time()
    
    monitor = get_monitor()
    status = monitor.get_status()
    tracked_pids = status.get('tracked_pids', [])

    print("\n[LIFECYCLE] Tracked Processes (Instance PID: {})".format(os.getpid()))
    print("="*80)
    
    if not tracked_pids:
        print("[NONE] No processes currently tracked by ProcessMonitor.")
        print("       (This is normal if you haven't spawned any child processes)")
    else:
        print(f"[{len(tracked_pids)} TRACKED]\n")
        print(f"{'PID':<10} {'Name':<25} {'Status':<12} {'Memory':<12} {'Created':<20}")
        print("-"*80)
        for pid in tracked_pids:
            details = _get_process_details(pid)
            print(f"{details['pid']:<10} {details['name']:<25} {details['status']:<12} {_format_bytes(details['memory']):<12} {details['create_time']:<20}")
    print("="*80)
    
    # Log to DHIS
    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'lifecycle_status_check',
        'files_modified': ['codesentinel/utils/process_monitor.py'],
        'success': True,
        'duration_ms': duration_ms,
        'metadata': {
            'tracked_count': len(tracked_pids),
            'instance_pid': os.getpid()
        }
    })

def handle_lifecycle_history(args):
    """Handler for `codesentinel memory process history` - Show cleanup history."""
    start_time = time.time()
    
    print("\n[LIFECYCLE] Orphan Cleanup History")
    print("="*80)
    
    monitor = get_monitor()
    status = monitor.get_status()
    cleanup_history = status.get('cleanup_history', [])
    
    # Optional --limit flag
    limit = getattr(args, 'limit', 20)
    
    if not cleanup_history:
        print("[NONE] No orphan processes have been cleaned up.")
        print("       (This is good - no resource leaks detected)")
    else:
        print(f"[{len(cleanup_history)} TOTAL] Recent cleanups (showing last {limit}):\n")
        print(f"{'Time':<22} {'PID':<8} {'Process':<25} {'Action':<15}")
        print("-"*80)
        for event in cleanup_history[-limit:]:
            timestamp = event['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            pid = event['pid']
            name = event['name'][:24]
            action = event['action'].upper()
            print(f"{timestamp:<22} {pid:<8} {name:<25} {action:<15}")
    
    print("="*80)
    
    # Log to DHIS
    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'lifecycle_history_query',
        'files_modified': ['codesentinel/utils/process_monitor.py'],
        'success': True,
        'duration_ms': duration_ms,
        'metadata': {
            'total_cleanups': len(cleanup_history),
            'limit_requested': limit
        }
    })


def handle_discovery_instances(args):
    """Handler for `codesentinel memory process instances` - Show all CodeSentinel instances."""
    start_time = time.time()
    
    verbose = getattr(args, 'verbose', False)
    print("\n[DISCOVERY] All Detected CodeSentinel Instances")
    print("="*80)
    
    # Use file-based registry first for reliability
    instances = get_registered_instances()
    
    # Fallback to process scanning if registry is empty
    if not instances:
        print("(Registry empty, falling back to process scan...)")
        raw_instances = find_instances()
        # Convert to the same format as registered instances
        instances = [_get_process_details(inst['pid']) for inst in raw_instances]

    if not instances:
        print("[NONE] No other CodeSentinel instances found.")
    else:
        print(f"[{len(instances)} INSTANCES]\n")
        if verbose:
            print(f"{'PID':<10} {'Username':<20} {'Status':<12} {'Memory':<12} {'Command':<40}")
        else:
            print(f"{'PID':<10} {'Username':<20} {'Status':<12} {'Memory':<12}")
        print("-"*80)
        for inst in instances:
            details = _get_process_details(inst['pid'])
            if verbose:
                print(f"{details['pid']:<10} {inst.get('username', 'N/A'):<20} {details['status']:<12} {_format_bytes(details['memory']):<12} {details['cmdline']:<40}")
            else:
                print(f"{details['pid']:<10} {inst.get('username', 'N/A'):<20} {details['status']:<12} {_format_bytes(details['memory']):<12}")
    print("="*80)
    
    # Log to DHIS
    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'discovery_instances_query',
        'files_modified': [],
        'success': True,
        'duration_ms': duration_ms,
        'metadata': {
            'instances_found': len(instances),
            'verbose_mode': verbose
        }
    })

def handle_discovery_system(args):
    """Handler for `codesentinel memory process system` - Show top system processes by memory."""
    start_time = time.time()
    
    limit = getattr(args, 'limit', 15)
    verbose = getattr(args, 'verbose', False)
    print(f"\n[DISCOVERY] Top {limit} System Processes by Memory Usage")
    print("="*80)
    header = f"{'PID':<10} {'Name':<30} {'Username':<25} {'Memory':<12}"
    if verbose:
        header += " Command"
    print(header)
    print("-"*80)
    
    procs = []
    attrs = ['pid', 'name', 'username', 'memory_info']
    if verbose:
        attrs.append('cmdline')
    for p in psutil.process_iter(attrs):
        try:
            if p.info['memory_info']:
                procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Sort by memory usage, descending
    procs.sort(key=lambda x: x['memory_info'].rss if x.get('memory_info') else 0, reverse=True)
    
    print(f"[{len(procs)} TOTAL]\n")
    for p_info in procs[:limit]:
        mem_bytes = p_info['memory_info'].rss if p_info.get('memory_info') else 0
        username = p_info.get('username') or 'N/A'
        line = f"{p_info['pid']:<10} {p_info['name']:<30} {username:<25} {_format_bytes(mem_bytes):<12}"
        if verbose:
            cmd = " ".join(p_info.get('cmdline', [])[:25]) if p_info.get('cmdline') else ''
            line += f" {cmd}"
        print(line)
    print("="*80)
    
    # Log to DHIS
    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'discovery_system_scan',
        'files_modified': [],
        'success': True,
        'duration_ms': duration_ms,
        'metadata': {
            'total_processes': len(procs),
            'limit_requested': limit,
            'verbose_mode': verbose
        }
    })


def handle_process_detail(args):
    """Show detailed information about a specific process."""
    start_time = time.time()
    pid = args.pid
    verbose = getattr(args, 'verbose', False)
    success = False
    try:
        proc = psutil.Process(pid)
        name = _safe_name(proc)
        proc.cpu_percent(interval=None)
        time.sleep(0.05)
        cpu = proc.cpu_percent(interval=None)
        try:
            mem = proc.memory_info()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            mem = None
        create_time = datetime.fromtimestamp(proc.create_time())
        now = datetime.now()
        runtime = _format_duration((now - create_time).total_seconds())
        print("\n[DETAIL] Process Inspection")
        print("="*80)
        print(f"PID:        {pid}")
        print(f"Name:       {name}")
        print(f"Status:     {proc.status()}")
        try:
            username = proc.username()
        except (psutil.AccessDenied, psutil.ZombieProcess):
            username = 'N/A'
        print(f"User:       {username}")
        print(f"CPU:        {cpu:.1f}%")
        if mem:
            print(f"Memory:     {_format_bytes(mem.rss)} (RSS) | {_format_bytes(mem.vms)} (VMS)")
        else:
            print("Memory:     Access denied")
        print(f"Runtime:    {runtime}")
        print(f"Started:    {create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if verbose:
            try:
                thread_count = proc.num_threads()
            except (psutil.AccessDenied, psutil.ZombieProcess):
                thread_count = 0
            print(f"Threads:    {thread_count}")
            io = None
            try:
                io = proc.io_counters()
            except (psutil.AccessDenied, AttributeError):
                io = None
            if io:
                print(f"I/O:        Read {_format_bytes(io.read_bytes)} | Write {_format_bytes(io.write_bytes)}")
            print(f"Cmdline:    {_safe_cmdline(proc)}")
            try:
                cwd = proc.cwd()
            except (psutil.AccessDenied, FileNotFoundError, AttributeError):
                cwd = None
            if cwd:
                print(f"CWD:        {cwd}")
            parent = proc.parent()
            if parent:
                print(f"Parent:     {parent.pid} ({_safe_name(parent)})")
        print("="*80)
        success = True
    except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
        print(f"[FAIL] Unable to inspect PID {pid}: {exc}")
    except Exception as exc:
        print(f"[FAIL] Unexpected error inspecting PID {pid}: {exc}")
    finally:
        duration_ms = int((time.time() - start_time) * 1000)
        session = SessionMemory()
        session.log_domain_activity('process', {
            'action': 'detail_inspection',
            'files_modified': [],
            'success': success,
            'duration_ms': duration_ms,
            'metadata': {
                'pid': pid,
                'verbose_mode': verbose
            }
        })


def handle_process_kill(args):
    """Terminate a process safely, respecting SEAM prompts."""
    start_time = time.time()
    pid = args.pid
    force = getattr(args, 'force', False)
    assume_yes = getattr(args, 'yes', False)
    reason = getattr(args, 'reason', 'unspecified')
    success = False
    try:
        proc = psutil.Process(pid)
        try:
            name = proc.name()
        except (psutil.AccessDenied, psutil.ZombieProcess):
            name = 'unknown'
    except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
        print(f"[FAIL] Unable to access PID {pid}: {exc}")
        return

    if not assume_yes:
        mode = 'FORCE' if force else 'terminate'
        prompt = f"Confirm {mode.lower()} kill for PID {pid} ({name})? (y/N): "
        response = input(prompt)
        if response.lower() != 'y':
            print("[INFO] Kill operation cancelled")
            return

    try:
        if force:
            proc.kill()
        else:
            proc.terminate()
        timeout = 5 if force else 10
        proc.wait(timeout=timeout)
        print(f"[OK] PID {pid} ({name}) terminated")
        success = True
    except psutil.TimeoutExpired:
        print(f"[WARN] PID {pid} did not exit within {timeout}s")
    except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
        print(f"[FAIL] Unable to complete kill for PID {pid}: {exc}")

    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'process_kill',
        'files_modified': [],
        'success': success,
        'duration_ms': duration_ms,
        'metadata': {
            'pid': pid,
            'force': force,
            'reason': reason
        }
    })


def handle_process_anomalies(args):
    """Detect processes exceeding CPU/memory/runtime thresholds."""
    start_time = time.time()
    cpu_threshold = getattr(args, 'cpu_threshold', 50.0)
    mem_threshold_mb = getattr(args, 'memory_threshold', 512.0)
    runtime_threshold = getattr(args, 'min_runtime', 600)
    limit = getattr(args, 'limit', 25)
    verbose = getattr(args, 'verbose', False)
    anomalies: List[Dict[str, Any]] = []

    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info', 'status', 'create_time']):
        try:
            cpu = proc.cpu_percent(interval=None)
            mem_bytes = proc.info['memory_info'].rss if proc.info.get('memory_info') else 0
            mem_mb = mem_bytes / (1024 * 1024)
            create_time = proc.info.get('create_time') or time.time()
            runtime = time.time() - create_time
            triggers = []
            if cpu >= cpu_threshold:
                triggers.append(f"cpu>={cpu_threshold}")
            if mem_mb >= mem_threshold_mb:
                triggers.append(f"mem>={mem_threshold_mb}MB")
            if runtime >= runtime_threshold:
                triggers.append(f"runtime>={runtime_threshold}s")
            if triggers:
                anomalies.append({
                    'pid': proc.pid,
                    'name': proc.info.get('name', 'unknown'),
                    'username': proc.info.get('username', 'N/A'),
                    'cpu': cpu,
                    'mem': mem_bytes,
                    'runtime': runtime,
                    'status': proc.info.get('status', 'unknown'),
                    'triggers': triggers,
                    'cmdline': _safe_cmdline(proc)
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    anomalies.sort(key=lambda item: (item['cpu'], item['mem']), reverse=True)
    print("\n[ANALYSIS] Suspect Processes")
    print("="*80)
    if not anomalies:
        print("[OK] No processes exceeded the configured thresholds")
    else:
        print(f"Thresholds -> CPU: {cpu_threshold}%, Memory: {mem_threshold_mb} MB, Runtime: {runtime_threshold}s")
        print(f"Showing top {min(limit, len(anomalies))} of {len(anomalies)} hits\n")
        header = f"{'PID':<8} {'Name':<25} {'CPU%':<8} {'Memory':<12} {'Runtime':<10} Triggers"
        print(header)
        print("-"*80)
        for entry in anomalies[:limit]:
            line = f"{entry['pid']:<8} {entry['name']:<25} {entry['cpu']:<8.1f} {_format_bytes(entry['mem']):<12} {_format_duration(entry['runtime']):<10} {', '.join(entry['triggers'])}"
            print(line)
            if verbose:
                print(f"    User: {entry['username']} | Status: {entry['status']}")
                print(f"    Cmd:  {entry['cmdline']}")
    print("="*80)

    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'process_anomalies_scan',
        'files_modified': [],
        'success': True,
        'duration_ms': duration_ms,
        'metadata': {
            'hits': len(anomalies),
            'cpu_threshold': cpu_threshold,
            'memory_threshold_mb': mem_threshold_mb,
            'runtime_threshold_s': runtime_threshold
        }
    })


def handle_process_tree(args):
    """Show parent/child context around a PID."""
    start_time = time.time()
    pid = args.pid
    depth = getattr(args, 'depth', 2)
    success = False
    try:
        proc = psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
        print(f"[FAIL] Unable to access PID {pid}: {exc}")
        return

    def _print_parent_chain(p: psutil.Process):
        chain = []
        parent = p.parent()
        while parent and len(chain) < 5:
            chain.append(parent)
            parent = parent.parent()
        if not chain:
            return
        print("Parents:")
        for idx, parent in enumerate(reversed(chain), 1):
            print(f"  {' ' * (idx-1)}- PID {parent.pid} ({_safe_name(parent)}) [{parent.status()}]")

    def _print_children(p: psutil.Process, level: int) -> None:
        if level > depth:
            return
        try:
            children = p.children()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            children = []
        for child in children[:10]:
            try:
                mem = child.memory_info().rss if child.is_running() else 0
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                mem = 0
                print(f"  {'  ' * level}-> PID {child.pid} ({_safe_name(child)}) {_format_bytes(mem)}")
            _print_children(child, level + 1)

    print("\n[TOPOLOGY] Process Tree Context")
    print("="*80)
    _print_parent_chain(proc)
            print(f"Target PID {proc.pid}: {_safe_name(proc)} [{proc.status()}]")
    try:
        target_mem = proc.memory_info().rss
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        target_mem = 0
    try:
        cpu_now = proc.cpu_percent(interval=0.0)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        cpu_now = 0.0
    print(f"  Memory: {_format_bytes(target_mem)} | CPU: {cpu_now:.1f}%")
    print("Children (depth {}):".format(depth))
    _print_children(proc, 1)
    print("="*80)
    success = True

    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'process_tree_view',
        'files_modified': [],
        'success': success,
        'duration_ms': duration_ms,
        'metadata': {
            'pid': pid,
            'depth': depth
        }
    })


def handle_process_watch(args):
    """Continuously sample a process to observe behavior."""
    start_time = time.time()
    pid = args.pid
    interval = max(1, getattr(args, 'interval', 5))
    duration = max(interval, getattr(args, 'duration', 30))
    verbose = getattr(args, 'verbose', False)
    success = False

    try:
        proc = psutil.Process(pid)
        name = _safe_name(proc)
        print("\n[OBSERVE] Process Watch")
        print("="*80)
        print(f"Watching PID {pid} ({name}) for {duration}s @ {interval}s intervals")
        print(f"{'Time':<12} {'CPU%':<8} {'Memory':<12} {'Threads':<8} Status")
        print("-"*80)
        end_time = time.time() + duration
        proc.cpu_percent(interval=None)
        while time.time() < end_time:
            cpu = proc.cpu_percent(interval=None)
            try:
                mem = proc.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                mem = 0
            try:
                threads = proc.num_threads()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                threads = 0
            status = proc.status()
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"{timestamp:<12} {cpu:<8.1f} {_format_bytes(mem):<12} {threads:<8} {status}")
            if verbose:
                print(f"    Cmd: {_safe_cmdline(proc)}")
            time.sleep(interval)
        print("="*80)
        success = True
    except psutil.NoSuchProcess:
        print(f"[FAIL] PID {pid} no longer exists")
    except psutil.AccessDenied:
        print(f"[FAIL] Access denied while watching PID {pid}")
    except KeyboardInterrupt:
        print("\n[INFO] Watch cancelled by user")
        success = True

    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'process_watch',
        'files_modified': [],
        'success': success,
        'duration_ms': duration_ms,
        'metadata': {
            'pid': pid,
            'interval': interval,
            'duration': duration
        }
    })


def handle_process_snapshot(args):
    """Capture a snapshot of processes and store as JSONL."""
    start_time = time.time()
    filter_term = getattr(args, 'filter', None)
    limit = getattr(args, 'limit', 0)
    output_path = getattr(args, 'output', None)
    verbose = getattr(args, 'verbose', False)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    if output_path:
        out_path = Path(output_path)
    else:
        out_path = Path('docs/metrics') / f'process_snapshot_{timestamp}.jsonl'
    out_path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'memory_info', 'create_time']):
        try:
            cmdline = _safe_cmdline(proc)
            if filter_term and filter_term.lower() not in (proc.info.get('name', '') + cmdline).lower():
                continue
            record = {
                'timestamp': timestamp,
                'pid': proc.pid,
                'name': proc.info.get('name'),
                'username': proc.info.get('username'),
                'status': proc.info.get('status'),
                'memory_rss': proc.info['memory_info'].rss if proc.info.get('memory_info') else 0,
                'create_time': proc.info.get('create_time'),
                'cmdline': cmdline
            }
            records.append(record)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if limit:
        records = records[:limit]

    with out_path.open('w', encoding='utf-8') as fh:
        for record in records:
            fh.write(json.dumps(record) + '\n')

    print(f"[OK] Snapshot saved to {out_path} ({len(records)} records)")
    if verbose:
        print("Sample record:")
        if records:
            sample = records[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")

    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'process_snapshot',
        'files_modified': [str(out_path)],
        'success': True,
        'duration_ms': duration_ms,
        'metadata': {
            'records': len(records),
            'filter': filter_term,
            'output': str(out_path)
        }
    })

def handle_intelligence_info(args):
    """Handler for `codesentinel memory process info` - Full instance diagnostics."""
    start_time = time.time()
    
    print("\n[INTELLIGENCE] CodeSentinel Instance Diagnostics")
    print("="*80)
    
    # Current instance
    current_pid = os.getpid()
    current_details = _get_process_details(current_pid)
    print("Current Instance:")
    print(f"  PID:           {current_pid}")
    print(f"  Memory:        {_format_bytes(current_details['memory'])}")
    print(f"  Status:        {current_details['status']}")
    print(f"  CPU:           {current_details['cpu_percent']:.1f}%")
    print(f"  Command:       {current_details['cmdline']}")
    
    # Its process monitor
    monitor = get_monitor()
    status = monitor.get_status()
    print("\nAssociated Process Monitor:")
    print(f"  Running:       {status['running']}")
    print(f"  Enabled:       {status['enabled']}")
    print(f"  Interval:      {status['check_interval']}s")
    print(f"  Tracked PIDs:  {status['tracked_count']}")
    print(f"  Cleanups:      {len(status.get('cleanup_history', []))}")

    # Other instances
    other_instances = get_registered_instances()
    if other_instances:
        print("\nOther Registered Instances:")
        for inst in other_instances:
            if inst['pid'] == current_pid:
                continue
            details = _get_process_details(inst['pid'])
            print(f"\n  Instance PID: {inst['pid']}")
            print(f"    Status:      {details['status']}")
            print(f"    Memory:      {_format_bytes(details['memory'])}")
            print(f"    Command:     {details['cmdline']}")
            # Note: We can't get the monitor status of another process directly.
            # This would require IPC.
            print("    Monitor:     Unknown (requires IPC)")
    else:
        print("\nOther Registered Instances: [NONE]")

    print("="*80)
    
    # Log to DHIS
    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'intelligence_info_diagnostics',
        'files_modified': ['codesentinel/utils/process_monitor.py'],
        'success': True,
        'duration_ms': duration_ms,
        'metadata': {
            'current_pid': current_pid,
            'tracked_count': status['tracked_count'],
            'other_instances': len([i for i in other_instances if i['pid'] != current_pid]) if other_instances else 0
        }
    })

def handle_coordination_coordinate(args):
    """Handler for `codesentinel memory process coordinate` - Inter-ORACL communication entry point."""
    start_time = time.time()
    
    print("\n[COORDINATION] Inter-ORACL Communication")
    print("="*80)
    print("This feature enables communication and coordination between CodeSentinel instances.")
    print("\nProtocol: File-based messaging in shared directory.")
    
    # For now, this is a placeholder to demonstrate the concept.
    # A full implementation would involve creating task files and watching for responses.
    
    instances = get_registered_instances()
    current_pid = os.getpid()
    
    other_instances = [inst for inst in instances if inst['pid'] != current_pid]
    
    if not other_instances:
        print("\n[NONE] No other instances to coordinate with.")
    else:
        print(f"\n[{len(other_instances)} INSTANCES] Found instance(s) to coordinate with:")
        for inst in other_instances:
            print(f"  - PID: {inst['pid']}")
            
        print("\nDemonstration: Preparing 'share_context' request...")
        # This is where the IPC logic would go.
        # 1. Create a task file in a shared directory.
        #    e.g., /tmp/codesentinel_ipc/{target_pid}/task_{uuid}.json
        # 2. The task file would contain: { "task": "share_context", "requester_pid": current_pid }
        # 3. The target instance's file watcher would pick it up.
        # 4. The target instance would write its context to a response file.
        #    e.g., /tmp/codesentinel_ipc/{requester_pid}/response_{uuid}.json
        # 5. This instance would read the response.
        print("[CONCEPT] Task file would be created and a response awaited.")
        print("[CONCEPT] This requires a file watcher in each instance's main loop (v1.2).")

    print("="*80)
    
    # Log to DHIS
    duration_ms = int((time.time() - start_time) * 1000)
    session = SessionMemory()
    session.log_domain_activity('process', {
        'action': 'coordination_coordinate_check',
        'files_modified': [],
        'success': True,
        'duration_ms': duration_ms,
        'metadata': {
            'other_instances': len(other_instances),
            'current_pid': current_pid
        }
    })
