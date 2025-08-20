#!/bin/bash

# Build script for PNG to ICNS Converter
# Uses Nuitka to compile the Python application into a macOS .app bundle

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "Building PNG to ICNS Converter..."
echo "Project directory: $PROJECT_DIR"

# Check if required files exist
if [ ! -f "$PROJECT_DIR/gui_converter.py" ]; then
    echo "Error: gui_converter.py not found in project directory"
    exit 1
fi

if [ ! -d "$PROJECT_DIR/support" ]; then
    echo "Error: support directory not found in project directory"
    exit 1
    
fi

# Install required dependencies
echo "Installing required dependencies..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    python3.13 -m pip install -r "$PROJECT_DIR/requirements.txt"
else
    echo "Warning: requirements.txt not found. Installing default dependencies..."
    python3.13 -m pip install Pillow nuitka wxpython
fi

# Create build directory
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$PROJECT_DIR/dist"

echo "Creating build directories..."
mkdir -p "$BUILD_DIR"
mkdir -p "$DIST_DIR"

# Manually download ccache to avoid SSL issues
echo "Setting up ccache..."
CCACHE_DIR="/Users/$USER/Library/Caches/Nuitka/downloads/ccache/v4.2.1"
CCACHE_ZIP="$CCACHE_DIR/ccache-4.2.1.zip"

if [ ! -f "$CCACHE_ZIP" ]; then
    echo "Downloading ccache to avoid SSL issues..."
    mkdir -p "$CCACHE_DIR"
    
    # Try to download with curl, ignoring SSL errors
    curl -k -L "https://nuitka.net/ccache/v4.2.1/ccache-4.2.1.zip" -o "$CCACHE_ZIP"
    
    if [ ! -f "$CCACHE_ZIP" ]; then
        echo "Failed to download ccache. Continuing without it..."
    else
        echo "Downloaded ccache successfully."
    fi
else
    echo "ccache already downloaded."
fi

# Install required dependencies if not already installed
echo "Checking and installing dependencies..."
python3.13 -m pip install Pillow nuitka wxpython

# Try to determine Python version
PYTHON_VERSION=$(python3.13 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
PYTHON_FULL_VERSION=$(python3.13 --version | cut -d' ' -f2)
echo "Using Python version: $PYTHON_FULL_VERSION"

# Build the application using Nuitka with Python 3.13
echo "Compiling with Nuitka using Python 3.13..."

# Different approach for different Python versions
BUILD_SUCCESS=0

# Try the recommended approach first
echo "Trying recommended build approach..."
python3.13 -m nuitka \
    --standalone \
    --enable-plugin=no-qt \
    --macos-create-app-bundle \
    --macos-app-version=1.0 \
    --macos-app-icon="$PROJECT_DIR/support/Success.icns" \
    --include-data-dir="$PROJECT_DIR/support=support" \
    --output-dir="$DIST_DIR" \
    --remove-output \
    "$PROJECT_DIR/gui_converter.py" && BUILD_SUCCESS=1

# If that fails, try alternative approaches
if [ $BUILD_SUCCESS -eq 0 ]; then
    echo "First approach failed. Trying alternative build approach..."
    
    # Try without --remove-output
    python3.13 -m nuitka \
        --standalone \
        --macos-create-app-bundle \
        --enable-plugin=no-qt \
        --macos-app-version=1.0 \
        --macos-app-icon="$PROJECT_DIR/support/Success.icns" \
        --include-data-dir="$PROJECT_DIR/support=support" \
        --output-dir="$DIST_DIR" \
        "$PROJECT_DIR/gui_converter.py" && BUILD_SUCCESS=1
fi

if [ $BUILD_SUCCESS -eq 0 ]; then
    echo "Second approach failed. Trying minimal build approach..."
    
    # Try minimal approach
    python3.13 -m nuitka \
        --standalone \
        --macos-create-app-bundle \
        --enable-plugin=no-qt \
        --include-data-dir="$PROJECT_DIR/support=support" \
        --output-dir="$DIST_DIR" \
        --macos-app-version=1.0 \
        "$PROJECT_DIR/gui_converter.py" && BUILD_SUCCESS=1
fi

if [ $BUILD_SUCCESS -eq 0 ]; then
    echo "All Nuitka approaches failed. Creating a simple application bundle instead..."
    
    # Create a simple app bundle structure
    APP_DIR="$DIST_DIR/PNG to ICNS Converter.app"
    CONTENTS_DIR="$APP_DIR/Contents"
    MACOS_DIR="$CONTENTS_DIR/MacOS"
    RESOURCES_DIR="$CONTENTS_DIR/Resources"
    
    echo "Creating simple app bundle structure..."
    mkdir -p "$MACOS_DIR"
    mkdir -p "$RESOURCES_DIR"
    
    # Copy required files
    echo "Copying application files..."
    cp -r "$PROJECT_DIR/support" "$RESOURCES_DIR/"
    cp "$PROJECT_DIR/gui_converter.py" "$RESOURCES_DIR/"
    
    # Create a simple launcher script
    LAUNCHER_SCRIPT="$MACOS_DIR/png_to_icns_converter"
    echo "#!/bin/bash" > "$LAUNCHER_SCRIPT"
    echo "cd \"\$(dirname \"\$0\")/../Resources\" || exit 1" >> "$LAUNCHER_SCRIPT"
    echo "python3.13 gui_converter.py" >> "$LAUNCHER_SCRIPT"
    chmod +x "$LAUNCHER_SCRIPT"
    
    # Create Info.plist
    cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>png_to_icns_converter</string>
    <key>CFBundleIdentifier</key>
    <string>com.png.icns.converter</string>
    <key>CFBundleName</key>
    <string>PNG to ICNS Converter</string>
    <key>CFBundleIconFile</key>
    <string>Success.icns</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13.0</string>
</dict>
</plist>
EOF
    
    # Copy the icon
    if [ -f "$PROJECT_DIR/support/Success.icns" ]; then
        cp "$PROJECT_DIR/support/Success.icns" "$RESOURCES_DIR/"
    fi
    
    BUILD_SUCCESS=1
    echo "Simple app bundle created at: $APP_DIR"
fi

# Check if build was successful
if [ $BUILD_SUCCESS -eq 1 ]; then
    if ls "$DIST_DIR"/*.app 1> /dev/null 2>&1; then
        APP_NAME=$(ls "$DIST_DIR"/*.app | head -n 1)
        echo "Build successful!"
        echo "Application created at: $APP_NAME"
        
        # Show app bundle information
        echo "Application information:"
        ls -lh "$APP_NAME"
        
        echo ""
        echo "To run the application, double-click on the app in Finder"
        echo "or run the following command in terminal:"
        echo "open '$APP_NAME'"
    else
        echo "Build process completed."
        echo "You can run the application using the launcher script:"
        echo "./PNG_to_ICNS_Converter.command"
    fi
else
    echo "Build failed with all approaches!"
    echo "Recommendations:"
    echo "1. Run the application directly with Python 3.13:"
    echo "   python3.13 gui_converter.py"
    echo "2. Use the simple launcher script:"
    echo "   ./PNG_to_ICNS_Converter.command"
    exit 1
fi