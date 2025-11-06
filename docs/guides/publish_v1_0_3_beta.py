#!/usr/bin/env python3
"""
CodeSentinel v1.0.3.beta Publication Script
Publication automation for PyPI upload
"""

import subprocess
import sys
from pathlib import Path

def validate_distributions():
    """Validate distribution files before upload."""
    print("\n" + "="*80)
    print("STEP 1: Validating Distribution Files")
    print("="*80)
    
    dist_dir = Path("dist")
    distributions = list(dist_dir.glob("codesentinel-1.0.3b0*"))
    
    if not distributions:
        print("ERROR: No distributions found for v1.0.3b0")
        return False
    
    print(f"\nFound {len(distributions)} distributions:")
    for dist in distributions:
        size_kb = dist.stat().st_size / 1024
        print(f"  ✅ {dist.name} ({size_kb:.1f} KB)")
    
    # Validate with twine
    print("\nValidating with twine...")
    try:
        result = subprocess.run(
            ["python", "-m", "twine", "check"] + [str(d) for d in distributions],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ All distributions passed validation")
            return True
        else:
            print("❌ Validation failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

def publish_to_test_pypi():
    """Publish to test.pypi.org."""
    print("\n" + "="*80)
    print("STEP 2: Publishing to test.pypi.org")
    print("="*80)
    
    print("\nThis will upload v1.0.3b0 to test.pypi.org")
    print("You will need your test.pypi.org token when prompted")
    
    response = input("\nProceed with upload to test PyPI? (y/n): ").strip().lower()
    if response != 'y':
        print("Upload cancelled.")
        return False
    
    try:
        result = subprocess.run(
            ["python", "-m", "twine", "upload", "--repository", "testpypi",
             "dist/codesentinel-1.0.3b0.tar.gz",
             "dist/codesentinel-1.0.3b0-py3-none-any.whl"],
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def publish_to_production_pypi():
    """Publish to production pypi.org."""
    print("\n" + "="*80)
    print("STEP 3: Publishing to production PyPI")
    print("="*80)
    
    print("\nBefore publishing to production, verify on test.pypi.org:")
    print("  1. Visit: https://test.pypi.org/project/codesentinel/")
    print("  2. Check version 1.0.3b0 appears")
    print("  3. Test install: pip install --index-url https://test.pypi.org/simple/ codesentinel==1.0.3b0")
    
    response = input("\nHave you validated test.pypi.org? (y/n): ").strip().lower()
    if response != 'y':
        print("Publication to production cancelled.")
        return False
    
    print("\nThis will upload v1.0.3b0 to production PyPI")
    print("You will need your pypi.org token when prompted")
    
    response = input("\nProceed with upload to production PyPI? (y/n): ").strip().lower()
    if response != 'y':
        print("Upload cancelled.")
        return False
    
    try:
        result = subprocess.run(
            ["python", "-m", "twine", "upload",
             "dist/codesentinel-1.0.3b0.tar.gz",
             "dist/codesentinel-1.0.3b0-py3-none-any.whl"],
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def verify_production_upload():
    """Verify production upload was successful."""
    print("\n" + "="*80)
    print("STEP 4: Verifying Production Upload")
    print("="*80)
    
    print("\nAfter upload completes, verify at:")
    print("  ✅ https://pypi.org/project/codesentinel/")
    print("\nLook for version 1.0.3b0 (marked as pre-release/beta)")

def main():
    """Main publication workflow."""
    print("\n" + "="*80)
    print("CodeSentinel v1.0.3.beta - PyPI Publication")
    print("="*80)
    
    # Step 1: Validate
    if not validate_distributions():
        print("\n❌ Validation failed. Publication cancelled.")
        sys.exit(1)
    
    # Step 2: Test PyPI
    if not publish_to_test_pypi():
        print("\n❌ Test PyPI upload failed.")
        sys.exit(1)
    
    print("\n✅ Test PyPI upload successful!")
    print("Now testing installation from test.pypi.org...")
    
    # Step 3: Production PyPI
    if not publish_to_production_pypi():
        print("\n❌ Production PyPI upload failed.")
        sys.exit(1)
    
    print("\n✅ Production PyPI upload successful!")
    
    # Step 4: Verify
    verify_production_upload()
    
    print("\n" + "="*80)
    print("✅ Publication Complete!")
    print("="*80)
    print("\nNext steps:")
    print("  1. Create GitHub release: v1.0.3-beta")
    print("  2. Announce to beta testers")
    print("  3. Collect feedback for 2 weeks")
    print("  4. Plan v1.0.3 final release")

if __name__ == "__main__":
    main()
