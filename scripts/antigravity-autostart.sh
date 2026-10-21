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

# Configure networking, localhost resolution, and DNS paths
mkdir -p "$PREFIX/etc" "$PREFIX/glibc/etc"

cat << 'EOF' > "$PREFIX/etc/hosts"
127.0.0.1 localhost
::1 localhost ip6-localhost ip6-loopback
EOF
cp -f "$PREFIX/etc/hosts" "$PREFIX/glibc/etc/hosts"

cat << 'EOF' > "$PREFIX/etc/resolv.conf"
nameserver 8.8.8.8
nameserver 1.1.1.1
EOF
cp -f "$PREFIX/etc/resolv.conf" "$PREFIX/glibc/etc/resolv.conf"

cat << 'EOF' > "$PREFIX/etc/nsswitch.conf"
hosts: files dns
networks: files
EOF
cp -f "$PREFIX/etc/nsswitch.conf" "$PREFIX/glibc/etc/nsswitch.conf"

# Ensure glibc permissions
if [ -d "$PREFIX/glibc" ]; then
    chmod -R 755 "$PREFIX/glibc" 2>/dev/null || true
    chmod +x "$PREFIX/glibc/lib/ld-linux-aarch64.so.1" 2>/dev/null || true
fi

# Set Go DNS resolution to cgo (uses glibc getaddrinfo + /etc/hosts)
export GODEBUG="netdns=cgo"

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
