import os
import zipfile
import rarfile
import py7zr
import tarfile # Import tarfile for .tar and .tar.gz
from pathlib import Path

# Define supported formats
SUPPORTED_ARCHIVE_FORMATS = ["zip", "rar", "7z", "tar", "tar.gz"]

def _get_archive_type(file_path):
    """Determines the archive type based on file extension."""
    ext = Path(file_path).suffix.lower()
    if ext == ".zip":
        return "zip"
    elif ext == ".rar":
        return "rar"
    elif ext == ".7z":
        return "7z"
    elif ext == ".tar":
        return "tar"
    elif ext == ".tar.gz" or ext == ".tgz": # .tgz is a common alias for .tar.gz
        return "tar.gz"
    return None

def create_archive(output_path, source_paths, archive_format, progress_callback=None):
    """
    Create an archive file from the specified source paths.

    Args:
        output_path (str): Path to the output archive file.
        source_paths (list): List of file/directory paths to include in the archive.
        archive_format (str): The format of the archive to create ("zip", "rar", "7z", "tar", "tar.gz").
        progress_callback (function): Optional callback for progress updates.
    """
    try:
        if archive_format == "zip":
            _create_zip(output_path, source_paths, progress_callback)
        elif archive_format == "rar":
            raise NotImplementedError("Creating RAR archives is not directly supported by rarfile. Consider using the command-line 'rar' tool manually.")
        elif archive_format == "7z":
            _create_7z(output_path, source_paths, progress_callback)
        elif archive_format == "tar":
            _create_tar(output_path, source_paths, progress_callback)
        elif archive_format == "tar.gz":
            _create_tar_gz(output_path, source_paths, progress_callback)
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
            if progress_callback:
                progress = ((i + 1) / total_files) * 100
                progress_callback(f"Extracting {file_name}", progress)

def _extract_rar(rar_path, extract_to, progress_callback=None):
    with rarfile.RarFile(rar_path, 'r') as rar_ref:
        file_list = rar_ref.namelist()
        total_files = len(file_list)
        for i, file_name in enumerate(file_list):
            rar_ref.extract(file_name, extract_to)
            if progress_callback:
                progress = ((i + 1) / total_files) * 100
                progress_callback(f"Extracting {file_name}", progress)

def _extract_7z(sz_path, extract_to, progress_callback=None):
    if progress_callback:
        progress_callback("Starting 7z archive extraction...", 0)
    with py7zr.SevenZipFile(sz_path, mode='r') as sz_ref:
        sz_ref.extractall(path=extract_to)
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
            if progress_callback:
                progress = ((i + 1) / total_files) * 100
                progress_callback(f"Extracting {member.name}", progress)
    if progress_callback:
        progress_callback("TAR.GZ archive extracted.", 100)


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
            raise NotImplementedError("Adding files to RAR archives is not directly supported by rarfile.")
        elif archive_format == "7z":
            _add_to_7z(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "tar":
            _add_to_tar(archive_path, file_to_add_path, progress_callback)
        elif archive_format == "tar.gz":
            _add_to_tar_gz(archive_path, file_to_add_path, progress_callback)
        
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

def _add_to_tar_gz(tar_gz_path, file_to_add_path, progress_callback=None):
    # Similar to _add_to_tar, rewrite for progress tracking
    temp_tar_gz_path = tar_gz_path + ".temp"
    with tarfile.open(tar_gz_path, 'r:gz') as original_tar_gz:
        with tarfile.open(temp_tar_gz_path, 'w:gz') as new_tar_gz:
            for member in original_tar_gz.getmembers():
                extracted_file = original_tar_gz.extractfile(member)
                if extracted_file:
                    temp_file_path = Path(temp_tar_gz_path).parent / member.name
                    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(temp_file_path, 'wb') as f:
                        f.write(extracted_file.read())
                    new_tar_gz.add(temp_file_path, arcname=member.name)
                    os.remove(temp_file_path)
            file_name = os.path.basename(file_to_add_path)
            new_tar_gz.add(file_to_add_path, arcname=file_name)
            if progress_callback:
                progress_callback(f"Added {file_name} to TAR.GZ", 100)
    os.replace(temp_tar_gz_path, tar_gz_path)


def list_archive_contents(archive_path):
    """
    List the contents of an archive file.

    Args:
        archive_path (str): Path to the archive file.
    """
    file_info_list = []
    try:
        archive_format = _get_archive_type(archive_path)
        if not archive_format:
            file_info_list.append(f"Error: Unknown archive format for listing: {archive_path}")
            return file_info_list

        if archive_format == "zip":
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                for info in zipf.filelist:
                    file_info_list.append(f"{info.filename:<40} {info.file_size:>10} bytes")
        elif archive_format == "rar":
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                for info in rar_ref.infolist():
                    file_info_list.append(f"{info.filename:<40} {info.file_size:>10} bytes")
        elif archive_format == "7z":
            with py7zr.SevenZipFile(archive_path, mode='r') as sz_ref:
                for info in sz_ref.list():
                    file_info_list.append(f"{info.name:<40} {info.size:>10} bytes") # Using .name and .size based on py7zr docs
        elif archive_format == "tar" or archive_format == "tar.gz":
            mode = 'r:gz' if archive_format == "tar.gz" else 'r'
            with tarfile.open(archive_path, mode) as tarf:
                for member in tarf.getmembers():
                    file_info_list.append(f"{member.name:<40} {member.size:>10} bytes")

        return file_info_list

    except Exception as e:
        file_info_list.append(f"Error reading archive file: {str(e)}")
        return file_info_list

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

if __name__ == "__main__":
    # Example usage for testing
    # This block will not be part of the GUI, but for CLI testing
    pass
