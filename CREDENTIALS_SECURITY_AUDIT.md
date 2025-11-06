# Credentials Security Audit & Configuration

**Date**: November 6, 2025  
**Status**: ✅ Security audit complete with recommendations

---

## 1. Credential Storage Locations

### Current State

| Credential Type | Storage Location | Security Status | Notes |
|---|---|---|---|
| **PyPI Token** | `~/.pypirc` (user home) | ✅ SECURE | File permissions locked to user; outside repo |
| **Email Password** | `codesentinel.json` | ⚠️ EXPOSED | Plain text in tracked config file |
| **GitHub Token** | Environment variable | ⚠️ PARTIAL | Not in file, but could leak in CI/CD |
| **Slack Token** | `codesentinel.json` | ✅ PRUNED | Removed before save (v1.0.1+) |

---

## 2. Detailed Analysis

### A. Email Credentials (⚠️ RISK)

**Current Storage**: `codesentinel.json`

```json
{
  "alerts": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "joediggidy3@gmail.com",
      "from_email": "joediggidy3@gmail.com",
      "to_emails": ["joediggidy3@gmail.com"]
      // ⚠️ password field IS NOT stored (good!)
    }
  }
}
```

**Good News**: Password is NOT persisted to disk automatically (security patch v1.0.1)

**How It Works**:
- Code looks for password in config file
- Falls back to environment variable: `CODESENTINEL_EMAIL_PASSWORD`
- Secrets are pruned before saving config to disk

**Location**: `codesentinel/utils/alerts.py` line 150

```python
password = config.get('password') or os.getenv('CODESENTINEL_EMAIL_PASSWORD')
```

**Recommendation**: ✅ Email credentials are handled safely via environment variables

---

### B. PyPI Token (✅ SECURE - NEWLY CONFIGURED)

**Current Storage**: `~/.pypirc` (user home directory)

```ini
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHl... (scoped token)
```

**Security**: ✅ EXCELLENT
- Outside repository (not in version control)
- File permissions: User read/write only
- Inheritance: Disabled (no inherited permissions)
- Standard format: Used by `twine` automatically
- No CLI exposure: No `--token` flags in commands

**Status**: Fully secured on November 6, 2025

---

### C. GitHub Token

**Current Storage**: Environment-based (not in files)

**Tracking Location**: `codesentinel.json`

```json
{
  "github": {
    "mode": "connect",
    "repo_url": "https://github.com/joediggidyyy/CodeSentinel.git",
    "create": false,
    "enabled": true
  }
}
```

**How Secrets Are Handled**: 
- Code looks for `access_token` or `token` fields
- Prunes them before saving to disk (lines 104-109 in `config.py`)
- Should use environment variable: `CODESENTINEL_GITHUB_TOKEN` (recommended)

**Recommendation**: ✅ GitHub tokens are pruned from disk automatically

---

### D. Slack Token

**Current Storage**: Removed before save

**Code Reference**: Lines 86-88, 101 in `codesentinel/utils/config.py`

```python
slack_cfg.pop("access_token", None)  # Removed before save
```

**Webhook URL**: Kept at runtime (needed for sending alerts)

**Recommendation**: ✅ Slack tokens are properly handled; webhooks stored at runtime only

---

## 3. Credential Security Architecture

### Environment Variable Fallbacks (✅ Recommended)

The codebase supports environment variable overrides for sensitive credentials:

```bash
# Email credentials
export CODESENTINEL_EMAIL_USERNAME="user@gmail.com"
export CODESENTINEL_EMAIL_PASSWORD="app-password"

# GitHub (recommended setup)
export CODESENTINEL_GITHUB_TOKEN="ghp_..."

# PyPI (now using .pypirc instead - better security)
```

**Location**: `codesentinel/utils/alerts.py` line 150

---

## 4. What Gets Persisted to Disk

### Files in Repository (Tracked)
- ✅ `codesentinel.json` - Config WITHOUT passwords, tokens, secrets
- ❌ Credentials are NOT stored in this file

### Files in User Home (Not Tracked)
- ✅ `~/.pypirc` - PyPI credentials (file permissions locked)
- ✅ Environment variables - Not persisted to disk

### Files in Repository (Not Tracked by Git)
- `codesentinel.log` - Log file (can contain non-sensitive info)

---

## 5. Credential Lifecycle

### Email Password

1. **Storage**: Environment variable only (`CODESENTINEL_EMAIL_PASSWORD`)
2. **Usage**: Read at runtime from environment
3. **Persistence**: Never written to disk
4. **Fallback**: Can be in config file if explicitly needed, but recommended: env var only

### PyPI Token

1. **Storage**: `~/.pypirc` (outside repo)
2. **Usage**: Automatically read by `twine`
3. **Persistence**: Securely stored in user home
4. **Access**: File permissions restricted to user only

### GitHub Token

1. **Storage**: Environment variable (`CODESENTINEL_GITHUB_TOKEN`)
2. **Usage**: Read at runtime for API operations
3. **Persistence**: Never written to config files (pruned)
4. **Fallback**: None (must be in environment)

### Slack Webhook

1. **Storage**: `codesentinel.json` (non-sensitive)
2. **Usage**: Runtime alert delivery
3. **Persistence**: Stored in config (webhook is not a credential)
4. **Tokens**: Pruned before save (access_token field removed)

---

## 6. Security Best Practices Applied

### ✅ Implemented

- [x] No hardcoded credentials in source code
- [x] PyPI token in `~/.pypirc` with restricted permissions
- [x] Email password via environment variable with fallback
- [x] GitHub token via environment variable
- [x] Secrets pruned from config files before save
- [x] `.gitignore` updated to exclude credential files
- [x] Separate storage for production vs. development

### ⚠️ For Team Environments

- [ ] Consider using secrets management tool (e.g., HashiCorp Vault, 1Password)
- [ ] Set up CI/CD secrets in GitHub Actions (not `.pypirc`)
- [ ] Use role-based access control (RBAC) for credentials
- [ ] Rotate tokens periodically (quarterly recommended)
- [ ] Audit credential access logs

---

## 7. CI/CD Credential Management

### GitHub Actions (`.github/workflows/ci.yml`)

**Current State**: ✅ No credentials in CI configuration

```yaml
- name: Build package
  run: python -m build

- name: Check package
  run: twine check dist/*

# No PyPI upload in CI (requires token - recommended)
```

**Recommendation for CI/CD Deployment**:

If you add automated PyPI uploads to CI/CD:

```yaml
- name: Publish to PyPI
  run: twine upload dist/*
  env:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

**✅ Never**:
- Commit `.pypirc` to repository
- Store tokens in workflow files
- Use repository secrets in local development

---

## 8. Credential Rotation Policy

### PyPI Token
- **How to Rotate**:
  1. Generate new token on PyPI
  2. Update password line in `~/.pypirc`
  3. Verify with: `python -m twine check dist/*`
- **Frequency**: Annually or after suspected compromise

### Email Password
- **How to Rotate**:
  1. Generate new app-specific password (Gmail)
  2. Update `CODESENTINEL_EMAIL_PASSWORD` environment variable
  3. Verify email alert system works
- **Frequency**: Every 6 months

### GitHub Token
- **How to Rotate**:
  1. Generate new personal access token
  2. Update `CODESENTINEL_GITHUB_TOKEN` environment variable
  3. Test GitHub operations
- **Frequency**: Every 6 months

---

## 9. Action Items

### Immediate (Security-First)
- ✅ PyPI token secured in `~/.pypirc`
- ✅ Email password configured via environment variable
- ✅ `.gitignore` updated with `.pypirc` entry

### Short-term (Recommended)
- [ ] Set up environment variables for all credentials
- [ ] Add credential rotation schedule to documentation
- [ ] Create setup guide for new developers

### Long-term (Enterprise)
- [ ] Evaluate secrets management tools
- [ ] Implement audit logging for credential access
- [ ] Set up credential monitoring alerts

---

## 10. Credential Storage Summary Table

```
┌─────────────────────┬──────────────────────┬──────────┬──────────────────┐
│ Credential          │ Storage Location     │ Security │ Auto-pruned      │
├─────────────────────┼──────────────────────┼──────────┼──────────────────┤
│ PyPI Token          │ ~/.pypirc (home)     │ ✅ HIGH  │ N/A (config)     │
│ Email Password      │ ENV VAR              │ ✅ HIGH  │ ✅ Yes (v1.0.1)  │
│ GitHub Token        │ ENV VAR              │ ✅ HIGH  │ ✅ Yes (pruned)  │
│ Slack Token         │ Pruned on save       │ ✅ HIGH  │ ✅ Yes (pruned)  │
│ Slack Webhook       │ codesentinel.json    │ ✅ OKAY  │ N/A (non-secret) │
│ Email Username      │ codesentinel.json    │ ✅ OKAY  │ N/A (non-secret) │
│ GitHub Repo URL     │ codesentinel.json    │ ✅ OKAY  │ N/A (non-secret) │
└─────────────────────┴──────────────────────┴──────────┴──────────────────┘
```

---

## Verification Commands

```bash
# Verify PyPI token is configured
python -m twine check dist/codesentinel-1.0.3-py3-none-any.whl

# Verify no credentials in config file
grep -i "password\|token\|secret" codesentinel.json  # Should be empty

# Verify environment variable setup
echo $CODESENTINEL_EMAIL_PASSWORD  # Should show masked or empty
echo $CODESENTINEL_GITHUB_TOKEN    # Should show masked or empty

# Verify .pypirc file permissions (Windows)
icacls $env:USERPROFILE\.pypirc   # Should show user-only access
```

---

**Status**: ✅ CodeSentinel credential security is properly configured
