#!/usr/bin/env python3

"""
PNG to ICNS Converter

This script converts PNG images to ICNS format, which is used for macOS icons.
It requires PIL (Pillow) library and supports customizable size ranges.

Usage:
    python3 convert.py input.png output.icns [--min-size SIZE] [--max-size SIZE]
"""

import sys
import os
import argparse
import tempfile
import shutil
import subprocess
from PIL import Image

def create_icns(png_path, icns_path, min_size=16, max_size=None):
    """
    Convert a PNG image to ICNS format using iconset method.
    
    Args:
        png_path (str): Path to the input PNG file
        icns_path (str): Path for the output ICNS file
        min_size (int): Minimum size for the icon (default: 16)
        max_size (int): Maximum size for the icon (default: original image size)
    """
    # Open the source image
    img = Image.open(png_path)
    
    # Determine max size if not provided
    if max_size is None:
        max_size = min(img.width, img.height)
    
    # Ensure the image is square
    if img.width != img.height:
        print("Warning: Image is not square. Cropping to square.")
        min_dimension = min(img.width, img.height)
        left = (img.width - min_dimension) // 2
        top = (img.height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension
        img = img.crop((left, top, right, bottom))
    
    # Create a temporary directory for iconset
    with tempfile.TemporaryDirectory() as tmp_dir:
        iconset_dir = os.path.join(tmp_dir, "iconset.iconset")
        os.makedirs(iconset_dir)
        
        # Define standard sizes for ICNS (based on Apple's specifications)
        standard_sizes = [16, 32, 64, 128, 256, 512, 1024]
        
        # Generate icons for standard sizes within our range
        generated_sizes = []
        for size in standard_sizes:
            if min_size <= size <= max_size:
                # Create a copy of the image and resize it
                resized_img = img.copy().resize((size, size), Image.LANCZOS)
                
                # Save as PNG in iconset directory
                filename = f"icon_{size}x{size}.png"
                resized_img.save(os.path.join(iconset_dir, filename), "PNG")
                generated_sizes.append(size)
                print(f"Generated size: {size}x{size}")
                
                # For specific sizes, also generate retina versions
                retina_pairs = {16: 32, 32: 64, 128: 256, 256: 512, 512: 1024}
                if size in retina_pairs and retina_pairs[size] <= max_size:
                    retina_size = retina_pairs[size]
                    retina_img = img.copy().resize((retina_size, retina_size), Image.LANCZOS)
                    retina_filename = f"icon_{size}x{size}@2x.png"
                    retina_img.save(os.path.join(iconset_dir, retina_filename), "PNG")
                    generated_sizes.append(retina_size)
                    print(f"Generated retina size: {retina_size}x{retina_size}")
        
        # Make sure we include max_size if it's not already included
        if max_size not in generated_sizes:
            resized_img = img.copy().resize((max_size, max_size), Image.LANCZOS)
            filename = f"icon_{max_size}x{max_size}.png"
            resized_img.save(os.path.join(iconset_dir, filename), "PNG")
            generated_sizes.append(max_size)
            print(f"Generated max size: {max_size}x{max_size}")
        
        # Use iconutil to create ICNS file (macOS only)
        try:
            subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], check=True)
            print(f"Successfully converted {png_path} to {icns_path}")
            print(f"Generated sizes: {sorted(set(generated_sizes))}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating ICNS with iconutil: {e}")
            print("Falling back to Pillow method...")
            # Fallback to Pillow method if iconutil fails
            fallback_method(iconset_dir, icns_path)

def fallback_method(iconset_dir, icns_path):
    """
    Fallback method using Pillow if iconutil is not available
    """
    icon_files = os.listdir(iconset_dir)
    if not icon_files:
        print("No icons generated, cannot create ICNS file")
        return
        
    # Find the largest icon file to use as main image
    icon_paths = [os.path.join(iconset_dir, f) for f in icon_files]
    largest_icon = max(icon_paths, key=lambda p: Image.open(p).size[0])
    
    # Open the largest icon as main image
    main_img = Image.open(largest_icon)
    
    # Create list of additional images
    append_images = []
    for icon_path in icon_paths:
        if icon_path != largest_icon:
            append_images.append(Image.open(icon_path))
    
    # Save as ICNS
    if append_images:
        main_img.save(
            icns_path,
            format='ICNS',
            append_images=append_images
        )
    else:
        main_img.save(icns_path, format='ICNS')
    
    print(f"Successfully converted using fallback method to {icns_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert PNG to ICNS format")
    parser.add_argument("input", help="Input PNG file path")
    parser.add_argument("output", help="Output ICNS file path")
    parser.add_argument("--min-size", type=int, default=16, help="Minimum icon size (default: 16)")
    parser.add_argument("--max-size", type=int, help="Maximum icon size (default: original image size)")
    
    args = parser.parse_args()
    
    png_path = args.input
    icns_path = args.output
    
    # Check if input file exists
    if not os.path.exists(png_path):
        print(f"Error: Input file '{png_path}' does not exist.")
        sys.exit(1)
    
    # Check if input file is a PNG
    if not png_path.lower().endswith('.png'):
        print("Error: Input file must be a PNG image.")
        sys.exit(1)
    
    try:
        create_icns(png_path, icns_path, args.min_size, args.max_size)
    except Exception as e:
        print(f"Error converting image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()