#!/usr/bin/env python3
"""
ZIP File Processing Tool

This script provides functionality for creating, extracting, and managing ZIP files
with progress tracking and error handling.
"""

import os
import sys
import zipfile
import argparse
from pathlib import Path


def create_zip(output_path, source_paths, progress_callback=None):
    """
    Create a ZIP file from the specified source paths.
    
    Args:
        output_path (str): Path to the output ZIP file
        source_paths (list): List of file/directory paths to include in the ZIP
        progress_callback (function): Optional callback for progress updates
    """
    try:
        # Calculate total files for progress tracking
        total_files = 0
        for source_path in source_paths:
            path = Path(source_path)
            if path.is_file():
                total_files += 1
            elif path.is_dir():
                total_files += sum(1 for _ in path.rglob('*') if _.is_file())
        
        processed_files = 0
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for source_path in source_paths:
                path = Path(source_path)
                
                if path.is_file():
                    # Add single file
                    arcname = path.name
                    zipf.write(path, arcname)
                    processed_files += 1
                    
                    if progress_callback:
                        progress = (processed_files / total_files) * 100
                        progress_callback(f"Adding {arcname}", progress)
                        
                elif path.is_dir():
                    # Add directory and all its contents
                    for file_path in path.rglob('*'):
                        if file_path.is_file():
                            # Calculate archive name (relative to source directory)
                            arcname = file_path.relative_to(path.parent)
                            zipf.write(file_path, arcname)
                            processed_files += 1
                            
                            if progress_callback:
                                progress = (processed_files / total_files) * 100
                                progress_callback(f"Adding {arcname}", progress)
                
        if progress_callback:
            progress_callback(f"ZIP file created: {output_path}", 100)
            
        return True
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"Error creating ZIP: {str(e)}", -1)
        return False


def extract_zip(zip_path, extract_to, progress_callback=None):
    """
    Extract a ZIP file to the specified directory.
    
    Args:
        zip_path (str): Path to the ZIP file to extract
        extract_to (str): Directory to extract files to
        progress_callback (function): Optional callback for progress updates
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Get list of files in ZIP
            file_list = zipf.namelist()
            total_files = len(file_list)
            
            # Create extraction directory if it doesn't exist
            os.makedirs(extract_to, exist_ok=True)
            
            # Extract files
            for i, file_name in enumerate(file_list):
                zipf.extract(file_name, extract_to)
                
                if progress_callback:
                    progress = ((i + 1) / total_files) * 100
                    progress_callback(f"Extracting {file_name}", progress)
            
        if progress_callback:
            progress_callback(f"ZIP file extracted to: {extract_to}", 100)
            
        return True
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"Error extracting ZIP: {str(e)}", -1)
        return False


def add_to_zip(zip_path, file_path, progress_callback=None):
    """
    Add a file to an existing ZIP file.
    
    Args:
        zip_path (str): Path to the existing ZIP file
        file_path (str): Path to the file to add
        progress_callback (function): Optional callback for progress updates
    """
    try:
        # Read existing ZIP content
        temp_zip_path = zip_path + ".temp"
        
        with zipfile.ZipFile(zip_path, 'r') as original_zip:
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                # Copy existing files
                for item in original_zip.namelist():
                    new_zip.writestr(item, original_zip.read(item))
                
                # Add new file
                file_name = os.path.basename(file_path)
                new_zip.write(file_path, file_name)
                
                if progress_callback:
                    progress_callback(f"Added {file_name} to ZIP", 100)
        
        # Replace original ZIP with updated version
        os.replace(temp_zip_path, zip_path)
        
        return True
        
    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
            
        if progress_callback:
            progress_callback(f"Error adding to ZIP: {str(e)}", -1)
        return False


def list_zip_contents(zip_path):
    """
    List the contents of a ZIP file.
    
    Args:
        zip_path (str): Path to the ZIP file
    """
    file_info_list = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Removed console print statements
            
            for info in zipf.filelist:
                file_info_list.append(f"{info.filename:<40} {info.file_size:>10} bytes")
            
        return file_info_list
        
    except Exception as e:
        file_info_list.append(f"Error reading ZIP file: {str(e)}")
        return file_info_list


def main():
    parser = argparse.ArgumentParser(description="ZIP File Processing Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create ZIP command
    create_parser = subparsers.add_parser('create', help='Create a ZIP file')
    create_parser.add_argument('output', help='Output ZIP file path')
    create_parser.add_argument('sources', nargs='+', help='Source files/directories to include')
    
    # Extract ZIP command
    extract_parser = subparsers.add_parser('extract', help='Extract a ZIP file')
    extract_parser.add_argument('zipfile', help='ZIP file to extract')
    extract_parser.add_argument('destination', help='Destination directory')
    
    # Add to ZIP command
    add_parser = subparsers.add_parser('add', help='Add file to existing ZIP')
    add_parser.add_argument('zipfile', help='Existing ZIP file')
    add_parser.add_argument('file', help='File to add')
    
    # List ZIP contents command
    list_parser = subparsers.add_parser('list', help='List ZIP file contents')
    list_parser.add_argument('zipfile', help='ZIP file to list')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        def progress_callback(message, progress):
            if progress >= 0:
                print(f"[{progress:.1f}%] {message}")
            else:
                print(f"[ERROR] {message}")
                
        success = create_zip(args.output, args.sources, progress_callback)
        sys.exit(0 if success else 1)
        
    elif args.command == 'extract':
        def progress_callback(message, progress):
            if progress >= 0:
                print(f"[{progress:.1f}%] {message}")
            else:
                print(f"[ERROR] {message}")
                
        success = extract_zip(args.zipfile, args.destination, progress_callback)
        sys.exit(0 if success else 1)
        
    elif args.command == 'add':
        def progress_callback(message, progress):
            if progress >= 0:
                print(f"[{progress:.1f}%] {message}")
            else:
                print(f"[ERROR] {message}")
                
        success = add_to_zip(args.zipfile, args.file, progress_callback)
        sys.exit(0 if success else 1)
        
    elif args.command == 'list':
        success = list_zip_contents(args.zipfile)
        sys.exit(0 if success else 1)
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
