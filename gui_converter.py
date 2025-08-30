#!/usr/bin/env python3

"""
PNG to ICNS Converter with wxPython GUI

This script provides a graphical interface for converting PNG images to ICNS format.
"""

import sys
import os
import threading
import subprocess
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox, QProgressBar,
    QFileDialog, QMessageBox, QTabWidget, QGroupBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QPixmap, QIcon, QFont, QImage, QPalette
from PySide6.QtCore import Qt, QSize, Signal, QObject, QThread

# Add the current directory to Python path to import convert module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from support import convert


class ConversionWorker(QObject):
    finished = Signal()
    progress_updated = Signal(str, int)
    conversion_error = Signal(str)

    def __init__(self, input_path, output_path, output_format, min_size_param=None, max_size_param=None):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.output_format = output_format
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
                    progress_callback=self._update_progress_callback
                )
            else:
                convert.convert_image(
                    self.input_path,
                    self.output_path,
                    self.output_format,
                    progress_callback=self._update_progress_callback
                )
            self.finished.emit()
        except Exception as e:
            self.conversion_error.emit(str(e))

    def _update_progress_callback(self, message, percentage):
        self.progress_updated.emit(message, percentage)


class ICNSConverterGUI(QMainWindow):

    # Define QSS for light mode
    LIGHT_QSS = """
        QMainWindow {
            background-color: #f0f2f5;
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 14px;
            color: #333333;
        }
        QWidget {
            background-color: #ffffff;
            color: #333333;
        }
        QLabel {
            color: #333333;
        }
        QPushButton {
            background-color: #4CAF50; /* Green */
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            min-height: 30px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QLineEdit, QComboBox, QSpinBox {
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 5px;
            background-color: #fdfdfd;
            color: #333333;
            min-height: 24px; /* Ensure sufficient height */
        }
        QComboBox {
            min-width: 100px; /* Ensure QComboBox itself has enough width */
            /* Style for the dropdown arrow */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #cccccc;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox::down-arrow {
                image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#333333' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-chevron-down'><polyline points='6 9 12 15 18 9'></polyline></svg>");
                width: 16px;
                height: 16px;
            }
        }
        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right; /* Position for up button */
            width: 20px;
            height: 12px; /* Half height for each button */
            border-left: 1px solid #cccccc;
            border-bottom: 1px solid #cccccc;
            border-top-right-radius: 5px;
            background-color: #e0e0e0;
        }
        QSpinBox::up-button:hover {
            background-color: #d0d0d0;
        }
        QSpinBox::up-button:pressed {
            background-color: #c0c0c0;
        }
        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right; /* Position for down button */
            width: 20px;
            height: 12px; /* Half height for each button */
            border-left: 1px solid #cccccc;
            border-top: 1px solid #cccccc;
            border-bottom-right-radius: 5px;
            background-color: #e0e0e0;
        }
        QSpinBox::down-button:hover {
            background-color: #d0d0d0;
        }
        QSpinBox::down-button:pressed {
            background-color: #c0c0c0;
        }
        QSpinBox::up-arrow {
            image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#333333' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-chevron-up'><polyline points='18 15 12 9 6 15'></polyline></svg>");
            width: 16px;
            height: 12px; /* Half height for each arrow */
        }
        QSpinBox::down-arrow {
            image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#333333' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-chevron-down'><polyline points='6 9 12 15 18 9'></polyline></svg>");
            width: 16px;
            height: 12px; /* Half height for each arrow */
        }
        QGroupBox {
            font-weight: bold;
            margin-top: 10px;
            border: 1px solid #dddddd;
            border-radius: 8px;
            padding-top: 20px;
            background-color: #ffffff;
            color: #333333;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            margin-left: 5px;
            color: #333333;
        }
        QProgressBar {
            border: 1px solid #cccccc;
            border-radius: 5px;
            text-align: center;
            background-color: #e0e0e0;
            color: #333333;
        }
        QProgressBar::chunk {
            background-color: #2196F3; /* Blue */
            border-radius: 5px;
        }
        QTabWidget::pane {
            border: 1px solid #dddddd;
            border-radius: 8px;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background: #e0e0e0;
            border: 1px solid #dddddd;
            border-bottom-color: #dddddd; /* same as pane color */
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 15px;
            margin-right: 2px;
            color: #555555;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom-color: #ffffff; /* same as pane color */
            color: #333333;
        }
        QTabBar::tab:hover {
            background-color: #f0f0f0;
        }
        QComboBox QAbstractItemView {
            min-width: 150px; /* Ensure dropdown has enough width */
            background-color: #fdfdfd;
            border: 1px solid #cccccc;
            border-radius: 5px;
            selection-background-color: #2196F3;
            selection-color: white;
            padding: 5px;
            color: #333333;
        }
        #success_message_label {
            font-size: 16px;
            font-weight: normal;
            color: #555555;
        }
        #open_converted_file_button, #return_to_converter_button {
            background-color: #007bff; /* Blue for action buttons */
        }
        #open_converted_file_button:hover, #return_to_converter_button:hover {
            background-color: #0056b3;
        }
    """

    # Define QSS for dark mode
    DARK_QSS = """
        QMainWindow {
            background-color: #2b2b2b;
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 14px;
            color: #e0e0e0;
        }
        QWidget {
            background-color: #3c3c3c;
            color: #e0e0e0;
        }
        QLabel {
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #4CAF50; /* Green */
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            min-height: 30px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QLineEdit, QComboBox, QSpinBox {
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 5px;
            background-color: #4c4c4c;
            color: #e0e0e0;
            min-height: 24px; /* Ensure sufficient height */
        }
        QComboBox {
            min-width: 100px; /* Ensure QComboBox itself has enough width */
            /* Style for the dropdown arrow */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #555555;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox::down-arrow {
                image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#e0e0e0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-chevron-down'><polyline points='6 9 12 15 18 9'></polyline></svg>");
                width: 16px;
                height: 16px;
            }
        }
        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right; /* Position for up button */
            width: 20px;
            height: 12px; /* Half height for each button */
            border-left: 1px solid #555555;
            border-bottom: 1px solid #555555;
            border-top-right-radius: 5px;
            background-color: #4c4c4c;
        }
        QSpinBox::up-button:hover {
            background-color: #5a5a5a;
        }
        QSpinBox::up-button:pressed {
            background-color: #6a6a6a;
        }
        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right; /* Position for down button */
            width: 20px;
            height: 12px; /* Half height for each button */
            border-left: 1px solid #555555;
            border-top: 1px solid #555555;
            border-bottom-right-radius: 5px;
            background-color: #4c4c4c;
        }
        QSpinBox::down-button:hover {
            background-color: #5a5a5a;
        }
        QSpinBox::down-button:pressed {
            background-color: #6a6a6a;
        }
        QSpinBox::up-arrow {
            image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#e0e0e0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-chevron-up'><polyline points='18 15 12 9 6 15'></polyline></svg>");
            width: 16px;
            height: 12px; /* Half height for each arrow */
        }
        QSpinBox::down-arrow {
            image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#e0e0e0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-chevron-down'><polyline points='6 9 12 15 18 9'></polyline></svg>");
            width: 16px;
            height: 12px; /* Half height for each arrow */
        }
        QGroupBox {
            font-weight: bold;
            margin-top: 10px;
            border: 1px solid #555555;
            border-radius: 8px;
            padding-top: 20px;
            background-color: #3c3c3c;
            color: #e0e0e0;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            margin-left: 5px;
            color: #e0e0e0;
        }
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 5px;
            text-align: center;
            background-color: #4c4c4c;
            color: #e0e0e0;
        }
        QProgressBar::chunk {
            background-color: #2196F3; /* Blue */
            border-radius: 5px;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            border-radius: 8px;
            background-color: #3c3c3c;
        }
        QTabBar::tab {
            background: #4c4c4c;
            border: 1px solid #555555;
            border-bottom-color: #555555; /* same as pane color */
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 15px;
            margin-right: 2px;
            color: #b0b0b0;
        }
        QTabBar::tab:selected {
            background: #3c3c3c;
            border-bottom-color: #3c3c3c; /* same as pane color */
            color: #e0e0e0;
        }
        QTabBar::tab:hover {
            background-color: #404040;
        }
        QComboBox QAbstractItemView {
            min-width: 150px; /* Ensure dropdown has enough width */
            background-color: #4c4c4c;
            border: 1px solid #555555;
            border-radius: 5px;
            selection-background-color: #2196F3;
            selection-color: white;
            padding: 5px;
            color: #e0e0e0;
        }
        #success_message_label {
            font-size: 16px;
            font-weight: normal;
            color: #b0b0b0;
        }
        #open_converted_file_button, #return_to_converter_button {
            background-color: #007bff; /* Blue for action buttons */
        }
        #open_converted_file_button:hover, #return_to_converter_button:hover {
            background-color: #0056b3;
        }
    """

    def __init__(self, initial_dark_mode=False):
        super().__init__()
        self.setWindowTitle("Image Converter")
        self.setGeometry(200, 200, 1000, 800)
        self.setMinimumSize(500, 400)

        self.init_variables()
        self.setup_ui()
        self.center_window()

        # Apply initial theme
        self._apply_theme(initial_dark_mode)

    def _apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.setStyleSheet(self.DARK_QSS)
            # Adjust specific widget properties if QSS is not enough
            # Example: For QSpinBox, the text color might need direct adjustment if not picked up by QSS
            for spinbox in self.findChildren(QSpinBox):
                spinbox.setStyleSheet("color: #e0e0e0;")
        else:
            self.setStyleSheet(self.LIGHT_QSS)
            for spinbox in self.findChildren(QSpinBox):
                spinbox.setStyleSheet("color: #333333;")
        
    def init_variables(self):
        """初始化或重置所有变量"""
        self.input_path = ""
        self.output_path = ""
        self.min_size = 16
        self.max_size = 1024
        self.converting = False
        self.current_view = "main"
        self.output_format = "icns"  # Default output format
        
    def setup_ui(self):
        """Setup initial UI"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        self.create_widgets()
        self.create_success_view()
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

        # Main content area: Left Panel (Input/Output) and Right Side (Options/Preview)
        main_content_h_layout = QHBoxLayout()
        main_content_h_layout.setSpacing(20) # Increased spacing between left and right sections
        self.main_layout.addLayout(main_content_h_layout)

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
        self.input_text = QLineEdit()
        self.input_text.setReadOnly(True)
        input_button = QPushButton("Browse...")
        input_button.clicked.connect(self.on_browse_input)

        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_text, 1) # Give text field more stretch
        input_layout.addWidget(input_button)
        file_ops_group_layout.addLayout(input_layout)

        # Output File Selection (inside merged group box)
        output_layout = QHBoxLayout()
        output_label = QLabel("Output File:")
        self.output_text = QLineEdit()
        self.output_text.setReadOnly(True)
        output_button = QPushButton("Browse...")
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
        self.preview_label.setStyleSheet("border: 1px solid #cccccc; background-color: #f8f8f8; border-radius: 5px; color: #777777;")
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

        self.info_text = QLineEdit("No image selected")
        self.info_text.setReadOnly(True)
        self.info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_group_layout.addWidget(self.info_text)

        # Conversion Options
        options_group_box = QGroupBox("Conversion Options")
        options_group_layout = QVBoxLayout(options_group_box)
        options_group_layout.setContentsMargins(10, 25, 10, 10)
        options_group_layout.setSpacing(10)
        right_side_v_layout.addWidget(options_group_box, 0) # No stretch for options, compact
        
        # Output Format Selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Output Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(convert.SUPPORTED_FORMATS)
        self.format_combo.setCurrentText("icns")
        self.format_combo.currentIndexChanged.connect(self.on_format_change)
        format_layout.addWidget(format_label, 1)
        format_layout.addStretch(1)
        format_layout.addWidget(self.format_combo, 2)
        options_group_layout.addLayout(format_layout)

        # Minimum Size
        min_size_layout = QHBoxLayout()
        min_size_label = QLabel("Minimum Size:")
        self.min_spin = QSpinBox()
        self.min_spin.setRange(16, 512)
        self.min_spin.setValue(16)
        self.min_spin.valueChanged.connect(self.on_min_size_change)
        min_size_layout.addWidget(min_size_label, 1)
        min_size_layout.addStretch(1)
        min_size_layout.addWidget(self.min_spin, 2)
        options_group_layout.addLayout(min_size_layout)

        # Maximum Size
        max_size_layout = QHBoxLayout()
        max_size_label = QLabel("Maximum Size:")
        self.max_spin = QSpinBox()
        self.max_spin.setRange(32, 1024)
        self.max_spin.setValue(1024)
        self.max_spin.valueChanged.connect(self.on_max_size_change)
        max_size_layout.addWidget(max_size_label, 1)
        max_size_layout.addStretch(1)
        max_size_layout.addWidget(self.max_spin, 2)
        options_group_layout.addLayout(max_size_layout)
        
        # Auto-detect button
        self.auto_button = QPushButton("Auto-detect Max Size")
        self.auto_button.clicked.connect(self.on_auto_detect)
        options_group_layout.addWidget(self.auto_button, 0, Qt.AlignmentFlag.AlignCenter)

        # Progress Area
        progress_group_box = QGroupBox("Progress")
        progress_group_layout = QVBoxLayout(progress_group_box)
        progress_group_layout.setContentsMargins(10, 25, 10, 10)
        right_side_v_layout.addWidget(progress_group_box, 0) # No stretch for progress, compact

        self.progress_label = QLabel("Ready")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        progress_group_layout.addWidget(self.progress_label)
        progress_group_layout.addWidget(self.progress)

        # Convert Button
        self.convert_button = QPushButton("Convert to ICNS")
        self.convert_button.setFixedSize(180, 40)
        font = self.convert_button.font()
        font.setPointSize(font.pointSize() + 1)
        font.setBold(True)
        self.convert_button.setFont(font)
        self.convert_button.clicked.connect(self.on_start_conversion)
        right_side_v_layout.addWidget(self.convert_button, 0, Qt.AlignmentFlag.AlignCenter)

        # Add a stretch to the right_side_v_layout to push content to top
        right_side_v_layout.addStretch(1)

        # Add final stretch to main horizontal layout if needed, to push content to top-left
        # main_content_h_layout.addStretch(1) # This stretch is handled by the left/right panel stretches

        # Add a stretch to the main_layout to push everything to the top
        self.main_layout.addStretch(1)

    def create_success_view(self):
        self.success_widget = QWidget(self.main_widget)
        self.success_layout = QVBoxLayout(self.success_widget)

        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(50, 50, 50, 50) # Increased margins
        center_layout.setSpacing(20)

        center_layout.addStretch()

        title = QLabel("Conversion Successful!")
        font = title.font()
        font.setPointSize(font.pointSize() + 8) # Larger title
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #28a745;") # Success green
        center_layout.addWidget(title)

        checkmark = QLabel("✓")
        checkmark_font = checkmark.font()
        checkmark_font.setPointSize(checkmark_font.pointSize() + 30) # Larger checkmark
        checkmark_font.setBold(True)
        checkmark.setFont(checkmark_font)
        checkmark.setStyleSheet("color: #28a745;")  # Success green
        checkmark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(checkmark)

        msg = QLabel(f"Your {self.output_format.upper()} file has been created successfully!")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setObjectName("success_message_label") # Object name for QSS
        msg.setStyleSheet("color: #555555;")
        center_layout.addWidget(msg)

        open_btn = QPushButton("Open Converted File")
        open_btn.clicked.connect(self.on_open_converted_file)
        open_btn.setFixedSize(200, 45) # Larger buttons
        open_btn.setObjectName("open_converted_file_button") # Object name for QSS
        center_layout.addWidget(open_btn, 0, Qt.AlignmentFlag.AlignCenter)

        return_btn = QPushButton("Return to Converter")
        return_btn.clicked.connect(self.show_main_view)
        return_btn.setFixedSize(200, 45) # Larger buttons
        return_btn.setObjectName("return_to_converter_button") # Object name for QSS
        center_layout.addWidget(return_btn, 0, Qt.AlignmentFlag.AlignCenter)

        center_layout.addStretch()

        self.success_layout.addStretch()
        self.success_layout.addWidget(center_panel, 0, Qt.AlignmentFlag.AlignCenter)
        self.success_layout.addStretch()

        self.main_layout.addWidget(self.success_widget)
        self.success_widget.hide() # Initially hidden

    def _set_placeholder_preview(self):
        placeholder_text = "拖放图像到此处\n或点击'Browse...'选择文件\n🖼️"
        font = QFont()
        font.setPointSize(16) # Larger font for placeholder
        self.preview_label.setFont(font)
        self.preview_label.setText(placeholder_text)
        self.preview_label.setPixmap(QPixmap()) # Clear any previous image

    def on_browse_input(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.ico);;All files (*.*)")
        if file_dialog.exec():
            self.input_path = file_dialog.selectedFiles()[0]
            self.input_text.setText(self.input_path)
            self.auto_set_output()
            self.show_preview()
            self.update_image_info()
            
    def on_browse_output(self):
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
        default_filter = wildcard_map.get(self.output_format, "All files (*.*)")
        
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave) # Corrected enum
        file_dialog.setNameFilter(f"{default_filter};;All files (*.*)")
        file_dialog.setDefaultSuffix(self.output_format)

        if file_dialog.exec():
            self.output_path = file_dialog.selectedFiles()[0]
            expected_extension = '.' + self.output_format
            if not self.output_path.lower().endswith(expected_extension):
                self.output_path += expected_extension
            self.output_text.setText(self.output_path)
            
    def on_format_change(self, index):
        self.output_format = self.format_combo.currentText().lower()
        self.auto_set_output()
        
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
                QMessageBox.critical(self, "Error", f"Could not detect image size: {str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "Please select an input file first.")
            
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
        
    def on_max_size_change(self, value):
        self.max_size = value
            
    def on_start_conversion(self):
        if self.converting:
            return
            
        if not self.input_path:
            QMessageBox.critical(self, "Error", "Please select an input image file.")
            return
            
        if not self.output_path:
            QMessageBox.critical(self, "Error", f"Please specify an output {self.output_format.upper()} file.")
            return
            
        if not os.path.exists(self.input_path):
            QMessageBox.critical(self, "Error", "Input file does not exist.")
            return
            
        self.converting = True
        self.convert_button.setEnabled(False)
        self.progress.setValue(0)
        self.progress_label.setText("Starting conversion...")
        
        self._worker = ConversionWorker(
            self.input_path, self.output_path, self.output_format,
            self.min_size, # 始终传递整数值
            self.max_size  # 始终传递整数值
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
        self.show_success_view()
        
    def on_conversion_error(self, error_message):
        self.converting = False
        self.convert_button.setEnabled(True)
        if hasattr(self, '_thread') and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
        QMessageBox.critical(self, "Conversion Failed", error_message)
        self.progress_label.setText("Conversion Failed")

    def show_success_view(self):
        # The tab_widget is removed, so we just show the success widget
        self.success_widget.show()
        # Update success message based on current output format
        msg_label = self.success_widget.findChild(QLabel, "success_message_label")
        if msg_label:
            msg_label.setText(f"Your {self.output_format.upper()} file has been created successfully!")


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
                QMessageBox.critical(self, "Error", f"无法打开文件: {e}")
        else:
            QMessageBox.critical(self, "Error", "找不到转换后的文件。")

    def show_main_view(self):
        # Reset all variables
        self.init_variables()
        
        # Reset UI elements
        self.input_text.clear()
        self.output_text.clear()
        self.info_text.setText("No image selected")
        self.preview_label.clear()
        self._set_placeholder_preview() # Show placeholder when returning to main view
        self.min_spin.setValue(16)
        self.max_spin.setValue(1024)
        self.format_combo.setCurrentText("icns")
        # The on_format_change also handles enabling/disabling min/max spin boxes and auto-detect button
        self.on_format_change(self.format_combo.currentIndex()) # Explicitly call to set initial state
        self.progress.setValue(0)
        self.progress_label.setText("Ready")
        self.convert_button.setEnabled(True)
        self.status_bar.showMessage("Ready")
        # The tab_widget is removed, so we just hide the success widget
        self.success_widget.hide()

            
    def update_progress(self, message, percentage):
        self.progress_label.setText(message)
        self.progress.setValue(percentage)

    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class ICNSConverterApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = ICNSConverterGUI(
            initial_dark_mode=self.app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5
        ) # Pass initial dark mode state to GUI
        self.window.show()

        # Connect to palette changes for real-time theme switching
        self.app.paletteChanged.connect(self._on_palette_changed)

    def _on_palette_changed(self):
        is_dark_mode = self.app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5
        self.window._apply_theme(is_dark_mode)

    def MainLoop(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app_runner = ICNSConverterApp()
    app_runner.MainLoop()
