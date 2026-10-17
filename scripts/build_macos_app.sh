#!/bin/bash
set -e

PROJECT_DIR="/Users/efekoc/.gemini/antigravity/scratch/youtube-shorts-automation"
APP_NAME="Flow Studio.app"
APP_BUNDLE="$PROJECT_DIR/$APP_NAME"
DESKTOP_DIR="/Users/efekoc/Desktop"

echo "=== Building $APP_NAME for macOS ==="

# Clean old bundle if exists
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# 1. Copy AppIcon.icns
cp "$PROJECT_DIR/AppIcon.icns" "$APP_BUNDLE/Contents/Resources/AppIcon.icns"

# 2. Write Info.plist
cat << 'PLIST' > "$APP_BUNDLE/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>tr</string>
    <key>CFBundleDisplayName</key>
    <string>Flow Studio</string>
    <key>CFBundleExecutable</key>
    <string>FlowStudio</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.efekoc.flowstudio</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Flow Studio</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>2.5.0</string>
    <key>CFBundleVersion</key>
    <string>250</string>
    <key>LSMinimumSystemVersion</key>
    <string>12.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>
PLIST

# 3. Write executable launcher
cat << 'LAUNCHER' > "$APP_BUNDLE/Contents/MacOS/FlowStudio"
#!/bin/bash
PROJECT_DIR="/Users/efekoc/.gemini/antigravity/scratch/youtube-shorts-automation"
cd "$PROJECT_DIR" || exit 1

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

exec "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/run_desktop.py"
LAUNCHER

chmod +x "$APP_BUNDLE/Contents/MacOS/FlowStudio"

# Lint plist
plutil -lint "$APP_BUNDLE/Contents/Info.plist"

# Copy to Desktop
echo "Copying to $DESKTOP_DIR/$APP_NAME..."
rm -rf "$DESKTOP_DIR/$APP_NAME"
cp -R "$APP_BUNDLE" "$DESKTOP_DIR/$APP_NAME"

# Also copy or link to ~/Applications if exists
USER_APPS="/Users/efekoc/Applications"
if [ -d "$USER_APPS" ]; then
    rm -rf "$USER_APPS/$APP_NAME"
    cp -R "$APP_BUNDLE" "$USER_APPS/$APP_NAME"
    echo "Copied to $USER_APPS/$APP_NAME"
fi

# Touch to refresh Finder icon cache
touch "$DESKTOP_DIR/$APP_NAME"

echo "=== Build Complete! Flow Studio.app is now on your Desktop! ==="
