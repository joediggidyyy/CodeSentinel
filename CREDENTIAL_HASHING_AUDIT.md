# Credential Hashing & Encryption Audit

**Date**: November 6, 2025  
**Status**: ⚠️ **AUDIT COMPLETE - CRITICAL FINDINGS**

---

## Executive Summary

**❌ NOT PROPERLY HASHED**: Credentials in CodeSentinel are **NOT hashed or encrypted** at rest. They are:

- ✅ **Removed from disk** (pruned before save) - GOOD
- ✅ **Not in version control** (excluded from Git) - GOOD  
- ❌ **NOT encrypted** - when stored, they're stored in plain text
- ❌ **NOT hashed** - no bcrypt/argon2/PBKDF2 implementation found

---

## Detailed Findings

### 1. Email Credentials ❌ NOT HASHED

**Location**: `codesentinel/utils/alerts.py` line 150

```python
password = config.get('password') or os.getenv('CODESENTINEL_EMAIL_PASSWORD')
# ...
server.login(username, password)  # Plain text password used directly
```

**Status**:

- ❌ No hashing implementation
- ❌ Password used directly in plain text for SMTP login
- ✅ Password NOT persisted to config files (removed before save)
- ✅ Expected to be in environment variable

**Issue**: If password is ever stored in config, it would be stored as plain text.

---

### 2. PyPI Token ❌ NOT HASHED

**Location**: `~/.pypirc`

```ini
[pypi]
username = __token__
password = pypi-AgEIcHl...  # Plain text token
```

**Status**:

- ❌ No hashing/encryption
- ✅ File permissions restricted to user only
- ✅ Outside repository

**Issue**: Token is stored in plain text, relies entirely on file permissions for security.

---

### 3. GitHub Token ❌ NOT HASHED

**Location**: Environment variable or config (pruned)

```python
gh.pop("access_token", None)  # Removed before save
gh.pop("token", None)
```

**Status**:

- ❌ No hashing implementation
- ✅ Tokens removed from config files
- ✅ Expected to be in environment variables

**Issue**: No encryption layer; relies on environment variable security.

---

### 4. File Integrity Hashing ✅ IMPLEMENTED (but not for credentials)

**Location**: `codesentinel/utils/file_integrity.py`

```python
import hashlib

DEFAULT_HASH_ALGORITHM = "sha256"  # Used for file integrity, NOT credentials
```

**Status**:

- ✅ SHA256 hashing implemented for file integrity checking
- ❌ NOT used for credential hashing
- ✅ Proper use case: detecting file modifications

**Note**: File integrity hashing is NOT the same as credential hashing.

---

### 5. Available Encryption Libraries

**Imports Found**:

- ✅ `cryptography` - Available but NOT used for credentials
- ✅ `keyring` - Available but NOT used
- ❌ No bcrypt, argon2, or PBKDF2 imports found

**Location**: `codesentinel/gui_launcher.py` lines 143-156

These packages are loaded but **not actively used** for credential encryption.

---

## The Gap: What's Missing

### Current Approach (Pruning Only)

```
┌─────────────────────────────────────┐
│ Application reads credential        │
│ from environment variable           │
├─────────────────────────────────────┤
│ Application uses it in memory       │
│ (plain text in RAM)                 │
├─────────────────────────────────────┤
│ Before saving config: PRUNE         │
│ (Remove password fields)            │
├─────────────────────────────────────┤
│ Config file saved WITHOUT password  │
│ (Plain text file, no sensitive data)│
└─────────────────────────────────────┘
```

### What Should Exist (Encrypted Storage)

```
┌─────────────────────────────────────┐
│ Administrator stores credential     │
│ via secure input prompt             │
├─────────────────────────────────────┤
│ Credential encrypted using:         │
│ - Fernet (cryptography)             │
│ - System keyring (OS-level)         │
│ - Or AES-256-GCM                    │
├─────────────────────────────────────┤
│ Encrypted credential saved to:      │
│ ~/.codesentinel/credentials.enc     │
├─────────────────────────────────────┤
│ Application decrypts at runtime     │
│ (only when needed)                  │
├─────────────────────────────────────┤
│ Credential used in memory (RAM)     │
│ then cleared                        │
└─────────────────────────────────────┘
```

---

## Security Analysis

### Current Risk Model (Medium Risk)

**Threat**: Local file system compromise

| Attack Vector | Current Protection | Risk |
|---|---|---|
| Reading `~/.pypirc` | File permissions (600) | 🟡 Medium - Root/admin bypass |
| Reading `codesentinel.json` | Excluded from Git | 🟢 Low - Not in repo |
| Env var hijacking | Process isolation | 🟡 Medium - Attacker with shell access |
| Memory dump | Process-level protection | 🟡 Medium - Debug/VM escape |

### Improved Risk Model (With Encryption)

| Attack Vector | Encryption Protection | Risk |
|---|---|---|
| Reading encrypted files | AES-256-GCM | 🟢 Low - Encrypted at rest |
| Env var hijacking | Not applicable | 🟢 Low - Decrypted on-demand |
| Memory dump | Credential in RAM only briefly | 🟢 Low - Minimized exposure |
| Keyring access | OS-level protection | 🟢 Low - Delegated to OS |

---

## Verification: No Hashing Detected

### Search Results: Zero Encryption Implementations

```bash
# Searching for encryption/hashing of credentials:
grep -r "bcrypt\|argon2\|scrypt\|pbkdf2\|Fernet" codesentinel/
# Result: NO MATCHES

# Searching for cryptography usage:
grep -r "from cryptography\|import cryptography" codesentinel/
# Result: Only in gui_launcher.py for dependency checking

# Searching for keyring usage:
grep -r "keyring\." codesentinel/
# Result: Only in gui_launcher.py for dependency checking
```

**Conclusion**: Encryption libraries are installed but NOT actively used for credential encryption.

---

## Claims vs Reality

### What SECURITY.md Claims

> "passwords and tokens are hashed and stored in specific well-guarded locations, called by reference only"

### What Code Actually Does

1. ✅ Stores location: `~/.pypirc` (well-guarded)
2. ✅ Called by reference: Uses environment variables
3. ❌ "hashed and stored" - **NOT implemented**
   - NOT hashed
   - Stored in plain text (plain `.ini` format)
   - Protected by file permissions only

---

## Recommendations

### Tier 1: Immediate (No Code Changes Required)

- ✅ Continue using environment variables for passwords
- ✅ Keep `~/.pypirc` with restricted permissions
- ✅ Ensure all secrets are in `.gitignore`
- ✅ Document that credentials are stored in plain text at rest
- ✅ Update SECURITY.md to be accurate

### Tier 2: Short-term (Recommended for v1.1.0)

Implement encrypted credential storage:

```python
# codesentinel/utils/secrets.py
from cryptography.fernet import Fernet
import keyring

class CredentialStore:
    """Secure credential storage with encryption."""
    
    def __init__(self):
        self.cipher = keyring.get_keyring()
    
    def store_credential(self, service: str, username: str, password: str):
        """Store credential encrypted in system keyring."""
        keyring.set_password(service, username, password)
    
    def retrieve_credential(self, service: str, username: str) -> str:
        """Retrieve credential from system keyring."""
        return keyring.get_password(service, username)
```

### Tier 3: Enterprise (For Future)

- [ ] Multi-factor authentication for credential access
- [ ] Audit logging for all credential operations
- [ ] Hardware security module (HSM) integration
- [ ] Credential rotation automation
- [ ] Zero-knowledge architecture

---

## What IS Protected

### ✅ Good Security Practices (Implemented)

1. **Secrets Pruning** - Passwords/tokens removed before config save
2. **Environment Variables** - No hardcoded credentials in code
3. **File Permissions** - PyPI token file locked to user
4. **.gitignore** - Config files excluded from Git
5. **Separation of Concerns** - Credentials kept separate from config

### ❌ What's Missing

1. **Encryption at Rest** - Credentials not encrypted when stored
2. **Hashing** - No hash verification for credential integrity
3. **Keyring Integration** - Not using OS-level credential storage
4. **Key Management** - No encryption key strategy
5. **Audit Logging** - No logging of credential access

---

## Compliance Impact

### SECURITY.md Claims

- ⚠️ "hashed and stored" - **INACCURATE** (stored plain text, not hashed)
- ⚠️ "well-guarded locations" - **PARTIALLY TRUE** (guarded by file permissions)
- ✅ "called by reference only" - **ACCURATE** (env vars, not inline)

### Recommendation

Update SECURITY.md to accurately describe current implementation:

```markdown
## Credential Management (Current v1.0.3)

Credentials are:
- ✅ Stored outside version control
- ✅ Protected by file permissions (~/.pypirc)
- ✅ Loaded from environment variables at runtime
- ✅ Removed from configuration files before save
- ❌ NOT encrypted at rest (plain text in ~/.pypirc)
- ❌ NOT hashed (stored as-is)

Plan for v1.1.0:
- Implement OS keyring integration
- Add Fernet-based encryption for credentials
- Implement audit logging
```

---

## Summary Table

| Aspect | Current | Status | Risk |
|---|---|---|---|
| **Credentials in Git** | None | ✅ Excluded | 🟢 None |
| **Credentials in Memory** | Plain text | ✅ Normal | 🟢 Expected |
| **Credentials at Rest** | Plain text | ❌ Unencrypted | 🟡 Medium |
| **File Permissions** | User-only (600) | ✅ Restrictive | 🟢 Low |
| **Encryption Available** | cryptography lib | ✅ Installed | 🔴 Unused |
| **Keyring Integration** | Not implemented | ❌ Missing | 🟡 Medium |
| **Key Management** | None | ❌ None | ⚠️ TBD |

---

## Action Items

### For Security Documentation

- [ ] Update SECURITY.md line 33 to reflect reality (not hashed)
- [ ] Create ENCRYPTION_ROADMAP.md for v1.1.0 improvements
- [ ] Document current threat model accurately
- [ ] Add migration guide for encrypted storage

### For Code

- [ ] Create `codesentinel/utils/secrets.py` with encryption (v1.1.0+)
- [ ] Integrate keyring for OS-level credential storage
- [ ] Add credential rotation utilities
- [ ] Implement audit logging for credential access

### For Operations

- [ ] Rotate existing credentials (tokens, passwords)
- [ ] Document credential setup procedure
- [ ] Create credential recovery procedure
- [ ] Set up monitoring for unauthorized credential access

---

**Status**: ⚠️ **Credentials are NOT hashed/encrypted** - properly managed but unencrypted at rest

**Next Steps**: Review recommendations and plan v1.1.0 encryption implementation
