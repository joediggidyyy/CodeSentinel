# PyPI Token Security Configuration

## Overview

Your PyPI token is now stored securely in a local `.pypirc` configuration file instead of as an environment variable. This is the industry-standard approach for managing PyPI credentials.

## Location & Security

**File**: `~/.pypirc` (in your user home directory)
**Path**: `C:\Users\joedi\.pypirc`

**Security Features**:

- ✅ **Not in version control** - File is outside the repository
- ✅ **File permissions locked** - Only readable by your user account (DIGGIDY\joedi)
- ✅ **No environment variables** - Token never exposed in shell history or environment
- ✅ **Standard format** - Industry-standard `.pypirc` format recognized by all Python packaging tools

## Permissions

The `.pypirc` file has restrictive permissions set:

```
Owner: DIGGIDY\joedi
Access: Read/Write for user only
Inheritance: Disabled (no inherited permissions)
```

## How `twine` Uses This Configuration

When you run `twine upload`, it automatically reads from `~/.pypirc`:

```shell
# No credentials needed on command line anymore!
python -m twine upload dist/codesentinel-*.whl dist/codesentinel-*.tar.gz
```

The `.pypirc` configuration will be used automatically.

## File Contents Structure

```ini
[distutils]
index-servers =
    pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHl... (your token)
```

## For Team/CI/CD Environments

**IMPORTANT**: The `.pypirc` file is machine-specific and should NOT be:

- ❌ Committed to version control
- ❌ Shared between team members
- ❌ Used in CI/CD systems (use dedicated CI/CD secrets)

Each developer/CI system should have their own `.pypirc` with appropriate tokens.

## Using with `twine`

```shell
# Upload without any credential flags
twine upload dist/*

# twine automatically reads from ~/.pypirc
# No need to pass -u __token__ -p "token" anymore
```

## Rotating Your Token

If you need to update the token:

1. Generate a new token on PyPI
2. Open `~/.pypirc` in a text editor
3. Update the `password =` line with the new token
4. Save the file

The file permissions remain the same.

## Verification

To verify the configuration is working:

```shell
python -m twine check dist/codesentinel-1.0.3-py3-none-any.whl
```

This command tests that `twine` can read your configuration.

---

**Status**: ✅ PyPI token securely configured locally at `~/.pypirc`
