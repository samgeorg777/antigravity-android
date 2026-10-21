#!/usr/bin/env python3
import sys
import re

def patch_gradle(gradle_path, new_pkg="com.agycli", app_name="Antigravity CLI"):
    with open(gradle_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update package placeholders and applicationId
    content = content.replace(
        'manifestPlaceholders.TERMUX_PACKAGE_NAME = "com.termux"',
        f'manifestPlaceholders.TERMUX_PACKAGE_NAME = "{new_pkg}"\n        applicationId "{new_pkg}"'
    )
    content = content.replace(
        'manifestPlaceholders.TERMUX_APP_NAME = "Termux"',
        f'manifestPlaceholders.TERMUX_APP_NAME = "{app_name}"'
    )

    # 2. Disable downloadBootstraps and downloadBootstrap so custom bootstraps are NEVER deleted
    content = re.sub(
        r'def downloadBootstrap\(String arch[^\)]*\)\s*\{',
        'def downloadBootstrap(String arch, String expectedChecksum, String version) { return; ',
        content
    )
    content = re.sub(
        r'task downloadBootstraps\(\)\s*\{',
        'task downloadBootstraps() { enabled = false; ',
        content
    )

    # 3. Assert changes are applied
    assert f'applicationId "{new_pkg}"' in content, "Failed to inject applicationId"
    assert f'manifestPlaceholders.TERMUX_PACKAGE_NAME = "{new_pkg}"' in content, "Failed to inject package placeholder"
    assert 'task downloadBootstraps() { enabled = false;' in content, "Failed to disable downloadBootstraps task"

    with open(gradle_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[✓] Successfully patched {gradle_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: patch_gradle.py <app/build.gradle>")
        sys.exit(1)
    patch_gradle(sys.argv[1])
