#!/usr/bin/env python3
"""
apply_antigravity_theme.py
Customizes the Termux Android app with complete Antigravity branding,
deep cosmic UI theme, animations, vector icons, and startup experience.
"""

import os
import sys
import re

def apply_theme(termux_dir):
    print(f"[*] Applying Antigravity theme and branding to {termux_dir}...")

    # =========================================================================
    # 1. Update App Name in strings.xml and build.gradle
    # =========================================================================
    app_strings = os.path.join(termux_dir, "app/src/main/res/values/strings.xml")
    if os.path.exists(app_strings):
        with open(app_strings, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'<!ENTITY TERMUX_APP_NAME "[^"]*">', '<!ENTITY TERMUX_APP_NAME "Antigravity CLI">', c)
        c = re.sub(r'<string name="application_name">[^<]*</string>', '<string name="application_name">Antigravity CLI</string>', c)
        c = re.sub(r'<string name="app_name">[^<]*</string>', '<string name="app_name">Antigravity CLI</string>', c)
        c = re.sub(r'<string name="shared_user_label">[^<]*</string>', '<string name="shared_user_label">Antigravity CLI user</string>', c)
        with open(app_strings, "w", encoding="utf-8") as f:
            f.write(c)
        print("[+] Updated app name to 'Antigravity CLI' in app/strings.xml")

    shared_strings = os.path.join(termux_dir, "termux-shared/src/main/res/values/strings.xml")
    if os.path.exists(shared_strings):
        with open(shared_strings, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'<!ENTITY TERMUX_APP_NAME "[^"]*">', '<!ENTITY TERMUX_APP_NAME "Antigravity CLI">', c)
        c = re.sub(r'<string name="application_name">[^<]*</string>', '<string name="application_name">Antigravity CLI</string>', c)
        c = re.sub(r'<string name="app_name">[^<]*</string>', '<string name="app_name">Antigravity CLI</string>', c)
        with open(shared_strings, "w", encoding="utf-8") as f:
            f.write(c)
        print("[+] Updated app name in termux-shared/strings.xml")

    constants_java = os.path.join(termux_dir, "termux-shared/src/main/java/com/termux/shared/termux/TermuxConstants.java")
    if os.path.exists(constants_java):
        with open(constants_java, "r", encoding="utf-8") as f:
            c = f.read()
        c = c.replace('public static final String TERMUX_APP_NAME = "Termux";', 'public static final String TERMUX_APP_NAME = "Antigravity CLI";')
        with open(constants_java, "w", encoding="utf-8") as f:
            f.write(c)
        print("[+] Set TERMUX_APP_NAME to 'Antigravity CLI' in TermuxConstants.java")

    app_gradle = os.path.join(termux_dir, "app/build.gradle")
    if os.path.exists(app_gradle):
        with open(app_gradle, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'manifestPlaceholders\.TERMUX_APP_NAME = "[^"]*"', 'manifestPlaceholders.TERMUX_APP_NAME = "Antigravity CLI"', c)
        with open(app_gradle, "w", encoding="utf-8") as f:
            f.write(c)
        print("[+] Updated manifestPlaceholders.TERMUX_APP_NAME in app/build.gradle")

    # =========================================================================
    # 2. Window Animation XML files
    # =========================================================================
    anim_dir = os.path.join(termux_dir, "app/src/main/res/anim")
    os.makedirs(anim_dir, exist_ok=True)

    fade_in_xml = """<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <alpha
        android:fromAlpha="0.0"
        android:toAlpha="1.0"
        android:interpolator="@android:interpolator/decelerate_cubic"
        android:duration="220" />
    <scale
        android:fromXScale="0.97"
        android:toXScale="1.0"
        android:fromYScale="0.97"
        android:toYScale="1.0"
        android:pivotX="50%"
        android:pivotY="50%"
        android:interpolator="@android:interpolator/decelerate_cubic"
        android:duration="220" />
</set>"""

    fade_out_xml = """<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <alpha
        android:fromAlpha="1.0"
        android:toAlpha="0.0"
        android:interpolator="@android:interpolator/accelerate_cubic"
        android:duration="180" />
</set>"""

    with open(os.path.join(anim_dir, "antigravity_fade_in.xml"), "w", encoding="utf-8") as f:
        f.write(fade_in_xml)
    with open(os.path.join(anim_dir, "antigravity_fade_out.xml"), "w", encoding="utf-8") as f:
        f.write(fade_out_xml)
    print("[+] Created Antigravity window transition animations")

    # =========================================================================
    # 3. Colors, Styles & Themes with Antigravity Theme & Animations
    # =========================================================================
    colors_xml = os.path.join(termux_dir, "app/src/main/res/values/colors.xml")
    colors_content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="antigravity_bg">#0B0F19</color>
    <color name="antigravity_cyan">#00F0FF</color>
    <color name="antigravity_purple">#7928CA</color>
    <color name="antigravity_text">#E2E8F0</color>
    <color name="antigravity_keys_bg">#111625</color>
    <color name="antigravity_keys_active_bg">#1E293B</color>
</resources>"""
    with open(colors_xml, "w", encoding="utf-8") as f:
        f.write(colors_content)
    print("[+] Created Antigravity color resources in app/colors.xml")

    styles_xml = os.path.join(termux_dir, "app/src/main/res/values/styles.xml")
    if os.path.exists(styles_xml):
        with open(styles_xml, "r", encoding="utf-8") as f:
            c = f.read()

        anim_style = """
    <style name="AntigravityWindowAnimation" parent="@android:style/Animation.Activity">
        <item name="android:activityOpenEnterAnimation">@anim/antigravity_fade_in</item>
        <item name="android:activityOpenExitAnimation">@anim/antigravity_fade_out</item>
        <item name="android:activityCloseEnterAnimation">@anim/antigravity_fade_in</item>
        <item name="android:activityCloseExitAnimation">@anim/antigravity_fade_out</item>
    </style>
"""
        if "AntigravityWindowAnimation" not in c:
            c = c.replace("</resources>", anim_style + "</resources>")
            with open(styles_xml, "w", encoding="utf-8") as f:
                f.write(c)
            print("[+] Added AntigravityWindowAnimation to styles.xml")

    # Update themes in values/themes.xml and values-night/themes.xml
    for th_file in [
        os.path.join(termux_dir, "app/src/main/res/values/themes.xml"),
        os.path.join(termux_dir, "app/src/main/res/values-night/themes.xml")
    ]:
        if os.path.exists(th_file):
            with open(th_file, "r", encoding="utf-8") as f:
                c = f.read()

            theme_replacement = """    <!-- Antigravity Dark Cosmic Activity Theme -->
    <style name="Theme.TermuxActivity.DayNight.NoActionBar" parent="Theme.TermuxApp.DayNight.NoActionBar">
        <!-- Brand Colors -->
        <item name="colorPrimary">@color/antigravity_cyan</item>
        <item name="colorPrimaryVariant">@color/antigravity_purple</item>
        <item name="colorAccent">@color/antigravity_cyan</item>

        <item name="android:windowBackground">@color/antigravity_bg</item>
        <item name="android:colorBackground">@color/antigravity_bg</item>
        <item name="android:windowAnimationStyle">@style/AntigravityWindowAnimation</item>

        <item name="android:windowActionModeOverlay">true</item>
        <item name="android:windowTranslucentStatus">true</item>
        <item name="android:windowTranslucentNavigation">true</item>

        <item name="android:windowAllowReturnTransitionOverlap">true</item>
        <item name="android:windowAllowEnterTransitionOverlap">true</item>

        <!-- Left Drawer -->
        <item name="buttonBarButtonStyle">@style/TermuxActivity.Drawer.ButtonBarStyle.Dark</item>
        <item name="termuxActivityDrawerBackground">@color/antigravity_bg</item>
        <item name="termuxActivityDrawerImageTint">@color/antigravity_cyan</item>

        <!-- Extra Keys Bar Colors -->
        <item name="extraKeysButtonTextColor">@color/antigravity_text</item>
        <item name="extraKeysButtonActiveTextColor">@color/antigravity_cyan</item>
        <item name="extraKeysButtonBackgroundColor">@color/antigravity_keys_bg</item>
        <item name="extraKeysButtonActiveBackgroundColor">@color/antigravity_keys_active_bg</item>
    </style>"""

            pattern = r'<style name="Theme\.TermuxActivity\.DayNight\.NoActionBar" parent="Theme\.TermuxApp\.DayNight\.NoActionBar">.*?</style>'
            c = re.sub(pattern, theme_replacement, c, flags=re.DOTALL)

            with open(th_file, "w", encoding="utf-8") as f:
                f.write(c)
            print(f"[+] Themed {os.path.basename(os.path.dirname(th_file))}/themes.xml with Antigravity dark cosmic palette")

    # =========================================================================
    # 4. Antigravity Vector Drawables (Icon & Notifications)
    # =========================================================================
    drawables_dir = os.path.join(termux_dir, "app/src/main/res/drawable")
    os.makedirs(drawables_dir, exist_ok=True)

    # Modern Antigravity Vector Logo for Adaptive Icons & UI
    antigravity_vector = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">

    <!-- Anti-Gravity Cosmic Orbit Ring (Back) -->
    <path
        android:strokeColor="#7928CA"
        android:strokeWidth="3.2"
        android:strokeAlpha="0.75"
        android:pathData="M22,62 C22,50 86,44 86,54 C86,64 22,70 22,62 Z" />

    <!-- Left Ascending Wing (Vibrant Cyan) -->
    <path
        android:fillColor="#00E5FF"
        android:pathData="M54,22 L30,76 L42,76 L54,48 Z" />

    <!-- Right Ascending Wing (Electric Blue) -->
    <path
        android:fillColor="#0091FF"
        android:pathData="M54,22 L54,48 L66,76 L78,76 Z" />

    <!-- Quantum Core Prism (Pure White) -->
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M54,36 L61,48 L54,60 L47,48 Z" />

    <!-- Floating Base Crossbar (Neon Violet) -->
    <path
        android:fillColor="#C084FC"
        android:pathData="M38,64 L70,64 L68,68 L40,68 Z" />

    <!-- Quantum Orbit Ring (Front Glow) -->
    <path
        android:strokeColor="#00F0FF"
        android:strokeWidth="3.5"
        android:strokeLineCap="round"
        android:pathData="M20,62 C20,68 88,60 88,54" />

    <!-- Orbiting Satellite Particle -->
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M82,51 m-3.5,0 a3.5,3.5 0 1,0 7,0 a3.5,3.5 0 1,0 -7,0" />
</vector>"""

    with open(os.path.join(drawables_dir, "ic_foreground.xml"), "w", encoding="utf-8") as f:
        f.write(antigravity_vector)
    print("[+] Injected Antigravity vector emblem into drawable/ic_foreground.xml")

    # Notification icon
    notification_vector = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M12,3 L4,19 L8,19 L12,10 L16,19 L20,19 Z M12,7 L14,13 L10,13 Z" />
    <path
        android:strokeColor="#FFFFFF"
        android:strokeWidth="1.5"
        android:strokeLineCap="round"
        android:pathData="M3,16 C3,19 21,17 21,15" />
</vector>"""

    with open(os.path.join(drawables_dir, "ic_service_notification.xml"), "w", encoding="utf-8") as f:
        f.write(notification_vector)
    print("[+] Injected Antigravity notification icon into drawable/ic_service_notification.xml")

    # Adaptive Icon XMLs
    mipmap_v26 = os.path.join(termux_dir, "app/src/main/res/mipmap-anydpi-v26")
    os.makedirs(mipmap_v26, exist_ok=True)

    adaptive_icon_xml = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/black"/>
    <foreground android:drawable="@drawable/ic_foreground"/>
    <monochrome android:drawable="@drawable/ic_foreground"/>
</adaptive-icon>"""

    with open(os.path.join(mipmap_v26, "ic_launcher.xml"), "w", encoding="utf-8") as f:
        f.write(adaptive_icon_xml)
    with open(os.path.join(mipmap_v26, "ic_launcher_round.xml"), "w", encoding="utf-8") as f:
        f.write(adaptive_icon_xml)
    print("[+] Configured adaptive icons in mipmap-anydpi-v26/")

    # =========================================================================
    # 5. Left Drawer Branded Antigravity Header
    # =========================================================================
    layout_file = os.path.join(termux_dir, "app/src/main/res/layout/activity_termux.xml")
    if os.path.exists(layout_file):
        with open(layout_file, "r", encoding="utf-8") as f:
            c = f.read()

        old_header = """                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal">
                    <ImageButton
                        android:id="@+id/settings_button"
                        android:layout_width="40dp"
                        android:layout_height="40dp"
                        android:src="@drawable/ic_settings"
                        android:background="@null"
                        android:contentDescription="@string/action_open_settings"
                        app:tint="?attr/termuxActivityDrawerImageTint" />
                </LinearLayout>"""

        new_header = """                <!-- Antigravity Branded Header -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal"
                    android:gravity="center_vertical"
                    android:paddingHorizontal="14dp"
                    android:paddingTop="16dp"
                    android:paddingBottom="12dp">

                    <ImageView
                        android:layout_width="32dp"
                        android:layout_height="32dp"
                        android:src="@drawable/ic_foreground"
                        android:contentDescription="Antigravity Logo" />

                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:layout_marginStart="10dp"
                        android:orientation="vertical">

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="ANTIGRAVITY"
                            android:textSize="15sp"
                            android:textStyle="bold"
                            android:letterSpacing="0.08"
                            android:textColor="#00F0FF" />

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Agentic AI CLI"
                            android:textSize="11sp"
                            android:textColor="#94A3B8" />
                    </LinearLayout>

                    <ImageButton
                        android:id="@+id/settings_button"
                        android:layout_width="36dp"
                        android:layout_height="36dp"
                        android:src="@drawable/ic_settings"
                        android:background="@null"
                        android:contentDescription="@string/action_open_settings"
                        app:tint="#64748B" />
                </LinearLayout>"""

        if old_header in c:
            c = c.replace(old_header, new_header)
            print("[+] Added Antigravity branded header to left drawer")

        # Set toolbar ViewPager background to deep cosmic @color/antigravity_bg
        c = c.replace('android:id="@+id/terminal_toolbar_view_pager"\n            android:visibility="gone"\n            android:layout_width="match_parent"\n            android:layout_height="37.5dp"\n            android:background="@color/black"',
                      'android:id="@+id/terminal_toolbar_view_pager"\n            android:visibility="gone"\n            android:layout_width="match_parent"\n            android:layout_height="37.5dp"\n            android:background="@color/antigravity_bg"')

        with open(layout_file, "w", encoding="utf-8") as f:
            f.write(c)

    # =========================================================================
    # 6. Terminal Cursor Pulsing & Blinking Animation Defaults
    # =========================================================================
    prop_const = os.path.join(termux_dir, "termux-shared/src/main/java/com/termux/shared/termux/settings/properties/TermuxPropertyConstants.java")
    if os.path.exists(prop_const):
        with open(prop_const, "r", encoding="utf-8") as f:
            c = f.read()

        # Set default cursor blink rate to 500ms (pulsing terminal cursor animation)
        c = c.replace("public static final int DEFAULT_IVALUE_TERMINAL_CURSOR_BLINK_RATE = 0;",
                      "public static final int DEFAULT_IVALUE_TERMINAL_CURSOR_BLINK_RATE = 500;")

        with open(prop_const, "w", encoding="utf-8") as f:
            f.write(c)
        print("[+] Enabled pulsing cursor animation by default (500ms)")

    # =========================================================================
    # 7. Terminal Default Colors (Antigravity Palette in TerminalColorScheme)
    # =========================================================================
    colorscheme_java = os.path.join(termux_dir, "terminal-emulator/src/main/java/com/termux/terminal/TerminalColorScheme.java")
    if os.path.exists(colorscheme_java):
        with open(colorscheme_java, "r", encoding="utf-8") as f:
            c = f.read()

        # Default foreground: #E2E8F0, background: #0B0F19, cursor: #00F0FF
        target_default_colors = "        0xffffffff, 0xff000000, 0xffffffff};"
        replacement_default_colors = "        0xffe2e8f0, 0xff0b0f19, 0xff00f0ff};"

        if target_default_colors in c:
            c = c.replace(target_default_colors, replacement_default_colors)
            print("[+] Updated default terminal background to #0B0F19 and cursor to #00F0FF in TerminalColorScheme.java")

        with open(colorscheme_java, "w", encoding="utf-8") as f:
            f.write(c)

    print("[✓] All Antigravity themes, branding, animations, and vector icons applied successfully!")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "./termux-src"
    apply_theme(target)
