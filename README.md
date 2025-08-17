# PNG to ICNS Converter

This script converts PNG images to ICNS format, which is used for macOS icons.

## Requirements

- Python 3
- PIL (Pillow) library

Install Pillow with:
```
pip install Pillow
```

## Usage

Basic usage:
```
python3 convert.py input.png output.icns
```

Advanced usage with size options:
```
python3 convert.py input.png output.icns --min-size 16 --max-size 512
```

### Options

- `--min-size`: Minimum icon size (default: 16)
- `--max-size`: Maximum icon size (default: original image size)

## Features

- Automatically generates multiple icon sizes from the original image
- Supports retina (2x) versions for common sizes
- Crops non-square images to square format
- Generates icons from 16x16 up to the original image size (or specified max size)

## Example

To convert a 256x256 PNG image to ICNS with default settings:
```
python3 convert.py icon.png icon.icns
```

This will generate icons in sizes: 16x16, 32x32, 64x64, 128x128, and 256x256, including retina versions where appropriate.