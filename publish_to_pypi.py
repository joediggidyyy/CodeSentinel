#!/usr/bin/env python3
"""
CodeSentinel v1.0.3 - PyPI Publication Script

This script uploads the v1.0.3 distributions to PyPI.
It will prompt for credentials if not already configured in ~/.pypirc

Usage:
    python publish_to_pypi.py [--test]  # --test for test.pypi.org
    python publish_to_pypi.py            # production PyPI
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Publish CodeSentinel v1.0.3 to PyPI"""

    # Pre-publication version verification
    print("🔍 Running pre-publication version verification...")
    result = subprocess.run([sys.executable, "tools/verify_version.py", "--strict"],
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ VERSION VERIFICATION FAILED!")
        print(result.stdout)
        print(result.stderr)
        return 1
    print(" Version verification passed")

    use_test = "--test" in sys.argv
    repo = "testpypi" if use_test else "pypi"
    repo_name = "test.pypi.org" if use_test else "pypi.org"

    print(f"\n{'='*80}")
    print(f"CodeSentinel v1.0.3 - PyPI Publication")
    print(f"{'='*80}")
    print(f"\nTarget Repository: {repo_name}")
    print(f"Distributions to upload:")
    print(f"  - codesentinel-1.0.3.tar.gz")
    print(f"  - codesentinel-1.0.3-py3-none-any.whl")

    # Check distributions exist (look for any v1.0.3 distributions)
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print(f"\n❌ ERROR: dist/ directory not found")
        return 1

    dist_files = list(dist_dir.glob("codesentinel-1.0.3*"))
    if len(dist_files) < 2:
        print(f"\n❌ ERROR: Expected at least 2 distribution files, found {len(dist_files)}")
        for f in dist_files:
            print(f"  - {f.name}")
        return 1

    print(f"\n Found {len(dist_files)} distribution files:")
    for f in dist_files:
        print(f"  - {f.name}")

    # Build twine command
    cmd = [
        "python", "-m", "twine", "upload",
        "--repository", repo
    ] + [str(f) for f in dist_files]

    print(f"\nExecuting: {' '.join(cmd)}")
    print(f"\n{'='*80}")
    print("When prompted, use:")
    print(f"  Username: __token__")
    print(f"  Password: [your {repo_name} token]")
    print(f"{'='*80}\n")
    
    # Execute upload
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n{'='*80}")
        print(" Upload successful!")
        print(f"{'='*80}")
        
        if use_test:
            print(f"\nNext steps:")
            print(f"1. Verify at: https://test.pypi.org/project/codesentinel/")
            print(f"2. Test installation:")
            print(f"   pip install --index-url https://test.pypi.org/simple/ codesentinel==1.0.3b0")
            print(f"3. If successful, run without --test for production PyPI")
        else:
            print(f"\nNext steps:")
            print(f"1. Verify at: https://pypi.org/project/codesentinel/")
            print(f"2. Install and test:")
            print(f"   pip install codesentinel==1.0.3b0")
            print(f"3. Create GitHub release with tag v1.0.3-beta")
            print(f"4. Merge feature branch to main")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Upload failed with error code {e.returncode}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
