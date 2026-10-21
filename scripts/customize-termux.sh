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

# 4. Update TermuxInstaller.java to grant executable permission to glibc/ files
INSTALLER_JAVA="$TERMUX_DIR/app/src/main/java/com/termux/app/TermuxInstaller.java"
if [ -f "$INSTALLER_JAVA" ]; then
    echo "[*] Updating TermuxInstaller.java to set permissions on glibc/..."
    sed -i 's/zipEntryName.startsWith("bin\/") ||/zipEntryName.startsWith("bin\/") || zipEntryName.startsWith("glibc\/") ||/g' "$INSTALLER_JAVA"
fi

# 5. Update shortcuts.xml
SHORTCUTS_XML="$TERMUX_DIR/app/src/main/res/xml/shortcuts.xml"
if [ -f "$SHORTCUTS_XML" ]; then
    echo "[*] Updating targetPackage in shortcuts.xml..."
    sed -i "s/targetPackage=\"com.termux\"/targetPackage=\"$NEW_PKG\"/g" "$SHORTCUTS_XML"
fi

# 6. Patch app/build.gradle using Python helper
python3 "$SCRIPT_DIR/patch_gradle.py" "$TERMUX_DIR/app/build.gradle"

# 6.1 Patch Termux UI features (Clickable URLs, Drag & Drop, Image/File Insert)
python3 "$SCRIPT_DIR/patch_termux_features.py" "$TERMUX_DIR"

# 6.2 Apply Antigravity branding, themes, animations, and vector icons
python3 "$SCRIPT_DIR/apply_antigravity_theme.py" "$TERMUX_DIR"

# 6.3 Generate launcher icons for all screen densities
python3 "$SCRIPT_DIR/generate_png_icons.py" "$TERMUX_DIR"

# 7. Prepare directory for bootstrap archives
CPP_DIR="$TERMUX_DIR/app/src/main/cpp"
mkdir -p "$CPP_DIR"

# 8. Download base bootstrap archive for aarch64
BOOTSTRAP_VER="2026.02.12-r1%2Bapt.android-7"
BOOTSTRAP_URL="https://github.com/termux/termux-packages/releases/download/bootstrap-${BOOTSTRAP_VER}/bootstrap-aarch64.zip"

echo "[*] Fetching base bootstrap archive for aarch64..."
TMP_WORK=$(mktemp -d)
curl -fsSL -o "$TMP_WORK/bootstrap-aarch64.zip" "$BOOTSTRAP_URL"

# Extract base bootstrap
mkdir -p "$TMP_WORK/extracted"
unzip -q "$TMP_WORK/bootstrap-aarch64.zip" -d "$TMP_WORK/extracted"

# Inject glibc into the bootstrap rootfs
echo "[*] Injecting glibc into bootstrap rootfs..."
python3 "$SCRIPT_DIR/inject_glibc.py" "$TMP_WORK/extracted"

# Inject autostart hook and Antigravity color theme
mkdir -p "$TMP_WORK/extracted/etc/profile.d" "$TMP_WORK/extracted/home/.termux"
cp "$SCRIPT_DIR/antigravity-autostart.sh" "$TMP_WORK/extracted/etc/profile.d/00-antigravity.sh"
chmod 755 "$TMP_WORK/extracted/etc/profile.d/00-antigravity.sh"

# Inject agy-device autonomous device controller tool
cp "$SCRIPT_DIR/agy-device" "$TMP_WORK/extracted/bin/agy-device"
chmod 755 "$TMP_WORK/extracted/bin/agy-device"
ln -sf agy-device "$TMP_WORK/extracted/bin/device"
ln -sf agy-device "$TMP_WORK/extracted/bin/control"

cat << 'EOF' > "$TMP_WORK/extracted/home/.termux/colors.properties"
background=#0B0F19
foreground=#E2E8F0
cursor=#00F0FF

color0=#151B28
color1=#FF5370
color2=#22C55E
color3=#FFD166
color4=#38BDF8
color5=#C084FC
color6=#00F0FF
color7=#E2E8F0

color8=#475569
color9=#FF6E8A
color10=#4ADE80
color11=#FDE047
color12=#60A5FA
color13=#D8B4FE
color14=#67E8F9
color15=#FFFFFF
EOF

# Pre-bundle engine if requested
if [ "$PREBUNDLE" = "true" ]; then
    echo "[*] Downloading and pre-bundling Antigravity engine into APK..."
    curl -fsSL -o "$TMP_WORK/antigravity.tar.gz" \
      "https://github.com/wallentx/antigravity-cli-termux/releases/latest/download/antigravity-termux-standalone.tar.gz"
    tar -xzf "$TMP_WORK/antigravity.tar.gz" -C "$TMP_WORK/extracted/bin" agy agy.va39
    chmod 755 "$TMP_WORK/extracted/bin/agy"*
    touch "$TMP_WORK/extracted/home/.antigravity_installed"
fi

# Re-zip the combined rootfs
echo "[*] Creating unpatched bootstrap archive..."
(
    cd "$TMP_WORK/extracted"
    zip -r -q "$TMP_WORK/bootstrap-unpatched.zip" .
)

# Patch binary package references in combined bootstrap (com.termux -> com.agycli)
echo "[*] Patching binary paths in bootstrap archive..."
python3 "$SCRIPT_DIR/patch_bootstrap.py" "$TMP_WORK/bootstrap-unpatched.zip" "$CPP_DIR/bootstrap-aarch64.zip"

# Verify that the bootstrap is properly patched and includes glibc
python3 -c "
import zipfile
zf = zipfile.ZipFile('$CPP_DIR/bootstrap-aarch64.zip')
namelist = zf.namelist()
assert 'glibc/lib/ld-linux-aarch64.so.1' in namelist, 'Verification failed: glibc loader missing from bootstrap!'
assert 'glibc/etc/hosts' in namelist, 'Verification failed: glibc/etc/hosts missing!'
assert 'glibc/etc/resolv.conf' in namelist, 'Verification failed: glibc/etc/resolv.conf missing!'
login = zf.read('bin/login')
assert b'$NEW_PKG' in login, 'Verification failed: $NEW_PKG not found in bin/login'
assert b'com.termux' not in login, 'Verification failed: com.termux still in bin/login'
print('[✓] Verification passed: glibc and bin/login are correctly packaged for $NEW_PKG')
"

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

echo "=== Customization complete! Ready to compile as '$NEW_PKG'. ==="
