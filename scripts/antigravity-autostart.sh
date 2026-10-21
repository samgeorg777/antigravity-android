#!/data/data/com.agycli/files/usr/bin/bash
# Antigravity CLI Auto-Start and Zero-Setup Bootstrapper for Android

# Only run in interactive terminal sessions
if [ ! -t 1 ]; then
    return 0 2>/dev/null || exit 0
fi

# Prevent multiple nested runs
if [ -n "$AGY_ACTIVE_SESSION" ]; then
    return 0 2>/dev/null || exit 0
fi
export AGY_ACTIVE_SESSION=1

# Check if Antigravity CLI is already installed
if [ ! -x "$PREFIX/bin/agy" ] || [ ! -x "$PREFIX/bin/agy.va39" ]; then
    clear
    cat << 'EOF'
  ╔══════════════════════════════════════════════════════════════╗
  ║                 Antigravity CLI for Android                 ║
  ╚══════════════════════════════════════════════════════════════╝
EOF
    echo ""
    echo "  [*] First-time automatic setup in progress..."
    echo "  [*] Setting up DNS and runtime environment..."

    # Ensure resolv.conf exists for proper DNS resolution in Android
    mkdir -p "$PREFIX/etc"
    if [ ! -f "$PREFIX/etc/resolv.conf" ]; then
        cat << 'EOF' > "$PREFIX/etc/resolv.conf"
nameserver 8.8.8.8
nameserver 1.1.1.1
EOF
    fi

    # Set up glibc if needed
    if [ ! -d "$PREFIX/glibc" ]; then
        echo "  [*] Installing required glibc support..."
        pkg install -y glibc-repo 2>/dev/null || true
        pkg install -y glibc resolv-conf 2>/dev/null || true
    fi

    echo "  [*] Downloading Antigravity CLI engine..."
    TMP_DIR=$(mktemp -d)
    TAR_URL="https://github.com/wallentx/antigravity-cli-termux/releases/latest/download/antigravity-termux-standalone.tar.gz"

    if curl -fsSL -o "$TMP_DIR/antigravity.tar.gz" "$TAR_URL"; then
        echo "  [*] Extracting binaries..."
        tar -xzf "$TMP_DIR/antigravity.tar.gz" -C "$PREFIX/bin" agy agy.va39
        chmod +x "$PREFIX/bin/agy"*
        rm -rf "$TMP_DIR"
        touch "$HOME/.antigravity_installed"
        echo "  [✓] Installation complete!"
        echo ""
        sleep 1
    else
        echo "  [!] Error: Failed to download Antigravity CLI engine."
        echo "      Please ensure your device has internet access."
        echo "      You can retry anytime by running: agy"
        rm -rf "$TMP_DIR"
        return 0 2>/dev/null || exit 1
    fi
fi

# Launch Antigravity CLI directly
if [ -x "$PREFIX/bin/agy" ]; then
    clear
    exec "$PREFIX/bin/agy" "$@"
fi
