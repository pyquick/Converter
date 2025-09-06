import os
import sys
# import threading # PySide6 will use QThread
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QProgressBar,
    QFileDialog, QMessageBox, QTabWidget, QGroupBox, QSpacerItem, QSizePolicy, QComboBox
)
from PySide6.QtGui import QIcon, QFont, QPalette
from PySide6.QtCore import Qt, QSize, Signal, QObject, QThread
from qfluentwidgets import *

from support.toggle import ThemeManager
# Add the current directory to Python path to import convertzip module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from support.archive_manager import create_archive, extract_archive, add_to_archive, list_archive_contents, SUPPORTED_ARCHIVE_FORMATS


# --- Worker Classes for QThread ---
class CreateZipWorker(QObject):
    finished = Signal()
    progress_updated = Signal(str, int)
    conversion_error = Signal(str)

    def __init__(self, output_path, sources, archive_format):
        super().__init__()
        self.output_path = output_path
        
        self.sources = sources
        self.archive_format = archive_format

    def run(self):
        try:
            create_archive(self.output_path, self.sources, self.archive_format, self._update_progress_callback)
            self.finished.emit()
        except NotImplementedError as e:
            self.conversion_error.emit(str(e))
        except Exception as e:
            self.conversion_error.emit(str(e))

    def _update_progress_callback(self, message, percentage):
        self.progress_updated.emit(message, percentage)

class ExtractZipWorker(QObject):
    finished = Signal()
    progress_updated = Signal(str, int)
    conversion_error = Signal(str)

    def __init__(self, zip_path, dest_path):
        super().__init__()
        self.archive_path = zip_path # Renamed for clarity with generic archive_manager
        self.extract_to = dest_path

    def run(self):
        try:
            extract_archive(self.archive_path, self.extract_to, self._update_progress_callback)
            self.finished.emit()
        except Exception as e:
            self.conversion_error.emit(str(e))

    def _update_progress_callback(self, message, percentage):
        self.progress_updated.emit(message, percentage)

class AddToZipWorker(QObject):
    finished = Signal()
    progress_updated = Signal(str, int)
    conversion_error = Signal(str)

    def __init__(self, zip_path, file_path):
        super().__init__()
        self.archive_path = zip_path # Renamed for clarity with generic archive_manager
        self.file_to_add_path = file_path

    def run(self):
        try:
            add_to_archive(self.archive_path, self.file_to_add_path, self._update_progress_callback)
            self.finished.emit()
        except NotImplementedError as e:
            self.conversion_error.emit(str(e))
        except Exception as e:
            self.conversion_error.emit(str(e))

    def _update_progress_callback(self, message, percentage):
        self.progress_updated.emit(message, percentage)

class ListZipContentsWorker(QObject):
    finished = Signal(list) # Emits list of contents
    conversion_error = Signal(str)

    def __init__(self, zip_path):
        super().__init__()
        self.archive_path = zip_path # Renamed for clarity with generic archive_manager

    def run(self):
        try:
            contents = list_archive_contents(self.archive_path)
            self.finished.emit(contents)
        except Exception as e:
            self.conversion_error.emit(str(e))


class ZipGUI(QMainWindow):

    def _load_qss_file(self, filename):
        """Load QSS content from external file"""
        qss_path = os.path.join(os.path.dirname(__file__), 'qss', filename)
        try:
            with open(qss_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: QSS file not found: {qss_path}")
            return ""
        except Exception as e:
            print(f"Error loading QSS file {qss_path}: {e}")
            return ""

    @property
    def LIGHT_QSS(self):
        """Load light theme QSS from external file"""
        return self._load_qss_file('zip_light.qss')

    @property
    def DARK_QSS(self):
        """Load dark theme QSS from external file"""
        return self._load_qss_file('zip_dark.qss')

    def __init__(self, initial_dark_mode=False):
        super().__init__()
        self.setWindowTitle("ZIP File Processing Tool")
        self.setGeometry(200, 200, 800, 600)
        self.setMinimumSize(600, 500)
        

        self.init_variables()
        self.setup_ui()
        self._apply_theme(initial_dark_mode)
        self.center_window() # Center the window after UI setup
       
        setTheme(Theme.AUTO)
    
    def init_variables(self):
        # Variables for Create ZIP tab
        self.create_sources = []
        self.create_output_path = ""
        self.create_archive_format = "zip" # Default to zip
        self.create_zip_worker_thread = None # Renamed to generic for clarity
        self.create_zip_worker = None # Renamed to generic for clarity
        
        # Variables for Extract ZIP tab
        self.extract_zip_path = ""
        self.extract_dest_path = ""
        self.extract_zip_worker_thread = None # Renamed to generic for clarity
        self.extract_zip_worker = None # Renamed to generic for clarity
        
        # Variables for Add to ZIP tab
        self.add_zip_path = ""
        self.add_file_path = ""
        self.add_to_zip_worker_thread = None # Renamed to generic for clarity
        self.add_to_zip_worker = None # Renamed to generic for clarity
        
        # Variables for List Contents tab
        self.list_zip_path = ""
        self.list_zip_worker_thread = None # Renamed to generic for clarity
        self.list_zip_worker = None # Renamed to generic for clarity

    def setup_ui(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        
        self.notebook = QTabWidget(self.main_widget)
        self.main_layout.addWidget(self.notebook, 1) # Add notebook with stretch
        
        self.create_create_tab()
        self.create_extract_tab()
        self.create_add_tab()
        self.create_list_tab()
        
        # Add a stretch to the main_layout to push everything to the top
        self.main_layout.addStretch(1)

    def _apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.setStyleSheet(self.DARK_QSS)
        else:
            self.setStyleSheet(self.LIGHT_QSS)

    def _apply_system_theme(self, is_dark_mode):
        self._apply_theme(is_dark_mode)

    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # --- Tab creation methods (to be implemented with PySide6 widgets) ---
    def create_create_tab(self):
        tab_panel = QWidget()
        tab_sizer = QVBoxLayout(tab_panel)
        self.notebook.addTab(tab_panel, "Create Archive") # Changed tab title

        # Output file selection
        output_box = QGroupBox("Output Archive File") # Changed group box title
        output_box_sizer = QHBoxLayout(output_box)
        
        self.create_output_text = LineEdit()
        self.create_output_text.setReadOnly(True)
        output_box_sizer.addWidget(self.create_output_text, 1)
        output_button = QPushButton("Browse...")
        output_button.clicked.connect(self.browse_create_output)
        output_box_sizer.addWidget(output_button)
        tab_sizer.addWidget(output_box)

        # Archive Format Selection (new)
        format_layout = QHBoxLayout()
        format_label = QLabel("Archive Format:")
        self.create_format_combo = ComboBox()
        # Filter formats to only allow creation of supported types
        self.create_format_combo.addItems([f.upper() for f in SUPPORTED_ARCHIVE_FORMATS if f != 'rar' and f != 'tgz'])
        self.create_format_combo.setCurrentText("ZIP")
        self.create_format_combo.currentIndexChanged.connect(self.on_create_format_change)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.create_format_combo, 1)
        tab_sizer.addLayout(format_layout)

        # Source files list
        sources_box = QGroupBox("Source Files/Directories")
        sources_box_sizer = QVBoxLayout(sources_box)
        
        self.sources_listbox = ListWidget()
        sources_box_sizer.addWidget(self.sources_listbox, 1)
        # 设置右键点击立即选中
        
        # Buttons to add/remove sources
        button_sizer = QHBoxLayout()
        add_files_button = QPushButton("Add Files...")
        add_files_button.clicked.connect(self.add_source_files)
        button_sizer.addWidget(add_files_button)
        
        add_folder_button = QPushButton("Add Folder...")
        add_folder_button.clicked.connect(self.add_source_folder)
        button_sizer.addWidget(add_folder_button)
        
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_source)
        button_sizer.addWidget(remove_button)
        button_sizer.addStretch(1) # Push buttons to left
        
        sources_box_sizer.addLayout(button_sizer)
        tab_sizer.addWidget(sources_box, 1) # Give sources box more stretch

        # Progress bar
        self.create_progress_label = QLabel("")
        tab_sizer.addWidget(self.create_progress_label)
        
        self.create_progress = ProgressBar()
        self.create_progress.setRange(0, 100)
        self.create_progress.setValue(0)
        tab_sizer.addWidget(self.create_progress)

        # Create button
        create_button = QPushButton("Create Archive") # Changed button text
        create_button.clicked.connect(self.start_create_archive) # Changed signal
        tab_sizer.addWidget(create_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        tab_sizer.addStretch(1) # Push content to top

    def create_extract_tab(self):
        tab_panel = QWidget()
        tab_sizer = QVBoxLayout(tab_panel)
        self.notebook.addTab(tab_panel, "Extract Archive") # Changed tab title

        # Archive file selection (changed title)
        zip_box = QGroupBox("Archive File to Extract")
        zip_box_sizer = QHBoxLayout(zip_box)

        self.extract_zip_text = LineEdit()
        self.extract_zip_text.setReadOnly(True)
        zip_box_sizer.addWidget(self.extract_zip_text, 1)
        zip_button = QPushButton("Browse...")
        zip_button.clicked.connect(self.browse_extract_archive) # Changed signal
        zip_box_sizer.addWidget(zip_button)
        tab_sizer.addWidget(zip_box)

        # Destination folder selection
        dest_box = QGroupBox("Destination Folder")
        dest_box_sizer = QHBoxLayout(dest_box)

        self.extract_dest_text = LineEdit()
        self.extract_dest_text.setReadOnly(True)
        dest_box_sizer.addWidget(self.extract_dest_text, 1)
        dest_button = QPushButton("Browse...")
        dest_button.clicked.connect(self.browse_extract_dest)
        dest_box_sizer.addWidget(dest_button)
        tab_sizer.addWidget(dest_box)

        # Progress bar
        self.extract_progress_label = QLabel("")
        tab_sizer.addWidget(self.extract_progress_label)
        
        self.extract_progress = ProgressBar()
        self.extract_progress.setRange(0, 100)
        self.extract_progress.setValue(0)
        tab_sizer.addWidget(self.extract_progress)

        # Extract button
        extract_button = QPushButton("Extract Archive") # Changed button text
        extract_button.clicked.connect(self.start_extract_archive) # Changed signal
        tab_sizer.addWidget(extract_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        tab_sizer.addStretch(1) # Push content to top

    def create_add_tab(self):
        tab_panel = QWidget()
        tab_sizer = QVBoxLayout(tab_panel)
        self.notebook.addTab(tab_panel, "Add to Archive") # Changed tab title

        # Existing Archive file selection
        zip_box = QGroupBox("Existing Archive File") # Changed group box title
        zip_box_sizer = QHBoxLayout(zip_box)

        self.add_zip_text = LineEdit()
        self.add_zip_text.setReadOnly(True)
        zip_box_sizer.addWidget(self.add_zip_text, 1)
        zip_button = QPushButton("Browse...")
        zip_button.clicked.connect(self.browse_add_archive) # Changed signal
        zip_box_sizer.addWidget(zip_button)
        tab_sizer.addWidget(zip_box)

        # File to add selection
        file_box = QGroupBox("File to Add")
        file_box_sizer = QHBoxLayout(file_box)

        self.add_file_text = LineEdit()
        self.add_file_text.setReadOnly(True)
        file_box_sizer.addWidget(self.add_file_text, 1)
        file_button = QPushButton("Browse...")
        file_button.clicked.connect(self.browse_add_file)
        file_box_sizer.addWidget(file_button)
        tab_sizer.addWidget(file_box)

        # Progress bar
        self.add_progress_label = QLabel("")
        tab_sizer.addWidget(self.add_progress_label)
        
        self.add_progress = ProgressBar()
        self.add_progress.setRange(0, 100)
        self.add_progress.setValue(0)
        tab_sizer.addWidget(self.add_progress)

        # Add button
        add_button = QPushButton("Add to Archive") # Changed button text
        add_button.clicked.connect(self.start_add_to_archive) # Changed signal
        tab_sizer.addWidget(add_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        tab_sizer.addStretch(1) # Push content to top

    def create_list_tab(self):
        tab_panel = QWidget()
        tab_sizer = QVBoxLayout(tab_panel)
        self.notebook.addTab(tab_panel, "List Contents")

        # Archive file selection (changed title)
        zip_box = QGroupBox("Archive File")
        zip_box_sizer = QHBoxLayout(zip_box)
        
        self.list_zip_text = LineEdit()
        self.list_zip_text.setReadOnly(True)
        zip_box_sizer.addWidget(self.list_zip_text, 1)
        zip_button = QPushButton("Browse...")
        zip_button.clicked.connect(self.browse_list_archive) # Changed signal
        zip_box_sizer.addWidget(zip_button)
        tab_sizer.addWidget(zip_box)
        
        # Listbox for contents
        contents_box = QGroupBox("Archive Contents") # Changed group box title
        contents_box_sizer = QVBoxLayout(contents_box)

        self.contents_listbox = ListWidget()
        contents_box_sizer.addWidget(self.contents_listbox, 1)
        tab_sizer.addWidget(contents_box, 1) # Give contents box more stretch

        # List button
        list_button = QPushButton("List Contents")
        list_button.clicked.connect(self.start_list_archive_contents) # Changed signal
        tab_sizer.addWidget(list_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        tab_sizer.addStretch(1) # Push content to top

    # --- Event handlers (converted to PySide6) ---
    def on_create_format_change(self):
        selected_format = self.create_format_combo.currentText().lower()
        self.create_archive_format = selected_format
        # Adjust output path suffix automatically
        if self.create_output_path:
            base_name = os.path.splitext(self.create_output_path)[0]
            self.create_output_path = f"{base_name}.{selected_format}"
            self.create_output_text.setText(self.create_output_path)

    def browse_create_output(self):
        file_dialog = QFileDialog(self)
        selected_format = self.create_archive_format
        # Generate wildcard for creation, excluding formats not supported for creation
        creation_formats = [f.upper() for f in SUPPORTED_ARCHIVE_FORMATS if f not in ['rar', 'tgz']]
        wildcard_parts = [f"{fmt} files (*.{fmt.lower()})" for fmt in creation_formats]
        wildcard = ";;".join(wildcard_parts) + ";;All files (*.*)"
        
        file_dialog.setNameFilter(wildcard)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setDefaultSuffix(selected_format)
        if file_dialog.exec():
            self.create_output_path = file_dialog.selectedFiles()[0]
            if not self.create_output_path.lower().endswith(f".{selected_format}"):
                self.create_output_path += f".{selected_format}"
            self.create_output_text.setText(self.create_output_path)

    def add_source_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("All files (*.*)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        if file_dialog.exec():
            paths = file_dialog.selectedFiles()
            for path in paths:
                if path not in self.create_sources:
                    self.create_sources.append(path)
                    self.sources_listbox.addItem(path)

    def add_source_folder(self):
        dir_dialog = QFileDialog(self)
        dir_dialog.setFileMode(QFileDialog.FileMode.Directory)
        dir_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dir_dialog.exec():
            folder_path = dir_dialog.selectedFiles()[0]
            if folder_path not in self.create_sources:
                self.create_sources.append(folder_path)
                self.sources_listbox.addItem(f"[FOLDER] {folder_path}")

    def remove_source(self):
        selected_items = self.sources_listbox.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Info", "Please select items to remove.")
            return
        
        for item in selected_items:
            row = self.sources_listbox.row(item)
            self.sources_listbox.takeItem(row)
            # Remove the item from self.create_sources list by value, not index
            # This is safer if multiple items are selected and then removed in a loop
            item_text = item.text()
            if item_text.startswith("[FOLDER] "):
                item_text = item_text[len("[FOLDER] "):]
            if item_text in self.create_sources:
                self.create_sources.remove(item_text)

    def update_create_progress(self, message, progress):
        self.create_progress_label.setText(message)
        if progress >= 0:
            self.create_progress.setValue(int(progress))

    def start_create_archive(self):
        if not self.create_output_path:
            QMessageBox.critical(self, "Error", "Please specify an output archive file.")
            return
        if not self.create_sources:
            QMessageBox.critical(self, "Error", "Please add at least one source file or folder.")
            return
        if self.create_archive_format == 'rar':
            QMessageBox.critical(self, "Error", "Creating RAR archives is not supported.")
            return

        self.create_progress_label.setText("Starting archive creation...")
        self.create_progress.setValue(0)
        
        self.create_zip_worker = CreateZipWorker(self.create_output_path, self.create_sources, self.create_archive_format)
        self.create_zip_worker_thread = QThread()
        self.create_zip_worker.moveToThread(self.create_zip_worker_thread)

        self.create_zip_worker.finished.connect(self.on_create_archive_finished)
        self.create_zip_worker.progress_updated.connect(self.update_create_progress)
        self.create_zip_worker.conversion_error.connect(self.on_create_archive_error)
        self.create_zip_worker_thread.started.connect(self.create_zip_worker.run)
        self.create_zip_worker_thread.start()

    def on_create_archive_finished(self):
        if self.create_zip_worker_thread and self.create_zip_worker_thread.isRunning():
            self.create_zip_worker_thread.quit()
            self.create_zip_worker_thread.wait()
        QMessageBox.information(self, "Success", "Archive created successfully!")

    def on_create_archive_error(self, error_message):
        if self.create_zip_worker_thread and self.create_zip_worker_thread.isRunning():
            self.create_zip_worker_thread.quit()
            self.create_zip_worker_thread.wait()
        QMessageBox.critical(self, "Error", f"Error creating archive: {str(error_message)}")
        self.create_progress_label.setText("Archive creation failed.")


    def browse_extract_archive(self):
        file_dialog = QFileDialog(self)
        wildcard_parts = [f"{fmt.upper()} files (*.{fmt})" for fmt in SUPPORTED_ARCHIVE_FORMATS]
        wildcard = ";;".join(wildcard_parts) + ";;All files (*.*)"
        file_dialog.setNameFilter(wildcard)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            self.extract_zip_path = file_dialog.selectedFiles()[0]
            self.extract_zip_text.setText(self.extract_zip_path)

    def browse_extract_dest(self):
        dir_dialog = QFileDialog(self)
        dir_dialog.setFileMode(QFileDialog.FileMode.Directory)
        dir_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dir_dialog.exec():
            self.extract_dest_path = dir_dialog.selectedFiles()[0]
            self.extract_dest_text.setText(self.extract_dest_path)

    def update_extract_progress(self, message, progress):
        self.extract_progress_label.setText(message)
        if progress >= 0:
            self.extract_progress.setValue(int(progress))

    def start_extract_archive(self):
        if not self.extract_zip_path:
            QMessageBox.critical(self, "Error", "Please specify an archive file to extract.")
            return
        if not self.extract_dest_path:
            QMessageBox.critical(self, "Error", "Please specify a destination folder.")
            return

        self.extract_progress_label.setText("Starting archive extraction...")
        self.extract_progress.setValue(0)

        self.extract_zip_worker = ExtractZipWorker(self.extract_zip_path, self.extract_dest_path)
        self.extract_zip_worker_thread = QThread()
        self.extract_zip_worker.moveToThread(self.extract_zip_worker_thread)

        self.extract_zip_worker.finished.connect(self.on_extract_archive_finished)
        self.extract_zip_worker.progress_updated.connect(self.update_extract_progress)
        self.extract_zip_worker.conversion_error.connect(self.on_extract_archive_error)
        self.extract_zip_worker_thread.started.connect(self.extract_zip_worker.run)
        self.extract_zip_worker_thread.start()

    def on_extract_archive_finished(self):
        if self.extract_zip_worker_thread and self.extract_zip_worker_thread.isRunning():
            self.extract_zip_worker_thread.quit()
            self.extract_zip_worker_thread.wait()
        QMessageBox.information(self, "Success", "Archive extracted successfully!")

    def on_extract_archive_error(self, error_message):
        if self.extract_zip_worker_thread and self.extract_zip_worker_thread.isRunning():
            self.extract_zip_worker_thread.quit()
            self.extract_zip_worker_thread.wait()
        QMessageBox.critical(self, "Error", f"Error extracting archive: {str(error_message)}")
        self.extract_progress_label.setText("Archive extraction failed.")


    def browse_add_archive(self):
        file_dialog = QFileDialog(self)
        wildcard_parts = [f"{fmt.upper()} files (*.{fmt})" for fmt in SUPPORTED_ARCHIVE_FORMATS]
        wildcard = ";;".join(wildcard_parts) + ";;All files (*.*)"
        file_dialog.setNameFilter(wildcard)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            self.add_zip_path = file_dialog.selectedFiles()[0]
            self.add_zip_text.setText(self.add_zip_path)

    def browse_add_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("All files (*.*)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            self.add_file_path = file_dialog.selectedFiles()[0]
            self.add_file_text.setText(self.add_file_path)

    def update_add_progress(self, message, progress):
        self.add_progress_label.setText(message)
        if progress >= 0:
            self.add_progress.setValue(int(progress))

    def start_add_to_archive(self):
        if not self.add_zip_path:
            QMessageBox.critical(self, "Error", "Please specify an existing archive file to add to.")
            return
        if not self.add_file_path:
            QMessageBox.critical(self, "Error", "Please specify a file to add to the archive.")
            return
        archive_format = Path(self.add_zip_path).suffix.lower().lstrip('.')
        if archive_format == 'rar':
            QMessageBox.critical(self, "Error", "Adding files to RAR archives is not supported.")
            return

        self.add_progress_label.setText("Starting archive file addition...")
        self.add_progress.setValue(0)

        self.add_to_zip_worker = AddToZipWorker(self.add_zip_path, self.add_file_path)
        self.add_to_zip_worker_thread = QThread()
        self.add_to_zip_worker.moveToThread(self.add_to_zip_worker_thread)

        self.add_to_zip_worker.finished.connect(self.on_add_to_archive_finished)
        self.add_to_zip_worker.progress_updated.connect(self.update_add_progress)
        self.add_to_zip_worker.conversion_error.connect(self.on_add_to_archive_error)
        self.add_to_zip_worker_thread.started.connect(self.add_to_zip_worker.run)
        self.add_to_zip_worker_thread.start()

    def on_add_to_archive_finished(self):
        if self.add_to_zip_worker_thread and self.add_to_zip_worker_thread.isRunning():
            self.add_to_zip_worker_thread.quit()
            self.add_to_zip_worker_thread.wait()
        QMessageBox.information(self, "Success", "File added to archive successfully!")

    def on_add_to_archive_error(self, error_message):
        if self.add_to_zip_worker_thread and self.add_to_zip_worker_thread.isRunning():
            self.add_to_zip_worker_thread.quit()
            self.add_to_zip_worker_thread.wait()
        QMessageBox.critical(self, "Error", f"Error adding file to archive: {str(error_message)}")
        self.add_progress_label.setText("Archive file addition failed.")


    def browse_list_archive(self):
        file_dialog = QFileDialog(self)
        wildcard_parts = [f"{fmt.upper()} files (*.{fmt})" for fmt in SUPPORTED_ARCHIVE_FORMATS]
        wildcard = ";;".join(wildcard_parts) + ";;All files (*.*)"
        file_dialog.setNameFilter(wildcard)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            self.list_zip_path = file_dialog.selectedFiles()[0]
            self.list_zip_text.setText(self.list_zip_path)
            self.start_list_archive_contents() # Automatically list contents after selecting file

    def start_list_archive_contents(self):
        if not self.list_zip_path:
            QMessageBox.critical(self, "Error", "Please select an archive file to list contents.")
            return

        self.contents_listbox.clear()
        self.contents_listbox.addItem("Listing contents...")

        self.list_zip_worker = ListZipContentsWorker(self.list_zip_path)
        self.list_zip_worker_thread = QThread()
        self.list_zip_worker.moveToThread(self.list_zip_worker_thread)

        self.list_zip_worker.finished.connect(self.update_contents_list)
        self.list_zip_worker.conversion_error.connect(self.on_list_archive_error)
        self.list_zip_worker_thread.started.connect(self.list_zip_worker.run)
        self.list_zip_worker_thread.start()

    def update_contents_list(self, contents):
        if self.list_zip_worker_thread and self.list_zip_worker_thread.isRunning():
            self.list_zip_worker_thread.quit()
            self.list_zip_worker_thread.wait()
        self.contents_listbox.clear()
        if contents:
            for item in contents:
                    self.contents_listbox.addItem(item)
            QMessageBox.information(self, "Success", "Archive contents listed successfully!")
        else:
            self.contents_listbox.addItem("No contents found or invalid archive.")
            QMessageBox.warning(self, "Warning", "No contents found or invalid archive.")


    def on_list_archive_error(self, error_message):
        if self.list_zip_worker_thread and self.list_zip_worker_thread.isRunning():
            self.list_zip_worker_thread.quit()
            self.list_zip_worker_thread.wait()
        QMessageBox.critical(self, "Error", f"Error listing archive contents: {str(error_message)}")
        self.contents_listbox.clear()
        self.contents_listbox.addItem("Error listing contents.")


class ZipAppRunner: # Renamed to avoid conflict with QApp
    def __init__(self):
        self.app = QApplication(sys.argv)
        from support.toggle import theme_manager
        theme_manager.start()
        setTheme(Theme.AUTO)
        self.window = ZipGUI(initial_dark_mode=self.app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5)
        self.window.show()
        self.app.paletteChanged.connect(lambda: self.window._apply_system_theme(self.app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5))

    def MainLoop(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app_runner = ZipAppRunner()
    app_runner.MainLoop()