#!/usr/bin/env python3

"""
PNG to ICNS Converter with wxPython GUI

This script provides a graphical interface for converting PNG images to ICNS format.
"""

import wx
import os
import sys
import threading
from PIL import Image

# Add the current directory to Python path to import convert module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from support import convert


class ICNSConverterGUI(wx.Frame):
    def __init__(self, parent, title):
        super(ICNSConverterGUI, self).__init__(parent, title=title, size=(1000,800))
        self.SetMinSize((600, 500))
        
        # Variables
        self.init_variables()
        
        # Create UI
        self.setup_ui()
        
        # Center the window
        self.Centre()
        
        # Bind size event
        self.Bind(wx.EVT_SIZE, self.on_resize)
        
        # Show the window after everything is set up
        self.Layout()
        self.Show()
        
    def init_variables(self):
        """初始化或重置所有变量"""
        self.input_path = ""
        self.output_path = ""
        self.min_size = 16
        self.max_size = 1024
        self.converting = False
        self.current_view = "main"
        self.output_format = "icns" # Default output format
        
    def setup_ui(self):
        """Setup initial UI"""
        # Create status bar only if it doesn't exist
        if not hasattr(self, 'status_bar'):
            self.status_bar = self.CreateStatusBar()
            self.status_bar.SetStatusText("Ready")
        
        # Create main panel
        self.main_panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.main_sizer)
        
        # Create widgets
        self.create_widgets()
        
        # Set window sizer
        window_sizer = wx.BoxSizer(wx.VERTICAL)
        window_sizer.Add(self.main_panel, 1, wx.EXPAND)
        self.SetSizer(window_sizer)
        
    def create_widgets(self):
        """Create the main conversion interface"""
        # Set main panel color
        
        
        # Title panel
        title_panel = wx.Panel(self.main_panel)
       # title_panel.SetBackgroundColour(wx.Colour(51, 51, 51))
        title_text = wx.StaticText(title_panel, label="PNG to ICNS Converter")
        title_text.SetForegroundColour(wx.WHITE)
        title_font = title_text.GetFont()
        title_font.PointSize += 12
        title_font = title_font.Bold()
        title_text.SetFont(title_font)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(title_text, 0, wx.ALL | wx.CENTER, 20)
        title_panel.SetSizer(title_sizer)
        self.main_sizer.Add(title_panel, 0, wx.EXPAND)
        
        # Create notebook for tabs
        notebook = wx.Notebook(self.main_panel)
        #notebook.SetBackgroundColour(wx.WHITE)
        
        # Main conversion tab
        conversion_panel = wx.Panel(notebook)
        #conversion_panel.SetBackgroundColour(wx.WHITE)
        conversion_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left and Right panels
        left_panel = wx.Panel(conversion_panel)
        right_panel = wx.Panel(conversion_panel)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        left_panel.SetSizer(left_sizer)
        right_panel.SetSizer(right_sizer)
        
        # Add panels to conversion sizer
        conversion_sizer.Add(left_panel, 1, wx.EXPAND | wx.ALL, 10)
        conversion_sizer.Add(right_panel, 1, wx.EXPAND | wx.ALL, 10)
        
        # Input file selection
        input_box = wx.StaticBox(left_panel, label="Input File")
        #input_box.SetForegroundColour(wx.Colour(51, 51, 51))
        input_box_sizer = wx.StaticBoxSizer(input_box, wx.VERTICAL)
        
        input_grid = wx.FlexGridSizer(1, 3, 5, 5)
        input_grid.AddGrowableCol(1)
        
        self.input_text = wx.TextCtrl(input_box_sizer.GetStaticBox(), style=wx.TE_READONLY)
        input_button = wx.Button(input_box_sizer.GetStaticBox(), label="Browse...")
        input_button.Bind(wx.EVT_BUTTON, self.on_browse_input)
        
        input_label = wx.StaticText(input_box_sizer.GetStaticBox(), label="File Path:")
        #input_label.SetForegroundColour(wx.Colour(51, 51, 51))
        input_grid.Add(input_label, 0, wx.ALIGN_CENTER_VERTICAL)
        input_grid.Add(self.input_text, 1, wx.EXPAND)
        input_grid.Add(input_button, 0, wx.EXPAND)
        
        input_box_sizer.Add(input_grid, 1, wx.EXPAND | wx.ALL, 10)
        left_sizer.Add(input_box_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        
        # Output file selection
        output_box = wx.StaticBox(left_panel, label="Output File")
        #output_box.SetForegroundColour(wx.Colour(51, 51, 51))
        output_box_sizer = wx.StaticBoxSizer(output_box, wx.VERTICAL)
        
        output_grid = wx.FlexGridSizer(1, 3, 5, 5)
        output_grid.AddGrowableCol(1)
        
        self.output_text = wx.TextCtrl(output_box_sizer.GetStaticBox(), style=wx.TE_READONLY)
        output_button = wx.Button(output_box_sizer.GetStaticBox(), label="Browse...")
        output_button.Bind(wx.EVT_BUTTON, self.on_browse_output)
        
        output_label = wx.StaticText(output_box_sizer.GetStaticBox(), label="File Path:")
        #output_label.SetForegroundColour(wx.Colour(51, 51, 51))
        output_grid.Add(output_label, 0, wx.ALIGN_CENTER_VERTICAL)
        output_grid.Add(self.output_text, 1, wx.EXPAND)
        output_grid.Add(output_button, 0, wx.EXPAND)
        
        output_box_sizer.Add(output_grid, 1, wx.EXPAND | wx.ALL, 10)
        left_sizer.Add(output_box_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        
        # Image info
        info_box = wx.StaticBox(right_panel, label="Image Information")
        #info_box.SetForegroundColour(wx.Colour(51, 51, 51))
        info_box_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        
        info_panel = wx.Panel(info_box_sizer.GetStaticBox())
        #info_panel.SetBackgroundColour(wx.Colour(245, 245, 245))
        
        self.info_text = wx.TextCtrl(info_panel, style=wx.TE_READONLY | wx.TE_CENTER)
        self.info_text.SetValue("No image selected")
        info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel_sizer.Add(self.info_text, 0, wx.EXPAND | wx.ALL, 10)
        info_panel.SetSizer(info_panel_sizer)
        
        info_box_sizer.Add(info_panel, 1, wx.EXPAND | wx.ALL, 10)
        right_sizer.Add(info_box_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        
        # Size options
        size_box = wx.StaticBox(right_panel, label="Conversion Options")
        #size_box.SetForegroundColour(wx.Colour(51, 51, 51))
        size_box_sizer = wx.StaticBoxSizer(size_box, wx.VERTICAL)
        
        options_panel = wx.Panel(size_box_sizer.GetStaticBox())
        #options_panel.SetBackgroundColour(wx.Colour(245, 245, 245))
        options_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Output Format Selection
        format_sizer = wx.BoxSizer(wx.HORIZONTAL)
        format_label = wx.StaticText(options_panel, label="Output Format:")
        self.format_combo = wx.ComboBox(options_panel, choices=convert.SUPPORTED_FORMATS, 
                                        style=wx.CB_READONLY, value="icns")
        self.format_combo.Bind(wx.EVT_COMBOBOX, self.on_format_change)
        format_sizer.Add(format_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        format_sizer.AddStretchSpacer()
        format_sizer.Add(self.format_combo, 0, wx.ALL, 10)
        options_sizer.Add(format_sizer, 0, wx.EXPAND)
        
        # Min size
        min_sizer = wx.BoxSizer(wx.HORIZONTAL)
        min_label = wx.StaticText(options_panel, label="Minimum Size:")
        #min_label.SetForegroundColour(wx.Colour(51, 51, 51))
        self.min_spin = wx.SpinCtrl(options_panel, value="16", min=16, max=512, initial=16)
        self.min_spin.Bind(wx.EVT_SPINCTRL, self.on_min_size_change)
        min_sizer.Add(min_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        min_sizer.AddStretchSpacer()
        min_sizer.Add(self.min_spin, 0, wx.ALL, 10)
        options_sizer.Add(min_sizer, 0, wx.EXPAND)
        
        # Max size
        max_sizer = wx.BoxSizer(wx.HORIZONTAL)
        max_label = wx.StaticText(options_panel, label="Maximum Size:")
        #max_label.SetForegroundColour(wx.Colour(51, 51, 51))
        self.max_spin = wx.SpinCtrl(options_panel, value="1024", min=32, max=1024, initial=1024)
        self.max_spin.Bind(wx.EVT_SPINCTRL, self.on_max_size_change)
        max_sizer.Add(max_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        max_sizer.AddStretchSpacer()
        max_sizer.Add(self.max_spin, 0, wx.ALL, 10)
        options_sizer.Add(max_sizer, 0, wx.EXPAND)
        
        # Auto-detect button
        self.auto_button = wx.Button(options_panel, label="Auto-detect Max Size")
        self.auto_button.Bind(wx.EVT_BUTTON, self.on_auto_detect)
        options_sizer.Add(self.auto_button, 0, wx.ALL | wx.CENTER, 15)
        
        options_panel.SetSizer(options_sizer)
        size_box_sizer.Add(options_panel, 1, wx.EXPAND | wx.ALL, 10)
        right_sizer.Add(size_box_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        
        # Progress area
        progress_box = wx.StaticBox(right_panel, label="Progress")
       # progress_box.SetForegroundColour(wx.Colour(51, 51, 51))
        progress_box_sizer = wx.StaticBoxSizer(progress_box, wx.VERTICAL)
        
        progress_panel = wx.Panel(progress_box_sizer.GetStaticBox())
       # progress_panel.SetBackgroundColour(wx.Colour(245, 245, 245))
        progress_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.progress_label = wx.StaticText(progress_panel, label="Ready", style=wx.ALIGN_CENTER)
        #self.progress_label.SetForegroundColour(wx.Colour(51, 51, 51))
        self.progress = wx.Gauge(progress_panel, range=100)
        
        progress_panel_sizer.Add(self.progress_label, 0, wx.EXPAND | wx.ALL, 10)
        progress_panel_sizer.Add(self.progress, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        progress_panel.SetSizer(progress_panel_sizer)
        progress_box_sizer.Add(progress_panel, 1, wx.EXPAND | wx.ALL, 10)
        right_sizer.Add(progress_box_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        
        # Convert button
        self.convert_button = wx.Button(right_panel, label="Convert to ICNS", size=(200, 40))
        font = self.convert_button.GetFont()
        font = font.Bold()
        self.convert_button.SetFont(font)
        self.convert_button.Bind(wx.EVT_BUTTON, self.on_start_conversion)
        right_sizer.Add(self.convert_button, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        
        # Set sizer for conversion panel
        conversion_panel.SetSizer(conversion_sizer)
        notebook.AddPage(conversion_panel, "Conversion")
        
        # Preview tab
        preview_panel = wx.Panel(notebook)
        #preview_panel.SetBackgroundColour(wx.WHITE)
        preview_sizer = wx.BoxSizer(wx.VERTICAL)
        
        preview_box = wx.StaticBox(preview_panel, label="Image Preview")
       # preview_box.SetForegroundColour(wx.Colour(51, 51, 51))
        preview_box_sizer = wx.StaticBoxSizer(preview_box, wx.VERTICAL)
        
        preview_inner_panel = wx.Panel(preview_box_sizer.GetStaticBox())
       #preview_inner_panel.SetBackgroundColour(wx.Colour(245, 245, 245))
        preview_inner_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Preview area
        self.preview_bitmap = wx.StaticBitmap(preview_inner_panel, size=(300, 300))
        preview_inner_sizer.Add(self.preview_bitmap, 1, wx.CENTER | wx.ALL, 20)
        preview_inner_panel.SetSizer(preview_inner_sizer)
        
        preview_box_sizer.Add(preview_inner_panel, 1, wx.EXPAND | wx.ALL, 10)
        preview_sizer.Add(preview_box_sizer, 1, wx.EXPAND | wx.ALL, 15)
        
        preview_panel.SetSizer(preview_sizer)
        notebook.AddPage(preview_panel, "Preview")
        
        self.main_sizer.Add(notebook, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
    def on_browse_input(self, event):
        with wx.FileDialog(self, "Select PNG file", wildcard="PNG files (*.png)|*.png|All files (*.*)|*.*",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
                
            self.input_path = fileDialog.GetPath()
            self.input_text.SetValue(self.input_path)
            self.auto_set_output()
            self.show_preview()
            self.update_image_info()
            
    def on_browse_output(self, event):
        wildcard_map = {
            "icns": "ICNS files (*.icns)|*.icns",
            "png": "PNG files (*.png)|*.png",
            "jpg": "JPEG files (*.jpg)|*.jpg",
            "webp": "WebP files (*.webp)|*.webp",
        }
        default_wildcard = wildcard_map.get(self.output_format, "All files (*.*)|*.*")
        
        with wx.FileDialog(self, f"Save {self.output_format.upper()} file", wildcard=default_wildcard + "|All files (*.*)|*.*",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
                
            self.output_path = fileDialog.GetPath()
            # Ensure the output path has the correct extension based on selected format
            expected_extension = '.' + self.output_format
            if not self.output_path.lower().endswith(expected_extension):
                self.output_path += expected_extension
            self.output_text.SetValue(self.output_path)
            
    def on_format_change(self, event):
        self.output_format = self.format_combo.GetValue().lower()
        # Update output path with new extension if an input file is selected
        self.auto_set_output()
        self.convert_button.SetLabel(f"Convert to {self.output_format.upper()}")
        # Disable size options if not converting to ICNS
        enable_size_options = (self.output_format == "icns")
        self.min_spin.Enable(enable_size_options)
        self.max_spin.Enable(enable_size_options)
        self.auto_button.Enable(enable_size_options) # Corrected: Reference auto_button
        
    def auto_set_output(self):
        if self.input_path:
            base_name = os.path.splitext(os.path.basename(self.input_path))[0]
            output_file = f"{os.path.dirname(self.input_path)}{os.sep}{base_name}.{self.output_format}"
            self.output_path = output_file
            self.output_text.SetValue(output_file)
            
    def update_image_info(self):
        if self.input_path and os.path.exists(self.input_path):
            try:
                width, height = convert.get_image_info(self.input_path)
                self.info_text.SetValue(f"Dimensions: {width}x{height}px")
                self.max_size = min(width, height)
                self.max_spin.SetValue(self.max_size)
            except Exception as e:
                self.info_text.SetValue(f"Error reading image: {str(e)}")
        else:
            self.info_text.SetValue("No image selected")
            
    def on_auto_detect(self, event):
        if self.input_path and os.path.exists(self.input_path):
            try:
                width, height = convert.get_image_info(self.input_path)
                self.max_size = min(width, height)
                self.max_spin.SetValue(self.max_size)
                self.status_bar.SetStatusText(f"Max size auto-detected: {self.max_size}")
            except Exception as e:
                wx.MessageBox(f"Could not detect image size: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox("Please select an input file first.", "Warning", wx.OK | wx.ICON_WARNING)
            
    def show_preview(self):
        if self.input_path and os.path.exists(self.input_path):
            try:
                # Load and resize image for preview
                img = Image.open(self.input_path)
                img.thumbnail((300, 300))  # Resize for preview
                
                # Convert PIL image to wxPython image
                wx_image = wx.Image(img.size[0], img.size[1])
                wx_image.SetData(img.convert("RGB").tobytes())
                bitmap = wx_image.ConvertToBitmap()
                
                self.preview_bitmap.SetBitmap(bitmap)
                self.status_bar.SetStatusText(f"Loaded: {os.path.basename(self.input_path)} ({img.size[0]}x{img.size[1]})")
            except Exception as e:
                self.preview_bitmap.SetBitmap(wx.NullBitmap)
                self.status_bar.SetStatusText("Preview error")
        else:
            self.preview_bitmap.SetBitmap(wx.NullBitmap)
            self.status_bar.SetStatusText("Ready")
            
    def on_min_size_change(self, event):
        self.min_size = self.min_spin.GetValue()
        
    def on_max_size_change(self, event):
        self.max_size = self.max_spin.GetValue()
            
    def on_start_conversion(self, event):
        """Start conversion in a separate thread to avoid blocking the UI"""
        if self.converting:
            return
            
        if not self.input_path:
            wx.MessageBox("Please select an input PNG file.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        if not self.output_path:
            wx.MessageBox(f"Please specify an output {self.output_format.upper()} file.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        if not os.path.exists(self.input_path):
            wx.MessageBox("Input file does not exist.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # The input can be any image format now that Pillow handles it
        # No longer need to check for .png extension here
            
        # Start conversion in a separate thread
        self.converting = True
        self.convert_button.Enable(False)
        self.progress.SetValue(0)
        self.progress_label.SetLabel("Starting conversion...")
        conversion_thread = threading.Thread(target=self.convert)
        conversion_thread.daemon = True
        conversion_thread.start()
            
    def convert(self):
        """执行转换过程"""
        try:
            # 执行转换
            if self.output_format == "icns":
                convert.convert_image(
                    self.input_path, 
                    self.output_path, 
                    self.output_format,
                    self.min_size, 
                    self.max_size,
                    progress_callback=self.update_progress
                )
            else:
                convert.convert_image(
                    self.input_path,
                    self.output_path,
                    self.output_format,
                    progress_callback=self.update_progress
                )
            
            # 在主线程中显示成功界面
            wx.CallAfter(self.show_success_view)
            
        except Exception as e:
            wx.CallAfter(self.on_conversion_error, str(e))
            
    def show_success_view(self):
        """显示转换成功界面"""
        # 保存当前窗口位置和大小
        current_size = self.GetSize()
        current_pos = self.GetPosition()
        
        # 清除所有控件
        for child in self.GetChildren():
            if child != self.status_bar:
                child.Destroy()
        
        # 创建内容面板
        content_panel = wx.Panel(self)
        #content_panel.SetBackgroundColour(wx.WHITE)
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 创建子面板用于内容居中
        center_panel = wx.Panel(content_panel)
        #center_panel.SetBackgroundColour(wx.WHITE)
        center_sizer = wx.BoxSizer(wx.VERTICAL)
        
        center_sizer.AddStretchSpacer()
        
        # 添加标题
        title = wx.StaticText(center_panel, label="Conversion Successful!")
        font = title.GetFont()
        font.PointSize += 4
        font.MakeBold()
        title.SetFont(font)
        center_sizer.Add(title, 0, wx.CENTER | wx.BOTTOM, 20)
        
        # 添加成功图标（使用 ✓ 符号）
        checkmark = wx.StaticText(center_panel, label="✓")
        checkmark_font = checkmark.GetFont()
        checkmark_font.PointSize += 20
        checkmark_font.MakeBold()
        checkmark.SetFont(checkmark_font)
        checkmark.SetForegroundColour(wx.Colour(76, 175, 80))  # 设置为绿色
        center_sizer.Add(checkmark, 0, wx.CENTER | wx.ALL, 20)
        
        # 添加成功信息
        msg = wx.StaticText(center_panel, label=f"Your {self.output_format.upper()} file has been created successfully!")
        center_sizer.Add(msg, 0, wx.CENTER | wx.BOTTOM, 20)
        
        # 添加返回按钮
        btn = wx.Button(center_panel, label="Return to Converter")
        btn.Bind(wx.EVT_BUTTON, self.show_main_view)
        center_sizer.Add(btn, 0, wx.CENTER | wx.TOP, 20)
        
        center_sizer.AddStretchSpacer()
        
        center_panel.SetSizer(center_sizer)
        
        # 添加水平方向的空白区域
        content_sizer.AddStretchSpacer()
        content_sizer.Add(center_panel, 0, wx.CENTER | wx.EXPAND)
        content_sizer.AddStretchSpacer()
        
        content_panel.SetSizer(content_sizer)
        
        # 创建主窗口sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(content_panel, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        
        # 恢复窗口尺寸和位置
        self.SetSize(current_size)
        self.SetPosition(current_pos)
        
        # 更新布局
        self.Layout()
        self.Refresh()
        
        # 重置状态
        self.converting = False
        self.current_view = "success" # Set current view to success
        
    def on_conversion_error(self, error_message):
        """转换失败后的处理"""
        self.converting = False
        self.convert_button.Enable(True)
        wx.MessageBox(error_message, "Conversion Failed", wx.OK | wx.ICON_ERROR)
            
    def show_main_view(self, event=None):
        """返回主界面，重新初始化所有内容"""
        # 保存当前窗口位置和大小
        current_size = self.GetSize()
        current_pos = self.GetPosition()
        
        # Reset all variables
        self.init_variables()
        
        # Clear all controls (except status bar) to ensure a clean slate
        for child in self.GetChildren():
            if child != self.status_bar and child.GetName() != "FrameStatusBar": # Exclude status bar
                child.Destroy()
        
        # Re-setup UI (this will create new widgets and set self.main_panel)
        self.setup_ui()
        self.current_view = "main" # Ensure we are in the main view
        
        # Update widgets to reflect initial state (these are new widgets from setup_ui)
        self.input_text.SetValue("")
        self.output_text.SetValue("")
        self.info_text.SetValue("No image selected")
        self.preview_bitmap.SetBitmap(wx.NullBitmap)
        self.min_spin.SetValue(16)
        self.max_spin.SetValue(1024)
        self.format_combo.SetValue("icns")
        self.convert_button.SetLabel("Convert to ICNS")
        self.min_spin.Enable(True)
        self.max_spin.Enable(True)
        self.auto_button.Enable(True)
        self.progress.SetValue(0)
        self.progress_label.SetLabel("Ready")
        self.convert_button.Enable(True)
        
        # Re-layout the main panel
        self.main_panel.Layout()
        
        # Restore window size and position
        self.SetSize(current_size)
        self.SetPosition(current_pos)
        
        # Refresh display
        self.Layout()
        self.Refresh()

    def on_resize(self, event):
        """处理窗口大小改变事件"""
        self.Layout()
        event.Skip()
            
    def update_progress(self, message, percentage):
        """Update progress bar from the conversion thread"""
        wx.CallAfter(self.progress_label.SetLabel, message)
        wx.CallAfter(self.progress.SetValue, percentage)
        wx.CallAfter(self.Update)


class ICNSConverterApp(wx.App):
    def OnInit(self):
        frame = ICNSConverterGUI(None, "Image Converter")
        return True


def main():
    app = ICNSConverterApp()
    app.MainLoop()


if __name__ == "__main__":
    main()
