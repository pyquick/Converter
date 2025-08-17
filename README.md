# PNG to ICNS Converter

This script converts PNG images to ICNS format, which is used for macOS icons.

## Requirements

- Python 3.11, 3.12, or 3.13 (recommended)
- PIL (Pillow) library

Install Pillow with:
```
pip install Pillow
```

## Usage

### Command Line Version

Basic usage:
```
python3 support/convert.py input.png output.icns
```

Advanced usage with size options:
```
python3 support/convert.py input.png output.icns --min-size 16 --max-size 512
```

### GUI Version

For a graphical interface, run:
```
python3 gui_converter.py
```

## Building a Standalone Application

To compile the application into a macOS .app bundle, run:
```
./build.command
```

This will create a standalone application in the `dist` folder using Nuitka with Python 3.13.

**Note:** The build script is specifically designed to work with Python 3.13 to avoid compatibility issues.

### Requirements for Building

- Python 3.13
- Nuitka
- Pillow

Install build requirements:
```
python3.13 -m pip install Pillow nuitka
```

The build script will automatically:
1. Download ccache to avoid SSL certificate issues
2. Use Python 3.13 for compilation
3. Create a standalone .app bundle

## Alternative: Simple Launcher Script

If you cannot build the application with Nuitka, you can use the provided launcher script:
```
./PNG_to_ICNS_Converter.command
```

This script will run the application directly with Python without requiring compilation.

## Options

- `--min-size`: Minimum icon size (default: 16)
- `--max-size`: Maximum icon size (default: auto-detected from image)

## Features

- Automatically generates multiple icon sizes from the original image
- Supports retina (2x) versions for common sizes
- Crops non-square images to square format
- Automatically detects image size and uses it as maximum icon size
- GUI interface for easier use with image preview
- Progress indication during conversion
- Automatic opening of the result in Preview app

## Example

To convert a 256x256 PNG image to ICNS with default settings:
```
python3 support/convert.py icon.png icon.icns
```

This will generate icons in sizes: 16x16, 32x32, 64x64, 128x128, and 256x256, including retina versions where appropriate.

To use the GUI version:
```
python3 gui_converter.py
```

The GUI provides a user-friendly interface with:
- File browsing for input and output files
- Preview of the source image
- Image information display (dimensions)
- Customizable minimum and maximum icon sizes
- Auto-detect maximum size button
- Progress indication during conversion
- Status bar showing current operation

When using the GUI, the maximum icon size is automatically set to match the smaller dimension of the source image when you select an input file.

To build a standalone macOS application, run:
```
./build.command
```

This will create a .app bundle in the dist folder that can be run without requiring Python to be installed.

If you encounter issues with the build process, you can use the simple launcher script instead:
```
./PNG_to_ICNS_Converter.command
```

Or run directly with Python 3.13:
```
python3.13 gui_converter.py
```