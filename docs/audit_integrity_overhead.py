"""
Resource Overhead Audit - File Integrity Validation System

Analyzes CPU, memory, and I/O overhead of the integrity validation workflow.

SECURITY > EFFICIENCY > MINIMALISM
"""

import time
import psutil
import os
from pathlib import Path
from typing import Dict, Any
import json

# Import the integrity validator
from codesentinel.utils.file_integrity import FileIntegrityValidator


def measure_resource_usage(func, *args, **kwargs) -> Dict[str, Any]:
    """
    Measure resource usage for a function call.
    
    Returns:
        Dict with timing, memory, CPU, and I/O metrics
    """
    process = psutil.Process()
    
    # Baseline measurements
    cpu_before = process.cpu_percent(interval=0.1)
    mem_before = process.memory_info()
    io_before = process.io_counters() if hasattr(process, 'io_counters') else None
    
    # Execute function with timing
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    
    # Post measurements
    cpu_after = process.cpu_percent(interval=0.1)
    mem_after = process.memory_info()
    io_after = process.io_counters() if hasattr(process, 'io_counters') else None
    
    # Calculate deltas
    duration = end_time - start_time
    mem_delta = mem_after.rss - mem_before.rss
    cpu_delta = cpu_after - cpu_before
    
    io_delta = {}
    if io_before and io_after:
        io_delta = {
            'read_bytes': io_after.read_bytes - io_before.read_bytes,
            'write_bytes': io_after.write_bytes - io_before.write_bytes,
            'read_count': io_after.read_count - io_before.read_count,
            'write_count': io_after.write_count - io_before.write_count,
        }
    
    return {
        'duration_seconds': duration,
        'memory_delta_bytes': mem_delta,
        'memory_delta_mb': mem_delta / (1024 * 1024),
        'cpu_percent_delta': cpu_delta,
        'io': io_delta,
        'result': result
    }


def audit_baseline_generation(workspace_root: Path) -> Dict[str, Any]:
    """Audit overhead of baseline generation."""
    print("\n" + "=" * 70)
    print("AUDITING: Baseline Generation")
    print("=" * 70)
    
    validator = FileIntegrityValidator(workspace_root, {
        'enabled': True,
        'hash_algorithm': 'sha256',
        'whitelist_patterns': [],
        'critical_files': []
    })
    
    metrics = measure_resource_usage(validator.generate_baseline)
    
    baseline = metrics['result']
    stats = baseline.get('statistics', {})
    
    print(f"\nFiles processed: {stats.get('total_files', 0)}")
    print(f"Duration: {metrics['duration_seconds']:.3f} seconds")
    print(f"Memory delta: {metrics['memory_delta_mb']:.2f} MB")
    print(f"CPU delta: {metrics['cpu_percent_delta']:.1f}%")
    
    if metrics['io']:
        print(f"I/O Read: {metrics['io']['read_bytes'] / (1024*1024):.2f} MB ({metrics['io']['read_count']} ops)")
        print(f"I/O Write: {metrics['io']['write_bytes'] / (1024*1024):.2f} MB ({metrics['io']['write_count']} ops)")
    
    # Calculate per-file overhead
    if stats.get('total_files', 0) > 0:
        per_file_time = metrics['duration_seconds'] / stats['total_files']
        per_file_mem = metrics['memory_delta_bytes'] / stats['total_files']
        print(f"\nPer-file overhead:")
        print(f"  Time: {per_file_time * 1000:.2f} ms")
        print(f"  Memory: {per_file_mem / 1024:.2f} KB")
    
    return {
        'operation': 'baseline_generation',
        'files_processed': stats.get('total_files', 0),
        'metrics': metrics
    }


def audit_verification(workspace_root: Path, validator: FileIntegrityValidator) -> Dict[str, Any]:
    """Audit overhead of integrity verification."""
    print("\n" + "=" * 70)
    print("AUDITING: Integrity Verification")
    print("=" * 70)
    
    metrics = measure_resource_usage(validator.verify_integrity)
    
    results = metrics['result']
    stats = results.get('statistics', {})
    
    print(f"\nFiles checked: {stats.get('files_checked', 0)}")
    print(f"Duration: {metrics['duration_seconds']:.3f} seconds")
    print(f"Memory delta: {metrics['memory_delta_mb']:.2f} MB")
    print(f"CPU delta: {metrics['cpu_percent_delta']:.1f}%")
    
    if metrics['io']:
        print(f"I/O Read: {metrics['io']['read_bytes'] / (1024*1024):.2f} MB ({metrics['io']['read_count']} ops)")
        print(f"I/O Write: {metrics['io']['write_bytes'] / (1024*1024):.2f} MB ({metrics['io']['write_count']} ops)")
    
    # Calculate per-file overhead
    if stats.get('files_checked', 0) > 0:
        per_file_time = metrics['duration_seconds'] / stats['files_checked']
        per_file_mem = metrics['memory_delta_bytes'] / stats['files_checked']
        print(f"\nPer-file overhead:")
        print(f"  Time: {per_file_time * 1000:.2f} ms")
        print(f"  Memory: {per_file_mem / 1024:.2f} KB")
    
    return {
        'operation': 'verification',
        'files_checked': stats.get('files_checked', 0),
        'violations_found': len(results.get('violations', [])),
        'metrics': metrics
    }


def audit_baseline_save_load(workspace_root: Path, validator: FileIntegrityValidator) -> Dict[str, Any]:
    """Audit overhead of baseline save/load operations."""
    print("\n" + "=" * 70)
    print("AUDITING: Baseline Save/Load")
    print("=" * 70)
    
    # Save
    save_metrics = measure_resource_usage(validator.save_baseline)
    print(f"\nSave operation:")
    print(f"  Duration: {save_metrics['duration_seconds']:.3f} seconds")
    print(f"  Memory delta: {save_metrics['memory_delta_mb']:.2f} MB")
    
    baseline_file = workspace_root / ".codesentinel_integrity.json"
    baseline_size = baseline_file.stat().st_size if baseline_file.exists() else 0
    print(f"  Baseline file size: {baseline_size / 1024:.2f} KB")
    
    # Load
    load_metrics = measure_resource_usage(validator.load_baseline)
    print(f"\nLoad operation:")
    print(f"  Duration: {load_metrics['duration_seconds']:.3f} seconds")
    print(f"  Memory delta: {load_metrics['memory_delta_mb']:.2f} MB")
    
    return {
        'operation': 'save_load',
        'baseline_size_bytes': baseline_size,
        'save_metrics': save_metrics,
        'load_metrics': load_metrics
    }


def main():
    """Run complete resource overhead audit."""
    print("=" * 70)
    print("CodeSentinel File Integrity - Resource Overhead Audit")
    print("=" * 70)
    print("\nPrinciple: SECURITY > EFFICIENCY > MINIMALISM")
    print("This audit focuses on EFFICIENCY while maintaining SECURITY.\n")
    
    workspace_root = Path.cwd()
    print(f"Workspace: {workspace_root}")
    
    # Get system info
    print(f"\nSystem Information:")
    print(f"  CPU Count: {psutil.cpu_count()}")
    print(f"  Memory Total: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    print(f"  Memory Available: {psutil.virtual_memory().available / (1024**3):.2f} GB")
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'workspace': str(workspace_root),
        'system': {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'memory_available_gb': psutil.virtual_memory().available / (1024**3),
        },
        'audits': []
    }
    
    # Audit 1: Baseline Generation
    audit1 = audit_baseline_generation(workspace_root)
    results['audits'].append(audit1)
    
    # Create validator with baseline and save it
    validator = FileIntegrityValidator(workspace_root, {
        'enabled': True,
        'hash_algorithm': 'sha256',
        'whitelist_patterns': ['**/.codesentinel_integrity.json'],
        'critical_files': []
    })
    
    # Use the baseline from audit1
    validator.baseline = audit1['metrics']['result']
    
    # Audit 3: Save/Load (do this before verification to have a baseline file)
    audit3 = audit_baseline_save_load(workspace_root, validator)
    results['audits'].append(audit3)
    
    # Reload baseline for verification
    validator.load_baseline()
    
    # Audit 2: Verification
    audit2 = audit_verification(workspace_root, validator)
    results['audits'].append(audit2)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - File Integrity Resource Overhead")
    print("=" * 70)
    
    total_files = audit1['files_processed']
    gen_time = audit1['metrics']['duration_seconds']
    verify_time = audit2['metrics']['duration_seconds']
    
    print(f"\nWorkspace: {total_files} files")
    print(f"Baseline Generation: {gen_time:.3f}s ({total_files/gen_time if gen_time > 0 else 0:.0f} files/sec)")
    print(f"Verification: {verify_time:.3f}s ({total_files/verify_time if verify_time > 0 else 0:.0f} files/sec)")
    
    print(f"\nMemory Overhead:")
    print(f"  Generation: {audit1['metrics']['memory_delta_mb']:.2f} MB")
    print(f"  Verification: {audit2['metrics']['memory_delta_mb']:.2f} MB")
    print(f"  Baseline Storage: {audit3['baseline_size_bytes'] / 1024:.2f} KB")
    
    print(f"\nEfficiency Assessment:")
    if gen_time < 5.0 and verify_time < 3.0:
        print("  ✓ EXCELLENT - Low overhead, suitable for frequent checks")
    elif gen_time < 10.0 and verify_time < 5.0:
        print("  ✓ GOOD - Acceptable overhead for regular checks")
    elif gen_time < 30.0 and verify_time < 10.0:
        print("  ⚠ MODERATE - Consider optimizing for large workspaces")
    else:
        print("  ⚠ HIGH - Optimization recommended for production use")
    
    # Save detailed results
    output_file = workspace_root / "audit_integrity_overhead_results.json"
    with open(output_file, 'w') as f:
        # Remove 'result' objects which may not be JSON serializable
        for audit in results['audits']:
            if 'metrics' in audit and 'result' in audit['metrics']:
                del audit['metrics']['result']
            if 'save_metrics' in audit and 'result' in audit['save_metrics']:
                del audit['save_metrics']['result']
            if 'load_metrics' in audit and 'result' in audit['load_metrics']:
                del audit['load_metrics']['result']
        
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
