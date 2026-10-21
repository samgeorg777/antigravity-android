#!/usr/bin/env bash
set -e

TERMUX_DIR="${1:-./termux-src}"
PREBUNDLE="${2:-false}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NEW_PKG="com.agycli"

echo "=== Customizing Termux for Antigravity CLI ==="
echo "Target directory: $TERMUX_DIR"
echo "Package name:     $NEW_PKG"
echo "Prebundle engine: $PREBUNDLE"

if [ ! -d "$TERMUX_DIR" ]; then
    echo "Error: Directory $TERMUX_DIR does not exist!"
    exit 1
fi

# 1. Update App Name & Package Entity in app strings.xml
APP_STRINGS="$TERMUX_DIR/app/src/main/res/values/strings.xml"
if [ -f "$APP_STRINGS" ]; then
    echo "[*] Updating app name and package entity in app/strings.xml..."
    sed -i 's/<string name="app_name">Termux<\/string>/<string name="app_name">Antigravity CLI<\/string>/g' "$APP_STRINGS"
    sed -i "s/<!ENTITY TERMUX_PACKAGE_NAME \"com.termux\">/<!ENTITY TERMUX_PACKAGE_NAME \"$NEW_PKG\">/g" "$APP_STRINGS"
fi

# 2. Update termux-shared strings.xml
SHARED_STRINGS="$TERMUX_DIR/termux-shared/src/main/res/values/strings.xml"
if [ -f "$SHARED_STRINGS" ]; then
    echo "[*] Updating package entities in termux-shared/strings.xml..."
    sed -i "s/<!ENTITY TERMUX_PACKAGE_NAME \"com.termux\">/<!ENTITY TERMUX_PACKAGE_NAME \"$NEW_PKG\">/g" "$SHARED_STRINGS"
    sed -i "s/<!ENTITY TERMUX_PREFIX_DIR_PATH \"\/data\/data\/com.termux\/files\/usr\">/<!ENTITY TERMUX_PREFIX_DIR_PATH \"\/data\/data\/$NEW_PKG\/files\/usr\">/g" "$SHARED_STRINGS"
fi

# 3. Update TermuxConstants.java
CONSTANTS_JAVA="$TERMUX_DIR/termux-shared/src/main/java/com/termux/shared/termux/TermuxConstants.java"
if [ -f "$CONSTANTS_JAVA" ]; then
    echo "[*] Setting TERMUX_PACKAGE_NAME to '$NEW_PKG' in TermuxConstants.java..."
    sed -i "s/public static final String TERMUX_PACKAGE_NAME = \"com.termux\";/public static final String TERMUX_PACKAGE_NAME = \"$NEW_PKG\";/g" "$CONSTANTS_JAVA"
fi

# 4. Update shortcuts.xml
SHORTCUTS_XML="$TERMUX_DIR/app/src/main/res/xml/shortcuts.xml"
if [ -f "$SHORTCUTS_XML" ]; then
    echo "[*] Updating targetPackage in shortcuts.xml..."
    sed -i "s/targetPackage=\"com.termux\"/targetPackage=\"$NEW_PKG\"/g" "$SHORTCUTS_XML"
fi

# 5. Update app/build.gradle (applicationId and manifestPlaceholders)
BUILD_GRADLE="$TERMUX_DIR/app/build.gradle"
echo "[*] Configuring applicationId and manifestPlaceholders in app/build.gradle..."
sed -i "s/manifestPlaceholders.TERMUX_PACKAGE_NAME = \"com.termux\"/manifestPlaceholders.TERMUX_PACKAGE_NAME = \"$NEW_PKG\"\n        applicationId \"$NEW_PKG\"/g" "$BUILD_GRADLE"
sed -i 's/manifestPlaceholders.TERMUX_APP_NAME = "Termux"/manifestPlaceholders.TERMUX_APP_NAME = "Antigravity CLI"/g' "$BUILD_GRADLE"

# 6. Prepare directory for bootstrap archives
CPP_DIR="$TERMUX_DIR/app/src/main/cpp"
mkdir -p "$CPP_DIR"

# 7. Download and patch base bootstrap archive for aarch64
BOOTSTRAP_VER="2026.02.12-r1%2Bapt.android-7"
BOOTSTRAP_URL="https://github.com/termux/termux-packages/releases/download/bootstrap-${BOOTSTRAP_VER}/bootstrap-aarch64.zip"

echo "[*] Fetching base bootstrap archive for aarch64..."
TMP_WORK=$(mktemp -d)
curl -fsSL -o "$TMP_WORK/bootstrap-aarch64.zip" "$BOOTSTRAP_URL"

# Patch binary package references in aarch64 bootstrap (com.termux -> com.agycli)
echo "[*] Patching binary paths in bootstrap archive..."
python3 "$SCRIPT_DIR/patch_bootstrap.py" "$TMP_WORK/bootstrap-aarch64.zip" "$TMP_WORK/bootstrap-patched.zip"
mv "$TMP_WORK/bootstrap-patched.zip" "$TMP_WORK/bootstrap-aarch64.zip"

# Extract and prepare injection of autostart hook
mkdir -p "$TMP_WORK/extracted/etc/profile.d"
mkdir -p "$TMP_WORK/extracted/bin"

cp "$SCRIPT_DIR/antigravity-autostart.sh" "$TMP_WORK/extracted/etc/profile.d/00-antigravity.sh"
chmod 755 "$TMP_WORK/extracted/etc/profile.d/00-antigravity.sh"

# Pre-bundle engine if requested
if [ "$PREBUNDLE" = "true" ]; then
    echo "[*] Downloading and pre-bundling Antigravity engine into APK..."
    curl -fsSL -o "$TMP_WORK/antigravity.tar.gz" \
      "https://github.com/wallentx/antigravity-cli-termux/releases/latest/download/antigravity-termux-standalone.tar.gz"
    tar -xzf "$TMP_WORK/antigravity.tar.gz" -C "$TMP_WORK/extracted/bin" agy agy.va39
    chmod 755 "$TMP_WORK/extracted/bin/agy"*
    touch "$TMP_WORK/extracted/home/.antigravity_installed"
fi

# Inject modified files into bootstrap-aarch64.zip
echo "[*] Injecting Antigravity hooks into bootstrap-aarch64.zip..."
(
    cd "$TMP_WORK/extracted"
    zip -r "$TMP_WORK/bootstrap-aarch64.zip" .
)

cp "$TMP_WORK/bootstrap-aarch64.zip" "$CPP_DIR/bootstrap-aarch64.zip"

# Download and patch upstream bootstraps for other architectures
for arch in arm i686 x86_64; do
    if [ ! -f "$CPP_DIR/bootstrap-${arch}.zip" ]; then
        echo "[*] Fetching and patching upstream bootstrap for $arch..."
        curl -fsSL -o "$TMP_WORK/bootstrap-${arch}.zip" \
          "https://github.com/termux/termux-packages/releases/download/bootstrap-${BOOTSTRAP_VER}/bootstrap-${arch}.zip"
        python3 "$SCRIPT_DIR/patch_bootstrap.py" "$TMP_WORK/bootstrap-${arch}.zip" "$CPP_DIR/bootstrap-${arch}.zip"
    fi
done

# Clean up temporary work folder
rm -rf "$TMP_WORK"

# 8. Patch app/build.gradle to preserve custom bootstraps
echo "[*] Patching $BUILD_GRADLE to preserve custom bootstraps..."
sed -i 's/def downloadBootstrap(arch, expectedChecksum, version) {/def downloadBootstrap(arch, expectedChecksum, version) { return; /g' "$BUILD_GRADLE"

echo "=== Customization complete! Ready to compile as '$NEW_PKG'. ==="
