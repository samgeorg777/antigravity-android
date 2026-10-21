# 🚀 Antigravity CLI for Android (Zero-Setup Standalone App)

A fully automated, standalone Android application (`.apk`) that runs **Google's Antigravity CLI (`agy`)** natively on Android without requiring manual terminal configuration, package installation, or glibc setup.

Built with a dedicated package ID (`com.agycli`), it installs and runs completely independently alongside any existing Termux app on your device without conflicts.

---

## ✨ Features

- **Zero Manual Setup:** Install the APK, open the app, and Antigravity CLI initializes automatically and launches straight into the `agy` prompt.
- **Independent App & Identity (`com.agycli`):** Dedicated package ID, custom launcher name **Antigravity CLI**, and independent home storage. Runs side-by-side with standard Termux with zero conflict.
- **Futuristic Antigravity Visual Theme:**
  - **Custom Quantum Launcher Icons:** Custom vector and supersampled launcher icons across all screen densities with the signature levitating quantum delta emblem.
  - **Deep Cosmic Palette:** Obsidian space background (`#0B0F19`), neon cyan accents (`#00F0FF`), quantum violet highlights (`#7928CA`), and crisp white text.
  - **Pulsing Sci-Fi Cursor:** Terminal cursor pulses at 500ms like a modern mainframe.
  - **Window & Launch Animations:** Smooth activity fade/scale transitions and an animated cosmic startup sequence in the terminal.
  - **Branded Drawer:** Left slide-out navigation features an Antigravity header with glowing logo and clean navigation.
- **Pre-configured Glibc & Networking:** Comes with full glibc runtime pre-injected into the bootstrap rootfs, along with configured localhost name resolution (`/etc/hosts`, `resolv.conf`, `nsswitch.conf`, and `GODEBUG="netdns=cgo"`).
- **Single-Tap Clickable URLs:** Any URL output by `agy` (such as GitHub OAuth verification links or localhost servers) can be clicked directly to open immediately in your Android browser, with automatic Markdown punctuation trimming.
- **Full Storage & USB OTG Access:**
  - One-tap unlock for Android 11+ `MANAGE_EXTERNAL_STORAGE` permission via the drawer button (**All Files & USB**) or long-press menu.
  - Automatically mounts and symlinks internal storage (`~/storage/shared`, `downloads`, `dcim`, `pictures`) and any connected **USB Flash Drives / OTG Storage** (`~/storage/usb`, `~/storage/usb1..N`).
- **Autonomous Android Device Control (`agy-device`):**
  - Built-in on-device ADB loopback controller allowing Antigravity (`agy`) and the terminal to control the Android phone autonomously.
  - Supports screen capture (`agy-device screenshot`), UI tree inspection (`agy-device ui-dump`), touch simulation (`agy-device tap`, `agy-device swipe`), text input (`agy-device text`), key events (`agy-device key`), and app launching (`agy-device launch`).
  - Works locally without a PC using Android 11+ Wireless Debugging or USB debugging.
- **Image & File Picker (`[IMG]` / `[FILE]`):**
  - **Extra Keys Bar:** Tap `[IMG]` right above your soft keyboard to open the Android image gallery/picker, or swipe up on `[IMG]` (popup: `[FILE]`) to select any file.
  - **Left Drawer:** Swipe from the left edge to find dedicated **Add Image** and **Add File** buttons.
  - **Long-Press Menu:** Long-press anywhere on the terminal to choose **Insert Image** or **Insert File**.
  - Selected files are copied asynchronously to `~/uploads/` and their absolute paths are typed directly into the prompt.
- **Drag-and-Drop Support:** Drag images, files, or text snippets from file managers, galleries, or split-screen apps directly onto the terminal screen.
- **Optimized for ARM64:** Includes TCMalloc VA39 39-bit virtual address space compatibility for rock-solid stability on Android 64-bit kernels.
- **Full Coding Abilities:** Runs in a complete sandboxed Linux environment with `bash`, `python3`, `git`, and developer toolchains.

---

## 📥 Download & Installation

The latest pre-built `.apk` is built automatically by GitHub Actions on every commit:

1. Go to the [Actions tab](https://github.com/samgeorg777/antigravity-android/actions).
2. Click on the latest workflow run: **Build Antigravity Android APK**.
3. Scroll down to the **Artifacts** section at the bottom.
4. Download **`Antigravity-CLI-Android`**, unzip it, and tap **`Antigravity-CLI.apk`** to install on your Android device.

*(If you are building locally on your device, the generated APK is also saved to `/sdcard/Download/Antigravity-CLI.apk`).*

---

## 🎯 Quick Start Guide

### 1. Launching Antigravity CLI
When you open the **Antigravity CLI** app for the first time:
- The app automatically prepares the glibc rootfs and networking files.
- It downloads and extracts the Antigravity CLI engine in seconds.
- You are greeted with the interactive `agy` prompt!

### 2. GitHub Authentication
When `agy` asks you to log in to GitHub:
1. A verification link like `https://github.com/login/device` and an 8-character code will appear.
2. Simply **tap the link directly on your screen** to open it in your browser.
3. Enter the code and authorize. The app will immediately recognize the login and start.

### 3. Adding Images and Files to Prompts
You can pass images or documents to Antigravity CLI in several ways:
- **Tap `[IMG]`** on the toolbar above the keyboard to pick a photo from your gallery.
- **Swipe up on `[IMG]`** (or select **Insert File** from the long-press menu) to pick any document.
- **Drag and drop** any image or file from a split-screen file manager directly into the terminal window.
- The path (e.g. `/data/data/com.agycli/files/home/uploads/diagram.png`) will be typed right at your cursor!

### 4. Full Device Storage & USB Drive Access
To grant Antigravity CLI permission to view and edit files across your internal storage and USB drives:
1. Swipe from the left edge of your screen to open the drawer.
2. Tap **All Files & USB** (or long-press the terminal and choose **All Files & USB Access**).
3. Toggle on **Allow access to manage all files** for *Antigravity CLI*.
4. Your storage folders are now automatically accessible:
   - `~/storage/shared` -> Internal storage root (`/sdcard`)
   - `~/storage/downloads` -> Downloads folder
   - `~/storage/usb` (and `usb1..N`) -> Connected USB flash drives or external OTG storage

---

### 5. Autonomous Device Control with `agy-device`
Antigravity CLI can autonomously navigate your phone, click buttons, type text, capture screenshots, and automate tasks via local ADB:

1. **Enable Wireless Debugging:**
   - Tap **Device Control** in the left drawer (or long-press terminal -> **Device Control (ADB)**).
   - In Developer Options, enable **Wireless debugging**.
2. **Pair and Connect (One-Time / Local Loopback):**
   - Tap **Pair device with pairing code** in Wireless debugging settings.
   - Note the Port and 6-digit Wi-Fi pairing code.
   - In Antigravity CLI, run:
     ```bash
     agy-device pair <PORT> <CODE>
     agy-device connect <PORT>
     ```
3. **Autonomous CLI & AI Commands:**
   Once connected, both you and the `agy` AI assistant can use the controller:
   - `agy-device status` — Check ADB connection status.
   - `agy-device screenshot` — Capture screen to `~/uploads/screen.png` for visual analysis.
   - `agy-device ui-dump` — Dump all interactive buttons, text, and screen bounds.
   - `agy-device tap <x> <y>` — Simulate a tap at coordinates (e.g. `agy-device tap 540 1200`).
   - `agy-device swipe <x1> <y1> <x2> <y2>` — Scroll or swipe the screen.
   - `agy-device text "hello world"` — Type text into active fields.
   - `agy-device key <KEY_CODE>` — Press HOME (3), BACK (4), POWER (26), etc.
   - `agy-device launch <package>` — Launch any Android app (e.g. `agy-device launch com.android.settings`).
   - `agy-device shell <command>` — Run any privileged Android shell command.

*(Aliases `device` and `control` are also available as shortcuts for `agy-device`).*

---

## 🛠️ Repository Structure

```
antigravity-android/
├── .github/
│   └── workflows/
│       └── build-apk.yml          # Automated GitHub Actions APK build workflow
├── scripts/
│   ├── agy-device                 # Autonomous Android device controller (ADB loopback)
│   ├── antigravity-autostart.sh   # Session autostart, DNS setup & USB auto-linker
│   ├── customize-termux.sh        # Package rename, glibc injection & build pipeline
│   ├── inject_glibc.py            # Injects glibc libraries into bootstrap archive
│   ├── patch_bootstrap.py         # Patches binary package paths (com.termux -> com.agycli)
│   ├── patch_gradle.py            # Disables upstream bootstraps & configures build
│   └── patch_termux_features.py   # Patches clickable links, drag & drop, storage & ADB
└── README.md
```

---

## ⚙️ Build Modes

You can manually trigger builds from the **Actions** tab with custom options (**Run workflow**):

- **Fast / Compact Build (`prebundle: false`, Default):**
  - APK size: **~55 MB**
  - Compiles quickly. Glibc is pre-bundled; the AI binary is verified and set up on initial startup.
- **Offline / Pre-bundled Build (`prebundle: true`):**
  - APK size: **~250 MB**
  - Downloads and pre-bundles the entire Antigravity binary directly inside the APK assets for completely offline first-run.

---

## 📱 Recommended Android Settings

1. **Keep Running in Background:**
   To allow Antigravity to work on long coding tasks without Android suspending the process:
   - Go to **Android Settings** → **Apps** → **Antigravity CLI** → **Battery** → Select **Unrestricted**.
2. **Accessing Phone Storage:**
   To access files in your phone's main Downloads or storage folder:
   - Run `termux-setup-storage` in the shell and approve the permission popup. Your device storage will be linked at `~/storage/shared`.

---

## 📄 License
This project builds on open-source components from the Termux project and Antigravity CLI under their respective licenses.
