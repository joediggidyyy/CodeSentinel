#!/usr/bin/env python3
"""
CodeSentinel v1.0.3.beta - PyPI Publication Script

This script uploads the v1.0.3.beta distributions to PyPI.
It will prompt for credentials if not already configured in ~/.pypirc

Usage:
    python publish_to_pypi.py [--test]  # --test for test.pypi.org
    python publish_to_pypi.py            # production PyPI
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Publish CodeSentinel v1.0.3.beta to PyPI"""
    
    use_test = "--test" in sys.argv
    repo = "testpypi" if use_test else "pypi"
    repo_name = "test.pypi.org" if use_test else "pypi.org"
    
    print(f"\n{'='*80}")
    print(f"CodeSentinel v1.0.3.beta - PyPI Publication")
    print(f"{'='*80}")
    print(f"\nTarget Repository: {repo_name}")
    print(f"Distributions to upload:")
    print(f"  - codesentinel-1.0.3b0.tar.gz (91 KB)")
    print(f"  - codesentinel-1.0.3b0-py3-none-any.whl (77 KB)")
    
    # Check distributions exist
    dist_dir = Path("dist")
    sdist = dist_dir / "codesentinel-1.0.3b0.tar.gz"
    wheel = dist_dir / "codesentinel-1.0.3b0-py3-none-any.whl"
    
    if not sdist.exists():
        print(f"\n❌ ERROR: Source distribution not found: {sdist}")
        return 1
    
    if not wheel.exists():
        print(f"\n❌ ERROR: Wheel distribution not found: {wheel}")
        return 1
    
    print(f"\n✅ Both distributions found")
    
    # Build twine command
    cmd = [
        "python", "-m", "twine", "upload",
        "--repository", repo,
        str(sdist),
        str(wheel)
    ]
    
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
        print("✅ Upload successful!")
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
