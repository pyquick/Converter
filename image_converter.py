#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PNG to ICNS Converter with wxPython GUI

This script provides a graphical interface for converting PNG images to ICNS format.
"""

import platform
import sys
import os
import threading
import subprocess
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel,
    QFileDialog, QMessageBox, QTabWidget, QGroupBox, QSizePolicy,
     QTreeWidgetItem, QFrame, QScrollArea, QListWidgetItem
)
from PySide6.QtGui import QPixmap, QIcon, QFont, QImage, QPalette
from PySide6.QtCore import Qt, QSize, Signal, QObject, QThread
from PySide6.QtCore import QSettings
from darkdetect import isDark
import qfluentwidgets
from support.toggle import theme_manager
from qfluentwidgets import *
# Add the current directory to Python path to import convert module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from support import convert

from con import CON
class ConversionWorker(QObject):
    finished = Signal()
    progress_updated = Signal(str, int)
    conversion_error = Signal(str)

    def __init__(self, input_path, output_path, output_format, min_size_param=None, max_size_param=None, quality_param=None):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.output_format = output_format
        self.quality = int(quality_param) if quality_param is not None else 85
        self.qss=CON.qss
        if output_format == "icns":
            self.min_size = int(min_size_param) if min_size_param is not None else 16
            self.max_size = int(max_size_param) if max_size_param is not None else None # Keep None for convert.py
        else:
            self.min_size = None # Not relevant for non-icns
            self.max_size = None # Not relevant for non-icns
        

    def run(self):
        try:
            if self.output_format == "icns":
                convert.convert_image(
                    self.input_path,
                    self.output_path,
                    self.output_format,
                    int(self.min_size) if self.min_size is not None else 16, # 显式转换为 int
                    int(self.max_size) if self.max_size is not None else None, # 显式转换为 int
                    quality=self.quality,
                    progress_callback=self._update_progress_callback
                )
            else:
                convert.convert_image(
                    self.input_path,
                    self.output_path,
                    self.output_format,
                    quality=self.quality,
                    progress_callback=self._update_progress_callback
                )
            self.finished.emit()
        except Exception as e:
            self.conversion_error.emit(str(e))

    def _update_progress_callback(self, message, percentage):
        self.progress_updated.emit(message, percentage)


class ICNSConverterGUI(QMainWindow):

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
        return self._load_qss_file('converter_light.qss')

    @property
    def DARK_QSS(self):
        """Load dark theme QSS from external file"""
        return self._load_qss_file('converter_dark.qss')

    def __init__(self, initial_dark_mode=False):
        super().__init__()
        self.setWindowTitle("Image Converter")
        self.setGeometry(200, 200, 1000, 1000)
        self.setMinimumSize(1200, 400)

        self.init_variables()
        self.setup_ui()
        self.center_window()

        # Apply initial theme
        self._apply_theme(initial_dark_mode)
        
        # Connect to theme change signal for real-time theme switching
        self.theme_changed = False
        self.listener=SystemThemeListener(self)
        self.listener.start()
        qconfig.themeChanged.connect(self._onThemeChanged)
        # Load settings AFTER UI setup to ensure they override defaults
        self.load_settings()
        
    def _onThemeChanged(self):
        """主题变化处理"""
        
        setTheme(Theme.AUTO)
        
        
    def closeEvent(self, e):
        # 停止监听器线程
        self.listener.terminate()
        self.listener.deleteLater()
        super().closeEvent(e)

    def _apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.setStyleSheet(self.DARK_QSS)
           
           
        else:
            self.setStyleSheet(self.LIGHT_QSS)
            
        
        # Update success view theme if it exists and is visible
        if hasattr(self, 'success_widget') and self.success_widget and self.success_widget.isVisible():
            self._apply_success_theme()
            
    def load_settings(self):
        """Load settings from QSettings"""
        settings = QSettings("MyCompany", "ConverterApp")
        
        # Load image converter settings
        self.min_size = settings.value("image_converter/min_size", 16, type=int)
        self.max_size = settings.value("image_converter/max_size", 1024, type=int)
        self.output_format = settings.value("image_converter/output_format", "icns", type=str)
        
        # Load image processing options
        self.keep_aspect_ratio = settings.value("image_converter/keep_aspect_ratio", True, type=bool)
        self.auto_crop = settings.value("image_converter/auto_crop", False, type=bool)
        self.quality = settings.value("image_converter/quality", 85, type=int)
        
        # Load advanced options
        self.icns_method = settings.value("image_converter/icns_method", "iconutil (Recommended)")
        self.overwrite_confirm = settings.value("image_converter/overwrite_confirm", True, type=bool)
        
        # Load interface behavior settings
        auto_preview_val = settings.value("image_converter/auto_preview", True, type=bool)
        remember_path_val = settings.value("image_converter/remember_path", True, type=bool)
        completion_notify_val = settings.value("image_converter/completion_notify", True, type=bool)
        
        self.auto_preview = bool(auto_preview_val) if auto_preview_val is not None else True
        self.remember_path = bool(remember_path_val) if remember_path_val is not None else True
        self.completion_notify = bool(completion_notify_val) if completion_notify_val is not None else True
        
        # Load remembered paths if setting is enabled
        if self.remember_path:
            input_dir_val = settings.value("image_converter/last_input_dir", "", type=str)
            output_dir_val = settings.value("image_converter/last_output_dir", "", type=str)
            self.last_input_dir = str(input_dir_val) if input_dir_val is not None else ""
            self.last_output_dir = str(output_dir_val) if output_dir_val is not None else ""
        
        # Update UI with loaded settings
        if hasattr(self, 'min_spin') and isinstance(self.min_size, (int, str)):
            self.min_spin.setValue(int(self.min_size))
        if hasattr(self, 'max_spin') and isinstance(self.max_size, (int, str)):
            self.max_spin.setValue(int(self.max_size))
        if hasattr(self, 'format_combo') and self.output_format:
            self.format_combo.setCurrentText(str(self.output_format))
        if hasattr(self, 'keep_aspect_check'):
            self.keep_aspect_check.setChecked(bool(self.keep_aspect_ratio))
        if hasattr(self, 'auto_crop_check'):
            self.auto_crop_check.setChecked(bool(self.auto_crop))
        if hasattr(self, 'quality_slider') and isinstance(self.quality, (int, str)):
            self.quality_slider.setValue(int(self.quality))
            self.quality_label.setText(str(self.quality))
        if hasattr(self, 'icns_method_combo') and self.icns_method:
            self.icns_method_combo.setCurrentText(str(self.icns_method))
        if hasattr(self, 'overwrite_confirm_check'):
            self.overwrite_confirm_check.setChecked(bool(self.overwrite_confirm))
        
        print(f"Settings loaded: min_size={self.min_size}, max_size={self.max_size}, output_format={self.output_format}")
        
    def save_settings(self):
        """Save settings to QSettings"""
        settings = QSettings("MyCompany", "ConverterApp")
        
        # Save image converter settings
        settings.setValue("image_converter/min_size", self.min_size)
        settings.setValue("image_converter/max_size", self.max_size)
        settings.setValue("image_converter/output_format", self.output_format)
        
        # Save image processing options
        settings.setValue("image_converter/keep_aspect_ratio", self.keep_aspect_ratio)
        settings.setValue("image_converter/auto_crop", self.auto_crop)
        settings.setValue("image_converter/quality", self.quality)
        
        # Save advanced options
        settings.setValue("image_converter/icns_method", self.icns_method)
        settings.setValue("image_converter/overwrite_confirm", self.overwrite_confirm)
        
        # Save interface behavior settings
        settings.setValue("image_converter/auto_preview", self.auto_preview)
        settings.setValue("image_converter/remember_path", self.remember_path)
        settings.setValue("image_converter/completion_notify", self.completion_notify)
        
        # Save remembered paths if setting is enabled
        if self.remember_path:
            if hasattr(self, 'last_input_dir'):
                settings.setValue("image_converter/last_input_dir", self.last_input_dir)
            if hasattr(self, 'last_output_dir'):
                settings.setValue("image_converter/last_output_dir", self.last_output_dir)
        
        print(f"Settings saved: min_size={self.min_size}, max_size={self.max_size}, output_format={self.output_format}")
        
    def init_variables(self, reset_all=False):
        """初始化或重置所有变量
        
        Args:
            reset_all (bool): If True, reset all variables including interface behavior settings.
                             If False, only reset basic variables (preserves loaded settings).
        """
        self.input_path = ""
        self.output_path = ""
        self.min_size = 16
        self.max_size = 1024
        self.converting = False
        self.current_view = "main"
        self.output_format = "icns"  # Default output format
        
        # Image processing options
        self.keep_aspect_ratio = True
        self.auto_crop = False
        self.quality = 85
        
        # Advanced options
        self.icns_method = "iconutil (Recommended)"
        self.overwrite_confirm = True
        
        # Only reset interface behavior settings if explicitly requested
        if reset_all or not hasattr(self, 'auto_preview'):
            # Interface behavior settings - prioritize reading from launcher settings
            self._load_launcher_settings_for_interface()
        
        # History tracking
        if not hasattr(self, 'conversion_history'):
            self.conversion_history = []
    
    def _load_launcher_settings_for_interface(self):
        """Load interface behavior settings from launcher settings (QSettings) with fallback to defaults"""
        try:
            from PySide6.QtCore import QSettings
            settings = QSettings("MyCompany", "ConverterApp")
            
            # Read launcher settings for interface behavior
            # These settings might be managed by the launcher/settings dialog
            
            # Priority 1: Try to read from image_converter specific settings
            auto_preview_val = settings.value("image_converter/auto_preview", None)
            remember_path_val = settings.value("image_converter/remember_path", None)
            completion_notify_val = settings.value("image_converter/completion_notify", None)
            
            # Priority 2: If image_converter settings don't exist, check for global launcher settings
            if auto_preview_val is None:
                # Check if there's a global auto_preview setting from launcher
                auto_preview_val = settings.value("auto_preview", True)
            
            if remember_path_val is None:
                # Check if there's a global remember_path setting from launcher
                remember_path_val = settings.value("remember_path", True)
                
            if completion_notify_val is None:
                # Check if there's a global completion_notify setting from launcher
                completion_notify_val = settings.value("completion_notify", True)
            
            # Apply settings with proper type conversion
            self.auto_preview = bool(auto_preview_val) if auto_preview_val is not None else True
            self.remember_path = bool(remember_path_val) if remember_path_val is not None else True
            self.completion_notify = bool(completion_notify_val) if completion_notify_val is not None else True
            
            # Also check for other launcher-managed settings that might affect interface
            # Theme setting (for potential interface adjustments)
            theme_setting = settings.value("theme", 0, type=int)
            if hasattr(self, '_launcher_theme_setting'):
                self._launcher_theme_setting = theme_setting
            
            # Debug setting (for potential debug interface elements)
            debug_enabled = settings.value("debug_enabled", False, type=bool)
            if hasattr(self, '_launcher_debug_enabled'):
                self._launcher_debug_enabled = debug_enabled
                
            print(f"Loaded launcher settings: auto_preview={self.auto_preview}, remember_path={self.remember_path}, completion_notify={self.completion_notify}")
            
        except Exception as e:
            # Fallback to hardcoded defaults if settings loading fails
            print(f"Warning: Failed to load launcher settings, using defaults: {e}")
            self.auto_preview = True
            self.remember_path = True
            self.completion_notify = True
        
    def setup_ui(self):
        """Setup initial UI"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        self.create_widgets()
        self.create_success_view()
        self.create_history_tab()
        self.show_main_view()
        
    def create_widgets(self):
        """Create the main conversion interface"""
        # Title
        title_label = QLabel("Image Format Converter")
        title_font = QFont()
        title_font.setPointSize(title_label.font().pointSize() + 8)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label, 0, Qt.AlignmentFlag.AlignHCenter)

        # Create tab widget for main content and history
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Main converter tab
        self.converter_tab = QWidget()
        self.tab_widget.addTab(self.converter_tab, "Converter")
        
        # Setup main converter content
        self.setup_converter_tab()
        
    def setup_converter_tab(self):
        """Setup the main converter tab content"""
        converter_layout = QVBoxLayout(self.converter_tab)

        # Main content area: Left Panel (Input/Output) and Right Side (Options/Preview)
        main_content_h_layout = QHBoxLayout()
        main_content_h_layout.setSpacing(20) # Increased spacing between left and right sections
        converter_layout.addLayout(main_content_h_layout)

        # Left Panel: Merged Input/Output File Selection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(15) # Spacing between input and output sections
        main_content_h_layout.addWidget(left_panel, 1) # Give left panel some stretch

        # Merged File Operations Group Box
        file_ops_group_box = QGroupBox("File Operations")
        file_ops_group_layout = QVBoxLayout(file_ops_group_box)
        file_ops_group_layout.setContentsMargins(10, 25, 10, 10)
        file_ops_group_layout.setSpacing(10)
        left_layout.addWidget(file_ops_group_box)

        # Input File Selection (inside merged group box)
        input_layout = QHBoxLayout()
        input_label = QLabel("Input File:")
        self.input_text = LineEdit()
        # self.input_text.setReadOnly(True)  # 允许用户手动输入路径
        input_button = PushButton("Browse...")
        # Apply custom style to input button
        setCustomStyleSheet(input_button, CON.qss, CON.qss)
        setCustomStyleSheet(self.input_text, CON.qss_line, CON.qss_line)
        input_button.clicked.connect(self.on_browse_input)

        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_text, 1) # Give text field more stretch
        input_layout.addWidget(input_button)
        file_ops_group_layout.addLayout(input_layout)

        # Output File Selection (inside merged group box)
        output_layout = QHBoxLayout()
        output_label = QLabel("Output File:")
        self.output_text = LineEdit()
        # self.output_text.setReadOnly(True)  # 允许用户手动输入路径
        output_button = PushButton("Browse...")
        # Apply custom style to output button
        setCustomStyleSheet(output_button, CON.qss, CON.qss)
        setCustomStyleSheet(self.output_text, CON.qss_line, CON.qss_line)
        output_button.clicked.connect(self.on_browse_output)

        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_text, 1) # Give text field more stretch
        output_layout.addWidget(output_button)
        file_ops_group_layout.addLayout(output_layout)

        # Image Preview (moved from right panel)
        preview_group_box = QGroupBox("Image Preview")
        preview_group_layout = QVBoxLayout(preview_group_box)
        preview_group_layout.setContentsMargins(10, 25, 10, 10)
        left_layout.addWidget(preview_group_box, 1) # Give preview some stretch on the left

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedSize(250, 250) # Reduced fixed size for the preview area
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) # Allow it to expand
        self._set_placeholder_preview()
        preview_group_layout.addWidget(self.preview_label, 1, Qt.AlignmentFlag.AlignCenter)

        # Add stretch to left layout to push content to top
        left_layout.addStretch(1)

        # Right Side: Image Info, Conversion Options, Progress, Convert Button
        right_side_v_layout = QVBoxLayout()
        right_side_v_layout.setContentsMargins(15, 15, 15, 15) # Add margins to the right side overall
        right_side_v_layout.setSpacing(15) # Spacing between groups on the right side
        main_content_h_layout.addLayout(right_side_v_layout, 1) # Give right side some stretch

        # Image Info
        info_group_box = QGroupBox("Image Information")
        info_group_layout = QVBoxLayout(info_group_box)
        info_group_layout.setContentsMargins(10, 25, 10, 10)
        right_side_v_layout.addWidget(info_group_box, 0) # No stretch for info, compact
        self.qss_lie="""LineEdit{ border-radius: 15px; }"""
        self.info_text = LineEdit()
        setCustomStyleSheet(self.info_text, self.qss_lie, self.qss_lie)
        self.info_text.setText("No image selected")
        self.info_text.setReadOnly(True)  # 不允许用户手动输入信息
        self.info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_group_layout.addWidget(self.info_text)

        # Conversion Options with TreeWidget for better organization
        options_group_box = QGroupBox("Conversion Options")
        options_group_layout = QVBoxLayout(options_group_box)
        options_group_layout.setContentsMargins(10, 25, 10, 10) # Reset margins for options group
        right_side_v_layout.addWidget(options_group_box, 6)  # Give more stretch to options
        
        # Create scroll area for TreeWidget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(450)  # Set minimum height for scroll area
        
        # Create TreeWidget for organized settings
        self.options_tree = TreeWidget()
        self.options_tree.setHeaderHidden(True)
        self.options_tree.setRootIsDecorated(True)
        self.options_tree.setIndentation(20)
        # Remove height restrictions to allow natural expansion
        
        # Add TreeWidget to scroll area
        scroll_area.setWidget(self.options_tree)
        options_group_layout.addWidget(scroll_area)
        
        # Setup tree structure
        self._setup_options_tree()
        # Progress Area (moved to bottom)
        progress_group_box = QGroupBox("Process")
        progress_group_layout = QVBoxLayout(progress_group_box)
        progress_group_layout.setContentsMargins(10, 25, 10, 10)
        left_layout.addWidget(progress_group_box, 0) # No stretch for progress, compact

        self.progress_label = QLabel("Ready")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = ProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        progress_group_layout.addWidget(self.progress_label)
        progress_group_layout.addWidget(self.progress)
        # Convert Button (moved before Progress) - Replace with PrimaryPushButton and apply custom style
        self.convert_button = PrimaryPushButton("Convert to ICNS")
        self.convert_button.setFixedSize(180, 40)
        font = self.convert_button.font()
        font.setPointSize(font.pointSize() + 1)
        font.setBold(True)
        self.convert_button.setFont(font)
        # Apply custom style to convert button
        setCustomStyleSheet(self.convert_button, CON.qss, CON.qss)
        self.convert_button.clicked.connect(self.on_start_conversion)
        left_layout.addWidget(self.convert_button, 0, Qt.AlignmentFlag.AlignCenter)

        

        # Add a stretch to the right_side_v_layout to push content to top
        right_side_v_layout.addStretch(1)

        # Add final stretch to main horizontal layout if needed, to push content to top-left
        # main_content_h_layout.addStretch(1) # This stretch is handled by the left/right panel stretches

        # Add a stretch to the converter layout to push everything to the top
        converter_layout.addStretch(1)
    
    def create_history_tab(self):
        """Create the history tab for conversion history"""
        if not self.remember_path:
            # If remember_path is disabled, remove history tab if it exists
            if hasattr(self, 'history_tab') and self.history_tab:
                tab_index = self.tab_widget.indexOf(self.history_tab)
                if tab_index != -1:
                    self.tab_widget.removeTab(tab_index)
                self.history_tab = None
            return
            
        # Only create history tab if it doesn't already exist
        if hasattr(self, 'history_tab') and self.history_tab:
            # History tab already exists, just update its content
            self.load_conversion_history()
            return
            
        # Create history tab
        self.history_tab = QWidget()
        self.tab_widget.addTab(self.history_tab, "History")
        
        history_layout = QVBoxLayout(self.history_tab)
        history_layout.setContentsMargins(15, 15, 15, 15)
        history_layout.setSpacing(15)
        
        # History title
        history_title = QLabel("Conversion History")
        title_font = QFont()
        title_font.setPointSize(history_title.font().pointSize() + 4)
        title_font.setBold(True)
        history_title.setFont(title_font)
        history_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        history_layout.addWidget(history_title)
        
        # History list
        self.history_list = ListWidget()
        history_layout.addWidget(self.history_list)
        
        # Clear history button
        clear_history_btn = PushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_conversion_history)
        setCustomStyleSheet(clear_history_btn, CON.qss, CON.qss)
        history_layout.addWidget(clear_history_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Load existing history
        self.load_conversion_history()
    
    def add_to_history(self, input_file: str, output_file: str, format_type: str):
        """Add a conversion to history"""
        if not self.remember_path:
            return
            
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        history_item = {
            'timestamp': timestamp,
            'input': input_file,
            'output': output_file,
            'format': format_type
        }
        
        self.conversion_history.append(history_item)
        
        # Keep only last 50 items
        if len(self.conversion_history) > 50:
            self.conversion_history = self.conversion_history[-50:]
            
        self.save_conversion_history()
        self.update_history_display()
    
    def load_conversion_history(self):
        """Load conversion history from settings"""
        if not self.remember_path:
            return
            
        settings = QSettings("MyCompany", "ConverterApp")
        history_size = settings.beginReadArray("conversion_history")
        
        self.conversion_history = []
        for i in range(history_size):
            settings.setArrayIndex(i)
            item = {
                'timestamp': settings.value("timestamp", ""),
                'input': settings.value("input", ""),
                'output': settings.value("output", ""),
                'format': settings.value("format", "")
            }
            self.conversion_history.append(item)
        
        settings.endArray()
        self.update_history_display()
    
    def save_conversion_history(self):
        """Save conversion history to settings"""
        if not self.remember_path:
            return
            
        settings = QSettings("MyCompany", "ConverterApp")
        settings.beginWriteArray("conversion_history")
        
        for i, item in enumerate(self.conversion_history):
            settings.setArrayIndex(i)
            settings.setValue("timestamp", item['timestamp'])
            settings.setValue("input", item['input'])
            settings.setValue("output", item['output'])
            settings.setValue("format", item['format'])
        
        settings.endArray()
    
    def update_history_display(self):
        """Update the history list display"""
        if not hasattr(self, 'history_list'):
            return
            
        self.history_list.clear()
        
        for item in reversed(self.conversion_history):  # Show newest first
            display_text = f"{item['timestamp']} - {os.path.basename(item['input'])} → {item['format'].upper()}"
            list_item = QListWidgetItem(display_text)
            list_item.setToolTip(f"Input: {item['input']}\nOutput: {item['output']}")
            self.history_list.addItem(list_item)
    
    def clear_conversion_history(self):
        """Clear all conversion history"""
        self.conversion_history = []
        self.save_conversion_history()
        self.update_history_display()

    def _setup_options_tree(self):
        """Setup the TreeWidget with organized settings"""
        # Clear existing items
        self.options_tree.clear()
        
        # Create main categories
        basic_item = QTreeWidgetItem(["Basic Options"])
        processing_item = QTreeWidgetItem(["Image Processing"])
        advanced_item = QTreeWidgetItem(["Advanced Settings"])
        
        # Add to tree
        self.options_tree.addTopLevelItem(basic_item)
        self.options_tree.addTopLevelItem(processing_item)
        self.options_tree.addTopLevelItem(advanced_item)
        
        # Basic Options
        self._create_basic_options(basic_item)
        
        # Processing Options
        self._create_processing_options(processing_item)
        
        # Advanced Options (initially collapsed)
        self._create_advanced_options(advanced_item)
        
        # Set expansion state
        basic_item.setExpanded(True)
        processing_item.setExpanded(True)
        advanced_item.setExpanded(False)  # Hidden by default
        
        # Connect tree signals
        self.options_tree.itemExpanded.connect(self._on_tree_item_expanded)
        self.options_tree.itemCollapsed.connect(self._on_tree_item_collapsed)
    
    def _create_basic_options(self, parent_item):
        """Create basic options widgets"""
        # Output Format
        format_widget = QWidget()
        format_widget.setMinimumSize(300, 55)
        format_layout = QHBoxLayout(format_widget)
        v_layout=QVBoxLayout(format_widget)
        format_layout.setContentsMargins(5, 2, 5, 2)
        
        format_label = QLabel("Output Format:")
        
        self.format_combo = ModelComboBox()
        
        self.format_combo.addItems(convert.SUPPORTED_FORMATS)
        
        self.format_combo.currentIndexChanged.connect(self.on_format_change)
        
        format_layout.addWidget(format_label)
        setCustomStyleSheet(self.format_combo, CON.qss_combo, CON.qss_combo)
        format_layout.addWidget(self.format_combo)
        
        format_item = QTreeWidgetItem()
        parent_item.addChild(format_item)
        
        self.options_tree.setItemWidget(format_item, 0, format_widget)
        
        # Minimum Size
        min_size_widget = QWidget()
        min_size_layout = QHBoxLayout(min_size_widget)
        
        min_size_layout.setContentsMargins(5, 2, 5, 2)
        min_size_widget.setMinimumSize(300, 65)
        min_size_label = QLabel("Minimum Size:")
        self.spin=CON.qss_spin
        self.min_spin = SpinBox()
        setCustomStyleSheet(self.min_spin, self.spin, self.spin)
        self.min_spin.setRange(16, 512)
        
        self.min_spin.valueChanged.connect(self.on_min_size_change)
        
        min_size_layout.addWidget(min_size_label)
       
        min_size_layout.addWidget(self.min_spin)
        
        min_size_item = QTreeWidgetItem()
        parent_item.addChild(min_size_item)
        self.options_tree.setItemWidget(min_size_item, 0, min_size_widget)
        
        # Maximum Size
        max_size_widget = QWidget()
        max_size_widget.setMinimumSize(300, 65)
        max_size_layout = QHBoxLayout(max_size_widget)
        max_size_layout.setContentsMargins(5, 2, 5, 2)
        
        max_size_label = QLabel("Maximum Size:")
        self.max_spin = SpinBox()
        setCustomStyleSheet(self.max_spin, self.spin, self.spin)
        self.max_spin.setRange(32, 1024)
        
        self.max_spin.valueChanged.connect(self.on_max_size_change)
        
        max_size_layout.addWidget(max_size_label)
       
        max_size_layout.addWidget(self.max_spin)
        
        max_size_item = QTreeWidgetItem()
        parent_item.addChild(max_size_item)
        self.options_tree.setItemWidget(max_size_item, 0, max_size_widget)
        
        # Auto-detect button
        auto_widget = QWidget()
        auto_layout = QHBoxLayout(auto_widget)
        auto_layout.setContentsMargins(5, 2, 5, 2)
        auto_widget.setMinimumSize(10, 52)  # 适当调小按钮尺寸
        self.auto_button = PrimaryPushButton("Auto-detect Max Size")
        # Apply custom style to auto button
        setCustomStyleSheet(self.auto_button, CON.qss, CON.qss)
        self.auto_button.clicked.connect(self.on_auto_detect)
        auto_layout.addWidget(self.auto_button)
        
        auto_item = QTreeWidgetItem()
        parent_item.addChild(auto_item)
        self.options_tree.setItemWidget(auto_item, 0, auto_widget)
    
    def _create_processing_options(self, parent_item):
        """Create image processing options widgets"""
        # Keep aspect ratio
        aspect_widget = QWidget()
        aspect_layout = QHBoxLayout(aspect_widget)
        aspect_layout.setContentsMargins(5, 2, 5, 2)
        aspect_widget.setMinimumSize(200,40)
        self.keep_aspect_check = CheckBox("Maintain original aspect ratio")
        self.keep_aspect_check.stateChanged.connect(self.on_keep_aspect_changed)
        aspect_layout.addWidget(self.keep_aspect_check)
        
        aspect_item = QTreeWidgetItem()
        parent_item.addChild(aspect_item)
        self.options_tree.setItemWidget(aspect_item, 0, aspect_widget)
        
        # Auto crop
        crop_widget = QWidget()
        crop_layout = QHBoxLayout(crop_widget)
        crop_layout.setContentsMargins(5, 2, 5, 2)
        
        self.auto_crop_check = CheckBox("Auto-crop non-square to square")
        self.auto_crop_check.stateChanged.connect(self.on_auto_crop_changed)
        crop_layout.addWidget(self.auto_crop_check)
        crop_widget.setMinimumSize(200,40)
        crop_item = QTreeWidgetItem()
        parent_item.addChild(crop_item)
        self.options_tree.setItemWidget(crop_item, 0, crop_widget)
        
        # Quality slider
        quality_widget = QWidget()
        quality_layout = QHBoxLayout(quality_widget)
        quality_layout.setContentsMargins(5, 2, 5, 2)
        quality_widget.setMinimumSize(200,45)
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_slider = Slider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(85)
        self.quality_slider.valueChanged.connect(self.on_quality_changed)
        quality_layout.addWidget(self.quality_slider)
        
        self.quality_label = QLabel("85")
        quality_layout.addWidget(self.quality_label)
        
        quality_item = QTreeWidgetItem()
        parent_item.addChild(quality_item)
        self.options_tree.setItemWidget(quality_item, 0, quality_widget)
    
    def _create_advanced_options(self, parent_item):
        """Create advanced options widgets"""
        # ICNS method
        method_widget = QWidget()
        method_layout = QHBoxLayout(method_widget)
        method_layout.setContentsMargins(5, 2, 5, 2)
        method_widget.setMinimumSize(100, 80)
        method_layout.addWidget(QLabel("ICNS method:"))
        self.icns_method_combo = ModelComboBox()
        self.icns_method_combo.addItems(["iconutil (Recommended)", "Pillow Fallback"])
        self.icns_method_combo.currentTextChanged.connect(self.on_icns_method_changed)
        setCustomStyleSheet(self.icns_method_combo, CON.qss_combo, CON.qss_combo)
        method_layout.addWidget(self.icns_method_combo)
        
        method_item = QTreeWidgetItem()
        parent_item.addChild(method_item)
        
        self.options_tree.setItemWidget(method_item, 0, method_widget)
        
        # Overwrite confirmation
        overwrite_widget = QWidget()
        overwrite_layout = QHBoxLayout(overwrite_widget)
        overwrite_layout.setContentsMargins(5, 2, 5, 2)
        overwrite_widget.setMinimumSize(100, 80)
        self.overwrite_confirm_check = CheckBox("Confirm before overwriting files")
        self.overwrite_confirm_check.stateChanged.connect(self.on_overwrite_confirm_changed)
        overwrite_layout.addWidget(self.overwrite_confirm_check)
        
        #method_widget.setMinimumSize(100, 150)
        overwrite_item = QTreeWidgetItem()
        parent_item.addChild(overwrite_item)
        self.options_tree.setItemWidget(overwrite_item, 0, overwrite_widget)
    
    def _on_tree_item_expanded(self, item):
        """Handle tree item expansion"""
        # Optional: Add any logic when items are expanded
        pass
    
    def _on_tree_item_collapsed(self, item):
        """Handle tree item collapse"""
        # Optional: Add any logic when items are collapsed
        pass

    def create_success_view(self):
        # Create success widget as a top-level overlay
        self.success_widget = QWidget(self)
        self.success_widget.setObjectName("success_overlay")
        
        # Set it to cover the entire window
        self.success_widget.setGeometry(self.rect())
        
        # Create layout for success widget
        self.success_layout = QVBoxLayout(self.success_widget)
        self.success_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a semi-transparent overlay background
        overlay = QWidget()
        overlay.setObjectName("success_overlay")
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        
        center_panel = QWidget()
        center_panel.setObjectName("success_center_panel")
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(50, 50, 50, 50) # Increased margins
        center_layout.setSpacing(20)
        
        # Add stretch to center the panel vertically
        overlay_layout.addStretch()
        overlay_layout.addWidget(center_panel, 0, Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addStretch()
        
        self.success_layout.addWidget(overlay)

        center_layout.addStretch()

        title = QLabel("Conversion Successful!")
        font = title.font()
        font.setPointSize(font.pointSize() + 8) # Larger title
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("success_title_label")
        center_layout.addWidget(title)

        checkmark = QLabel("✓")
        checkmark_font = checkmark.font()
        checkmark_font.setPointSize(checkmark_font.pointSize() + 30) # Larger checkmark
        checkmark_font.setBold(True)
        checkmark.setFont(checkmark_font)
        checkmark.setObjectName("success_checkmark_label")
        checkmark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(checkmark)

        msg = QLabel(f"Your {str(self.output_format).upper()} file has been created successfully!")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setObjectName("success_message_label") # Object name for QSS
        center_layout.addWidget(msg)

        # Conditionally show "Open Converted File" button based on auto_preview setting
        if not self.auto_preview:
            open_btn = PrimaryPushButton("Open Converted File")
            open_btn.clicked.connect(self.on_open_converted_file)
            open_btn.setFixedSize(200, 45) # Larger buttons
            open_btn.setObjectName("open_converted_file_button") # Object name for QSS
            # Apply custom style to open button
            setCustomStyleSheet(open_btn, CON.qss, CON.qss)
            center_layout.addWidget(open_btn, 0, Qt.AlignmentFlag.AlignCenter)

        return_btn = PushButton("Return to Converter")
        return_btn.clicked.connect(self.show_main_view)
        return_btn.setFixedSize(200, 45) # Larger buttons
        return_btn.setObjectName("return_to_converter_button") # Object name for QSS
        # Apply custom style to return button
        setCustomStyleSheet(return_btn, CON.qss, CON.qss)
        center_layout.addWidget(return_btn, 0, Qt.AlignmentFlag.AlignCenter)

        center_layout.addStretch()

        self.success_widget.hide() # Initially hidden

    def _set_placeholder_preview(self):
        placeholder_text = "拖放图像到此处\n或点击'Browse...'选择文件\n🖼️"
        font = QFont()
        font.setPointSize(16) # Larger font for placeholder
        self.preview_label.setFont(font)
        self.preview_label.setText(placeholder_text)
        self.preview_label.setPixmap(QPixmap()) # Clear any previous image
        
        # Enable drag and drop for the preview label
        self.preview_label.setAcceptDrops(True)
        self.preview_label.dragEnterEvent = self.dragEnterEvent
        self.preview_label.dropEvent = self.dropEvent

    def on_browse_input(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.ico);;All files (*.*)")
        
        # Remember last path if setting is enabled
        if self.remember_path and hasattr(self, 'last_input_dir') and self.last_input_dir:
            file_dialog.setDirectory(str(self.last_input_dir))
            
        if file_dialog.exec():
            self.input_path = file_dialog.selectedFiles()[0]
            self.input_text.setText(self.input_path)
            
            # Remember the directory for next time if setting is enabled
            if self.remember_path:
                self.last_input_dir = os.path.dirname(self.input_path)
                
            self.auto_set_output()
            
            # Show preview if auto_preview setting is enabled
            if self.auto_preview:
                self.show_preview()
                
            self.update_image_info()
            
    def on_browse_output(self):
        system=platform.system()
        if "Darwin" in system.lower():
            wildcard_map = {
                "icns": "ICNS files (*.icns)",
                "jpg": "JPEG files (*.jpg)",
                "jpeg": "JPEG files (*.jpeg)",
                "webp": "WebP files (*.webp)",
                "bmp": "BMP files (*.bmp)",
                "gif": "GIF files (*.gif)",
                "tiff": "TIFF files (*.tiff)",
                "ico": "ICO files (*.ico)",
                "png": "PNG files (*.png)",
            }
        else:
            wildcard_map = {
                "jpg": "JPEG files (*.jpg)",
                "jpeg": "JPEG files (*.jpeg)",
                "webp": "WebP files (*.webp)",
                "bmp": "BMP files (*.bmp)",
                "gif": "GIF files (*.gif)",
                "tiff": "TIFF files (*.tiff)",
                "ico": "ICO files (*.ico)",
                "png": "PNG files (*.png)",
            }
        default_filter = wildcard_map.get(str(self.output_format), "All files (*.*)")
        
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave) # Corrected enum
        file_dialog.setNameFilter(f"{default_filter};;All files (*.*)")
        file_dialog.setDefaultSuffix(str(self.output_format))
        
        # Remember last path if setting is enabled
        if self.remember_path and hasattr(self, 'last_output_dir') and self.last_output_dir:
            file_dialog.setDirectory(str(self.last_output_dir))

        if file_dialog.exec():
            self.output_path = file_dialog.selectedFiles()[0]
            expected_extension = '.' + str(self.output_format)
            if not self.output_path.lower().endswith(expected_extension):
                self.output_path += expected_extension
            self.output_text.setText(self.output_path)
            
            # Remember the directory for next time if setting is enabled
            if self.remember_path:
                self.last_output_dir = os.path.dirname(self.output_path)
            
    def on_format_change(self, index):
        self.output_format = self.format_combo.currentText().lower()
        self.auto_set_output()
        self.save_settings()
        
        if self.output_format == "png":
            self.convert_button.setText("Convert to PNG")
        else:
            self.convert_button.setText(f"Convert to {self.output_format.upper()}")
        
        enable_size_options = (self.output_format == "icns")
        self.min_spin.setEnabled(enable_size_options)
        self.max_spin.setEnabled(enable_size_options)
        self.auto_button.setEnabled(enable_size_options)
        
    def auto_set_output(self):
        if self.input_path:
            base_name = os.path.splitext(os.path.basename(self.input_path))[0]
            output_file = os.path.join(os.path.dirname(self.input_path), f"{base_name}.{self.output_format}")
            self.output_path = output_file
            self.output_text.setText(output_file)
            
    def update_image_info(self):
        if self.input_path and os.path.exists(self.input_path):
            try:
                width, height = convert.get_image_info(self.input_path)
                self.info_text.setText(f"Dimensions: {width}x{height}px")
                self.max_size = min(width, height)
                self.max_spin.setValue(self.max_size)
            except Exception as e:
                self.info_text.setText(f"Error reading image: {str(e)}")
        else:
            self.info_text.setText("No image selected")
            
    def on_auto_detect(self):
        if self.input_path and os.path.exists(self.input_path):
            try:
                width, height = convert.get_image_info(self.input_path)
                self.max_size = min(width, height)
                self.max_spin.setValue(self.max_size)
                self.status_bar.showMessage(f"Max size auto-detected: {self.max_size}")
            except Exception as e:
                PopupTeachingTip.create(
                    target=self.auto_button,
                    icon=InfoBarIcon.ERROR,
                    title='ERROR',
                    content=f"Could not detect image size: {str(e)}",
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.LEFT_BOTTOM,
                    duration=10000,
                    parent=self
                )
                
        else:
            PopupTeachingTip.create(
                    target=self.auto_button,
                    icon=InfoBarIcon.WARNING,
                    title='Warning',
                    content="Please select an input file first.",
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.RIGHT_BOTTOM,
                    duration=2000,
                    parent=self
            )
            
            
    def show_preview(self):
        if self.input_path and os.path.exists(self.input_path):
            try:
                img = Image.open(self.input_path)
                # img.thumbnail((350, 350)) # Removed PIL thumbnailing
                
                if img.mode == 'RGBA':
                    qimage = QImage(img.tobytes("raw", "RGBA"), img.size[0], img.size[1], QImage.Format.Format_RGBA8888) # Corrected enum
                else:
                    qimage = QImage(img.tobytes("raw", "RGB"), img.size[0], img.size[1], QImage.Format.Format_RGB888) # Corrected enum

                pixmap = QPixmap.fromImage(qimage)
                # Scale pixmap to fit the label, maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
                # Reset font to default if it was changed by placeholder
                self.preview_label.setFont(QFont())
                self.preview_label.setText("") # Clear placeholder text
                self.status_bar.showMessage(f"Loaded: {os.path.basename(self.input_path)} ({img.size[0]}x{img.size[1]})")
            except Exception as e:
                self.preview_label.setText("Preview error")
                self.status_bar.showMessage("Preview error")
        else:
            self.preview_label.clear()
            self._set_placeholder_preview() # Show placeholder when no image selected
            self.status_bar.showMessage("Ready")
            
    def on_min_size_change(self, value):
        self.min_size = value
        self.save_settings()
        
    def on_max_size_change(self, value):
        self.max_size = value
        self.save_settings()
        
    # New signal handlers for image processing and advanced options
    def on_keep_aspect_changed(self, state):
        self.keep_aspect_ratio = bool(state)
        self.save_settings()
        
    def on_auto_crop_changed(self, state):
        self.auto_crop = bool(state)
        self.save_settings()
        
    def on_quality_changed(self, value):
        self.quality = value
        self.quality_label.setText(str(value))
        self.save_settings()
        
    def on_icns_method_changed(self, text):
        self.icns_method = text
        self.save_settings()
        
    def on_overwrite_confirm_changed(self, state):
        self.overwrite_confirm = bool(state)
        self.save_settings()
    
    def on_interface_setting_changed(self):
        """Handle changes to interface behavior settings"""
        # This method will be called when settings are changed from the settings dialog
        # Reload the settings and update the UI accordingly
        self.load_settings()
        
        # Update history tab visibility only when remember_path setting actually changes
        self.create_history_tab()
        
        # If auto_preview setting changed, update preview behavior
        if hasattr(self, 'input_path') and self.input_path and self.auto_preview:
            self.show_preview()
    
    def dragEnterEvent(self, event):
        """Handle drag enter events for image files"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # Check if any URL is a valid image file
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if os.path.isfile(file_path):
                        # Check if it's an image file
                        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.ico', '.webp']
                        if any(file_path.lower().endswith(ext) for ext in image_extensions):
                            event.acceptProposedAction()
                            return
            event.ignore()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop events for image files"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            image_files = []
            
            # Collect all valid image files
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if os.path.isfile(file_path):
                        # Check if it's an image file
                        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.ico', '.webp']
                        if any(file_path.lower().endswith(ext) for ext in image_extensions):
                            image_files.append(file_path)
            
            if image_files:
                # Use the first image file
                self.input_path = image_files[0]
                self.input_text.setText(self.input_path)
                
                # Remember the directory for next time if setting is enabled
                if self.remember_path:
                    self.last_input_dir = os.path.dirname(self.input_path)
                
                self.auto_set_output()
                
                # Show preview if auto_preview setting is enabled
                if self.auto_preview:
                    self.show_preview()
                
                self.update_image_info()
                
                # Show success message
                self.status_bar.showMessage(f"Loaded {len(image_files)} image(s) via drag & drop")
                
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()
            
    def on_start_conversion(self):
        if self.converting:
            return
            
        if not self.input_path:
            PopupTeachingTip.create(
                target=self.convert_button,
                icon=InfoBarIcon.ERROR,
                title='ERROR',
                content=f"Please select an input image file.",
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
            return

        if not self.output_path:
            PopupTeachingTip.create(
                target=self.convert_button,
                icon=InfoBarIcon.ERROR,
                title='ERROR',
                content=f"Please specify an output {str(self.output_format).upper()} file.",
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,  
                duration=2000,
                parent=self
            )
            return
            
        if not os.path.exists(self.input_path):
            PopupTeachingTip.create(
                target=self.convert_button,
                icon=InfoBarIcon.ERROR,
                title='ERROR',
                content=f"Input file does not exist.",
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )
            return
            
        self.converting = True
        self.convert_button.setEnabled(False)
        self.progress.setValue(0)
        self.progress_label.setText("Starting conversion...")
        
        self._worker = ConversionWorker(
            self.input_path, self.output_path, self.output_format,
            self.min_size, # 始终传递整数值
            self.max_size,  # 始终传递整数值
            self.quality  # 传递图像质量参数
        )
        self._thread = QThread() 
        self._worker.moveToThread(self._thread)
        
        self._worker.finished.connect(self.on_conversion_finished)
        self._worker.progress_updated.connect(self.update_progress)
        self._worker.conversion_error.connect(self.on_conversion_error)
        self._thread.started.connect(self._worker.run)
        self._thread.start()

    def on_conversion_finished(self):
        self.converting = False
        if hasattr(self, '_thread') and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
        
        # Add to history if remember_path is enabled
        if self.remember_path:
            self.add_to_history(self.input_path, self.output_path, str(self.output_format))
        
        # Auto-open file if auto_preview is enabled
        if self.auto_preview:
            self.on_open_converted_file()
        
        # Show completion notification based on settings
        if self.completion_notify:
            self.show_success_view()
        else:
            # If completion notification is disabled, just show a simple status message
            self.convert_button.setEnabled(True)
            self.progress.setValue(100)
            self.progress_label.setText("Conversion completed successfully!")
            self.status_bar.showMessage(f"Conversion completed: {os.path.basename(self.output_path)}")
        
    def on_conversion_error(self, error_message):
        self.converting = False
        self.convert_button.setEnabled(True)
        if hasattr(self, '_thread') and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
        PopupTeachingTip.create(
            target=self.convert_button,
            icon=InfoBarIcon.ERROR,
            title='ERROR',
            content=f"Conversion Failed,{error_message}",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=2000,
            parent=self
        )
        self.progress_label.setText("Conversion Failed")

    def show_success_view(self):
        # Update the success widget geometry to match the window
        self.success_widget.setGeometry(self.rect())
        # Show the success widget as an overlay
        self.success_widget.show()
        self.success_widget.raise_()  # Bring to front
        # Update success message based on current output format
        msg_label = self.success_widget.findChild(QLabel, "success_message_label")
        if msg_label:
            msg_label.setText(f"Your {str(self.output_format).upper()} file has been created successfully!")
        # Apply theme-specific styles
        self._apply_success_theme()


    def on_open_converted_file(self):
        if self.output_path and os.path.exists(self.output_path):
            try:
                if sys.platform == "win32":
                    os.startfile(self.output_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", self.output_path])
                else:  # Linux and other POSIX systems
                    subprocess.run(["xdg-open", self.output_path])
            except Exception as e:
                PopupTeachingTip.create(
                    target=self.convert_button,
                    icon=InfoBarIcon.ERROR,
                    title='ERROR',
                    content=f"Conversion Failed:\n,{e}",
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.TOP,
                    duration=2000,
                    parent=self
                )
        else:
           
            PopupTeachingTip.create(
                target=self.convert_button,
                icon=InfoBarIcon.ERROR,
                title='ERROR',
                content=f"Conversion Failed: Cannot find the converted file.",
                isClosable=True,
                tailPosition=TeachingTipTailPosition.TOP,
                duration=2000,
                parent=self
            )

    def show_main_view(self):
        # Hide the success widget if it's shown
        if hasattr(self, 'success_widget'):
            self.success_widget.hide()
        
        # Only reset variables if remember_path is disabled
        if not self.remember_path:
            # Reset all variables when remember_path is disabled
            self.init_variables(reset_all=True)
            
            # Reset UI elements
            if hasattr(self, 'input_text'):
                self.input_text.clear()
            if hasattr(self, 'output_text'):
                self.output_text.clear()
            if hasattr(self, 'info_text'):
                self.info_text.setText("No image selected")
            if hasattr(self, 'preview_label'):
                self.preview_label.clear()
                self._set_placeholder_preview() # Show placeholder when returning to main view
        else:
            # If remember_path is enabled, only reset the UI state but keep the paths
            pass
        
        # Always reset these UI elements regardless of remember_path setting
        if hasattr(self, 'min_spin'):
            self.min_spin.setValue(16)
        if hasattr(self, 'max_spin'):
            self.max_spin.setValue(1024)
        if hasattr(self, 'format_combo'):
            self.format_combo.setCurrentText("icns")
        # Reset tree state
        if hasattr(self, 'options_tree'):
            self.options_tree.collapseAll()
            # Expand basic categories but keep advanced collapsed
            if self.options_tree.topLevelItemCount() >= 3:
                item0 = self.options_tree.topLevelItem(0)
                item1 = self.options_tree.topLevelItem(1)
                item2 = self.options_tree.topLevelItem(2)
                if item0:
                    item0.setExpanded(True)  # Basic Options
                if item1:
                    item1.setExpanded(True)  # Image Processing
                if item2:
                    item2.setExpanded(False)  # Advanced Settings
        # The on_format_change also handles enabling/disabling min/max spin boxes and auto-detect button
        if hasattr(self, 'format_combo'):
            self.on_format_change(self.format_combo.currentIndex()) # Explicitly call to set initial state
        if hasattr(self, 'progress'):
            self.progress.setValue(0)
        if hasattr(self, 'progress_label'):
            self.progress_label.setText("Ready")
        if hasattr(self, 'convert_button'):
            self.convert_button.setEnabled(True)
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Ready")
        
        # Only update history tab visibility if it's the first time or remember_path setting changed
        if not hasattr(self, '_history_tab_initialized'):
            self.create_history_tab()
            self._history_tab_initialized = True

            
    def update_progress(self, message, percentage):
        self.progress_label.setText(message)
        self.progress.setValue(percentage)

    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def _apply_success_theme(self):
        """Apply theme-specific styles to success view elements"""
        # Get current theme from CON
        try:
            from support.toggle import CON
            is_dark_mode = CON.theme_system == "dark"
        except:
            # Fallback to system detection if CON is not available
            from PySide6.QtWidgets import QApplication as QApp
            app = QApp.instance()
            from support.toggle import theme_manager
            theme_manager.start()
            if app and hasattr(app, 'palette'):
                is_dark_mode = app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5
            else:
                # Default to light theme if we can't determine
                is_dark_mode = False
        
        # Find all relevant widgets in success view
        title_label = self.success_widget.findChild(QLabel, "success_title_label")
        checkmark_label = self.success_widget.findChild(QLabel, "success_checkmark_label")
        message_label = self.success_widget.findChild(QLabel, "success_message_label")
        
        if is_dark_mode:
            # Dark theme styles
            if title_label:
                title_label.setStyleSheet("color: #28a745; font-size: 24px;")
            if checkmark_label:
                checkmark_label.setStyleSheet("color: #28a745;")
            if message_label:
                message_label.setStyleSheet("color: #aaaaaa; font-size: 16px;")
        else:
            # Light theme styles
            if title_label:
                title_label.setStyleSheet("color: #28a745; font-size: 24px;")
            if checkmark_label:
                checkmark_label.setStyleSheet("color: #28a745;")
            if message_label:
                message_label.setStyleSheet("color: #555555; font-size: 16px;")
        
    def resizeEvent(self, event):
        """Handle window resize events to ensure success overlay covers the entire window"""
        super().resizeEvent(event)
        # Update the success widget geometry when the window is resized
        if hasattr(self, 'success_widget') and self.success_widget:
            self.success_widget.setGeometry(self.rect())


class ICNSConverterApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        setTheme(Theme.AUTO)
        from PySide6.QtWidgets import QApplication as QApp
        app = QApp.instance()
        from support.toggle import theme_manager
        theme_manager.start()
        if app and hasattr(app, 'palette'):
            initial_dark_mode = app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5
        else:
            # Default to light theme if we can't determine
            initial_dark_mode = False
        self.window = ICNSConverterGUI(
            initial_dark_mode=initial_dark_mode
        ) # Pass initial dark mode state to GUI
        self.window.show()

        # Connect to palette changes for real-time theme switching
        from PySide6.QtWidgets import QApplication as QApp
        app = QApp.instance()
        if app and hasattr(app, 'paletteChanged'):
            app.paletteChanged.connect(self._on_palette_changed)

    def _on_palette_changed(self):
        from PySide6.QtWidgets import QApplication as QApp
        app = QApp.instance()
        if app and hasattr(app, 'palette'):
            is_dark_mode = app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5
            self.window._apply_theme(is_dark_mode)
            
            # Also update success view theme if it's visible
            if hasattr(self.window, 'success_widget') and self.window.success_widget and self.window.success_widget.isVisible():
                self.window._apply_success_theme()
        else:
            # Fallback to light theme if we can't determine
            self.window._apply_theme(False)
            if hasattr(self.window, 'success_widget') and self.window.success_widget and self.window.success_widget.isVisible():
                self.window._apply_success_theme()
        

    def MainLoop(self):
        app = QApplication.instance()
        if app:
            sys.exit(app.exec())
        else:
            # Fallback exit if app instance is not available
            sys.exit(1)


if __name__ == "__main__":
    app_runner = ICNSConverterApp()
    app_runner.MainLoop()
