#!/usr/bin/env python3
"""
Tuff Bot - One-Click Installer
Run this in Python 3.12+ to install everything and start the bot
"""

import subprocess
import sys
import os

def install_packages():
    """Install all packages from requirements.txt"""
    print("=" * 60)
    print("🎯 Tuff Bot - Auto Installer")
    print("=" * 60)
    print()
    
    # Upgrade pip, setuptools, wheel
    print("📦 Upgrading pip, setuptools, wheel...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
    print("✅ Pip tools upgraded\n")
    
    # Install from requirements.txt
    print("📥 Installing dependencies from requirements.txt...")
    print("   This may take 3-5 minutes...")
    print()
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print()
        print("=" * 60)
        print("✅ Installation Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run: python launcher.py")
        print("  2. Adjust settings in the GUI")
        print("  3. Click 'Run Tuff Bot'")
        print("  4. Hold 'E' in your game to lock-on!")
        print()
        print("=" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print()
        print("❌ Installation failed!")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print()
    print(f"Python Version: {sys.version}")
    print()
    
    # Check Python version
    if sys.version_info.major != 3 or sys.version_info.minor < 12:
        print("⚠️  WARNING: This bot is optimized for Python 3.12+")
        print(f"You are using Python {sys.version_info.major}.{sys.version_info.minor}")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Please install Python 3.12 from https://www.python.org/downloads/release/python-31212/")
            sys.exit(1)
    else:
        print("✅ Python 3.12+ detected - Perfect!")
        print()
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ Error: requirements.txt not found!")
        print("Make sure you're in the Tuffromai folder")
        sys.exit(1)
    
    # Install packages
    success = install_packages()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
