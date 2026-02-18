#!/usr/bin/env python3
"""
Test script to verify the Voxtral application setup
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.9+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    required = ['websockets', 'numpy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Install missing packages with: pip install {' '.join(missing)}")
        return False
    return True

def check_files():
    """Check if all required files exist"""
    required_files = [
        'index.html',
        'style.css',
        'app.js',
        'server.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 60)
    print("Voxtral Application Setup Test")
    print("=" * 60)
    print()
    
    print("Checking Python version...")
    python_ok = check_python_version()
    print()
    
    print("Checking dependencies...")
    deps_ok = check_dependencies()
    print()
    
    print("Checking project files...")
    files_ok = check_files()
    print()
    
    print("=" * 60)
    if python_ok and deps_ok and files_ok:
        print("✅ All checks passed! Setup is complete.")
        print()
        print("Next steps:")
        print("1. Start the vLLM server (see README.md)")
        print("2. Run: python server.py")
        print("3. Open index.html in your browser")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 60)

if __name__ == "__main__":
    main()

# Made with Bob
