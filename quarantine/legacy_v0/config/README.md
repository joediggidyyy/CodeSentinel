# Configuration Files & Settings

`Joe Waller`  
email: `rellawj@unc.edu` \
github: `joediggidyyy` \
url: `https://github.com/joediggidyyy/`

---

This directory contains configuration files and settings used by various tools in the development environment.

## Configuration Files

### `size_whitelist.json` - **File Size Formatting Limits**

**Purpose**: Defines file size limits for automatic formatting to prevent performance issues

**Structure:**

```json
{
  "max_file_size_kb": 10,
  "whitelisted_files": [
    "path/to/large/file.ipynb"
  ],
  "excluded_patterns": [
    "**/*.min.js",
    "**/node_modules/**"
  ]
}
```

**Usage**: Referenced by `../formatting/format_daemon.py` and `../formatting/format_control.py`

### `nb_analysis.json` - **Notebook Analysis Configuration**

**Purpose**: Configuration settings for notebook analysis and reporting tools

**Settings:**

- Analysis depth and scope
- Report generation preferences
- Output format specifications
- Performance optimization settings

**Usage**: Used by analysis tools for report generation and formatting

### `.fix_r_cells_cache.json` - **R Styling Cache**

**Purpose**: Cache file for R cell styling operations to improve performance

**Contents:**

- Previously processed R cells
- Styling results and timestamps
- Error tracking and recovery data
- Performance optimization data

**Management**: Automatically managed by `../r-styling/fix_r_cells.R`

### `format_daemon.pid` - **Format Daemon Process ID**

**Purpose**: Stores the process ID of the running format daemon

**Usage:**

- Process management for `../formatting/format_daemon.py`
- Cleanup and restart operations
- Status checking and monitoring

## File Management

**Automatic Cleanup:**

- Cache files are periodically cleaned
- Old PID files are removed on restart
- Temporary configuration is purged

**Manual Management:**

```bash
# Clear R styling cache
rm tools/config/.fix_r_cells_cache.json

# Remove daemon PID file
rm tools/config/format_daemon.pid

# Reset size whitelist (use carefully)
# Edit tools/config/size_whitelist.json manually
```

## Integration Points

**Formatting System:**

- Size limits prevent performance issues
- Daemon PID management ensures single instance
- Cache improves R styling performance

**Analysis Tools:**

- Notebook analysis configuration
- Report generation settings
- Performance optimization

## Related Tools

- **Formatting**: `../formatting/` - Uses size_whitelist.json
- **R Styling**: `../r-styling/` - Uses .fix_r_cells_cache.json  
- **Analysis**: `../analysis/` - Uses nb_analysis.json
- **Monitoring**: `../monitoring/` - References configuration files

## Best Practices

1. **Size Whitelist**: Only add files that genuinely need large size limits
2. **Cache Management**: Let tools manage cache automatically unless troubleshooting
3. **PID Files**: Don't manually edit PID files while processes are running
4. **Backup**: Keep backups of custom configuration before major changes

---

`joediggidyyy | Configuration Files & Settings`
