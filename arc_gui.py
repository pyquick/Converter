import os
import sys
# import threading # PySide6 will use QThread
import subprocess
from pathlib import Path

from PySide6.QtCore import QThread, Signal, Qt, QTimer, QUrl, QObject
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar, 
                               QTabWidget, QWidget, QGroupBox, QListWidget, QListWidgetItem,
                               QFileDialog, QCheckBox, QComboBox, QFrame, QMessageBox, QMenu)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPalette
from qfluentwidgets import *

from con import CON
from support.toggle import ThemeManager
# Add the current directory to Python path to import convertzip module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from support.archive_manager import create_archive, extract_archive, add_to_archive, list_archive_contents, SUPPORTED_ARCHIVE_FORMATS

# Remove the problematic reconfigure calls
# sys.stdout.reconfigure(encoding='utf-8')
# sys.stderr.reconfigure(encoding='utf-8')
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

    def __init__(self, zip_path, file_paths):
        super().__init__()
        self.archive_path = zip_path # Renamed for clarity with generic archive_manager
        self.files_to_add = file_paths if isinstance(file_paths, list) else [file_paths]

    def run(self):
        try:
            # Handle multiple files
            total_files = len(self.files_to_add)
            for i, file_path in enumerate(self.files_to_add):
                self._update_progress_callback(f"Adding file {i+1}/{total_files}: {os.path.basename(file_path)}", (i/total_files)*100)
                add_to_archive(self.archive_path, file_path, None)  # No individual progress for each file
            
            self._update_progress_callback(f"Added {total_files} files to archive", 100)
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
    password_required = Signal(str) # Emits error message when password is required

    def __init__(self, zip_path):
        super().__init__()
        self.archive_path = zip_path # Renamed for clarity with generic archive_manager

    def run(self):
        try:
            contents = list_archive_contents(self.archive_path)
            self.finished.emit(contents)
        except RuntimeError as e:
            # 处理需要密码的情况
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                self.password_required.emit(str(e))
            else:
                self.conversion_error.emit(str(e))
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
        self.setWindowTitle("Archive File Processing Tool")
        self.setGeometry(200, 200, 800, 600)
        self.setMinimumSize(600, 500)
        
        # Enable drag and drop for the main window
        self.setAcceptDrops(True)
        
        self.themeListener = SystemThemeListener(self)
        self.init_variables()
        self.setup_ui()
        self._apply_theme(initial_dark_mode)
        self.center_window() # Center the window after UI setup
        self.qss_combo=CON.qss_combo
        setTheme(Theme.AUTO)
        self.themeListener.start()
        qconfig.themeChanged.connect(self._onThemeChanged)
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止监听器线程
        if hasattr(self, 'themeListener'):
            self.themeListener.terminate()
            self.themeListener.deleteLater()
        super().closeEvent(event)
    def _onThemeChanged(self, theme: Theme):
        """主题变化处理"""
        # 更新界面以响应主题变化
        self.update()
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
        
        # Password protection status for archive contents
        self.is_password_protected = False

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
        
        # Apply custom stylesheets to all buttons after UI creation
        self.apply_custom_styles()

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
        
    def apply_custom_styles(self):
        """Apply custom stylesheets to all buttons after UI creation"""
        try:
            # Find all PushButton and PrimaryPushButton widgets and apply custom styles
            for button in self.findChildren(PushButton):
                setCustomStyleSheet(button, CON.qss, CON.qss)
            for button in self.findChildren(PrimaryPushButton):
                setCustomStyleSheet(button, CON.qss, CON.qss)
        except Exception as e:
            print(f"Warning: Could not apply custom stylesheets: {e}")

    # --- Tab creation methods (to be implemented with PySide6 widgets) ---
    def create_create_tab(self):
        tab_panel = QWidget()
        tab_sizer = QVBoxLayout(tab_panel)
        self.notebook.addTab(tab_panel, "Create Archive") # Changed tab title

        # Output file selection
        output_box = QGroupBox("Output Archive File") # Changed group box title
        output_box_sizer = QHBoxLayout(output_box)
        
        self.create_output_text = LineEdit()
        setCustomStyleSheet(self.create_output_text, CON.qss_line, CON.qss_line)
        # self.create_output_text.setReadOnly(True)  # 允许用户手动输入路径
        output_box_sizer.addWidget(self.create_output_text, 1)
        output_button = PushButton("Browse...")
        output_button.clicked.connect(self.browse_create_output)
        output_box_sizer.addWidget(output_button)
        tab_sizer.addWidget(output_box)

        # Archive Format Selection (new)
        format_layout = QHBoxLayout()
        format_label = QLabel("Archive Format:")
        self.create_format_combo = ModelComboBox()
        # Filter formats to only allow creation of supported types
        self.create_format_combo.addItems([f.upper() for f in SUPPORTED_ARCHIVE_FORMATS if f != 'tgz'])
        self.create_format_combo.setCurrentText("ZIP")
        setCustomStyleSheet(self.create_format_combo, CON.qss_combo, CON.qss_combo)
        self.create_format_combo.currentIndexChanged.connect(self.on_create_format_change)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.create_format_combo, 1)
        tab_sizer.addLayout(format_layout)

        # Source files list
        sources_box = QGroupBox("Source Files/Directories")
        sources_box_sizer = QVBoxLayout(sources_box)
        
        self.sources_listbox = ListWidget()
        self.sources_listbox.setMinimumHeight(200)  # 设置最小高度
        sources_box_sizer.addWidget(self.sources_listbox, 2)  # 增加拉伸权重
        # 设置右键点击立即选中
        self.sources_listbox.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sources_listbox.customContextMenuRequested.connect(self.show_sources_context_menu)
        
        # Buttons to add/remove sources
        button_sizer = QHBoxLayout()
        add_files_button = PushButton("Add Files...")
        add_files_button.clicked.connect(self.add_source_files)
        button_sizer.addWidget(add_files_button)
        
        add_folder_button = PushButton("Add Folder...")
        add_folder_button.clicked.connect(self.add_source_folder)
        button_sizer.addWidget(add_folder_button)
        
        remove_button = PushButton("Remove Selected")
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
        create_button = PrimaryPushButton("Create Archive") # Changed button text
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
        setCustomStyleSheet(self.extract_zip_text, CON.qss_line, CON.qss_line)
        # self.extract_zip_text.setReadOnly(True)  # 允许用户手动输入路径
        zip_box_sizer.addWidget(self.extract_zip_text, 1)
        zip_button = PushButton("Browse...")

        zip_button.clicked.connect(self.browse_extract_archive) # Changed signal
        zip_box_sizer.addWidget(zip_button)
        tab_sizer.addWidget(zip_box)

        # Destination folder selection
        dest_box = QGroupBox("Destination Folder")
        dest_box_sizer = QHBoxLayout(dest_box)

        self.extract_dest_text = LineEdit()
        setCustomStyleSheet(self.extract_dest_text, CON.qss_line, CON.qss_line)
        # self.extract_dest_text.setReadOnly(True)  # 允许用户手动输入路径
        dest_box_sizer.addWidget(self.extract_dest_text, 1)
        dest_button = PushButton("Browse...")

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
        extract_button = PrimaryPushButton("Extract Archive") # Changed button text

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
        setCustomStyleSheet(self.add_zip_text, CON.qss_line, CON.qss_line)
        # self.add_zip_text.setReadOnly(True)  # 允许用户手动输入路径
        zip_box_sizer.addWidget(self.add_zip_text, 1)
        zip_button = PushButton("Browse...")

        zip_button.clicked.connect(self.browse_add_archive) # Changed signal
        zip_box_sizer.addWidget(zip_button)
        tab_sizer.addWidget(zip_box)

        # File to add selection
        file_box = QGroupBox("Files to Add")
        file_box_sizer = QVBoxLayout(file_box)

        # File list for multiple files (always visible)
        self.add_files_listbox = ListWidget()
        self.add_files_listbox.setMinimumHeight(150)
        self.add_files_listbox.setVisible(True)  # Always visible
        file_box_sizer.addWidget(self.add_files_listbox)
        
        # Browse button
        file_button = PushButton("Browse...")
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
        add_button = PrimaryPushButton("Add to Archive") # Changed button text

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
        setCustomStyleSheet(self.list_zip_text, CON.qss_line, CON.qss_line)
        # self.list_zip_text.setReadOnly(True)  # 允许用户手动输入路径
        zip_box_sizer.addWidget(self.list_zip_text, 1)
        zip_button = PushButton("Browse...")

        zip_button.clicked.connect(self.browse_list_archive) # Changed signal
        zip_box_sizer.addWidget(zip_button)
        tab_sizer.addWidget(zip_box)
        
        # Listbox for contents
        contents_box = QGroupBox("Archive Contents") # Changed group box title
        contents_box_sizer = QVBoxLayout(contents_box)

        self.contents_listbox = ListWidget()
        self.contents_listbox.setMinimumHeight(250)  # 设置更大的最小高度
        contents_box_sizer.addWidget(self.contents_listbox, 3)  # 增加拉伸权重
        # 设置右键菜单
        self.contents_listbox.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.contents_listbox.customContextMenuRequested.connect(self.show_contents_context_menu)
        tab_sizer.addWidget(contents_box, 2) # Give contents box more stretch

        # List button
        list_button = PrimaryPushButton("List Contents")

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
        creation_formats = [f.upper() for f in SUPPORTED_ARCHIVE_FORMATS if f != 'tgz']
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
            PopupTeachingTip.create(
                target=self.sources_listbox,
                icon=InfoBarIcon.INFORMATION,
                title='Info',
                content='Please select items to remove.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
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
            PopupTeachingTip.create(
                target=self.create_output_text,
                icon=InfoBarIcon.ERROR,
                title='Error',
                content='Please specify an output archive file.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        if not self.create_sources:
            PopupTeachingTip.create(
                target=self.sources_listbox,
                icon=InfoBarIcon.ERROR,
                title='Error',
                content='Please add at least one source file or folder.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        # RAR format is now supported through external rar command
        # No need to show error message

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
        PopupTeachingTip.create(
            target=self.create_progress,
            icon=InfoBarIcon.SUCCESS,
            title='Success',
            content='Archive created successfully!',
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=2000,
            parent=self
        )

    def on_create_archive_error(self, error_message):
        if self.create_zip_worker_thread and self.create_zip_worker_thread.isRunning():
            self.create_zip_worker_thread.quit()
            self.create_zip_worker_thread.wait()
        PopupTeachingTip.create(
            target=self.create_progress,
            icon=InfoBarIcon.ERROR,
            title='Error',
            content=f'Error creating archive: {str(error_message)}',
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=3000,
            parent=self
        )
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
            # Auto-configure output directory to the file's parent directory
            self.auto_set_extract_dest_from_file(self.extract_zip_path)

    def browse_extract_dest(self):
        dir_dialog = QFileDialog(self)
        dir_dialog.setFileMode(QFileDialog.FileMode.Directory)
        dir_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dir_dialog.exec():
            self.extract_dest_path = dir_dialog.selectedFiles()[0]
            self.extract_dest_text.setText(self.extract_dest_path)

    def auto_set_extract_dest_from_file(self, file_path):
        """Automatically set the extract destination to the file's parent directory"""
        try:
            parent_dir = os.path.dirname(file_path)
            if parent_dir and os.path.exists(parent_dir):
                self.extract_dest_path = parent_dir
                self.extract_dest_text.setText(self.extract_dest_path)
        except Exception as e:
            print(f"Warning: Could not auto-set extract destination: {e}")

    def update_extract_progress(self, message, progress):
        self.extract_progress_label.setText(message)
        if progress >= 0:
            self.extract_progress.setValue(int(progress))

    def start_extract_archive(self):
        if not self.extract_zip_path:
            PopupTeachingTip.create(
                target=self.extract_zip_text,
                icon=InfoBarIcon.ERROR,
                title='Error',
                content='Please specify an archive file to extract.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        if not self.extract_dest_path:
            PopupTeachingTip.create(
                target=self.extract_dest_text,
                icon=InfoBarIcon.ERROR,
                title='Error',
                content='Please specify a destination folder.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
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
        PopupTeachingTip.create(
            target=self.extract_progress,
            icon=InfoBarIcon.SUCCESS,
            title='Success',
            content='Archive extracted successfully!',
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=2000,
            parent=self
        )

    def on_extract_archive_error(self, error_message):
        if self.extract_zip_worker_thread and self.extract_zip_worker_thread.isRunning():
            self.extract_zip_worker_thread.quit()
            self.extract_zip_worker_thread.wait()
        PopupTeachingTip.create(
            target=self.extract_progress,
            icon=InfoBarIcon.ERROR,
            title='Error',
            content=f'Error extracting archive: {str(error_message)}',
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=3000,
            parent=self
        )
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
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # Allow multiple file selection
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                # Store files as list
                self.add_file_path = selected_files
                
                # Update the UI display
                self.update_add_files_list(selected_files)

    def update_add_progress(self, message, progress):
        self.add_progress_label.setText(message)
        if progress >= 0:
            self.add_progress.setValue(int(progress))

    def start_add_to_archive(self):
        if not self.add_zip_path:
            PopupTeachingTip.create(
                target=self.add_zip_text,
                icon=InfoBarIcon.ERROR,
                title='Error',
                content='Please specify an existing archive file to add to.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        if not self.add_file_path:
            PopupTeachingTip.create(
                target=self.add_files_listbox,
                icon=InfoBarIcon.ERROR,
                title='Error',
                content='Please specify a file to add to the archive.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        archive_format = Path(self.add_zip_path).suffix.lower().lstrip('.')
        # RAR format is now supported through external rar command
        # No need to show error message

        self.add_progress_label.setText("Starting archive file addition...")
        self.add_progress.setValue(0)

        # Handle multiple files - split by semicolon if contains multiple paths
        if isinstance(self.add_file_path, list):
            # Direct list of files (from drag and drop)
            file_paths = self.add_file_path
        elif ';' in self.add_file_path:
            # Semicolon-separated paths from browse dialog
            file_paths = [path.strip() for path in self.add_file_path.split(';') if path.strip()]
        else:
            # Single file path
            file_paths = [self.add_file_path.strip()]

        self.add_to_zip_worker = AddToZipWorker(self.add_zip_path, file_paths)
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
        
        # Count number of files added
        file_count = len(self.add_to_zip_worker.files_to_add) if hasattr(self.add_to_zip_worker, 'files_to_add') else 1
        file_text = "files" if file_count > 1 else "file"
        
        PopupTeachingTip.create(
            target=self.add_progress,
            icon=InfoBarIcon.SUCCESS,
            title='Success',
            content=f'{file_count} {file_text} added to archive successfully!',
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=2000,
            parent=self
        )

    def on_add_to_archive_error(self, error_message):
        if self.add_to_zip_worker_thread and self.add_to_zip_worker_thread.isRunning():
            self.add_to_zip_worker_thread.quit()
            self.add_to_zip_worker_thread.wait()
        PopupTeachingTip.create(
            target=self.add_progress,
            icon=InfoBarIcon.ERROR,
            title='Error',
            content=f'Error adding file to archive: {str(error_message)}',
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=3000,
            parent=self
        )
        self.add_progress_label.setText("Archive file addition failed.")

    def update_add_files_list(self, files):
        """更新添加文件列表显示"""
        if not hasattr(self, 'add_files_listbox'):
            return
            
        self.add_files_listbox.clear()
        
        # 始终显示文件列表
        for file_path in files:
            self.add_files_listbox.addItem(os.path.basename(file_path))

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

    def show_sources_context_menu(self, position):
        """显示source files列表的右键菜单"""
        item = self.sources_listbox.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        copy_action = menu.addAction("Copy File")
        
        action = menu.exec(self.sources_listbox.mapToGlobal(position))
        if action == copy_action:
            self.copy_source_file(item)
    
    def copy_source_file(self, item):
        """复制source file到剪贴板"""
        file_path = item.text()
        if file_path.startswith("[FOLDER] "):
            file_path = file_path[len("[FOLDER] "):]
        
        if os.path.exists(file_path):
            clipboard = QApplication.clipboard()
            clipboard.setText(file_path)
            
            PopupTeachingTip.create(
                target=self.sources_listbox,
                icon=InfoBarIcon.SUCCESS,
                title='Success',
                content=f'File path copied: {os.path.basename(file_path)}',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
        else:
            PopupTeachingTip.create(
                target=self.sources_listbox,
                icon=InfoBarIcon.ERROR,
                title='Error',
                content='File does not exist.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
    
    def show_contents_context_menu(self, position):
        """显示archive contents列表的右键菜单"""
        item = self.contents_listbox.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        copy_action = menu.addAction("Copy File")
        
        # 检查文件是否受密码保护
        if self.is_password_protected:
            copy_action.setEnabled(False)
            copy_action.setText("Copy File (Disabled - Password Protected)")
        
        action = menu.exec(self.contents_listbox.mapToGlobal(position))
        if action == copy_action and copy_action.isEnabled():
            self.copy_archive_content(item)
    
    def copy_archive_content(self, item):
        """复制archive content文件路径到剪贴板"""
        content_text = item.text()
        
        # 提取文件名（去掉大小信息）
        filename = content_text.split()[0] if content_text else content_text
        
        clipboard = QApplication.clipboard()
        clipboard.setText(filename)
        
        PopupTeachingTip.create(
            target=self.contents_listbox,
            icon=InfoBarIcon.SUCCESS,
            title='Success',
            content=f'Content path copied: {filename}',
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=2000,
            parent=self
        )

    def start_list_archive_contents(self):
        if not self.list_zip_path:
            PopupTeachingTip.create(
                target=self.list_zip_text,
                icon=InfoBarIcon.ERROR,
                title='Error',
                content='Please select an archive file to list contents.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
            return

        self.contents_listbox.clear()
        self.contents_listbox.addItem("Listing contents...")

        self.list_zip_worker = ListZipContentsWorker(self.list_zip_path)
        self.list_zip_worker_thread = QThread()
        self.list_zip_worker.moveToThread(self.list_zip_worker_thread)

        self.list_zip_worker.finished.connect(self.update_contents_list)
        self.list_zip_worker.conversion_error.connect(self.on_list_archive_error)
        self.list_zip_worker.password_required.connect(self.on_password_required)
        self.list_zip_worker_thread.started.connect(self.list_zip_worker.run)
        self.list_zip_worker_thread.start()

    def update_contents_list(self, contents):
        if self.list_zip_worker_thread and self.list_zip_worker_thread.isRunning():
            self.list_zip_worker_thread.quit()
            self.list_zip_worker_thread.wait()
        self.contents_listbox.clear()
        # 重置密码保护状态
        self.is_password_protected = False
        if contents:
            for item in contents:
                    self.contents_listbox.addItem(item)
            InfoBar.success(
                title='Success',
                content='Archive contents listed successfully!',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        else:
            self.contents_listbox.addItem("No contents found or invalid archive.")
            PopupTeachingTip.create(
                target=self.contents_listbox,
                icon=InfoBarIcon.WARNING,
                title='Warning',
                content='No contents found or invalid archive.',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )

    def on_password_required(self, error_message):
        """处理需要密码的情况"""
        if self.list_zip_worker_thread and self.list_zip_worker_thread.isRunning():
            self.list_zip_worker_thread.quit()
            self.list_zip_worker_thread.wait()
        
        # 设置密码保护状态
        self.is_password_protected = True
        
        PopupTeachingTip.create(
            target=self.contents_listbox,
            icon=InfoBarIcon.WARNING,
            title='Password Required',
            content=f'This archive is password protected: {str(error_message)}',
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=3000,
            parent=self
        )
        self.contents_listbox.clear()
        self.contents_listbox.addItem("Password protected archive - contents cannot be listed")

    def on_list_archive_error(self, error_message):
        if self.list_zip_worker_thread and self.list_zip_worker_thread.isRunning():
            self.list_zip_worker_thread.quit()
            self.list_zip_worker_thread.wait()
        PopupTeachingTip.create(
            target=self.contents_listbox,
            icon=InfoBarIcon.ERROR,
            title='Error',
            content=f'Error listing archive contents: {str(error_message)}',
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=3000,
            parent=self
        )
        self.contents_listbox.clear()
        self.contents_listbox.addItem("Error listing contents.")

    # --- Drag and Drop Event Handlers ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                current_tab = self.notebook.currentIndex()
                
                # Handle Add to Archive tab specially - support multiple files and folders
                if current_tab == 2:  # Add to Archive tab
                    # Accept if we have at least one valid file or folder
                    valid_items = []
                    for url in urls:
                        file_path = url.toLocalFile()
                        if os.path.isfile(file_path):
                            # Check if it's a supported archive format (for existing archive)
                            file_ext = Path(file_path).suffix.lower().lstrip('.')
                            if file_ext in SUPPORTED_ARCHIVE_FORMATS:
                                valid_items.append(file_path)
                            else:
                                # Accept regular files to add to archive
                                valid_items.append(file_path)
                        elif os.path.isdir(file_path):
                            # Accept folders to add to archive
                            valid_items.append(file_path)
                    
                    if valid_items:
                        event.acceptProposedAction()
                        return
                else:
                    # For other tabs, only accept single archive files
                    if len(urls) == 1:
                        file_path = urls[0].toLocalFile()
                        if os.path.isfile(file_path):
                            # Check if it's a supported archive format
                            file_ext = Path(file_path).suffix.lower().lstrip('.')
                            if file_ext in SUPPORTED_ARCHIVE_FORMATS:
                                event.acceptProposedAction()
                                return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                # Get current tab index
                current_tab = self.notebook.currentIndex()
                
                if current_tab == 2:  # Add to Archive tab
                    # Handle multiple files and folders for Add to Archive
                    archive_files = []
                    files_to_add = []
                    
                    # Get current archive file if already set
                    current_archive = self.add_zip_text.text()
                    
                    # Process all dropped items
                    for url in urls:
                        item_path = url.toLocalFile()
                        
                        if os.path.isfile(item_path):
                            file_ext = Path(item_path).suffix.lower().lstrip('.')
                            if file_ext in SUPPORTED_ARCHIVE_FORMATS:
                                # Archive file handling
                                if not current_archive and not archive_files:
                                    # No archive set yet, this becomes the target archive
                                    archive_files.append(item_path)
                                else:
                                    # Archive already exists, treat this as file to add
                                    files_to_add.append(item_path)
                            else:
                                # Regular files are added to the list
                                files_to_add.append(item_path)
                        elif os.path.isdir(item_path):
                            # Folders are added to the list
                            files_to_add.append(item_path)
                    
                    # If we found a new archive file, set it as the target
                    if archive_files:
                        self.add_zip_text.setText(archive_files[0])
                        current_archive = archive_files[0]
                    
                    # If we have files to add, update the UI
                    if files_to_add:
                        # Merge with existing files
                        existing_files = getattr(self, 'add_file_path', [])
                        if isinstance(existing_files, str):
                            existing_files = [existing_files]
                        all_files = existing_files + files_to_add
                        
                        # Remove duplicates while preserving order
                        seen = set()
                        unique_files = []
                        for f in all_files:
                            if f not in seen:
                                seen.add(f)
                                unique_files.append(f)
                        
                        self.add_file_path = unique_files
                        self.update_add_files_list(unique_files)
                        
                        # Show success message
                        InfoBar.success(
                            title='Files added',
                            content=f'Added {len(files_to_add)} items to add list',
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP,
                            duration=2000,
                            parent=self
                        )
                    elif archive_files:
                        # Only archive file was dropped
                        InfoBar.success(
                            title='Archive file set',
                            content=f'Set {os.path.basename(archive_files[0])} as target archive',
                            orient=Qt.Orientation.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP,
                            duration=2000,
                            parent=self
                        )
                    
                    event.acceptProposedAction()
                    return
                
                else:
                    # For other tabs, handle single files as before
                    if len(urls) == 1:
                        file_path = urls[0].toLocalFile()
                        if os.path.isfile(file_path):
                            # Check if it's a supported archive format
                            file_ext = Path(file_path).suffix.lower().lstrip('.')
                            if file_ext in SUPPORTED_ARCHIVE_FORMATS:
                                # Handle based on current tab
                                if current_tab == 0:  # Create Archive tab
                                    # Set as output archive file
                                    self.create_output_path = file_path
                                    self.create_output_text.setText(file_path)
                                    # Auto-detect format from file extension
                                    self.create_format_combo.setCurrentText(file_ext.upper())
                                    event.acceptProposedAction()
                                    
                                elif current_tab == 1:  # Extract Archive tab
                                    # Switch to Extract tab and set the file
                                    self.extract_zip_path = file_path
                                    self.extract_zip_text.setText(file_path)
                                    # Auto-configure output directory
                                    self.auto_set_extract_dest_from_file(file_path)
                                    event.acceptProposedAction()
                                    
                                elif current_tab == 3:  # List Contents tab
                                    # Set as archive file and automatically list contents
                                    self.list_zip_path = file_path
                                    self.list_zip_text.setText(file_path)
                                    # Automatically list contents
                                    self.start_list_archive_contents()
                                    event.acceptProposedAction()
                                
                                return
        event.ignore()


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