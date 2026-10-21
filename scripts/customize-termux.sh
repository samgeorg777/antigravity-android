#!/usr/bin/env bash
set -e

TERMUX_DIR="${1:-./termux-src}"
PREBUNDLE="${2:-false}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Customizing Termux for Antigravity CLI ==="
echo "Target directory: $TERMUX_DIR"
echo "Prebundle engine: $PREBUNDLE"

if [ ! -d "$TERMUX_DIR" ]; then
    echo "Error: Directory $TERMUX_DIR does not exist!"
    exit 1
fi

# 1. Update App Name
STRINGS_XML="$TERMUX_DIR/app/src/main/res/values/strings.xml"
if [ -f "$STRINGS_XML" ]; then
    echo "[*] Updating app name to 'Antigravity CLI'..."
    sed -i 's/<string name="app_name">Termux<\/string>/<string name="app_name">Antigravity CLI<\/string>/g' "$STRINGS_XML"
fi

# 2. Prepare directory for bootstrap archives
CPP_DIR="$TERMUX_DIR/app/src/main/cpp"
mkdir -p "$CPP_DIR"

# 3. Download official aarch64 bootstrap to inject hooks
BOOTSTRAP_VER="2026.02.12-r1%2Bapt.android-7"
BOOTSTRAP_URL="https://github.com/termux/termux-packages/releases/download/bootstrap-${BOOTSTRAP_VER}/bootstrap-aarch64.zip"

echo "[*] Fetching base bootstrap archive for aarch64..."
TMP_WORK=$(mktemp -d)
curl -fsSL -o "$TMP_WORK/bootstrap-aarch64.zip" "$BOOTSTRAP_URL"

# Extract and prepare injection
mkdir -p "$TMP_WORK/extracted/etc/profile.d"
mkdir -p "$TMP_WORK/extracted/bin"

# Copy the autostart hook
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
echo "[*] Injecting Antigravity hooks into bootstrap archive..."
(
    cd "$TMP_WORK/extracted"
    zip -r "$TMP_WORK/bootstrap-aarch64.zip" .
)

# Place custom bootstrap in Termux cpp folder
cp "$TMP_WORK/bootstrap-aarch64.zip" "$CPP_DIR/bootstrap-aarch64.zip"

# Download dummy/minimal bootstraps for other architectures (or standard ones)
for arch in arm i686 x86_64; do
    if [ ! -f "$CPP_DIR/bootstrap-${arch}.zip" ]; then
        echo "[*] Fetching upstream bootstrap for $arch..."
        curl -fsSL -o "$CPP_DIR/bootstrap-${arch}.zip" \
          "https://github.com/termux/termux-packages/releases/download/bootstrap-${BOOTSTRAP_VER}/bootstrap-${arch}.zip"
    fi
done

# Clean up temporary work folder
rm -rf "$TMP_WORK"

# 4. Patch app/build.gradle to bypass downloadBootstraps and keep our custom files
BUILD_GRADLE="$TERMUX_DIR/app/build.gradle"
echo "[*] Patching $BUILD_GRADLE to preserve custom bootstraps..."
sed -i 's/def downloadBootstrap(arch, expectedChecksum, version) {/def downloadBootstrap(arch, expectedChecksum, version) { return; /g' "$BUILD_GRADLE"

# 5. Disable uncompressed native libs check to ensure smooth packaging
echo "android.bundle.enableUncompressedNativeLibs=false" >> "$TERMUX_DIR/gradle.properties"

echo "=== Customization complete! Ready to compile. ==="
