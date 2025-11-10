# Security Policy

## Supported Versions

CodeSentinel follows a security-first approach. The following versions are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Architecture

CodeSentinel is SEAM Protected™: **Security, Efficiency, And Minimalism**

This principle guides all architectural and operational decisions, with Security taking absolute priority.

### Core Security Features

- **No Hardcoded Credentials**: All sensitive data must be stored in environment variables or secure configuration files
- **Audit Logging**: All operations are logged with timestamps for security review
- **Configuration Validation**: Automatic validation and secure defaults for all configuration files
- **Dependency Scanning**: Automated vulnerability detection in dependencies
- **Process Monitoring**: Built-in daemon to detect and manage orphan processes

### Security Practices

1. **Credential Management** ⚠️ **PERMANENT DIRECTIVES**
   - **NEVER store plain text passwords or tokens in files**
   - **NEVER store passwords or tokens in executable files**
   - **NEVER commit credentials to the repository**
   - Use environment variables for sensitive data
   - Configuration files containing credentials should be in `.gitignore`
   - Email passwords, API keys, and tokens must be externalized
   - In CodeSentinel dev spaces: passwords and tokens are hashed and stored in specific well-guarded locations, called by reference only

2. **File Permissions**
   - Configuration files: Read/write for owner only (600)
   - Log files: Read/write for owner only (600)
   - Executable scripts: Read/execute for owner, read for group (750)

3. **Data Storage**
   - Sensitive data encrypted at rest when possible
   - Temporary files cleaned up after use
   - Log rotation to prevent information leakage

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### DO NOT

- Open a public GitHub issue for security vulnerabilities
- Discuss the vulnerability in public forums or chat channels
- Exploit the vulnerability beyond confirming it exists

### DO

1. **Report Privately**: Email security details to **<joediggidy3@gmail.com>** with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)
   - Your contact information for follow-up

2. **Subject Line**: Use format `[SECURITY] CodeSentinel v1.0.x - Brief Description`

3. **Encryption**: For highly sensitive reports, request PGP key via initial email

### Response Timeline

- **Initial Response**: Within 48 hours of report
- **Assessment**: Within 7 days we will confirm or request more information
- **Fix Development**: Priority based on severity (Critical: 7 days, High: 14 days, Medium: 30 days)
- **Disclosure**: Public disclosure only after patch is released and users have time to update

### What to Expect

1. We will acknowledge receipt of your vulnerability report
2. We will investigate and assess the severity
3. We will develop and test a fix
4. We will release a security patch
5. We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Update Process

Security patches are released as:

- **Critical**: Immediate patch release (1.0.x+1)
- **High**: Priority patch in next scheduled release
- **Medium/Low**: Included in regular maintenance releases

Users will be notified via:

- GitHub Security Advisories
- Release notes
- Repository README updates

## File Integrity Validation

CodeSentinel includes hash-based file integrity validation to detect unauthorized modifications in your workspace.

### Features

- **SHA256 Hash Verification**: Baseline hashing of all workspace files
- **Whitelist System**: Exclude frequently-changing files from integrity checks
- **Critical File Designation**: Mark security-sensitive files for priority monitoring
- **Integrated Audit Reporting**: Violations reported during `codesentinel !!!!` audits

### Setup

1. **Generate Initial Baseline**:

   ```bash
   codesentinel integrity generate
   ```

   This creates `.codesentinel_integrity.json` with hashes of all workspace files.

2. **Enable in Configuration**:
   Edit `codesentinel.json`:

   ```json
   {
     "integrity": {
       "enabled": true,
       "hash_algorithm": "sha256",
       "whitelist_patterns": [
         "**/.codesentinel_integrity.json",
         "**/test_*.py",
         "**/__pycache__/**"
       ],
       "critical_files": [
         ".github/copilot-instructions.md",
         "SECURITY.md",
         "codesentinel/core/dev_audit.py"
       ],
       "alert_on_violation": true
     }
   }
   ```

3. **Verify Integrity**:

   ```bash
   codesentinel integrity verify
   ```

   Or run a full development audit:

   ```bash
   codesentinel !!!!
   ```

### Managing Whitelists and Critical Files

**Add to Whitelist** (files that change frequently):

```bash
codesentinel integrity whitelist "**/*.log" "**/temp/**"
```

**Mark Files as Critical** (must not be modified):

```bash
codesentinel integrity critical "SECURITY.md" "codesentinel/core/dev_audit.py"
```

### Update Baseline After Authorized Changes

When you intentionally modify files:

```bash
# Verify changes are what you expect
codesentinel integrity verify

# If correct, regenerate baseline
codesentinel integrity generate
```

**Note**: Never auto-update the baseline. Always verify changes first to ensure no unauthorized modifications occurred.

### Integrity Violation Response

If integrity check fails:

1. **Review violations** - Check which files were modified/deleted/added
2. **Investigate** - Determine if changes were authorized
3. **For unauthorized changes**:
   - Restore files from backup or git
   - Scan for malware or security breaches
   - Review access logs and security events
4. **For authorized changes**:
   - Verify changes match expectations
   - Update baseline with `codesentinel integrity generate`

### Security Considerations

- Store baseline (`.codesentinel_integrity.json`) in version control
- Generate baseline only from known-good, verified workspace state
- Enable `alert_on_violation` to receive immediate notifications
- Mark security-critical files (config, auth, core) as critical
- Review integrity violations during code reviews and audits

## Security Best Practices for Users

### Installation

```bash
# Always verify package integrity
pip install codesentinel==1.0.0 --require-hashes

# Use virtual environments
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install codesentinel
```

### Configuration

```bash
# Secure configuration file permissions
chmod 600 ~/.codesentinel/config.json

# Use environment variables for sensitive data
export CODESENTINEL_SMTP_PASSWORD="your-password"
export CODESENTINEL_SLACK_TOKEN="your-token"
```

### Running

```bash
# Review audit logs regularly
codesentinel status

# Run security audits
codesentinel !!!!

# Monitor process activity
tail -f ~/.codesentinel/codesentinel.log
```

## Known Security Considerations

### Dependencies

CodeSentinel relies on the following external packages. Keep them updated:

- `requests` - HTTP library (security updates critical)
- `schedule` - Task scheduling (low risk)
- `psutil` - Process monitoring (review permissions)

### Process Monitor

The built-in process monitor daemon:

- Runs with user permissions (not root/admin)
- Only monitors child processes it creates
- Cannot terminate system or other user processes
- Logs all termination actions

### Network Operations

CodeSentinel may make network requests for:

- Alert delivery (email, Slack, webhooks)
- Dependency checking (PyPI)
- GitHub API access (if configured)

All network operations respect proxy settings and can be disabled in configuration.

## Security Audit History

- **v1.0.0-beta.1** (2025-11-03): Initial security review completed
  - No hardcoded credentials found
  - Configuration validation implemented
  - Audit logging active
  - Process monitor documented as PERMANENT feature

## Contact

For security-related questions or concerns:

- **Email**: <joediggidy3@gmail.com>
- **GitHub**: @joediggidyyy
- **Repository**: <https://github.com/joediggidyyy/CodeSentinel>

---

**Last Updated**: November 3, 2025  
**Version**: 1.0.0
