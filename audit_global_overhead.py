"""
Global Resource Overhead Audit - All CodeSentinel Components

Comprehensive analysis of CPU, memory, and I/O usage across all components.

SECURITY > EFFICIENCY > MINIMALISM
"""

import time
import psutil
import os
from pathlib import Path
from typing import Dict, Any, List
import json
import sys


def measure_component_overhead(component_name: str, func, *args, **kwargs) -> Dict[str, Any]:
    """Measure resource overhead for a component."""
    process = psutil.Process()
    
    # Baseline
    cpu_before = process.cpu_percent(interval=0.1)
    mem_before = process.memory_info()
    io_before = process.io_counters() if hasattr(process, 'io_counters') else None
    
    # Execute
    start_time = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        success = True
        error = None
    except Exception as e:
        result = None
        success = False
        error = str(e)
    end_time = time.perf_counter()
    
    # Post measurements
    cpu_after = process.cpu_percent(interval=0.1)
    mem_after = process.memory_info()
    io_after = process.io_counters() if hasattr(process, 'io_counters') else None
    
    # Calculate deltas
    duration = end_time - start_time
    mem_delta = mem_after.rss - mem_before.rss
    
    io_delta = {}
    if io_before and io_after:
        io_delta = {
            'read_mb': (io_after.read_bytes - io_before.read_bytes) / (1024*1024),
            'write_mb': (io_after.write_bytes - io_before.write_bytes) / (1024*1024),
        }
    
    return {
        'component': component_name,
        'success': success,
        'error': error,
        'duration_ms': duration * 1000,
        'memory_delta_mb': mem_delta / (1024 * 1024),
        'cpu_percent': cpu_after,
        'io': io_delta
    }


def audit_config_manager() -> Dict[str, Any]:
    """Audit ConfigManager overhead."""
    print("\n[1/7] Config Manager...")
    from codesentinel.utils.config import ConfigManager
    
    config_path = Path.cwd() / "codesentinel.json"
    
    def test_config():
        manager = ConfigManager(config_path)
        config = manager.load_config()
        manager.save_config(config)
        return config
    
    return measure_component_overhead("ConfigManager", test_config)


def audit_alert_manager() -> Dict[str, Any]:
    """Audit AlertManager overhead."""
    print("[2/7] Alert Manager...")
    from codesentinel.utils.alerts import AlertManager
    from codesentinel.utils.config import ConfigManager
    
    def test_alerts():
        config_mgr = ConfigManager()
        alert_mgr = AlertManager(config_mgr)
        # Don't actually send alert, just initialize
        return True
    
    return measure_component_overhead("AlertManager", test_alerts)


def audit_process_monitor() -> Dict[str, Any]:
    """Audit Process Monitor overhead."""
    print("[3/7] Process Monitor...")
    from codesentinel.utils.process_monitor import start_monitor, stop_monitor
    
    def test_monitor():
        monitor = start_monitor(check_interval=60, enabled=True)
        time.sleep(0.1)  # Let it initialize
        stop_monitor()
        return True
    
    return measure_component_overhead("ProcessMonitor", test_monitor)


def audit_dev_audit_lightweight() -> Dict[str, Any]:
    """Audit DevAudit overhead (lightweight check)."""
    print("[4/7] Dev Audit (Lightweight)...")
    from codesentinel.core.dev_audit import DevAudit
    from codesentinel.utils.config import ConfigManager
    from codesentinel.utils.alerts import AlertManager
    
    def test_audit():
        config_mgr = ConfigManager()
        alert_mgr = AlertManager(config_mgr)
        audit = DevAudit(Path.cwd(), alert_mgr, config_mgr)
        # Run brief audit
        results = audit.run_brief()
        return results
    
    return measure_component_overhead("DevAudit_Brief", test_audit)


def audit_file_integrity_check() -> Dict[str, Any]:
    """Audit File Integrity check overhead."""
    print("[5/7] File Integrity Check...")
    from codesentinel.utils.file_integrity import FileIntegrityValidator
    
    def test_integrity():
        validator = FileIntegrityValidator(Path.cwd(), {'enabled': True})
        # Try to load and verify (may not exist)
        try:
            validator.load_baseline()
            results = validator.verify_integrity()
        except FileNotFoundError:
            # No baseline exists, that's okay for overhead test
            results = {'status': 'no_baseline'}
        return results
    
    return measure_component_overhead("FileIntegrity", test_integrity)


def audit_cli_overhead() -> Dict[str, Any]:
    """Audit CLI initialization overhead."""
    print("[6/7] CLI Initialization...")
    
    def test_cli():
        # Just measure import overhead
        from codesentinel.cli import main
        return True
    
    return measure_component_overhead("CLI_Init", test_cli)


def audit_full_codesentinel_init() -> Dict[str, Any]:
    """Audit full CodeSentinel initialization."""
    print("[7/7] Full CodeSentinel Init...")
    from codesentinel.core import CodeSentinel
    
    def test_init():
        cs = CodeSentinel()
        status = cs.get_status()
        return status
    
    return measure_component_overhead("CodeSentinel_Full", test_init)


def main():
    """Run complete global resource overhead audit."""
    print("=" * 70)
    print("CodeSentinel Global Resource Overhead Audit")
    print("=" * 70)
    print("\nPrinciple: SECURITY > EFFICIENCY > MINIMALISM")
    print("Auditing EFFICIENCY across all components.\n")
    
    # System info
    print(f"System Information:")
    print(f"  CPU Count: {psutil.cpu_count()}")
    print(f"  Memory Total: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    print(f"  Memory Available: {psutil.virtual_memory().available / (1024**3):.2f} GB")
    print(f"  Python Version: {sys.version}")
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'system': {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'memory_available_gb': psutil.virtual_memory().available / (1024**3),
            'python_version': sys.version
        },
        'components': []
    }
    
    # Run audits for each component
    print("\nAuditing Components:")
    print("=" * 70)
    
    audits = [
        audit_config_manager,
        audit_alert_manager,
        audit_process_monitor,
        audit_dev_audit_lightweight,
        audit_file_integrity_check,
        audit_cli_overhead,
        audit_full_codesentinel_init
    ]
    
    for audit_func in audits:
        try:
            result = audit_func()
            results['components'].append(result)
        except Exception as e:
            print(f"  ERROR: {e}")
            results['components'].append({
                'component': audit_func.__name__,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - Global Resource Overhead")
    print("=" * 70)
    
    total_mem = sum(c.get('memory_delta_mb', 0) for c in results['components'] if c['success'])
    total_time = sum(c.get('duration_ms', 0) for c in results['components'] if c['success'])
    
    print(f"\nTotal Overhead:")
    print(f"  Initialization Time: {total_time:.1f} ms")
    print(f"  Memory Footprint: {total_mem:.2f} MB")
    
    print(f"\nPer-Component Breakdown:")
    for component in results['components']:
        if component['success']:
            name = component['component']
            time_ms = component.get('duration_ms', 0)
            mem_mb = component.get('memory_delta_mb', 0)
            print(f"  {name:25s}: {time_ms:6.1f} ms, {mem_mb:6.2f} MB")
        else:
            print(f"  {component['component']:25s}: FAILED - {component.get('error', 'Unknown error')}")
    
    print(f"\nEfficiency Assessment:")
    if total_time < 1000 and total_mem < 50:
        print("  ✓ EXCELLENT - Minimal overhead, production-ready")
    elif total_time < 3000 and total_mem < 100:
        print("  ✓ GOOD - Acceptable overhead for regular use")
    elif total_time < 5000 and total_mem < 200:
        print("  ⚠ MODERATE - Consider optimization for high-frequency use")
    else:
        print("  ⚠ HIGH - Optimization recommended")
    
    # Identify heaviest components
    if results['components']:
        heaviest_time = max((c for c in results['components'] if c['success']), 
                           key=lambda x: x.get('duration_ms', 0), default=None)
        heaviest_mem = max((c for c in results['components'] if c['success']), 
                          key=lambda x: x.get('memory_delta_mb', 0), default=None)
        
        if heaviest_time:
            print(f"\nHeaviest Component (Time): {heaviest_time['component']} ({heaviest_time['duration_ms']:.1f} ms)")
        if heaviest_mem:
            print(f"Heaviest Component (Memory): {heaviest_mem['component']} ({heaviest_mem['memory_delta_mb']:.2f} MB)")
    
    # Save results
    output_file = Path.cwd() / "audit_global_overhead_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
