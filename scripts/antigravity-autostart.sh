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

# Ensure uploads and .termux configuration directories exist
mkdir -p "$HOME/uploads" "$HOME/.termux"

# Ensure Antigravity dark cosmic color palette is applied
if [ ! -f "$HOME/.termux/colors.properties" ]; then
    cat << 'EOF' > "$HOME/.termux/colors.properties"
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
fi

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
    CYAN="\033[38;2;0;240;255m"
    PURPLE="\033[38;2;168;85;247m"
    WHITE="\033[38;2;248;250;252m"
    GRAY="\033[38;2;148;163;184m"
    RESET="\033[0m"
    BOLD="\033[1m"

    clear
    echo -e "${PURPLE}  ╭────────────────────────────────────────────────────────────╮${RESET}"
    echo -e "${PURPLE}  │  ${CYAN}${BOLD}▲  A N T I G R A V I T Y   C L I${RESET}${PURPLE}                           │${RESET}"
    echo -e "${PURPLE}  │  ${GRAY}Google DeepMind Advanced Agentic AI for Android          ${PURPLE}│${RESET}"
    echo -e "${PURPLE}  ╰────────────────────────────────────────────────────────────╯${RESET}"
    echo ""

    spin_frames=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
    for frame in "${spin_frames[@]}"; do
        echo -ne "\r  ${CYAN}[$frame]${RESET} ${WHITE}Initializing Neural Engine & Workspace...${RESET}"
        sleep 0.03
    done
    echo -ne "\r  ${CYAN}[✓]${RESET} ${WHITE}${BOLD}Antigravity Agent Ready! Defying limits.${RESET}\n\n"
    sleep 0.2

    exec "$PREFIX/bin/agy" "$@"
fi
