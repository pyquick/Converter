#!/usr/bin/env python3

"""
PNG to ICNS Converter with GUI

This script provides a graphical interface for converting PNG images to ICNS format.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import tempfile
import subprocess
import threading
from PIL import Image, ImageTk

# Add the current directory to Python path to import convert module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from support import convert


class ICNSConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG to ICNS Converter")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.min_size = tk.IntVar(value=16)
        self.max_size = tk.IntVar(value=1024)
        self.image_info = tk.StringVar(value="No image selected")
        self.converting = False
        
        # Track current view mode (main or success)
        self.view_mode = "main"
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Success frame (initially hidden)
        self.success_frame = ttk.Frame(self.root, padding="20")
        
        # Create both views
        self.create_main_view()
        self.create_success_view()
        
        # Show main view by default
        self.show_main_view()
        
    def create_main_view(self):
        """Create the main conversion interface"""
        main_frame = self.main_frame
        
        # Title
        title_label = ttk.Label(main_frame, text="PNG to ICNS Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Input PNG File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(input_frame, textvariable=self.input_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(input_frame, text="Browse...", command=self.browse_input).grid(row=0, column=1)
        input_frame.columnconfigure(0, weight=1)
        
        # Output file selection
        ttk.Label(main_frame, text="Output ICNS File:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).grid(row=0, column=1)
        output_frame.columnconfigure(0, weight=1)
        
        # Image info
        ttk.Label(main_frame, text="Image Information:").grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Label(main_frame, textvariable=self.image_info, relief="sunken", padding=5).grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Size options
        ttk.Label(main_frame, text="Conversion Options:", font=("Arial", 12, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(20, 10))
        
        # Min size
        min_size_frame = ttk.Frame(main_frame)
        min_size_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(min_size_frame, text="Minimum Size:").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(min_size_frame, from_=16, to=512, increment=16, textvariable=self.min_size, width=10).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Max size
        max_size_frame = ttk.Frame(main_frame)
        max_size_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(max_size_frame, text="Maximum Size:").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(max_size_frame, from_=32, to=1024, increment=32, textvariable=self.max_size, width=10).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Auto-detect button
        ttk.Button(main_frame, text="Auto-detect Max Size", command=self.auto_detect_max_size).grid(row=10, column=0, pady=5, sticky=tk.W)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Progress label
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.grid(row=12, column=0, columnspan=3, pady=(0, 10))
        
        # Convert button
        self.convert_button = ttk.Button(main_frame, text="Convert to ICNS", command=self.start_conversion)
        self.convert_button.grid(row=13, column=0, columnspan=3, pady=10)
        
        # Preview area
        ttk.Label(main_frame, text="Preview:", font=("Arial", 12, "bold")).grid(row=14, column=0, sticky=tk.W, pady=(10, 5))
        self.preview_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=1)
        self.preview_frame.grid(row=15, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=0)
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=16, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(15, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def create_success_view(self):
        """Create the success view with success.icns display and return button"""
        success_frame = self.success_frame
        
        # Title
        title_label = ttk.Label(success_frame, text="Conversion Successful!", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Success image
        self.success_image_label = ttk.Label(success_frame)
        self.success_image_label.grid(row=1, column=0, pady=20)
        
        # Load and display success.icns if available
        self.load_success_image()
        
        # Success message
        message_label = ttk.Label(success_frame, text="Your ICNS file has been created successfully!", 
                                 font=("Arial", 12))
        message_label.grid(row=2, column=0, pady=(0, 30))
        
        # Return button
        return_button = ttk.Button(success_frame, text="Return to Converter", 
                                  command=self.show_main_view)
        return_button.grid(row=3, column=0, pady=10)
        
        # Configure grid weights
        success_frame.columnconfigure(0, weight=1)
        success_frame.rowconfigure(1, weight=1)
        
    def load_success_image(self):
        """Load and display the success.icns image"""
        success_icns_path = os.path.join(os.path.dirname(__file__), "support", "Success.icns")
        if os.path.exists(success_icns_path):
            try:
                # Load and resize image for display
                img = Image.open(success_icns_path)
                img.thumbnail((128, 128))  # Resize for display
                photo = ImageTk.PhotoImage(img)
                self.success_image_label.configure(image=photo)
                self.success_image_label.image = photo  # Keep a reference
            except Exception as e:
                self.success_image_label.configure(text="Success image could not be loaded")
        else:
            self.success_image_label.configure(text="Success image not found")
        
    def show_main_view(self):
        """Show the main conversion interface"""
        self.success_frame.grid_remove()
        self.main_frame.grid()
        self.view_mode = "main"
        
    def show_success_view(self):
        """Show the success view"""
        self.main_frame.grid_remove()
        self.success_frame.grid()
        self.view_mode = "success"
        
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select PNG file",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            self.auto_set_output()
            self.show_preview()
            self.update_image_info()
            
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save ICNS file",
            defaultextension=".icns",
            filetypes=[("ICNS files", "*.icns"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            
    def auto_set_output(self):
        input_file = self.input_path.get()
        if input_file and input_file.lower().endswith('.png'):
            output_file = os.path.splitext(input_file)[0] + '.icns'
            self.output_path.set(output_file)
            
    def update_image_info(self):
        input_file = self.input_path.get()
        if input_file and os.path.exists(input_file):
            try:
                width, height = convert.get_image_info(input_file)
                self.image_info.set(f"Dimensions: {width}x{height}px")
                self.max_size.set(min(width, height))  # Auto-set max size
            except Exception as e:
                self.image_info.set(f"Error reading image: {str(e)}")
        else:
            self.image_info.set("No image selected")
            
    def auto_detect_max_size(self):
        input_file = self.input_path.get()
        if input_file and os.path.exists(input_file):
            try:
                width, height = convert.get_image_info(input_file)
                self.max_size.set(min(width, height))
                self.status_var.set(f"Max size auto-detected: {min(width, height)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not detect image size: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please select an input file first.")
            
    def show_preview(self):
        input_file = self.input_path.get()
        if input_file and os.path.exists(input_file):
            try:
                # Load and resize image for preview
                img = Image.open(input_file)
                img.thumbnail((100, 100))  # Resize for preview
                photo = ImageTk.PhotoImage(img)
                self.preview_label.configure(image=photo)
                self.preview_label.image = photo  # Keep a reference
                self.status_var.set(f"Loaded: {os.path.basename(input_file)} ({img.size[0]}x{img.size[1]})")
            except Exception as e:
                self.preview_label.configure(image='', text=f"Preview error: {str(e)}")
                self.status_var.set("Preview error")
        else:
            self.preview_label.configure(image='', text="No preview available")
            self.status_var.set("Ready")
            
    def start_conversion(self):
        """Start conversion in a separate thread to avoid blocking the UI"""
        if self.converting:
            return
            
        input_file = self.input_path.get()
        output_file = self.output_path.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input PNG file.")
            return
            
        if not output_file:
            messagebox.showerror("Error", "Please specify an output ICNS file.")
            return
            
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist.")
            return
            
        if not input_file.lower().endswith('.png'):
            messagebox.showerror("Error", "Input file must be a PNG image.")
            return
            
        # Start conversion in a separate thread
        self.converting = True
        self.convert_button.config(state="disabled")
        conversion_thread = threading.Thread(target=self.convert)
        conversion_thread.daemon = True
        conversion_thread.start()
            
    def convert(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()
        
        # Reset progress
        self.progress['value'] = 0
        self.root.after(0, self._update_progress_text, "Starting conversion...")
        self.root.after(0, self._update_status, "Converting...")
        
        try:
            # Perform conversion with progress callback
            convert.create_icns(
                input_file, 
                output_file, 
                self.min_size.get(), 
                self.max_size.get(),
                progress_callback=self.update_progress
            )
            
            # Show success view
            self.root.after(0, self._show_success)
        except Exception as e:
            self.root.after(0, self._update_status, "Conversion failed")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Conversion failed: {str(e)}"))
            self.root.after(0, self._enable_convert_button)
        finally:
            self.converting = False
            
    def _show_success(self):
        """Show success view after conversion"""
        self.show_success_view()
        self._enable_convert_button()
        self._clear_form()
        
    def _clear_form(self):
        """Clear all form fields"""
        self.input_path.set("")
        self.output_path.set("")
        self.image_info.set("No image selected")
        self.min_size.set(16)
        self.max_size.set(1024)
        self.preview_label.configure(image='', text="No preview available")
        self.progress['value'] = 0
        self.progress_label.config(text="")
        self.status_var.set("Ready")
            
    def _update_progress_text(self, text):
        """Helper method to update progress label text"""
        self.progress_label.config(text=text)
        
    def _update_status(self, text):
        """Helper method to update status bar text"""
        self.status_var.set(text)
        
    def _update_progress_value(self, value):
        """Helper method to update progress bar value"""
        self.progress['value'] = value
        
    def _enable_convert_button(self):
        """Helper method to re-enable the convert button"""
        self.convert_button.config(state="normal")
            
    def update_progress(self, message, percentage):
        """Update progress bar from the conversion thread"""
        self.root.after(0, self._update_progress_text, message)
        self.root.after(0, self._update_progress_value, percentage)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = ICNSConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()