#!/usr/bin/env python3
import sys
import zipfile

def patch_zip(input_path, output_path, old_pkg=b"com.termux", new_pkg=b"com.agycli"):
    print(f"[*] Patching bootstrap package references: {old_pkg.decode()} -> {new_pkg.decode()}")
    with zipfile.ZipFile(input_path, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if old_pkg in data:
                    data = data.replace(old_pkg, new_pkg)
                zout.writestr(item, data)
    print(f"[✓] Successfully wrote patched bootstrap to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: patch_bootstrap.py <input.zip> <output.zip>")
        sys.exit(1)
    patch_zip(sys.argv[1], sys.argv[2])
