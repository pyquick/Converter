import os
import zipfile
import rarfile
import py7zr
import tarfile # Import tarfile for .tar and .tar.gz
import subprocess
import platform
from pathlib import Path

# Define supported formats
SUPPORTED_ARCHIVE_FORMATS = ["zip", "rar", "7z", "tar", "tar.gz", "bz2", "tar.bz2", "xz", "tar.xz", "lzma", "zipx", "iso", "cab", "arj", "lzh"]

def _get_archive_type(file_path):
    """Determines the archive type based on file extension."""
    file_path_str = str(file_path).lower()
    
    # Check for multi-part extensions first
    if file_path_str.endswith('.tar.bz2') or file_path_str.endswith('.tbz2'):
        return "tar.bz2"
    elif file_path_str.endswith('.tar.gz') or file_path_str.endswith('.tgz'):
        return "tar.gz"
    elif file_path_str.endswith('.tar.xz') or file_path_str.endswith('.txz'):
        return "tar.xz"
    
    # Check for single extensions
    ext = Path(file_path).suffix.lower()
    if ext == ".zip":
        return "zip"
    elif ext == ".rar":
        return "rar"
    elif ext == ".7z":
        return "7z"
    elif ext == ".tar":
        return "tar"
    elif ext == ".bz2":
        return "bz2"
    elif ext == ".xz":
        return "xz"
    elif ext == ".lzma":
        return "lzma"
    elif ext == ".zipx":
        return "zipx"
    elif ext == ".iso":
        return "iso"
    elif ext == ".cab":
        return "cab"
    elif ext == ".arj":
        return "arj"
    elif ext == ".lzh" or ext == ".lha":
        return "lzh"
    return None

def create_archive(output_path, source_paths, archive_format, progress_callback=None):
    """
    Create an archive file from the specified source paths.

    Args:
        output_path (str): Path to the output archive file.
        source_paths (list): List of file/directory paths to include in the archive.
        archive_format (str): The format of the archive to create ("zip", "rar", "7z", "tar", "tar.gz", "bz2", "tar.bz2", "xz", "tar.xz", "lzma", "zipx", "iso", "cab", "arj", "lzh").
        progress_callback (function): Optional callback for progress updates.
    """
    try:
        if archive_format == "zip":
            _create_zip(output_path, source_paths, progress_callback)
        elif archive_format == "rar":
            _create_rar(output_path, source_paths, progress_callback)
        elif archive_format == "7z":
            _create_7z(output_path, source_paths, progress_callback)
        elif archive_format == "tar":
            _create_tar(output_path, source_paths, progress_callback)
        elif archive_format == "tar.gz":
            _create_tar_gz(output_path, source_paths, progress_callback)
        elif archive_format == "bz2":
            _create_bz2(output_path, source_paths, progress_callback)
        elif archive_format == "tar.bz2":
            _create_tar_bz2(output_path, source_paths, progress_callback)
        elif archive_format == "xz":
            _create_xz(output_path, source_paths, progress_callback)
        elif archive_format == "tar.xz":
            _create_tar_xz(output_path, source_paths, progress_callback)
        elif archive_format == "lzma":
            _create_lzma(output_path, source_paths, progress_callback)
        elif archive_format == "zipx":
            _create_zipx(output_path, source_paths, progress_callback)
        elif archive_format == "iso":
            _create_iso(output_path, source_paths, progress_callback)
        elif archive_format == "cab":
            _create_cab(output_path, source_paths, progress_callback)
        elif archive_format == "arj":
            _create_arj(output_path, source_paths, progress_callback)
        elif archive_format == "lzh":
            _create_lzh(output_path, source_paths, progress_callback)
        else:
            raise ValueError(f"Unsupported archive format for creation: {archive_format}")

        if progress_callback:
            progress_callback(f"Archive created: {output_path}", 100)
        return True

    except Exception as e:
        if progress_callback:
            progress_callback(f"Error creating archive: {str(e)}", -1)
        return False

def _create_zip(output_path, source_paths, progress_callback=None):
    total_files = _count_files_in_sources(source_paths)
    processed_files = 0
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for source_path in source_paths:
            path = Path(source_path)
            if path.is_file():
                arcname = path.name
                zipf.write(path, arcname)
                processed_files += 1
                if progress_callback:
                    progress_callback(f"Adding {arcname}", (processed_files / total_files) * 100)
            elif path.is_dir():
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(path.parent)
                        zipf.write(file_path, arcname)
                        processed_files += 1
                        if progress_callback:
                            progress_callback(f"Adding {arcname}", (processed_files / total_files) * 100)

def _create_7z(output_path, source_paths, progress_callback=None):
    if progress_callback:
        progress_callback("Starting 7z archive creation...", 0)

    with py7zr.SevenZipFile(output_path, 'w') as szf:
        for source_path in source_paths:
            path = Path(source_path)
            if path.is_file():
                szf.write(path, arcname=path.name)
            elif path.is_dir():
                szf.writeall(path, arcname=path.name)
    
    if progress_callback:
        progress_callback("7z archive created.", 100)

def _create_tar(output_path, source_paths, progress_callback=None):
    total_files = _count_files_in_sources(source_paths)
    processed_files = 0
    if progress_callback:
        progress_callback("Starting TAR archive creation...", 0)
    with tarfile.open(output_path, 'w') as tarf:
        for source_path in source_paths:
            path = Path(source_path)
            if path.is_file():
                tarf.add(path, arcname=path.name)
                processed_files += 1
                if progress_callback:
                    progress_callback(f"Adding {path.name}", (processed_files / total_files) * 100)
            elif path.is_dir():
                # tarfile.add can add directories recursively
                tarf.add(path, arcname=path.name)
                # For progress, we need to count files inside the added directory
                # This is a simplification; a more accurate progress would require pre-counting
                processed_files += sum(1 for _ in path.rglob('*') if _.is_file())
                if progress_callback:
                    progress_callback(f"Adding directory {path.name}/", (processed_files / total_files) * 100)
    if progress_callback:
        progress_callback("TAR archive created.", 100)

def _create_tar_gz(output_path, source_paths, progress_callback=None):
    total_files = _count_files_in_sources(source_paths)
    processed_files = 0
    if progress_callback:
        progress_callback("Starting TAR.GZ archive creation...", 0)
    with tarfile.open(output_path, 'w:gz') as tarf:
        for source_path in source_paths:
            path = Path(source_path)
            if path.is_file():
                tarf.add(path, arcname=path.name)
                processed_files += 1
                if progress_callback:
                    progress_callback(f"Adding {path.name}", (processed_files / total_files) * 100)
            elif path.is_dir():
                tarf.add(path, arcname=path.name)
                processed_files += sum(1 for _ in path.rglob('*') if _.is_file())
                if progress_callback:
                    progress_callback(f"Adding directory {path.name}/", (processed_files / total_files) * 100)
    if progress_callback:
        progress_callback("TAR.GZ archive created.", 100)

def _create_bz2(output_path, source_paths, progress_callback=None):
    """Create a bz2 compressed file (single file only)."""
    import bz2
    
    if len(source_paths) != 1 or not os.path.isfile(source_paths[0]):
        raise ValueError("bz2 format only supports compressing a single file")
    
    source_file = source_paths[0]
    
    with open(source_file, 'rb') as f_in:
        with bz2.open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(8192)
                if not chunk:
                    break
                f_out.write(chunk)
    
    if progress_callback:
        progress_callback(f"Compressed {source_file}", 100)
    
    return True

def _create_tar_bz2(output_path, source_paths, progress_callback=None):
    """Create a tar.bz2 archive."""
    import tarfile
    
    total_files = _count_files_in_sources(source_paths)
    processed_files = 0
    
    with tarfile.open(output_path, "w:bz2") as tar:
        for source_path in source_paths:
            if os.path.isfile(source_path):
                tar.add(source_path, arcname=os.path.basename(source_path))
                processed_files += 1
            elif os.path.isdir(source_path):
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_path)
                        tar.add(file_path, arcname=arcname)
                        processed_files += 1
                        
                        if progress_callback:
                            progress = int((processed_files / total_files) * 100)
                            progress_callback(f"Adding {file}", progress)
    
    return True

def _create_xz(output_path, source_paths, progress_callback=None):
    """Create a xz compressed file (single file only)."""
    import lzma
    
    if len(source_paths) != 1 or not os.path.isfile(source_paths[0]):
        raise ValueError("xz format only supports compressing a single file")
    
    source_file = source_paths[0]
    
    with open(source_file, 'rb') as f_in:
        with lzma.open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(8192)
                if not chunk:
                    break
                f_out.write(chunk)
    
    if progress_callback:
        progress_callback(f"Compressed {source_file}", 100)
    
    return True

def _create_tar_xz(output_path, source_paths, progress_callback=None):
    """Create a tar.xz archive."""
    import tarfile
    
    total_files = _count_files_in_sources(source_paths)
    processed_files = 0
    
    with tarfile.open(output_path, "w:xz") as tar:
        for source_path in source_paths:
            if os.path.isfile(source_path):
                tar.add(source_path, arcname=os.path.basename(source_path))
                processed_files += 1
            elif os.path.isdir(source_path):
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_path)
                        tar.add(file_path, arcname=arcname)
                        processed_files += 1
                        
                        if progress_callback:
                            progress = int((processed_files / total_files) * 100)
                            progress_callback(f"Adding {file}", progress)
    
    return True

def _create_lzma(output_path, source_paths, progress_callback=None):
    """Create a lzma compressed file (single file only)."""
    import lzma
    
    if len(source_paths) != 1 or not os.path.isfile(source_paths[0]):
        raise ValueError("lzma format only supports compressing a single file")
    
    source_file = source_paths[0]
    
    with open(source_file, 'rb') as f_in:
        with lzma.open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(8192)
                if not chunk:
                    break
                f_out.write(chunk)
    
    if progress_callback:
        progress_callback(f"Compressed {source_file}", 100)
    
    return True

def _create_zipx(output_path, source_paths, progress_callback=None):
    """Create a zipx archive (using patool for better compression)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for zipx format support")
    
    # Create a temporary directory to store files for patool
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Copy all source files to temp directory
        for i, source_path in enumerate(source_paths):
            if os.path.isfile(source_path):
                shutil.copy2(source_path, os.path.join(temp_dir, os.path.basename(source_path)))
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, os.path.join(temp_dir, os.path.basename(source_path)))
        
        # Use patool to create zipx archive
        patoolib.create_archive(output_path, [temp_dir])
        
        if progress_callback:
            progress_callback("Zipx archive created", 100)
        
        return True
    finally:
        shutil.rmtree(temp_dir)

def _create_iso(output_path, source_paths, progress_callback=None):
    """Create an ISO image (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for ISO format support")
    
    if len(source_paths) != 1 or not os.path.isdir(source_paths[0]):
        raise ValueError("ISO format only supports creating from a single directory")
    
    source_dir = source_paths[0]
    patoolib.create_archive(output_path, [source_dir])
    
    if progress_callback:
        progress_callback("ISO image created", 100)
    
    return True

def _create_cab(output_path, source_paths, progress_callback=None):
    """Create a CAB archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for CAB format support")
    
    patoolib.create_archive(output_path, source_paths)
    
    if progress_callback:
        progress_callback("CAB archive created", 100)
    
    return True

def _create_arj(output_path, source_paths, progress_callback=None):
    """Create an ARJ archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for ARJ format support")
    
    patoolib.create_archive(output_path, source_paths)
    
    if progress_callback:
        progress_callback("ARJ archive created", 100)
    
    return True

def _create_lzh(output_path, source_paths, progress_callback=None):
    """Create an LZH archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for LZH format support")
    
    patoolib.create_archive(output_path, source_paths)
    
    if progress_callback:
        progress_callback("LZH archive created", 100)
    
    return True

def _create_rar(output_path, source_paths, progress_callback=None):
    """Create RAR archive using system rar command."""
    rar_cmd = _get_rar_command_name()
    if not rar_cmd:
        raise RuntimeError("RAR command not found. Please install RAR: https://www.rarlab.com/download.htm")
    
    if progress_callback:
        progress_callback("Starting RAR archive creation...", 0)
    
    try:
        # Build the rar command
        cmd = [rar_cmd, 'a', '-r', output_path]
        
        # Add source paths to the command
        for source_path in source_paths:
            cmd.append(str(Path(source_path).absolute()))
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if progress_callback:
            progress_callback("RAR archive created.", 100)
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to create RAR archive: {e.stderr if e.stderr else str(e)}"
        raise RuntimeError(error_msg)
    except Exception as e:
        raise RuntimeError(f"Error creating RAR archive: {str(e)}")

def _add_to_rar(archive_path, file_to_add_path, progress_callback=None):
    """Add file to RAR archive using system rar command."""
    rar_cmd = _get_rar_command_name()
    if not rar_cmd:
        raise RuntimeError("RAR command not found. Please install RAR: https://www.rarlab.com/download.htm")
    
    if progress_callback:
        progress_callback("Starting adding to RAR archive...", 0)
    
    try:
        # Build the rar command to add file
        cmd = [rar_cmd, 'a', archive_path, str(Path(file_to_add_path).absolute())]
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if progress_callback:
            file_name = os.path.basename(file_to_add_path)
            progress_callback(f"Added {file_name} to RAR archive", 100)
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to add to RAR archive: {e.stderr if e.stderr else str(e)}"
        raise RuntimeError(error_msg)
    except Exception as e:
        raise RuntimeError(f"Error adding to RAR archive: {str(e)}")


def extract_archive(archive_path, extract_to, progress_callback=None):
    """
    Extract an archive file to the specified directory.

    Args:
        archive_path (str): Path to the archive file to extract.
        extract_to (str): Directory to extract files to.
        progress_callback (function): Optional callback for progress updates.
    """
    try:
        archive_format = _get_archive_type(archive_path)
        if not archive_format:
            raise ValueError(f"Unknown archive format for extraction: {archive_path}")

        os.makedirs(extract_to, exist_ok=True)

        if archive_format == "zip":
            _extract_zip(archive_path, extract_to, progress_callback)
        elif archive_format == "rar":
            _extract_rar(archive_path, extract_to, progress_callback)
        elif archive_format == "7z":
            _extract_7z(archive_path, extract_to, progress_callback)
        elif archive_format == "tar":
            _extract_tar(archive_path, extract_to, progress_callback)
        elif archive_format == "tar.gz":
            _extract_tar_gz(archive_path, extract_to, progress_callback)
        elif archive_format == "bz2":
            _extract_bz2(archive_path, extract_to, progress_callback)
        elif archive_format == "tar.bz2":
            _extract_tar_bz2(archive_path, extract_to, progress_callback)
        elif archive_format == "xz":
            _extract_xz(archive_path, extract_to, progress_callback)
        elif archive_format == "tar.xz":
            _extract_tar_xz(archive_path, extract_to, progress_callback)
        elif archive_format == "lzma":
            _extract_lzma(archive_path, extract_to, progress_callback)
        elif archive_format == "zipx":
            _extract_zipx(archive_path, extract_to, progress_callback)
        elif archive_format == "iso":
            _extract_iso(archive_path, extract_to, progress_callback)
        elif archive_format == "cab":
            _extract_cab(archive_path, extract_to, progress_callback)
        elif archive_format == "arj":
            _extract_arj(archive_path, extract_to, progress_callback)
        elif archive_format == "lzh":
            _extract_lzh(archive_path, extract_to, progress_callback)
        else:
            raise ValueError(f"Unsupported archive format for extraction: {archive_format}")

        if progress_callback:
            progress_callback(f"Archive extracted to: {extract_to}", 100)
        return True

    except Exception as e:
        if progress_callback:
            progress_callback(f"Error extracting archive: {str(e)}", -1)
        return False

def _extract_zip(zip_path, extract_to, progress_callback=None):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        file_list = zipf.namelist()
        total_files = len(file_list)
        for i, file_name in enumerate(file_list):
            zipf.extract(file_name, extract_to)
            # Add execute permission to extracted files
            extracted_path = os.path.join(extract_to, file_name)
            if os.path.isfile(extracted_path):
                try:
                    os.chmod(extracted_path, os.stat(extracted_path).st_mode | 0o111)
                except (OSError, PermissionError):
                    pass  # Ignore permission errors
            if progress_callback:
                progress = ((i + 1) / total_files) * 100
                progress_callback(f"Extracting {file_name}", progress)

def _extract_rar(rar_path, extract_to, progress_callback=None):
    with rarfile.RarFile(rar_path, 'r') as rar_ref:
        file_list = rar_ref.namelist()
        total_files = len(file_list)
        for i, file_name in enumerate(file_list):
            rar_ref.extract(file_name, extract_to)
            # Add execute permission to extracted files
            extracted_path = os.path.join(extract_to, file_name)
            if os.path.isfile(extracted_path):
                try:
                    os.chmod(extracted_path, os.stat(extracted_path).st_mode | 0o111)
                except (OSError, PermissionError):
                    pass  # Ignore permission errors
            if progress_callback:
                progress = ((i + 1) / total_files) * 100
                progress_callback(f"Extracting {file_name}", progress)

def _extract_7z(sz_path, extract_to, progress_callback=None):
    if progress_callback:
        progress_callback("Starting 7z archive extraction...", 0)
    with py7zr.SevenZipFile(sz_path, mode='r') as sz_ref:
        sz_ref.extractall(path=extract_to)
    # Add execute permission to extracted files
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.chmod(file_path, os.stat(file_path).st_mode | 0o111)
            except (OSError, PermissionError):
                pass  # Ignore permission errors
    if progress_callback:
        progress_callback("7z archive extracted.", 100)

def _extract_tar(tar_path, extract_to, progress_callback=None):
    if progress_callback:
        progress_callback("Starting TAR archive extraction...", 0)
    with tarfile.open(tar_path, 'r') as tarf:
        file_list = tarf.getnames()
        total_files = len(file_list)
        for i, member in enumerate(tarf.getmembers()):
            tarf.extract(member, path=extract_to)
            # Add execute permission to extracted files
            extracted_path = os.path.join(extract_to, member.name)
            if member.isfile() and os.path.isfile(extracted_path):
                try:
                    os.chmod(extracted_path, os.stat(extracted_path).st_mode | 0o111)
                except (OSError, PermissionError):
                    pass  # Ignore permission errors
            if progress_callback:
                progress = ((i + 1) / total_files) * 100
                progress_callback(f"Extracting {member.name}", progress)
    if progress_callback:
        progress_callback("TAR archive extracted.", 100)

def _extract_tar_gz(tar_gz_path, extract_to, progress_callback=None):
    if progress_callback:
        progress_callback("Starting TAR.GZ archive extraction...", 0)
    with tarfile.open(tar_gz_path, 'r:gz') as tarf:
        file_list = tarf.getnames()
        total_files = len(file_list)
        for i, member in enumerate(tarf.getmembers()):
            tarf.extract(member, path=extract_to)
            # Add execute permission to extracted files
            extracted_path = os.path.join(extract_to, member.name)
            if member.isfile() and os.path.isfile(extracted_path):
                try:
                    os.chmod(extracted_path, os.stat(extracted_path).st_mode | 0o111)
                except (OSError, PermissionError):
                    pass  # Ignore permission errors
            if progress_callback:
                progress = ((i + 1) / total_files) * 100
                progress_callback(f"Extracting {member.name}", progress)
    if progress_callback:
        progress_callback("TAR.GZ archive extracted.", 100)

def _extract_bz2(archive_path, extract_to, progress_callback=None):
    """Extract bz2 compressed file."""
    import bz2
    
    # For bz2 files, we extract to a single file with the same name (without .bz2 extension)
    output_filename = os.path.basename(archive_path)
    if output_filename.endswith('.bz2'):
        output_filename = output_filename[:-4]
    elif output_filename.endswith('.tbz2'):
        output_filename = output_filename[:-5] + '.tar'
    
    output_path = os.path.join(extract_to, output_filename)
    
    with bz2.open(archive_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(8192)
                if not chunk:
                    break
                f_out.write(chunk)
    
    if progress_callback:
        progress_callback(f"Extracted {output_filename}", 100)
    
    return True

def _extract_tar_bz2(archive_path, extract_to, progress_callback=None):
    """Extract tar.bz2 archive."""
    import tarfile
    
    with tarfile.open(archive_path, "r:bz2") as tar:
        members = tar.getmembers()
        total_members = len(members)
        
        for i, member in enumerate(members):
            tar.extract(member, extract_to)
            
            # Try to set executable permissions if it's a file
            if member.isfile():
                extracted_path = os.path.join(extract_to, member.name)
                try:
                    os.chmod(extracted_path, 0o755)
                except:
                    pass
            
            if progress_callback:
                progress = int((i + 1) / total_members * 100)
                progress_callback(f"Extracting {member.name}", progress)
    
    return True

def _extract_xz(archive_path, extract_to, progress_callback=None):
    """Extract xz compressed file."""
    import lzma
    
    # For xz files, we extract to a single file with the same name (without .xz extension)
    output_filename = os.path.basename(archive_path)
    if output_filename.endswith('.xz'):
        output_filename = output_filename[:-3]
    elif output_filename.endswith('.txz'):
        output_filename = output_filename[:-4] + '.tar'
    
    output_path = os.path.join(extract_to, output_filename)
    
    with lzma.open(archive_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(8192)
                if not chunk:
                    break
                f_out.write(chunk)
    
    if progress_callback:
        progress_callback(f"Extracted {output_filename}", 100)
    
    return True

def _extract_tar_xz(archive_path, extract_to, progress_callback=None):
    """Extract tar.xz archive."""
    import tarfile
    
    with tarfile.open(archive_path, "r:xz") as tar:
        members = tar.getmembers()
        total_members = len(members)
        
        for i, member in enumerate(members):
            tar.extract(member, extract_to)
            
            # Try to set executable permissions if it's a file
            if member.isfile():
                extracted_path = os.path.join(extract_to, member.name)
                try:
                    os.chmod(extracted_path, 0o755)
                except:
                    pass
            
            if progress_callback:
                progress = int((i + 1) / total_members * 100)
                progress_callback(f"Extracting {member.name}", progress)
    
    return True

def _extract_lzma(archive_path, extract_to, progress_callback=None):
    """Extract lzma compressed file."""
    import lzma
    
    # For lzma files, we extract to a single file with the same name (without .lzma extension)
    output_filename = os.path.basename(archive_path)
    if output_filename.endswith('.lzma'):
        output_filename = output_filename[:-5]
    
    output_path = os.path.join(extract_to, output_filename)
    
    with lzma.open(archive_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(8192)
                if not chunk:
                    break
                f_out.write(chunk)
    
    if progress_callback:
        progress_callback(f"Extracted {output_filename}", 100)
    
    return True

def _extract_zipx(archive_path, extract_to, progress_callback=None):
    """Extract zipx archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for zipx format support")
    
    patoolib.extract_archive(archive_path, outdir=extract_to)
    
    if progress_callback:
        progress_callback("Zipx archive extracted", 100)
    
    return True

def _extract_iso(archive_path, extract_to, progress_callback=None):
    """Extract ISO image (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for ISO format support")
    
    patoolib.extract_archive(archive_path, outdir=extract_to)
    
    if progress_callback:
        progress_callback("ISO image extracted", 100)
    
    return True

def _extract_cab(archive_path, extract_to, progress_callback=None):
    """Extract CAB archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for CAB format support")
    
    patoolib.extract_archive(archive_path, outdir=extract_to)
    
    if progress_callback:
        progress_callback("CAB archive extracted", 100)
    
    return True

def _extract_arj(archive_path, extract_to, progress_callback=None):
    """Extract ARJ archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for ARJ format support")
    
    patoolib.extract_archive(archive_path, outdir=extract_to)
    
    if progress_callback:
        progress_callback("ARJ archive extracted", 100)
    
    return True

def _extract_lzh(archive_path, extract_to, progress_callback=None):
    """Extract LZH archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for LZH format support")
    
    patoolib.extract_archive(archive_path, outdir=extract_to)
    
    if progress_callback:
        progress_callback("LZH archive extracted", 100)
    
    return True


def add_to_archive(archive_path, file_to_add_path, progress_callback=None):
    """
    Add a file to an existing archive file.

    Args:
        archive_path (str): Path to the existing archive file.
        file_to_add_path (str): Path to the file to add.
        progress_callback (function): Optional callback for progress updates.
    """
    try:
        archive_format = _get_archive_type(archive_path)
        if not archive_format:
            raise ValueError(f"Unknown archive format for adding: {archive_path}")

        if archive_format == "zip":
            _add_to_zip(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "rar":
            _add_to_rar(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "7z":
            _add_to_7z(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "tar":
            _add_to_tar(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "tar.gz":
            _add_to_tar_gz(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "tar.bz2":
            _add_to_tar_bz2(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "tar.xz":
            _add_to_tar_xz(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "zipx":
            _add_to_zipx(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "cab":
            _add_to_cab(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "arj":
            _add_to_arj(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "lzh":
            _add_to_lzh(archive_path, file_to_add_path, progress_callback)
        else:
            raise ValueError(f"Unsupported archive format for adding files: {archive_format}")
        
        if progress_callback:
            progress_callback(f"File added to archive: {file_to_add_path}", 100)
        return True

    except Exception as e:
        if progress_callback:
            progress_callback(f"Error adding to archive: {str(e)}", -1)
        return False

def _add_to_zip(zip_path, file_to_add_path, progress_callback=None):
    temp_zip_path = zip_path + ".temp"
    with zipfile.ZipFile(zip_path, 'r') as original_zip:
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            for item in original_zip.namelist():
                new_zip.writestr(item, original_zip.read(item))
            file_name = os.path.basename(file_to_add_path)
            new_zip.write(file_to_add_path, file_name)
            if progress_callback:
                progress_callback(f"Added {file_name} to ZIP", 100)
    os.replace(temp_zip_path, zip_path)

def _add_to_7z(sz_path, file_to_add_path, progress_callback=None):
    if progress_callback:
        progress_callback("Starting adding to 7z archive...", 0)
    with py7zr.SevenZipFile(sz_path, mode='a') as szf: # 'a' for append
        szf.write(file_to_add_path, arcname=Path(file_to_add_path).name)
    if progress_callback:
        progress_callback("File added to 7z archive.", 100)

def _add_to_tar(tar_path, file_to_add_path, progress_callback=None):
    # tarfile.add can add directly if in 'a' mode, but it's safer to rewrite for progress tracking
    # For simplicity, we'll rewrite the archive for now, similar to ZIP.
    temp_tar_path = tar_path + ".temp"
    with tarfile.open(tar_path, 'r') as original_tar:
        with tarfile.open(temp_tar_path, 'w') as new_tar:
            for member in original_tar.getmembers():
                # Read content of each member and add to new archive
                extracted_file = original_tar.extractfile(member)
                if extracted_file:
                    # Write to a temporary file, then add to new_tar
                    temp_file_path = Path(temp_tar_path).parent / member.name # Simplified temp path
                    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(temp_file_path, 'wb') as f:
                        f.write(extracted_file.read())
                    new_tar.add(temp_file_path, arcname=member.name)
                    os.remove(temp_file_path) # Clean up temp file
            # Add the new file
            file_name = os.path.basename(file_to_add_path)
            new_tar.add(file_to_add_path, arcname=file_name)
            if progress_callback:
                progress_callback(f"Added {file_name} to TAR", 100)
    os.replace(temp_tar_path, tar_path)

def _add_to_tar_gz(archive_path, file_to_add_path, progress_callback=None):
    """Add file to tar.gz archive."""
    import tarfile
    
    # For tar.gz, we need to extract, add, and recompress
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Extract existing archive
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(temp_dir)
        
        # Add new file
        file_name = os.path.basename(file_to_add_path)
        shutil.copy2(file_to_add_path, os.path.join(temp_dir, file_name))
        
        # Recreate archive
        with tarfile.open(archive_path, "w:gz") as tar:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    tar.add(file_path, arcname=arcname)
        
        if progress_callback:
            progress_callback(f"File added to tar.gz archive", 100)
        
        return True
    finally:
        shutil.rmtree(temp_dir)


def _add_to_tar_bz2(archive_path, file_to_add_path, progress_callback=None):
    """Add file to tar.bz2 archive."""
    import tarfile
    
    # For tar.bz2, we need to extract, add, and recompress
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Extract existing archive
        with tarfile.open(archive_path, "r:bz2") as tar:
            tar.extractall(temp_dir)
        
        # Add new file
        file_name = os.path.basename(file_to_add_path)
        shutil.copy2(file_to_add_path, os.path.join(temp_dir, file_name))
        
        # Recreate archive
        with tarfile.open(archive_path, "w:bz2") as tar:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    tar.add(file_path, arcname=arcname)
        
        if progress_callback:
            progress_callback(f"File added to tar.bz2 archive", 100)
        
        return True
    finally:
        shutil.rmtree(temp_dir)


def _add_to_tar_xz(archive_path, file_to_add_path, progress_callback=None):
    """Add file to tar.xz archive."""
    import tarfile
    
    # For tar.xz, we need to extract, add, and recompress
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Extract existing archive
        with tarfile.open(archive_path, "r:xz") as tar:
            tar.extractall(temp_dir)
        
        # Add new file
        file_name = os.path.basename(file_to_add_path)
        shutil.copy2(file_to_add_path, os.path.join(temp_dir, file_name))
        
        # Recreate archive
        with tarfile.open(archive_path, "w:xz") as tar:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    tar.add(file_path, arcname=arcname)
        
        if progress_callback:
            progress_callback(f"File added to tar.xz archive", 100)
        
        return True
    finally:
        shutil.rmtree(temp_dir)


def _add_to_zipx(archive_path, file_to_add_path, progress_callback=None):
    """Add file to zipx archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for zipx format support")
    
    # For zipx, we use patool to add files
    patoolib.add_to_archive(archive_path, [file_to_add_path])
    
    if progress_callback:
        progress_callback(f"File added to zipx archive", 100)
    
    return True


def _add_to_cab(archive_path, file_to_add_path, progress_callback=None):
    """Add file to CAB archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for CAB format support")
    
    # For CAB, we use patool to add files
    patoolib.add_to_archive(archive_path, [file_to_add_path])
    
    if progress_callback:
        progress_callback(f"File added to CAB archive", 100)
    
    return True


def _add_to_arj(archive_path, file_to_add_path, progress_callback=None):
    """Add file to ARJ archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for ARJ format support")
    
    # For ARJ, we use patool to add files
    patoolib.add_to_archive(archive_path, [file_to_add_path])
    
    if progress_callback:
        progress_callback(f"File added to ARJ archive", 100)
    
    return True


def _add_to_lzh(archive_path, file_to_add_path, progress_callback=None):
    """Add file to LZH archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for LZH format support")
    
    # For LZH, we use patool to add files
    patoolib.add_to_archive(archive_path, [file_to_add_path])
    
    if progress_callback:
        progress_callback(f"File added to LZH archive", 100)
    
    return True


def list_archive_contents(archive_path, progress_callback=None):
    """
    List the contents of an archive file.

    Args:
        archive_path (str): Path to the archive file.
        progress_callback (function): Optional callback for progress updates.

    Returns:
        list: List of dictionaries containing file information.
    """
    try:
        archive_type = _get_archive_type(archive_path)
        
        if archive_type == "zip":
            return _list_zip_contents(archive_path, progress_callback)
        elif archive_type == "rar":
            return _list_rar_contents(archive_path, progress_callback)
        elif archive_type == "7z":
            return _list_7z_contents(archive_path, progress_callback)
        elif archive_type == "tar":
            return _list_tar_contents(archive_path, progress_callback)
        elif archive_type == "tar.gz":
            return _list_tar_gz_contents(archive_path, progress_callback)
        elif archive_type == "tar.bz2":
            return _list_tar_bz2_contents(archive_path, progress_callback)
        elif archive_type == "tar.xz":
            return _list_tar_xz_contents(archive_path, progress_callback)
        elif archive_type == "zipx":
            return _list_zipx_contents(archive_path, progress_callback)
        elif archive_type == "iso":
            return _list_iso_contents(archive_path, progress_callback)
        elif archive_type == "cab":
            return _list_cab_contents(archive_path, progress_callback)
        elif archive_type == "arj":
            return _list_arj_contents(archive_path, progress_callback)
        elif archive_type == "lzh":
            return _list_lzh_contents(archive_path, progress_callback)
        elif archive_type == "bz2":
            return _list_bz2_contents(archive_path, progress_callback)
        elif archive_type == "xz":
            return _list_xz_contents(archive_path, progress_callback)
        elif archive_type == "lzma":
            return _list_lzma_contents(archive_path, progress_callback)
        else:
            raise ValueError(f"Unsupported archive format for listing: {archive_type}")

    except Exception as e:
        if progress_callback:
            progress_callback(f"Error listing archive contents: {str(e)}", -1)
        return []

def _list_tar_gz_contents(archive_path, progress_callback=None):
    """List contents of tar.gz archive."""
    import tarfile
    
    contents = []
    with tarfile.open(archive_path, "r:gz") as tar:
        members = tar.getmembers()
        total_members = len(members)
        
        for i, member in enumerate(members):
            file_info = {
                "name": member.name,
                "size": member.size,
                "compressed_size": member.size,  # tar doesn't have separate compressed size
                "date": member.mtime,
                "is_dir": member.isdir()
            }
            contents.append(file_info)
            
            if progress_callback:
                progress = int((i + 1) / total_members * 100)
                progress_callback(f"Listing {member.name}", progress)
    
    return contents

def _list_tar_bz2_contents(archive_path, progress_callback=None):
    """List contents of tar.bz2 archive."""
    import tarfile
    
    contents = []
    with tarfile.open(archive_path, "r:bz2") as tar:
        members = tar.getmembers()
        total_members = len(members)
        
        for i, member in enumerate(members):
            file_info = {
                "name": member.name,
                "size": member.size,
                "compressed_size": member.size,  # tar doesn't have separate compressed size
                "date": member.mtime,
                "is_dir": member.isdir()
            }
            contents.append(file_info)
            
            if progress_callback:
                progress = int((i + 1) / total_members * 100)
                progress_callback(f"Listing {member.name}", progress)
    
    return contents

def _list_tar_xz_contents(archive_path, progress_callback=None):
    """List contents of tar.xz archive."""
    import tarfile
    
    contents = []
    with tarfile.open(archive_path, "r:xz") as tar:
        members = tar.getmembers()
        total_members = len(members)
        
        for i, member in enumerate(members):
            file_info = {
                "name": member.name,
                "size": member.size,
                "compressed_size": member.size,  # tar doesn't have separate compressed size
                "date": member.mtime,
                "is_dir": member.isdir()
            }
            contents.append(file_info)
            
            if progress_callback:
                progress = int((i + 1) / total_members * 100)
                progress_callback(f"Listing {member.name}", progress)
    
    return contents

def _list_zipx_contents(archive_path, progress_callback=None):
    """List contents of zipx archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for zipx format support")
    
    # For zipx, we use patool to list contents
    import tempfile
    import json
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Use patool to list archive contents
        result = patoolib.list_archive(archive_path)
        
        # Parse the result (patool returns a list of file info)
        contents = []
        for file_info in result:
            contents.append({
                "name": file_info.get("filename", ""),
                "size": file_info.get("size", 0),
                "compressed_size": file_info.get("compressed_size", 0),
                "date": file_info.get("date", 0),
                "is_dir": file_info.get("isdir", False)
            })
        
        if progress_callback:
            progress_callback("Zipx archive contents listed", 100)
        
        return contents
    finally:
        import shutil
        shutil.rmtree(temp_dir)

def _list_iso_contents(archive_path, progress_callback=None):
    """List contents of ISO image (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for ISO format support")
    
    # For ISO, we use patool to list contents
    result = patoolib.list_archive(archive_path)
    
    contents = []
    for file_info in result:
        contents.append({
            "name": file_info.get("filename", ""),
            "size": file_info.get("size", 0),
            "compressed_size": file_info.get("compressed_size", 0),
            "date": file_info.get("date", 0),
            "is_dir": file_info.get("isdir", False)
        })
    
    if progress_callback:
        progress_callback("ISO image contents listed", 100)
    
    return contents

def _list_cab_contents(archive_path, progress_callback=None):
    """List contents of CAB archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for CAB format support")
    
    # For CAB, we use patool to list contents
    result = patoolib.list_archive(archive_path)
    
    contents = []
    for file_info in result:
        contents.append({
            "name": file_info.get("filename", ""),
            "size": file_info.get("size", 0),
            "compressed_size": file_info.get("compressed_size", 0),
            "date": file_info.get("date", 0),
            "is_dir": file_info.get("isdir", False)
        })
    
    if progress_callback:
        progress_callback("CAB archive contents listed", 100)
    
    return contents

def _list_arj_contents(archive_path, progress_callback=None):
    """List contents of ARJ archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for ARJ format support")
    
    # For ARJ, we use patool to list contents
    result = patoolib.list_archive(archive_path)
    
    contents = []
    for file_info in result:
        contents.append({
            "name": file_info.get("filename", ""),
            "size": file_info.get("size", 0),
            "compressed_size": file_info.get("compressed_size", 0),
            "date": file_info.get("date", 0),
            "is_dir": file_info.get("isdir", False)
        })
    
    if progress_callback:
        progress_callback("ARJ archive contents listed", 100)
    
    return contents

def _list_lzh_contents(archive_path, progress_callback=None):
    """List contents of LZH archive (using patool)."""
    try:
        import patoolib
    except ImportError:
        raise ImportError("patool is required for LZH format support")
    
    # For LZH, we use patool to list contents
    result = patoolib.list_archive(archive_path)
    
    contents = []
    for file_info in result:
        contents.append({
            "name": file_info.get("filename", ""),
            "size": file_info.get("size", 0),
            "compressed_size": file_info.get("compressed_size", 0),
            "date": file_info.get("date", 0),
            "is_dir": file_info.get("isdir", False)
        })
    
    if progress_callback:
        progress_callback("LZH archive contents listed", 100)
    
    return contents


def _list_bz2_contents(archive_path, progress_callback=None):
    """List contents of bz2 compressed file."""
    import os
    
    # For single bz2 files, we just return the filename
    filename = os.path.basename(archive_path)
    if filename.endswith('.bz2'):
        filename = filename[:-4]
    
    file_size = os.path.getsize(archive_path)
    
    contents = [{
        "name": filename,
        "size": file_size,  # We don't know original size for bz2
        "compressed_size": file_size,
        "date": os.path.getmtime(archive_path),
        "is_dir": False
    }]
    
    if progress_callback:
        progress_callback(f"Listing {filename}", 100)
    
    return contents


def _list_xz_contents(archive_path, progress_callback=None):
    """List contents of xz compressed file."""
    import os
    
    # For single xz files, we just return the filename
    filename = os.path.basename(archive_path)
    if filename.endswith('.xz'):
        filename = filename[:-3]
    
    file_size = os.path.getsize(archive_path)
    
    contents = [{
        "name": filename,
        "size": file_size,  # We don't know original size for xz
        "compressed_size": file_size,
        "date": os.path.getmtime(archive_path),
        "is_dir": False
    }]
    
    if progress_callback:
        progress_callback(f"Listing {filename}", 100)
    
    return contents


def _list_lzma_contents(archive_path, progress_callback=None):
    """List contents of lzma compressed file."""
    import os
    
    # For single lzma files, we just return the filename
    filename = os.path.basename(archive_path)
    if filename.endswith('.lzma'):
        filename = filename[:-5]
    
    file_size = os.path.getsize(archive_path)
    
    contents = [{
        "name": filename,
        "size": file_size,  # We don't know original size for lzma
        "compressed_size": file_size,
        "date": os.path.getmtime(archive_path),
        "is_dir": False
    }]
    
    if progress_callback:
        progress_callback(f"Listing {filename}", 100)
    
    return contents

def _count_files_in_sources(source_paths):
    """Helper to count total files for progress tracking."""
    total_files = 0
    for source_path in source_paths:
        path = Path(source_path)
        if path.is_file():
            total_files += 1
        elif path.is_dir():
            total_files += sum(1 for _ in path.rglob('*') if _.is_file())
    return total_files

def _check_rar_command():
    """Check if rar command is available in the system."""
    try:
        # rar command doesn't support --help, try running it without arguments or with ?
        result = subprocess.run(['rar', '?'], capture_output=True, check=False)
        # rar returns 0 or 7 for help/info commands, both indicate command is available
        return result.returncode in [0, 7]
    except FileNotFoundError:
        return False

def _get_rar_command_name():
    """Get the appropriate rar command name based on the platform."""
    system = platform.system()
    if system == "Windows":
        # On Windows, it might be rar.exe or unrar.exe
        for cmd in ['rar.exe', 'rar']:
            try:
                result = subprocess.run([cmd, '?'], capture_output=True, check=False)
                if result.returncode in [0, 7]:
                    return cmd
            except FileNotFoundError:
                continue
        return None
    else:
        # On Unix-like systems, it's usually just 'rar'
        return 'rar' if _check_rar_command() else None

if __name__ == "__main__":
    # Example usage for testing
    # This block will not be part of the GUI, but for CLI testing
    pass
