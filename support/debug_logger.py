#!/usr/bin/env python3
"""
Debug logger module for Converter application
Handles debug mode logging to ~/.converter/log folder
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from PySide6.QtCore import QSettings
import datetime
import traceback

class DebugLogger:
    def __init__(self):
        self.logger = None
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.debug_enabled = False
        self.setup_logger()
    
    def setup_logger(self):
        """Setup logger with rotating file handler"""
        # Get debug setting
        settings = QSettings("MyCompany", "ConverterApp")
        self.debug_enabled = settings.value("debug_enabled", False, type=bool)
        
        if not self.debug_enabled:
            return
        
        # Create log directory
        log_dir = os.path.expanduser("~/.converter/log")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("converter")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create rotating file handler
        log_file = os.path.join(log_dir, f"converter_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
        # Redirect stdout and stderr
        self._redirect_output()
        
        self.logger.info("Debug logger initialized")
        self.logger.info(f"Log file: {log_file}")
    
    def _redirect_output(self):
        """Redirect stdout and stderr to logger with enhanced output"""
        class EnhancedLoggerWriter:
            def __init__(self, logger, level, original_stream):
                self.logger = logger
                self.level = level
                self.original_stream = original_stream
            
            def write(self, message):
                if message.strip():
                    # Enhanced debug output with timestamp and module info
                    import inspect
                    import os
                    
                    # Get caller frame information
                    frame = inspect.currentframe()
                    try:
                        # Walk up the call stack to find the actual module
                        for i in range(6):  # Look up to 6 frames
                            if frame is None:
                                break
                            frame = frame.f_back
                            if frame is None:
                                break
                            
                            module_name = frame.f_globals.get('__name__', '')
                            file_path = frame.f_code.co_filename
                            
                            # Filter out internal modules
                            if (module_name and 
                                not module_name.startswith('PySide6') and
                                not module_name.startswith('logging') and
                                not module_name.startswith('debug_logger')):
                                
                                # Extract filename from path
                                filename = os.path.basename(file_path)
                                if filename.endswith('.py'):
                                    filename = filename[:-3]
                                
                                # Enhanced log message
                                enhanced_message = f"[{filename}] {message.strip()}"
                                self.logger.log(self.level, enhanced_message)
                                
                                # Also write to original stream for immediate feedback
                                self.original_stream.write(f"DEBUG: {enhanced_message}\n")
                                self.original_stream.flush()
                                return
                        
                        # Fallback: log without module info
                        self.logger.log(self.level, message.strip())
                        self.original_stream.write(f"DEBUG: {message.strip()}\n")
                        self.original_stream.flush()
                        
                    finally:
                        del frame
            
            def flush(self):
                self.original_stream.flush()
            
            def reconfigure(self, **kwargs):
                """Handle reconfigure method calls to avoid AttributeError"""
                # Ignore reconfigure calls to prevent errors
                pass
        
        if self.logger:
            sys.stdout = EnhancedLoggerWriter(self.logger, logging.INFO, self.original_stdout)
            sys.stderr = EnhancedLoggerWriter(self.logger, logging.ERROR, self.original_stderr)
    
    def restore_output(self):
        """Restore original stdout and stderr"""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
    
    def log_debug(self, message):
        """Log debug message with enhanced output"""
        if self.debug_enabled and self.logger:
            import inspect
            import os
            
            # Get caller information for enhanced logging
            frame = inspect.currentframe()
            if frame:
                frame = frame.f_back
            
            if frame:
                module_name = frame.f_globals.get('__name__', '')
                file_path = frame.f_code.co_filename
                
                # Extract filename
                filename = os.path.basename(file_path)
                if filename.endswith('.py'):
                    filename = filename[:-3]
                
                enhanced_message = f"[{filename}] {message}"
                self.logger.debug(enhanced_message)
                
                # Also print to console for immediate feedback
                self.original_stdout.write(f"DEBUG: {enhanced_message}\n")
                self.original_stdout.flush()
            else:
                # Fallback without frame info
                self.logger.debug(message)
                self.original_stdout.write(f"DEBUG: {message}\n")
                self.original_stdout.flush()
        else:
            # Normal print when debug is disabled
            print(f"DEBUG: {message}")
    
    def log_info(self, message):
        """Log info message with enhanced output"""
        if self.debug_enabled and self.logger:
            import inspect
            import os
            
            # Get caller information for enhanced logging
            frame = inspect.currentframe()
            if frame:
                frame = frame.f_back
            
            if frame:
                module_name = frame.f_globals.get('__name__', '')
                file_path = frame.f_code.co_filename
                
                # Extract filename
                filename = os.path.basename(file_path)
                if filename.endswith('.py'):
                    filename = filename[:-3]
                
                enhanced_message = f"[{filename}] {message}"
                self.logger.info(enhanced_message)
                
                # Also print to console for immediate feedback
                self.original_stdout.write(f"INFO: {enhanced_message}\n")
                self.original_stdout.flush()
            else:
                # Fallback without frame info
                self.logger.info(message)
                self.original_stdout.write(f"INFO: {message}\n")
                self.original_stdout.flush()
        else:
            # Normal print when debug is disabled
            print(f"INFO: {message}")
    
    def log_warning(self, message):
        """Log warning message"""
        if self.debug_enabled and self.logger:
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")
    
    def log_error(self, message):
        """Log error message"""
        if self.debug_enabled and self.logger:
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")
    
    def log_exception(self, message):
        """Log exception with traceback"""
        if self.debug_enabled and self.logger:
            self.logger.error(f"{message}\n{traceback.format_exc()}")
        else:
            print(f"EXCEPTION: {message}")
            traceback.print_exc()
    
    def is_debug_enabled(self):
        """Check if debug mode is enabled"""
        return self.debug_enabled

# Global debug logger instance
debug_logger = DebugLogger()

def debug_log(message):
    """Convenience function for debug logging"""
    debug_logger.log_debug(message)

def info_log(message):
    """Convenience function for info logging"""
    debug_logger.log_info(message)

def warning_log(message):
    """Convenience function for warning logging"""
    debug_logger.log_warning(message)

def error_log(message):
    """Convenience function for error logging"""
    debug_logger.log_error(message)

def exception_log(message):
    """Convenience function for exception logging"""
    debug_logger.log_exception(message)