"""
Utilities for the 'memory process' CLI command.
Handles displaying and managing CodeSentinel processes and instances.
"""

from typing import List, Dict, Any
import os
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
    print(f"\n[DISCOVERY] Top {limit} System Processes by Memory Usage")
    print("="*80)
    print(f"{'PID':<10} {'Name':<30} {'Username':<25} {'Memory':<12}")
    print("-"*80)
    
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'username', 'memory_info']):
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
        print(f"{p_info['pid']:<10} {p_info['name']:<30} {username:<25} {_format_bytes(mem_bytes):<12}")
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
            'limit_requested': limit
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
