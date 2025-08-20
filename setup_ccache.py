#!/usr/bin/env python3
"""
Script to manually download and setup ccache for Nuitka
"""

import os
import urllib.request
import zipfile
import shutil
from pathlib import Path

def setup_ccache():
    # Get the username
    username = os.getenv('USER')
    if not username:
        print("Could not determine username")
        return False
    
    # Define paths
    ccache_version = "v4.2.1"
    version="4.2.1"
    ccache_url = f"https://nuitka.net/ccache/{ccache_version}/ccache-{version}.zip"
    cache_dir = f"/Users/{username}/Library/Caches/Nuitka/downloads/ccache/{ccache_version}"
    zip_path = os.path.join(cache_dir, f"ccache-{ccache_version}.zip")
    
    print(f"Setting up ccache {ccache_version}")
    print(f"Cache directory: {cache_dir}")
    
    # Create directories if they don't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Download ccache
    if not os.path.exists(zip_path):
        print(f"Downloading ccache from {ccache_url}")
        try:
            # Create an unverified context for SSL to bypass certificate issues
            import ssl
            ssl_context = ssl._create_unverified_context()
            
            # Download using the context
            with urllib.request.urlopen(ccache_url, context=ssl_context) as response, \
                 open(zip_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            print("Download completed successfully")
        except Exception as e:
            print(f"Failed to download ccache: {e}")
            print("\nManual setup instructions:")
            print("1. Download ccache manually from a browser:")
            print(f"   URL: {ccache_url}")
            print(f"2. Save the file as 'ccache-{ccache_version}.zip'")
            print(f"3. Place it in this directory: {cache_dir}")
            print("4. Extract the contents of the zip file in the same directory")
            print("\nAlternatively, you can skip ccache setup and proceed with the build.")
            return False
    else:
        print("ccache zip file already exists")
    
    # Extract the zip file
    try:
        print("Extracting ccache...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(cache_dir)
        print("Extraction completed")
    except Exception as e:
        print(f"Failed to extract ccache: {e}")
        return False
    
    print("ccache setup completed successfully")
    return True

if __name__ == "__main__":
    setup_ccache()