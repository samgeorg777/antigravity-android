# 🚀 Antigravity CLI for Android (Zero-Setup Standalone App)

A fully automated standalone Android application (`.apk`) that runs **Google's Antigravity CLI (`agy`)** natively on Android without requiring manual package installation, terminal setup, or configuration.

---

## ✨ Features

- **Zero-Setup Out of the Box:** Install the APK, open the app, and Antigravity CLI immediately initializes and starts.
- **Full Coding Abilities:** Runs in a complete sandboxed Linux userspace with `bash`, `python3`, `git`, and developer toolchains.
- **Patched for Android ARM64:** Includes the TCMalloc VA39 virtual address space fix and bionic C wrapper for zero crash execution.
- **Touch & Mobile Optimized:** Built-in touch helper bar with `Ctrl`, `Alt`, `Esc`, `Tab`, and arrow keys.
- **Filesystem Access:** Can read and write directly to your phone's internal storage (`/sdcard`) to edit codebases and projects.

---

## 🛠️ How to Build Your APK with GitHub Actions

### Step 1: Create a New GitHub Repository
1. Go to [github.com/new](https://github.com/new).
2. Name your repository (e.g., `antigravity-android`).
3. Set visibility to **Public** (recommended for free, unlimited GitHub Actions minutes).
4. Do **not** initialize with a README (this project already has one).
5. Click **Create repository**.

### Step 2: Push This Project to GitHub
In your terminal, navigate to this directory and push:

```bash
cd ~/antigravity-android

# Initialize git repository
git init -b main
git add .
git commit -m "feat: Initial Antigravity Android APK builder setup"

# Link to your new GitHub repository (replace YOUR_USERNAME and YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/antigravity-android.git

# Push
git push -u origin main
```

*(If prompted for credentials, use your GitHub Username and a GitHub Personal Access Token as the password).*

---

### Step 3: Download Your APK

1. On your GitHub repository page, click the **Actions** tab at the top.
2. You will see the **Build Antigravity Android APK** workflow running.
3. Click on the running job to watch the live compilation (takes ~3 to 5 minutes).
4. When finished, click on the completed run:
   - Scroll down to the **Artifacts** section.
   - Click **`Antigravity-CLI-Android`** to download your ready-to-install `.apk`!
5. Transfer or download the APK directly on your phone and tap to install.

---

## ⚙️ Build Modes (Compact vs Offline)

In GitHub Actions, you can manually trigger builds under **Actions** → **Build Antigravity Android APK** → **Run workflow**:

- **Compact Build (Default):**
  - APK size: **~35 MB**
  - Build time: **~3 minutes**
  - Behavior: Extracts base rootfs instantly. On first run, it displays a friendly progress screen and automatically downloads the AI engine in ~10 seconds. From then on, it is completely permanent and launches in < 1 second.
- **Pre-bundled Offline Build (`prebundle: true`):**
  - APK size: **~250 MB**
  - Behavior: The entire AI engine and libraries are pre-packaged directly inside the APK. No first-run download needed.

---

## 📱 First-Time Phone Setup Tips

1. **Storage Access:** To allow Antigravity to work on project folders stored in your phone's internal storage or downloads, type `exit` once and run:
   ```bash
   termux-setup-storage
   ```
   Grant the Android storage permission popup. Your device storage will now be available under `~/storage/shared`.
2. **Background Execution:** If you want Antigravity to keep thinking when switching between apps, go to:
   - **Android Settings** → **Apps** → **Antigravity CLI** → **Battery** → Select **Unrestricted**.
