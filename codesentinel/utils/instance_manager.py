"""
Inter-Process Communication and Instance Management for CodeSentinel.

This module provides functionality for:
- Discovering other running CodeSentinel instances.
- Establishing communication between instances.
- Managing a shared state or registry of active instances.
"""

import os
import psutil
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

# Use a consistent temporary directory for instance discovery files
INSTANCE_REGISTRY_DIR = Path(tempfile.gettempdir()) / "codesentinel_registry"
INSTANCE_REGISTRY_DIR.mkdir(exist_ok=True)

def get_process_fingerprint(proc: psutil.Process) -> str:
    """
    Create a stable fingerprint for a process to identify it as a CodeSentinel instance.
    """
    try:
        cmd = " ".join(proc.cmdline())
        # Normalize path separators for consistency
        return cmd.replace("\\", "/")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return ""

def is_codesentinel_instance(proc: psutil.Process) -> bool:
    """
    Check if a process is a CodeSentinel instance based on its command line.
    Excludes the current process.
    """
    if proc.pid == os.getpid():
        return False
    
    try:
        # A process is a CodeSentinel instance if 'codesentinel' is in its command line.
        # This is a simple but effective first-pass filter.
        cmdline = " ".join(proc.cmdline()).lower()
        if "codesentinel" in cmdline and "python" in cmdline:
            return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    return False

def find_instances() -> List[Dict[str, Any]]:
    """
    Find all running CodeSentinel instances on the machine, excluding the current process.
    """
    instances = []
    current_user = psutil.Process(os.getpid()).username()

    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'create_time']):
        try:
            # Security: Only consider processes run by the same user
            if proc.info['username'] != current_user:
                continue

            if is_codesentinel_instance(proc):
                instances.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cmdline": " ".join(proc.info['cmdline']) if proc.info['cmdline'] else "",
                    "create_time": proc.info['create_time']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
            # Process may have terminated or we may not have access
            continue
            
    return instances

def register_instance():
    """
    Register the current process as an active CodeSentinel instance.
    This creates a PID file that other instances can discover.
    """
    pid = os.getpid()
    pid_file = INSTANCE_REGISTRY_DIR / f"{pid}.json"
    
    proc = psutil.Process(pid)
    
    instance_data = {
        "pid": pid,
        "username": proc.username(),
        "cmdline": " ".join(proc.cmdline()),
        "create_time": proc.create_time(),
        "status": "running"
    }
    
    with open(pid_file, "w") as f:
        json.dump(instance_data, f)
        
    return pid_file

def unregister_instance():
    """
    Unregister the current process by deleting its PID file.
    Should be called on graceful shutdown.
    """
    pid = os.getpid()
    pid_file = INSTANCE_REGISTRY_DIR / f"{pid}.json"
    if pid_file.exists():
        pid_file.unlink()

def get_registered_instances() -> List[Dict[str, Any]]:
    """
    List all instances from the file-based registry.
    """
    instances = []
    for f in INSTANCE_REGISTRY_DIR.glob("*.json"):
        try:
            pid = int(f.stem)
            if psutil.pid_exists(pid):
                with open(f, "r") as fp:
                    instances.append(json.load(fp))
            else:
                # Clean up stale PID file
                f.unlink()
        except (ValueError, json.JSONDecodeError):
            # Ignore malformed files
            continue
    return instances
