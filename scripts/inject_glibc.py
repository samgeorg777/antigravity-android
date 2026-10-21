#!/usr/bin/env python3
import urllib.request
import subprocess
import tempfile
import os
import tarfile
import shutil

GLIBC_DEB_URL = "https://packages-cf.termux.dev/apt/termux-glibc/pool/stable/g/glibc/glibc_2.44_aarch64.deb"

def inject_glibc(dest_extracted_dir):
    print(f"[*] Downloading glibc runtime from {GLIBC_DEB_URL}...")
    req = urllib.request.Request(GLIBC_DEB_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        deb_data = resp.read()

    with tempfile.TemporaryDirectory() as td:
        deb_path = os.path.join(td, "glibc.deb")
        with open(deb_path, "wb") as f:
            f.write(deb_data)

        subprocess.run(["ar", "-x", deb_path], cwd=td, check=True)
        data_tar = [f for f in os.listdir(td) if f.startswith("data.tar")][0]
        with tarfile.open(os.path.join(td, data_tar)) as tf:
            tf.extractall(path=td)

        src_glibc = os.path.join(td, "data/data/com.termux/files/usr/glibc")
        target_glibc = os.path.join(dest_extracted_dir, "glibc")

        if os.path.exists(target_glibc):
            shutil.rmtree(target_glibc)

        shutil.copytree(src_glibc, target_glibc, symlinks=True)
        print(f"[✓] Glibc successfully injected into {target_glibc}")

        # Check critical loader binary
        loader = os.path.join(target_glibc, "lib/ld-linux-aarch64.so.1")
        if os.path.exists(loader):
            os.chmod(loader, 0o755)
            print(f"[✓] Verified and set executable: {loader}")
        else:
            raise RuntimeError(f"Glibc loader missing at {loader}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: inject_glibc.py <path_to_extracted_bootstrap_dir>")
        sys.exit(1)
    inject_glibc(sys.argv[1])
