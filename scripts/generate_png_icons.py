#!/usr/bin/env python3
"""
generate_png_icons.py
Generates pixel-perfect Antigravity launcher icons for all Android densities:
mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi (both square and round).
"""

import os
import sys

def generate_icons(termux_dir):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("[!] Pillow not installed. Attempting to install pillow...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        from PIL import Image, ImageDraw

    densities = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    res_dir = os.path.join(termux_dir, "app/src/main/res")

    def create_antigravity_icon(size, is_round=False):
        # Render at 4x for high-quality supersampled anti-aliasing
        super_size = size * 4
        img = Image.new('RGBA', (super_size, super_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        bg_color = (11, 15, 25, 255)  # #0B0F19 Cosmic Obsidian
        if is_round:
            draw.ellipse([0, 0, super_size - 1, super_size - 1], fill=bg_color)
        else:
            corner = int(super_size * 0.22)
            draw.rounded_rectangle([0, 0, super_size - 1, super_size - 1], radius=corner, fill=bg_color)

        scale = super_size / 108.0

        def pt(x, y):
            return (x * scale, y * scale)

        # 1. Back Orbit Ellipse (Purple #7928CA)
        orbit_box = [pt(18, 44)[0], pt(18, 44)[1], pt(90, 72)[0], pt(90, 72)[1]]
        draw.ellipse(orbit_box, outline=(121, 40, 202, 190), width=max(1, int(3 * scale)))

        # 2. Left Wing (Cyan #00E5FF)
        draw.polygon([pt(54, 22), pt(30, 76), pt(42, 76), pt(54, 48)], fill=(0, 229, 255, 255))

        # 3. Right Wing (Electric Blue #0091FF)
        draw.polygon([pt(54, 22), pt(54, 48), pt(66, 76), pt(78, 76)], fill=(0, 145, 255, 255))

        # 4. Floating Base Bar (Violet #C084FC)
        draw.polygon([pt(38, 64), pt(70, 64), pt(68, 68), pt(40, 68)], fill=(192, 132, 252, 255))

        # 5. Core Prism (White #FFFFFF)
        draw.polygon([pt(54, 36), pt(61, 48), pt(54, 60), pt(47, 48)], fill=(255, 255, 255, 255))

        # 6. Front Orbit Glow (Bright Cyan #00F0FF arc)
        draw.arc(orbit_box, start=0, end=180, fill=(0, 240, 255, 255), width=max(1, int(3.5 * scale)))

        # 7. Orbit Satellite (White dot)
        sp = pt(82, 51)
        sr = 3.5 * scale
        draw.ellipse([sp[0] - sr, sp[1] - sr, sp[0] + sr, sp[1] + sr], fill=(255, 255, 255, 255))

        # Downsample with Lanczos filter for razor-sharp anti-aliased output
        return img.resize((size, size), Image.Resampling.LANCZOS)

    for folder_name, size in densities.items():
        folder_path = os.path.join(res_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        icon_square = create_antigravity_icon(size, is_round=False)
        icon_square.save(os.path.join(folder_path, "ic_launcher.png"), "PNG")

        icon_round = create_antigravity_icon(size, is_round=True)
        icon_round.save(os.path.join(folder_path, "ic_launcher_round.png"), "PNG")

        print(f"[+] Generated {size}x{size} icons in {folder_name}/")

    print("[✓] All launcher PNG icons generated successfully!")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "./termux-src"
    generate_icons(target)
