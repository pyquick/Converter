#!/usr/bin/env python3
"""
GUI for ZIP File Processing Tool

This script provides a graphical interface for creating, extracting, and managing ZIP files.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import threading
import zipfile
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Import functions from convertzip module
try:
    from convertzip import create_zip, extract_zip, add_to_zip, list_zip_contents
except ImportError:
    # If direct import fails, try alternative approach
    import importlib.util
    spec = importlib.util.spec_from_file_location("convertzip", 
                                                  os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                              "convertzip.py"))
    convertzip_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(convertzip_module)
    
    # Get functions from the module
    create_zip = convertzip_module.create_zip
    extract_zip = convertzip_module.extract_zip
    add_to_zip = convertzip_module.add_to_zip
    list_zip_contents = convertzip_module.list_zip_contents


class ZipGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ZIP File Processing Tool")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.create_sources = []
        self.create_output_path = tk.StringVar()
        self.extract_zip_path = tk.StringVar()
        self.extract_dest_path = tk.StringVar()
        self.add_zip_path = tk.StringVar()
        self.add_file_path = tk.StringVar()
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_create_tab()
        self.create_extract_tab()
        self.create_add_tab()
        self.create_list_tab()
        
    def create_create_tab(self):
        """Create tab for creating ZIP files"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Create ZIP")
        
        # Output file selection
        ttk.Label(frame, text="Output ZIP File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(frame)
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(output_frame, textvariable=self.create_output_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_create_output).grid(row=0, column=1)
        output_frame.columnconfigure(0, weight=1)
        
        # Source files list
        ttk.Label(frame, text="Source Files/Directories:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        # Listbox for sources
        listbox_frame = ttk.Frame(frame)
        listbox_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        self.sources_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED)
        self.sources_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.sources_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.sources_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Buttons to add/remove sources
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Add Files...", command=self.add_source_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Add Folder...", command=self.add_source_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_source).pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress bar
        self.create_progress = ttk.Progressbar(frame, mode='determinate')
        self.create_progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Progress label
        self.create_progress_label = ttk.Label(frame, text="")
        self.create_progress_label.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        # Create button
        ttk.Button(frame, text="Create ZIP", command=self.start_create_zip).grid(row=7, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        
    def create_extract_tab(self):
        """Create tab for extracting ZIP files"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Extract ZIP")
        
        # ZIP file selection
        ttk.Label(frame, text="ZIP File to Extract:").grid(row=0, column=0, sticky=tk.W, pady=5)
        zip_frame = ttk.Frame(frame)
        zip_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(zip_frame, textvariable=self.extract_zip_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(zip_frame, text="Browse...", command=self.browse_extract_zip).grid(row=0, column=1)
        zip_frame.columnconfigure(0, weight=1)
        
        # Destination folder selection
        ttk.Label(frame, text="Destination Folder:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        dest_frame = ttk.Frame(frame)
        dest_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(dest_frame, textvariable=self.extract_dest_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dest_frame, text="Browse...", command=self.browse_extract_dest).grid(row=0, column=1)
        dest_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.extract_progress = ttk.Progressbar(frame, mode='determinate')
        self.extract_progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Progress label
        self.extract_progress_label = ttk.Label(frame, text="")
        self.extract_progress_label.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        # Extract button
        ttk.Button(frame, text="Extract ZIP", command=self.start_extract_zip).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        frame.columnconfigure(0, weight=1)
        
    def create_add_tab(self):
        """Create tab for adding files to existing ZIP"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Add to ZIP")
        
        # ZIP file selection
        ttk.Label(frame, text="Existing ZIP File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        zip_frame = ttk.Frame(frame)
        zip_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(zip_frame, textvariable=self.add_zip_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(zip_frame, text="Browse...", command=self.browse_add_zip).grid(row=0, column=1)
        zip_frame.columnconfigure(0, weight=1)
        
        # File to add selection
        ttk.Label(frame, text="File to Add:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        file_frame = ttk.Frame(frame)
        file_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(file_frame, textvariable=self.add_file_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(file_frame, text="Browse...", command=self.browse_add_file).grid(row=0, column=1)
        file_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.add_progress = ttk.Progressbar(frame, mode='determinate')
        self.add_progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Progress label
        self.add_progress_label = ttk.Label(frame, text="")
        self.add_progress_label.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        # Add button
        ttk.Button(frame, text="Add to ZIP", command=self.start_add_to_zip).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        frame.columnconfigure(0, weight=1)
        
    def create_list_tab(self):
        """Create tab for listing ZIP contents"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="List Contents")
        
        # ZIP file selection
        ttk.Label(frame, text="ZIP File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        zip_frame = ttk.Frame(frame)
        zip_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.list_zip_path = tk.StringVar()
        ttk.Entry(zip_frame, textvariable=self.list_zip_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(zip_frame, text="Browse...", command=self.browse_list_zip).grid(row=0, column=1)
        zip_frame.columnconfigure(0, weight=1)
        
        # Listbox for contents
        ttk.Label(frame, text="ZIP Contents:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        listbox_frame = ttk.Frame(frame)
        listbox_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        self.contents_listbox = tk.Listbox(listbox_frame)
        self.contents_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.contents_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.contents_listbox.configure(yscrollcommand=scrollbar.set)
        
        # List button
        ttk.Button(frame, text="List Contents", command=self.list_zip_contents).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        
    # Browse methods for Create tab
    def browse_create_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save ZIP file",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if filename:
            self.create_output_path.set(filename)
            
    def add_source_files(self):
        filenames = filedialog.askopenfilenames(
            title="Select files to add"
        )
        if filenames:
            for filename in filenames:
                if filename not in self.create_sources:
                    self.create_sources.append(filename)
                    self.sources_listbox.insert(tk.END, filename)
                    
    def add_source_folder(self):
        folder = filedialog.askdirectory(
            title="Select folder to add"
        )
        if folder:
            if folder not in self.create_sources:
                self.create_sources.append(folder)
                self.sources_listbox.insert(tk.END, f"[FOLDER] {folder}")
                
    def remove_source(self):
        selection = self.sources_listbox.curselection()
        if selection:
            for i in reversed(selection):
                self.sources_listbox.delete(i)
                del self.create_sources[i]
                
    # Browse methods for Extract tab
    def browse_extract_zip(self):
        filename = filedialog.askopenfilename(
            title="Select ZIP file to extract",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if filename:
            self.extract_zip_path.set(filename)
            
    def browse_extract_dest(self):
        folder = filedialog.askdirectory(
            title="Select destination folder"
        )
        if folder:
            self.extract_dest_path.set(folder)
            
    # Browse methods for Add tab
    def browse_add_zip(self):
        filename = filedialog.askopenfilename(
            title="Select ZIP file",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if filename:
            self.add_zip_path.set(filename)
            
    def browse_add_file(self):
        filename = filedialog.askopenfilename(
            title="Select file to add"
        )
        if filename:
            self.add_file_path.set(filename)
            
    # Browse method for List tab
    def browse_list_zip(self):
        filename = filedialog.askopenfilename(
            title="Select ZIP file",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if filename:
            self.list_zip_path.set(filename)
            
    # Progress update methods
    def update_create_progress(self, message, progress):
        """Update progress for create operation"""
        self.root.after(0, lambda: self.create_progress_label.config(text=message))
        if progress >= 0:
            self.root.after(0, lambda: self.create_progress.config(value=progress))
        self.root.update_idletasks()
        
    def update_extract_progress(self, message, progress):
        """Update progress for extract operation"""
        self.root.after(0, lambda: self.extract_progress_label.config(text=message))
        if progress >= 0:
            self.root.after(0, lambda: self.extract_progress.config(value=progress))
        self.root.update_idletasks()
        
    def update_add_progress(self, message, progress):
        """Update progress for add operation"""
        self.root.after(0, lambda: self.add_progress_label.config(text=message))
        if progress >= 0:
            self.root.after(0, lambda: self.add_progress.config(value=progress))
        self.root.update_idletasks()
        
    # Start operation methods
    def start_create_zip(self):
        """Start ZIP creation in a separate thread"""
        output_path = self.create_output_path.get()
        if not output_path:
            messagebox.showerror("Error", "Please specify an output ZIP file.")
            return
            
        if not self.create_sources:
            messagebox.showerror("Error", "Please add at least one source file or folder.")
            return
            
        # Start in separate thread
        thread = threading.Thread(target=self.create_zip_thread, args=(output_path, self.create_sources))
        thread.daemon = True
        thread.start()
        
    def create_zip_thread(self, output_path, sources):
        """Thread function for creating ZIP"""
        try:
            success = create_zip(output_path, sources, self.update_create_progress)
            if success:
                self.root.after(0, lambda: messagebox.showinfo("Success", "ZIP file created successfully!"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to create ZIP file."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error creating ZIP: {str(e)}"))
            
    def start_extract_zip(self):
        """Start ZIP extraction in a separate thread"""
        zip_path = self.extract_zip_path.get()
        dest_path = self.extract_dest_path.get()
        
        if not zip_path:
            messagebox.showerror("Error", "Please specify a ZIP file to extract.")
            return
            
        if not dest_path:
            messagebox.showerror("Error", "Please specify a destination folder.")
            return
            
        # Start in separate thread
        thread = threading.Thread(target=self.extract_zip_thread, args=(zip_path, dest_path))
        thread.daemon = True
        thread.start()
        
    def extract_zip_thread(self, zip_path, dest_path):
        """Thread function for extracting ZIP"""
        try:
            success = extract_zip(zip_path, dest_path, self.update_extract_progress)
            if success:
                self.root.after(0, lambda: messagebox.showinfo("Success", "ZIP file extracted successfully!"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to extract ZIP file."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error extracting ZIP: {str(e)}"))
            
    def start_add_to_zip(self):
        """Start adding file to ZIP in a separate thread"""
        zip_path = self.add_zip_path.get()
        file_path = self.add_file_path.get()
        
        if not zip_path:
            messagebox.showerror("Error", "Please specify a ZIP file.")
            return
            
        if not file_path:
            messagebox.showerror("Error", "Please specify a file to add.")
            return
            
        # Start in separate thread
        thread = threading.Thread(target=self.add_to_zip_thread, args=(zip_path, file_path))
        thread.daemon = True
        thread.start()
        
    def add_to_zip_thread(self, zip_path, file_path):
        """Thread function for adding file to ZIP"""
        try:
            success = add_to_zip(zip_path, file_path, self.update_add_progress)
            if success:
                self.root.after(0, lambda: messagebox.showinfo("Success", "File added to ZIP successfully!"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to add file to ZIP."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error adding to ZIP: {str(e)}"))
            
    def list_zip_contents(self):
        """List contents of ZIP file"""
        zip_path = self.list_zip_path.get()
        
        if not zip_path:
            messagebox.showerror("Error", "Please specify a ZIP file.")
            return
            
        # Clear listbox
        self.contents_listbox.delete(0, tk.END)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                for info in zipf.filelist:
                    display_text = f"{info.filename:<40} {info.file_size:>10} bytes"
                    self.contents_listbox.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading ZIP file: {str(e)}")


def main():
    root = tk.Tk()
    app = ZipGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()