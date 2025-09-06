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
    main_script = os.path.join(current_dir, "launcher.py")
    
    # Check if the main script exists
    if not os.path.exists(main_script):
        print(f"Error: Main script not found at {main_script}")
        return False
    path= os.path.dirname(os.path.abspath(__file__))
    # Nuitka compilation command
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",           # Create standalone executable
        "--macos-create-app-bundle", # Create macOS app bundle
        "--macos-app-icon=" + os.path.join(current_dir,"AppIcon.icns"), # App icon
        "--include-data-file=" + os.path.join(current_dir,"zip.png")+ f"=./zip.png",
        "--include-data-file=" + os.path.join(current_dir,"update","update_apply.command")+ f"=./update/update_apply.command",
        "--include-data-file=" + os.path.join(current_dir,"zipd.png")+ f"=./zipd.png",
        "--include-data-file=" + os.path.join(current_dir,"AppIcon.png")+ f"=./AppIcon.png",
        "--include-data-file=" + os.path.join(current_dir,"AppIcond.png")+ f"=./AppIcond.png",
        "--include-data-dir="+os.path.join(current_dir,"qss")+"=./qss",
        "--macos-app-name=Converter", # App name
        "--macos-app-mode=gui",
        "--macos-app-version=2.0",
        "--include-package=zip_gui",
        "--include-package=gui_converter", 
        "--include-package=support",
        "--macos-signed-app-name=com.pyquick.converter",
        "--enable-plugin=pyside6",
        "--prefer-source-code",
        "--output-dir=dist",      # Output directory
        "--remove-output", 
        main_script
    ]
    
    try:
        print("Running Nuitka compilation...")
        subprocess.run(cmd, check=True, text=True)
        print("Compilation successful!")
        #如果有launcher.app,则重命名为Converter.app
        if os.path.exists(os.path.join(current_dir, "dist", "launcher.app")):
            os.rename(os.path.join(current_dir, "dist", "launcher.app"), os.path.join(current_dir, "dist", "Converter.app"))
        print("Executable created in dist/ directory")
        print("Copying Assets.car to Resources/")
        subprocess.run(["cp", os.path.join(current_dir,  "Assets.car"), os.path.join(current_dir, "dist", "Converter.app", "Contents", "Resources", "Assets.car")])
        print("Copying zip.png to MacOS/")
        subprocess.run(["cp", os.path.join(current_dir,  "zip.png"), os.path.join(current_dir, "dist", "Converter.app", "Contents", "MacOS", "zip.png")])
        subprocess.run(["cp", os.path.join(current_dir, "AppIcon.icns"), os.path.join(current_dir, "dist", "Converter.app", "Contents", "MacOS", "AppIcon.icns")])
        subprocess.run(["cp", os.path.join(current_dir, "AppIcon.png"), os.path.join(current_dir, "dist", "Converter.app", "Contents", "MacOS", "AppIcon.png")])
        subprocess.run(["cp", os.path.join(current_dir, "AppIcond.png"), os.path.join(current_dir, "dist", "Converter.app", "Contents", "MacOS", "AppIcond.png")])
        return True
    except subprocess.CalledProcessError as e:
        print("Compilation failed!")
        print(f"Error: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error during compilation: {e}")
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

    print("\n" + "=" * 40)
    if gui_success:
        print("All compilations completed successfully!")
        print("Executables are located in the 'dist' directory:")
        print("- GUI application: dist/launcher.app")
    else:
        print("Some compilations failed. Please check the error messages above.")
        if not gui_success:
            print("- GUI compilation failed")

