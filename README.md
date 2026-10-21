# 🚀 Antigravity CLI for Android (Zero-Setup Standalone App)

A fully automated, standalone Android application (`.apk`) that runs **Google's Antigravity CLI (`agy`)** natively on Android without requiring manual terminal configuration, package installation, or glibc setup.

Built with a dedicated package ID (`com.agycli`), it installs and runs completely independently alongside any existing Termux app on your device without conflicts.

---

## ✨ Features

- **Zero Manual Setup:** Install the APK, open the app, and Antigravity CLI initializes automatically and launches straight into the `agy` prompt.
- **Independent Installation (`com.agycli`):** Operates under its own package ID. You can run standard Termux and Antigravity CLI side-by-side with zero interference.
- **Pre-configured Glibc & Networking:** Comes with full glibc runtime pre-injected into the bootstrap rootfs, along with configured localhost name resolution (`/etc/hosts`, `resolv.conf`, `nsswitch.conf`, and `GODEBUG="netdns=cgo"`).
- **Single-Tap Clickable URLs:** Any URL output by `agy` (such as GitHub OAuth verification links or localhost servers) can be clicked directly to open immediately in your Android browser, with automatic Markdown punctuation trimming.
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

---

## 🛠️ Repository Structure

```
antigravity-android/
├── .github/
│   └── workflows/
│       └── build-apk.yml          # Automated GitHub Actions APK build workflow
├── scripts/
│   ├── antigravity-autostart.sh   # Interactive session autostart & DNS setup
│   ├── customize-termux.sh        # Package rename, glibc injection & build pipeline
│   ├── inject_glibc.py            # Injects glibc libraries into bootstrap archive
│   ├── patch_bootstrap.py         # Patches binary package paths (com.termux -> com.agycli)
│   ├── patch_gradle.py            # Disables upstream bootstraps & configures build
│   └── patch_termux_features.py   # Patches clickable links, drag & drop, and file pickers
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
