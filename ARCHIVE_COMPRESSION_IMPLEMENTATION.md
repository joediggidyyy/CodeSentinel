# Archive Compression Implementation

## Overview

The quarantine_legacy_archive compression mechanism implements the QUARANTINE_LEGACY_ARCHIVE POLICY with automated monthly maintenance and mandatory security scanning.

## How It Works

### Location

- **Implementation File**: `codesentinel/utils/scheduler.py`
- **Method**: `_compress_quarantine_archive()` (new)
- **Integration**: Called during monthly maintenance tasks via `_run_monthly_tasks()`

### Compression Process

1. **Activation Check**
   - Runs as part of monthly maintenance (can also be called on-demand)
   - Skips if `quarantine_legacy_archive/` directory doesn't exist
   - Checks file modification time (only compresses if 30+ days old)

2. **Pre-Compression Security Scan** (MANDATORY per policy)
   - Scans all files in archive for suspicious patterns:
     - Credential patterns: `password`, `secret`, `api_key`, `token`, `credential`
     - Dangerous code: `rm -rf`, `delete`, `exec`, `eval`, `system`, `__import__`
     - Executable files: `.exe`, `.cmd`, `.bat`, `.ps1`
     - Malware indicators: `malware`, `trojan`, `virus`, `backdoor`
   - Calculates SHA256 hash of every file for integrity verification
   - Reports suspicious patterns (non-blocking - logs warning)

3. **Compression**
   - Creates `.tar.gz` archive with timestamp: `quarantine_legacy_archive_YYYYMMDD_HHMMSS.tar.gz`
   - Stores file hashes in accompanying `.hashes.json` file
   - **PRESERVES** original directory (does NOT delete per NON-DESTRUCTIVE policy)
   - Reports size reduction achieved

4. **Verification & Reporting**
   - Returns comprehensive results:
     - `archive_found`: Whether archive directory exists
     - `archive_size_before/after`: Size reduction metrics
     - `compressed`: Success status
     - `security_scan_results`: Pattern detection results
     - `issues`: Any failures encountered

## Configuration

### Trigger Conditions

```python
# Monthly maintenance triggers compression check
# Schedule via maintenance config:
maintenance_config.get('monthly', {}).get('enabled', False)
maintenance_config.get('monthly', {}).get('schedule', '1 09:00')  # 1st of month at 9 AM
```

### Inactivity Threshold

```python
# Only compresses if inactive for 30+ days
days_inactive = (datetime.now() - last_modified).days
if days_inactive >= 30:  # Compress only if 30+ days old
    # Proceed with compression
```

## Security Features

### Malicious File Detection

- Regex patterns scan for credential leakage
- Detects common malware signatures
- Identifies dangerous code patterns
- Flags executable files for review

### Integrity Preservation

- SHA256 hash of all files pre-compression
- Hashes stored in accompanying `.hashes.json`
- Allows future verification that archive wasn't tampered with

### Non-Destructive Operations

- Original directory kept (not deleted)
- Compressed archives timestamped uniquely
- Can be manually verified/decompressed anytime
- Policy compliance logged

## Usage Examples

### Manual Compression (On-Demand)

```python
from codesentinel.utils.scheduler import MaintenanceScheduler

scheduler = MaintenanceScheduler(config_manager, alert_manager)
result = scheduler._compress_quarantine_archive()

# Check results
if result['compressed']:
    print(f"Compressed: {result['archive_size_before']} -> {result['archive_size_after']}")
if result['security_scan_results']['suspicious_patterns_found']:
    print(f"Security issues: {result['security_scan_results']['issues']}")
```

### Automatic Compression (Monthly)

```bash
# Enable monthly maintenance
python -m codesentinel config set maintenance.monthly.enabled true

# Run monthly tasks (includes compression)
python tools/codesentinel/scheduler.py --schedule monthly

# Or trigger via CLI
codesentinel run --task monthly
```

## Maintenance

### Monitoring

- Check logs: `~/.codesentinel/maintenance.log`
- Look for "Archive compression completed" or warnings
- Review security scan results for patterns

### Cleanup (Manual)

```bash
# List compressed archives
ls -la quarantine_legacy_archive_*.tar.gz

# Verify archive integrity (using stored hashes)
cat quarantine_legacy_archive_20240115_091000.tar.gz.hashes.json

# Decompress if needed (recovery)
tar -xzf quarantine_legacy_archive_20240115_091000.tar.gz
```

### Policy Compliance

- Archives are considered "compressed historical data" (not clutter)
- Excluded from minimalism checks per policy
- Removal requires explicit approval (non-destructive)
- All operations logged with timestamps

## Future Enhancements

1. **Automatic Cleanup of Old Archives**
   - Keep N most recent compressed archives
   - Delete oldest after retention period (e.g., 1 year)

2. **Archive Inventory Tracking**
   - Maintain manifest of all compressed archives
   - Track compression/decompression events

3. **Integrity Verification Task**
   - Add quarterly task to verify archive hashes
   - Alert if tampering detected

4. **Incremental Compression**
   - Only include changed files since last compression
   - Reduce storage requirements over time

## Policy References

- **QUARANTINE_LEGACY_ARCHIVE POLICY**: `.github/copilot-instructions.md`
- **NON-DESTRUCTIVE POLICY**: Archive never deleted, only compressed
- **Security-First Principle**: Mandatory scanning before compression
- **Minimalism Alignment**: Archive not considered clutter, has operational purpose

## Testing

### Test Compression (Dry Run)

```bash
# Create test archive with sample files
mkdir -p quarantine_legacy_archive/test
echo "test content" > quarantine_legacy_archive/test/file.py

# Run compression manually
python -c "
from codesentinel.utils.scheduler import MaintenanceScheduler
from codesentinel.utils.config import ConfigManager
from codesentinel.utils.alerts import AlertManager

config = ConfigManager()
alerts = AlertManager(config)
scheduler = MaintenanceScheduler(config, alerts)
result = scheduler._compress_quarantine_archive()
print(result)
"
```

### Verify Results

```bash
# Check if tar.gz and hashes file created
ls -la quarantine_legacy_archive_*.tar.gz*

# Verify original directory still exists
ls -la quarantine_legacy_archive/
```

## Troubleshooting

### Archive Not Compressing

- Check if directory exists: `quarantine_legacy_archive/` present?
- Check age: `stat quarantine_legacy_archive/` (< 30 days won't compress)
- Check permissions: Can write to parent directory?

### Security Warnings

- Review `.hashes.json` for detected patterns
- Check logs for specific file warnings
- Files with patterns are NOT deleted, only warned about

### Verification Failures

- Compare current hashes with stored `.hashes.json`
- If mismatch detected, archive may have been tampered with
- Log alert and preserve original archive

## Related Files

- `codesentinel/utils/scheduler.py` - Implementation
- `codesentinel/utils/config.py` - Configuration management
- `.github/copilot-instructions.md` - Policy documentation
- `tools/config/maintenance.json` - Maintenance settings
