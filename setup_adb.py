#!/usr/bin/env python3
"""
Download and setup ADB automatically for the application.
This allows distribution without requiring users to install Android SDK.
"""

import os
import sys
import zipfile
import urllib.request
from pathlib import Path

ADB_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
ADB_DIR = Path("tools/adb")

def download_adb():
    """Download ADB platform tools."""
    print("Downloading ADB platform tools...")
    print(f"URL: {ADB_URL}")
    
    zip_path = "platform-tools.zip"
    
    try:
        urllib.request.urlretrieve(ADB_URL, zip_path)
        print(f"✓ Downloaded to {zip_path}")
        return zip_path
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return None

def extract_adb(zip_path):
    """Extract ADB from zip file."""
    print(f"\nExtracting ADB...")
    
    try:
        # Create tools directory
        ADB_DIR.mkdir(parents=True, exist_ok=True)
        
        # Extract only necessary files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            files_to_extract = [
                'platform-tools/adb.exe',
                'platform-tools/AdbWinApi.dll',
                'platform-tools/AdbWinUsbApi.dll'
            ]
            
            for file in files_to_extract:
                try:
                    zip_ref.extract(file, ADB_DIR)
                    print(f"  ✓ {file}")
                except KeyError:
                    print(f"  ⚠ {file} not found in archive")
        
        # Move files from platform-tools subdirectory to adb directory
        platform_tools_dir = ADB_DIR / "platform-tools"
        if platform_tools_dir.exists():
            for file in platform_tools_dir.iterdir():
                file.rename(ADB_DIR / file.name)
            platform_tools_dir.rmdir()
        
        print(f"✓ Extracted to {ADB_DIR}")
        return True
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        return False

def verify_adb():
    """Verify ADB is working."""
    adb_exe = ADB_DIR / "adb.exe"
    
    if not adb_exe.exists():
        print(f"✗ ADB not found at {adb_exe}")
        return False
    
    print(f"\nVerifying ADB...")
    import subprocess
    try:
        result = subprocess.run(
            [str(adb_exe), "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ {version}")
            return True
    except Exception as e:
        print(f"✗ Verification failed: {e}")
    
    return False

def main():
    print("=" * 60)
    print("ADB Setup for AutoPQ")
    print("=" * 60)
    print()
    
    # Check if ADB already exists
    adb_exe = ADB_DIR / "adb.exe"
    if adb_exe.exists():
        print(f"ADB already exists at {adb_exe}")
        if verify_adb():
            print("\n✓ ADB is ready to use!")
            print(f"\nTo use bundled ADB, update your ADBClient to use:")
            print(f'  adb_path = "{adb_exe}"')
            return
        else:
            print("\n⚠ Existing ADB is not working, re-downloading...")
    
    # Download ADB
    zip_path = download_adb()
    if not zip_path:
        print("\n✗ Setup failed!")
        return
    
    # Extract ADB
    if not extract_adb(zip_path):
        print("\n✗ Setup failed!")
        return
    
    # Clean up zip file
    try:
        os.remove(zip_path)
        print(f"\nCleaned up {zip_path}")
    except:
        pass
    
    # Verify
    if verify_adb():
        print("\n" + "=" * 60)
        print("✓ ADB setup complete!")
        print("=" * 60)
        print(f"\nADB installed to: {ADB_DIR.absolute()}")
        print("\nNext steps:")
        print("1. Update core/input/adb_client.py to use bundled ADB")
        print("2. Enable ADB in BlueStacks (Settings > Advanced)")
        print("3. Run: tools/adb/adb.exe connect localhost:5555")
    else:
        print("\n✗ Setup failed!")

if __name__ == "__main__":
    main()
