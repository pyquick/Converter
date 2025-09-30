#!/usr/bin/env python3

"""
Compile Script for PNG to ICNS Converter

This script compiles the GUI application using Nuitka to create a standalone executable.
"""

import subprocess
import sys
import os

def compile_gui():
    """Compile the GUI application using Nuitka"""
    print("Compiling GUI application with Nuitka...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the main script to compile
    main_script = os.path.join(current_dir, "Converter.py")
    
    # Check if the main script exists
    if not os.path.exists(main_script):
        print(f"Error: Main script not found at {main_script}")
        return False
    
    # Nuitka compilation command
    cmd = [
        "pyinstaller",
        "convert.spec"
    ]
    
    try:
        print("Running Pyinstaller compilation...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Compilation successful!")
        #如果有Converter.app,则重命名为Converter.app
        return True
    except subprocess.CalledProcessError as e:
        print("Compilation failed!")
        print(f"Error: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error during compilation: {e}")
        return False

def compile_cli():
    """Compile the CLI application using Nuitka"""
    print("Compiling CLI application with Nuitka...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the main script to compile
    main_script = os.path.join(current_dir, "support", "convert.py")
    
    # Check if the main script exists
    if not os.path.exists(main_script):
        print(f"Error: Main script not found at {main_script}")
        return False
    
    # Nuitka compilation command for CLI
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",           # Create standalone executable
        "--onefile",              # Create single file executable
        "--output-dir=dist",      # Output directory
        "--remove-output",        # Remove build directory after compilation
        "--quiet",                # Reduce output verbosity
        main_script
    ]
    
    try:
        print("Running Nuitka compilation for CLI...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("CLI Compilation successful!")
        print("Executable created in dist/ directory")
        return True
    except subprocess.CalledProcessError as e:
        print("CLI Compilation failed!")
        print(f"Error: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error during CLI compilation: {e}")
        return False
def compile_cli_zip():
    """Compile the CLI application using Nuitka"""
    print("Compiling CLI (Zip_Converter) application with Nuitka...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the main script to compile
    main_script = os.path.join(current_dir, "support", "convertzip.py")
    
    # Check if the main script exists
    if not os.path.exists(main_script):
        print(f"Error: Main script not found at {main_script}")
        return False
    
    # Nuitka compilation command for CLI
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",           # Create standalone executable
        "--onefile",              # Create single file executable
        "--output-dir=dist",      # Output directory
        "--remove-output",        # Remove build directory after compilation
        "--quiet",                # Reduce output verbosity
        main_script
    ]
    
    try:
        print("Running Nuitka compilation for CLI...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("CLI Compilation successful!")
        print("Executable created in dist/ directory")
        return True
    except subprocess.CalledProcessError as e:
        print("CLI Compilation failed!")
        print(f"Error: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error during CLI compilation: {e}")
        return False

def main():
    print("PNG to ICNS Converter - Compilation Script")
    print("=" * 40)
    
    # Create dist directory if it doesn't exist
    dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # Compile both versions
    gui_success = compile_gui()
    print()
    cli_success = compile_cli()
    print()
    zip_success = compile_cli_zip()
    print("\n" + "=" * 40)
    if gui_success and cli_success and zip_success:
        print("All compilations completed successfully!")
        print("Executables are located in the 'dist' directory:")
        print("- GUI application: dist/Converter.app")
        print("- CLI application: dist/convert.bin")
    else:
        print("Some compilations failed. Please check the error messages above.")
        if not gui_success:
            print("- GUI compilation failed")
        if not cli_success:
            print("- CLI compilation failed")
        if not zip_success:
            print("- CLI (Zip_Converter) compilation failed")
if __name__ == "__main__":
    main()