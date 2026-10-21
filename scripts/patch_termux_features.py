#!/usr/bin/env python3
"""
patch_termux_features.py
Applies enhancements to Termux source code for Antigravity Android:
1. Clickable and directly openable URLs in terminal transcript and URL dialog.
2. Drag-and-drop file and image support directly onto TerminalView.
3. "IMG" and "FILE" buttons in extra keys bar and drawer menu.
4. "Insert Image" and "Insert File" options in long-press context menu.
5. Background asynchronous import of files to ~/uploads/ with path insertion.
"""

import os
import sys

def patch_termux(termux_dir):
    print(f"[*] Patching Termux features in {termux_dir}...")

    # 1. TermuxTerminalViewClient.java (URL Single Tap & Dialog Click)
    tv_client = os.path.join(termux_dir, "app/src/main/java/com/termux/app/terminal/TermuxTerminalViewClient.java")
    if os.path.exists(tv_client):
        with open(tv_client, "r", encoding="utf-8") as f:
            c = f.read()

        target1 = """        if (mActivity.getProperties().shouldOpenTerminalTranscriptURLOnClick()) {
            int[] columnAndRow = mActivity.getTerminalView().getColumnAndRow(e, true);
            String wordAtTap = term.getScreen().getWordAtLocation(columnAndRow[0], columnAndRow[1]);
            LinkedHashSet<CharSequence> urlSet = TermuxUrlUtils.extractUrls(wordAtTap);

            if (!urlSet.isEmpty()) {
                String url = (String) urlSet.iterator().next();
                ShareUtils.openUrl(mActivity, url);
                return;
            }
        }"""

        replacement1 = """        if (term != null && mActivity.getTerminalView() != null) {
            int[] columnAndRow = mActivity.getTerminalView().getColumnAndRow(e, true);
            String wordAtTap = term.getScreen().getWordAtLocation(columnAndRow[0], columnAndRow[1]);
            LinkedHashSet<CharSequence> urlSet = TermuxUrlUtils.extractUrls(wordAtTap);

            if (!urlSet.isEmpty()) {
                String url = (String) urlSet.iterator().next();
                while (url.endsWith(")") || url.endsWith("]") || url.endsWith("}") || url.endsWith(">") ||
                       url.endsWith("\\\"") || url.endsWith("\x27") || url.endsWith(".") || url.endsWith(",") ||
                       url.endsWith(";") || url.endsWith(":")) {
                    url = url.substring(0, url.length() - 1);
                }
                if (!url.isEmpty()) {
                    ShareUtils.openUrl(mActivity, url);
                    return;
                }
            }
        }"""

        if target1 in c:
            c = c.replace(target1, replacement1)
            print("[+] Patched single tap URL opening in TermuxTerminalViewClient.java")
        else:
            print("[!] Warning: target1 not found in TermuxTerminalViewClient.java")

        target1_dialog = """        // Click to copy url to clipboard:
        final AlertDialog dialog = new AlertDialog.Builder(mActivity).setItems(urls, (di, which) -> {
            String url = (String) urls[which];
            ShareUtils.copyTextToClipboard(mActivity, url, mActivity.getString(R.string.msg_select_url_copied_to_clipboard));
        }).setTitle(R.string.title_select_url_dialog).create();"""

        replacement1_dialog = """        // Click to open url directly:
        final AlertDialog dialog = new AlertDialog.Builder(mActivity).setItems(urls, (di, which) -> {
            String url = (String) urls[which];
            ShareUtils.openUrl(mActivity, url);
        }).setTitle(R.string.title_select_url_dialog).create();"""

        if target1_dialog in c:
            c = c.replace(target1_dialog, replacement1_dialog)
            print("[+] Patched URL dialog to open links on click in TermuxTerminalViewClient.java")
        else:
            print("[!] Warning: target1_dialog not found in TermuxTerminalViewClient.java")

        with open(tv_client, "w", encoding="utf-8") as f:
            f.write(c)

    # 2. TermuxPropertyConstants.java (Default Extra Keys & Properties)
    prop_file = os.path.join(termux_dir, "termux-shared/src/main/java/com/termux/shared/termux/settings/properties/TermuxPropertyConstants.java")
    if os.path.exists(prop_file):
        with open(prop_file, "r", encoding="utf-8") as f:
            c = f.read()

        old_keys = "public static final String DEFAULT_IVALUE_EXTRA_KEYS = \"[['ESC','/',{key: '-', popup: '|'},'HOME','UP','END','PGUP'], ['TAB','CTRL','ALT','LEFT','DOWN','RIGHT','PGDN']]\"; // Double row"
        new_keys = "public static final String DEFAULT_IVALUE_EXTRA_KEYS = \"[['ESC','/',{key: '-', popup: '|'},'HOME',{key: 'UP', popup: 'PGUP'},'END',{key: 'IMG', popup: 'FILE'}], ['TAB','CTRL','ALT','LEFT',{key: 'DOWN', popup: 'PGDN'},'RIGHT','PASTE']]\"; // Double row"

        if old_keys in c:
            c = c.replace(old_keys, new_keys)
            print("[+] Patched DEFAULT_IVALUE_EXTRA_KEYS with IMG/FILE/PASTE in TermuxPropertyConstants.java")

        target_false = "        KEY_HIDE_SOFT_KEYBOARD_ON_STARTUP,\n        KEY_TERMINAL_ONCLICK_URL_OPEN,\n        KEY_USE_CTRL_SPACE_WORKAROUND,"
        replacement_false = "        KEY_HIDE_SOFT_KEYBOARD_ON_STARTUP,\n        KEY_USE_CTRL_SPACE_WORKAROUND,"
        if target_false in c:
            c = c.replace(target_false, replacement_false)

        target_true = "        KEY_EXTRA_KEYS_TEXT_ALL_CAPS,\n        KEY_RUN_TERMUX_AM_SOCKET_SERVER"
        replacement_true = "        KEY_EXTRA_KEYS_TEXT_ALL_CAPS,\n        KEY_RUN_TERMUX_AM_SOCKET_SERVER,\n        KEY_TERMINAL_ONCLICK_URL_OPEN"
        if target_true in c:
            c = c.replace(target_true, replacement_true)
            print("[+] Enabled KEY_TERMINAL_ONCLICK_URL_OPEN by default in TermuxPropertyConstants.java")

        with open(prop_file, "w", encoding="utf-8") as f:
            f.write(c)

    # 3. TermuxTerminalExtraKeys.java (Handle IMG & FILE Extra Keys)
    extra_keys_file = os.path.join(termux_dir, "app/src/main/java/com/termux/app/terminal/io/TermuxTerminalExtraKeys.java")
    if os.path.exists(extra_keys_file):
        with open(extra_keys_file, "r", encoding="utf-8") as f:
            c = f.read()

        target_paste = """        } else if ("PASTE".equals(key)) {
            if(mTermuxTerminalSessionActivityClient != null)
                mTermuxTerminalSessionActivityClient.onPasteTextFromClipboard(null);"""

        replacement_paste = """        } else if ("PASTE".equals(key)) {
            if(mTermuxTerminalSessionActivityClient != null)
                mTermuxTerminalSessionActivityClient.onPasteTextFromClipboard(null);
        } else if ("IMG".equals(key) || "IMAGE".equals(key)) {
            mActivity.pickFileOrImage(true);
        } else if ("FILE".equals(key)) {
            mActivity.pickFileOrImage(false);"""

        if target_paste in c and "pickFileOrImage" not in c:
            c = c.replace(target_paste, replacement_paste)
            print("[+] Added IMG and FILE key handlers in TermuxTerminalExtraKeys.java")

        with open(extra_keys_file, "w", encoding="utf-8") as f:
            f.write(c)

    # 4. activity_termux.xml (Drawer Add Image & Add File Buttons)
    xml_file = os.path.join(termux_dir, "app/src/main/res/layout/activity_termux.xml")
    if os.path.exists(xml_file):
        with open(xml_file, "r", encoding="utf-8") as f:
            c = f.read()

        target_xml = """                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/new_session_button"
                        style="?android:attr/buttonBarButtonStyle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="@string/action_new_session" />
                </LinearLayout>"""

        replacement_xml = """                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/new_session_button"
                        style="?android:attr/buttonBarButtonStyle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="@string/action_new_session" />
                </LinearLayout>

                <LinearLayout
                    style="?android:attr/buttonBarStyle"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal">

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/add_image_button"
                        style="?android:attr/buttonBarButtonStyle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Add Image" />

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/add_file_button"
                        style="?android:attr/buttonBarButtonStyle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Add File" />
                </LinearLayout>

                <LinearLayout
                    style="?android:attr/buttonBarStyle"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal">

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/unlock_storage_button"
                        style="?android:attr/buttonBarButtonStyle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="All Files &amp; USB" />

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/developer_options_button"
                        style="?android:attr/buttonBarButtonStyle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Device Control" />
                </LinearLayout>"""

        if target_xml in c and "add_image_button" not in c:
            c = c.replace(target_xml, replacement_xml)
            print("[+] Added Add Image and Add File buttons to drawer in activity_termux.xml")

        with open(xml_file, "w", encoding="utf-8") as f:
            f.write(c)

    # 5. TermuxActivity.java (Drag-Drop, File Picker, Context Menu)
    act_file = os.path.join(termux_dir, "app/src/main/java/com/termux/app/TermuxActivity.java")
    if os.path.exists(act_file):
        with open(act_file, "r", encoding="utf-8") as f:
            c = f.read()

        target_import = "import android.widget.Toast;"
        replacement_import = """import android.widget.Toast;
import android.content.ClipData;
import android.database.Cursor;
import android.provider.OpenableColumns;
import android.view.DragEvent;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;"""

        if target_import in c and "import android.view.DragEvent;" not in c:
            c = c.replace(target_import, replacement_import, 1)
            print("[+] Added imports in TermuxActivity.java")

        target_tv = """        mTerminalView = findViewById(R.id.terminal_view);
        mTerminalView.setTerminalViewClient(mTermuxTerminalViewClient);"""

        replacement_tv = """        mTerminalView = findViewById(R.id.terminal_view);
        mTerminalView.setTerminalViewClient(mTermuxTerminalViewClient);
        mTerminalView.setOnDragListener((v, event) -> handleTerminalDragDrop(event));"""

        if target_tv in c and "handleTerminalDragDrop" not in c:
            c = c.replace(target_tv, replacement_tv, 1)
            print("[+] Set OnDragListener on TerminalView in TermuxActivity.java")

        target_drawer = """        findViewById(R.id.toggle_keyboard_button).setOnLongClickListener(v -> {
            toggleTerminalToolbar();
            return true;
        });"""

        replacement_drawer = """        findViewById(R.id.toggle_keyboard_button).setOnLongClickListener(v -> {
            toggleTerminalToolbar();
            return true;
        });

        View addImgBtn = findViewById(R.id.add_image_button);
        if (addImgBtn != null) {
            addImgBtn.setOnClickListener(v -> {
                pickFileOrImage(true);
                getDrawer().closeDrawers();
            });
        }
        View addFileBtn = findViewById(R.id.add_file_button);
        if (addFileBtn != null) {
            addFileBtn.setOnClickListener(v -> {
                pickFileOrImage(false);
                getDrawer().closeDrawers();
            });
        }
        View unlockStorageBtn = findViewById(R.id.unlock_storage_button);
        if (unlockStorageBtn != null) {
            unlockStorageBtn.setOnClickListener(v -> {
                requestAllFilesAccess();
                getDrawer().closeDrawers();
            });
        }
        View devOptionsBtn = findViewById(R.id.developer_options_button);
        if (devOptionsBtn != null) {
            devOptionsBtn.setOnClickListener(v -> {
                openDeveloperOptions();
                getDrawer().closeDrawers();
            });
        }"""

        if target_drawer in c and "add_image_button" not in c:
            c = c.replace(target_drawer, replacement_drawer, 1)
            print("[+] Attached drawer button click listeners in TermuxActivity.java")

        target_cm = "menu.add(Menu.NONE, CONTEXT_MENU_SELECT_URL_ID, Menu.NONE, R.string.action_select_url);"
        replacement_cm = """menu.add(Menu.NONE, CONTEXT_MENU_SELECT_URL_ID, Menu.NONE, R.string.action_select_url);
        menu.add(Menu.NONE, CONTEXT_MENU_INSERT_IMAGE_ID, Menu.NONE, "Insert Image");
        menu.add(Menu.NONE, CONTEXT_MENU_INSERT_FILE_ID, Menu.NONE, "Insert File");
        menu.add(Menu.NONE, CONTEXT_MENU_UNLOCK_STORAGE_ID, Menu.NONE, "All Files & USB Access");
        menu.add(Menu.NONE, CONTEXT_MENU_DEV_OPTIONS_ID, Menu.NONE, "Device Control (ADB)");"""

        if target_cm in c and "CONTEXT_MENU_INSERT_IMAGE_ID" not in c:
            c = c.replace(target_cm, replacement_cm, 1)
            print("[+] Added Insert Image / File / Storage / ADB to context menu in TermuxActivity.java")

        target_cms = "case CONTEXT_MENU_SELECT_URL_ID:"
        replacement_cms = """case CONTEXT_MENU_INSERT_IMAGE_ID:
                pickFileOrImage(true);
                return true;
            case CONTEXT_MENU_INSERT_FILE_ID:
                pickFileOrImage(false);
                return true;
            case CONTEXT_MENU_UNLOCK_STORAGE_ID:
                requestAllFilesAccess();
                return true;
            case CONTEXT_MENU_DEV_OPTIONS_ID:
                openDeveloperOptions();
                return true;
            case CONTEXT_MENU_SELECT_URL_ID:"""

        if target_cms in c and "case CONTEXT_MENU_INSERT_IMAGE_ID:" not in c:
            c = c.replace(target_cms, replacement_cms, 1)
            print("[+] Handled context menu selection in TermuxActivity.java")

        target_actres = """        if (requestCode == PermissionUtils.REQUEST_GRANT_STORAGE_PERMISSION) {
            requestStoragePermission(true);
        }"""

        replacement_actres = """        if (requestCode == PermissionUtils.REQUEST_GRANT_STORAGE_PERMISSION) {
            requestStoragePermission(true);
        }
        if (requestCode == REQUEST_CODE_PICK_FILE && resultCode == RESULT_OK && data != null) {
            handleFilePickerResult(data);
        }"""

        if target_actres in c and "REQUEST_CODE_PICK_FILE" not in c:
            c = c.replace(target_actres, replacement_actres, 1)
            print("[+] Handled file picker result in TermuxActivity.java")

        helper_methods = """
    public static final int REQUEST_CODE_PICK_FILE = 2001;
    public static final int CONTEXT_MENU_INSERT_IMAGE_ID = 201;
    public static final int CONTEXT_MENU_INSERT_FILE_ID = 202;
    public static final int CONTEXT_MENU_UNLOCK_STORAGE_ID = 203;
    public static final int CONTEXT_MENU_DEV_OPTIONS_ID = 204;

    public void requestAllFilesAccess() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.R) {
            try {
                Intent intent = new Intent(android.provider.Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                intent.setData(Uri.parse("package:" + getPackageName()));
                startActivity(intent);
                Toast.makeText(this, "Enable 'Allow access to manage all files' for full device & USB access", Toast.LENGTH_LONG).show();
            } catch (Exception e) {
                try {
                    Intent intent = new Intent(android.provider.Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION);
                    startActivity(intent);
                    Toast.makeText(this, "Select Antigravity CLI and enable All Files Access", Toast.LENGTH_LONG).show();
                } catch (Exception ex) {
                    requestStoragePermission(true);
                }
            }
        } else {
            requestStoragePermission(true);
        }
    }

    public void openDeveloperOptions() {
        try {
            Intent intent = new Intent(android.provider.Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS);
            startActivity(intent);
            Toast.makeText(this, "Enable 'Wireless debugging' or 'USB debugging' to control this device", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            try {
                Intent intent = new Intent(android.provider.Settings.ACTION_DEVICE_INFO_SETTINGS);
                startActivity(intent);
                Toast.makeText(this, "Tap 'Build number' 7 times in About Phone to enable Developer Options", Toast.LENGTH_LONG).show();
            } catch (Exception ignored) {}
        }
    }

    public void pickFileOrImage(boolean imagesOnly) {
        Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
        intent.setType(imagesOnly ? "image/*" : "*/*");
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        try {
            startActivityForResult(Intent.createChooser(intent, imagesOnly ? "Select Image" : "Select File"), REQUEST_CODE_PICK_FILE);
        } catch (Exception e) {
            Logger.logStackTraceWithMessage(LOG_TAG, "Failed to start file picker", e);
            Toast.makeText(this, "Unable to open file picker: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    public boolean handleTerminalDragDrop(DragEvent event) {
        switch (event.getAction()) {
            case DragEvent.ACTION_DRAG_STARTED:
                return true;
            case DragEvent.ACTION_DRAG_ENTERED:
            case DragEvent.ACTION_DRAG_LOCATION:
            case DragEvent.ACTION_DRAG_EXITED:
            case DragEvent.ACTION_DRAG_ENDED:
                return true;
            case DragEvent.ACTION_DROP:
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
                    try {
                        requestDragAndDropPermissions(event);
                    } catch (Throwable t) {
                        Logger.logStackTraceWithMessage(LOG_TAG, "Failed to request drag permissions", t);
                    }
                }
                ClipData clipData = event.getClipData();
                if (clipData != null) {
                    handleImportedClipData(clipData);
                    return true;
                }
                return false;
        }
        return false;
    }

    private void handleImportedClipData(ClipData clipData) {
        if (clipData == null || clipData.getItemCount() == 0) return;
        List<Uri> uris = new ArrayList<>();
        StringBuilder textSb = new StringBuilder();

        for (int i = 0; i < clipData.getItemCount(); i++) {
            ClipData.Item item = clipData.getItemAt(i);
            if (item.getUri() != null) {
                uris.add(item.getUri());
            } else if (item.getText() != null) {
                if (textSb.length() > 0) textSb.append(" ");
                textSb.append(item.getText().toString());
            }
        }

        if (!uris.isEmpty()) {
            importAndPasteUris(uris);
        } else if (textSb.length() > 0) {
            if (mTerminalView != null && mTerminalView.mEmulator != null) {
                mTerminalView.mEmulator.paste(textSb.toString());
            }
        }
    }

    private void handleFilePickerResult(Intent data) {
        List<Uri> uris = new ArrayList<>();
        if (data.getClipData() != null) {
            for (int i = 0; i < data.getClipData().getItemCount(); i++) {
                Uri u = data.getClipData().getItemAt(i).getUri();
                if (u != null) uris.add(u);
            }
        } else if (data.getData() != null) {
            uris.add(data.getData());
        }

        if (!uris.isEmpty()) {
            importAndPasteUris(uris);
        }
    }

    private void importAndPasteUris(List<Uri> uris) {
        Toast.makeText(this, "Importing " + uris.size() + " file(s)...", Toast.LENGTH_SHORT).show();
        new Thread(() -> {
            File uploadDir = new File(getFilesDir(), "home/uploads");
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }

            StringBuilder pathsResult = new StringBuilder();
            int importedCount = 0;

            for (Uri uri : uris) {
                try {
                    String fileName = getFileNameFromUri(uri);
                    File destFile = new File(uploadDir, fileName);
                    if (destFile.exists()) {
                        destFile = new File(uploadDir, System.currentTimeMillis() + "_" + fileName);
                    }

                    try (InputStream in = getContentResolver().openInputStream(uri);
                         OutputStream out = new FileOutputStream(destFile)) {
                        if (in != null) {
                            byte[] buffer = new byte[8192];
                            int len;
                            while ((len = in.read(buffer)) != -1) {
                                out.write(buffer, 0, len);
                            }
                            importedCount++;
                            String path = destFile.getAbsolutePath();
                            if (path.contains(" ")) {
                                path = "\\"" + path + "\\"";
                            }
                            if (pathsResult.length() > 0) pathsResult.append(" ");
                            pathsResult.append(path);
                        }
                    }
                } catch (Exception e) {
                    Logger.logStackTraceWithMessage(LOG_TAG, "Error importing URI: " + uri, e);
                }
            }

            final int count = importedCount;
            final String textToPaste = pathsResult.toString();

            runOnUiThread(() -> {
                if (count > 0 && mTerminalView != null && mTerminalView.mEmulator != null) {
                    mTerminalView.mEmulator.paste(textToPaste + " ");
                    Toast.makeText(TermuxActivity.this, "Inserted " + count + " file(s)", Toast.LENGTH_SHORT).show();
                } else if (count == 0) {
                    Toast.makeText(TermuxActivity.this, "Failed to import selected file(s)", Toast.LENGTH_SHORT).show();
                }
            });
        }).start();
    }

    private String getFileNameFromUri(Uri uri) {
        String name = null;
        if ("content".equals(uri.getScheme())) {
            try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
                if (cursor != null && cursor.moveToFirst()) {
                    int col = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                    if (col >= 0) {
                        name = cursor.getString(col);
                    }
                }
            } catch (Exception ignored) {}
        }
        if (name == null) {
            name = uri.getLastPathSegment();
        }
        if (name == null || name.trim().isEmpty()) {
            name = "file_" + System.currentTimeMillis();
        }
        return name.replaceAll("[\\\\/:*?\\"<>|]", "_");
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleWidgetCommand(intent);
    }

    private void handleWidgetCommand(Intent intent) {
        if (intent != null && intent.hasExtra("com.agycli.execute_command")) {
            String cmd = intent.getStringExtra("com.agycli.execute_command");
            intent.removeExtra("com.agycli.execute_command");
            if (cmd != null && !cmd.trim().isEmpty()) {
                if (mTerminalView != null) {
                    mTerminalView.postDelayed(() -> {
                        TerminalSession session = getCurrentSession();
                        if (session != null) {
                            session.write(cmd.trim() + "\n");
                        } else if (mTerminalView.mEmulator != null) {
                            mTerminalView.mEmulator.paste(cmd.trim() + "\n");
                        }
                    }, 400);
                }
            }
        }
    }
}
"""
        if "public void pickFileOrImage" not in c:
            last_brace = c.rfind("}")
            c = c[:last_brace] + helper_methods
            print("[+] Added file import, drag-drop and widget command methods in TermuxActivity.java")

        target_resume = "if (mIsInvalidState) return;"
        replacement_resume = """if (mIsInvalidState) return;
        handleWidgetCommand(getIntent());"""
        if target_resume in c and "handleWidgetCommand(getIntent());" not in c:
            c = c.replace(target_resume, replacement_resume, 1)
            print("[+] Added widget command handler to onResume() in TermuxActivity.java")

        with open(act_file, "w", encoding="utf-8") as f:
            f.write(c)

    # 6. AndroidManifest.xml (USB Host, Permissions & Widget Receiver)
    manifest_file = os.path.join(termux_dir, "app/src/main/AndroidManifest.xml")
    if os.path.exists(manifest_file):
        with open(manifest_file, "r", encoding="utf-8") as f:
            c = f.read()

        usb_perms = """    <uses-feature android:name="android.hardware.usb.host" android:required="false" />
    <uses-permission android:name="android.permission.USB_PERMISSION" />"""

        if "android.hardware.usb.host" not in c:
            c = c.replace("<uses-permission android:name=\"android.permission.INTERNET\" />",
                          "<uses-permission android:name=\"android.permission.INTERNET\" />\n" + usb_perms)

        widget_receiver = """
        <receiver
            android:name="com.termux.app.widget.AntigravityWidgetProvider"
            android:label="Antigravity Widget"
            android:exported="true">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
                <action android:name="com.agycli.action.WIDGET_UPDATE" />
                <action android:name="com.agycli.action.WIDGET_ACTION" />
            </intent-filter>
            <meta-data
                android:name="android.appwidget.provider"
                android:resource="@xml/antigravity_widget_provider_info" />
        </receiver>
    </application>"""

        if "AntigravityWidgetProvider" not in c:
            c = c.replace("</application>", widget_receiver)
            print("[+] Injected AntigravityWidgetProvider into AndroidManifest.xml")

        with open(manifest_file, "w", encoding="utf-8") as f:
            f.write(c)

    # 7. Antigravity Custom Widget Layouts, Drawables & Provider
    res_dir = os.path.join(termux_dir, "app/src/main/res")
    xml_dir = os.path.join(res_dir, "xml")
    layout_dir = os.path.join(res_dir, "layout")
    drawable_dir = os.path.join(res_dir, "drawable")
    widget_java_dir = os.path.join(termux_dir, "app/src/main/java/com/termux/app/widget")

    os.makedirs(xml_dir, exist_ok=True)
    os.makedirs(layout_dir, exist_ok=True)
    os.makedirs(drawable_dir, exist_ok=True)
    os.makedirs(widget_java_dir, exist_ok=True)

    # 7.1. Widget Provider Info XML
    provider_info_xml = """<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="180dp"
    android:minHeight="110dp"
    android:targetCellWidth="3"
    android:targetCellHeight="2"
    android:updatePeriodMillis="0"
    android:initialLayout="@layout/antigravity_app_widget"
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen" />
"""
    with open(os.path.join(xml_dir, "antigravity_widget_provider_info.xml"), "w", encoding="utf-8") as f:
        f.write(provider_info_xml)

    # 7.2. Widget Background and Button Drawables
    with open(os.path.join(drawable_dir, "widget_bg_rounded.xml"), "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#E60B0F19" />
    <corners android:radius="16dp" />
    <stroke android:width="1dp" android:color="#3300F0FF" />
</shape>
""")

    with open(os.path.join(drawable_dir, "widget_badge_bg.xml"), "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#2622C55E" />
    <corners android:radius="8dp" />
    <stroke android:width="1dp" android:color="#5922C55E" />
</shape>
""")

    with open(os.path.join(drawable_dir, "widget_btn_bg.xml"), "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#33151B28" />
    <corners android:radius="6dp" />
    <stroke android:width="1dp" android:color="#4D38BDF8" />
</shape>
""")

    # 7.3. Widget Layout XML
    widget_layout_xml = """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/widget_root"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@drawable/widget_bg_rounded">

    <ImageView
        android:id="@+id/widget_canvas"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:scaleType="fitXY"
        android:adjustViewBounds="true" />

    <LinearLayout
        android:id="@+id/widget_overlay"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical"
        android:padding="12dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical">

            <TextView
                android:id="@+id/widget_title"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:text="Antigravity Node"
                android:textColor="#00F0FF"
                android:textSize="14sp"
                android:textStyle="bold"
                android:singleLine="true" />

            <TextView
                android:id="@+id/widget_status"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:paddingStart="8dp"
                android:paddingEnd="8dp"
                android:paddingTop="2dp"
                android:paddingBottom="2dp"
                android:text="ONLINE"
                android:textColor="#22C55E"
                android:textSize="10sp"
                android:textStyle="bold"
                android:background="@drawable/widget_badge_bg" />
        </LinearLayout>

        <TextView
            android:id="@+id/widget_text"
            android:layout_width="match_parent"
            android:layout_height="0dp"
            android:layout_weight="1"
            android:layout_marginTop="6dp"
            android:layout_marginBottom="6dp"
            android:text="Tap to open Antigravity CLI"
            android:textColor="#E2E8F0"
            android:textSize="12sp"
            android:maxLines="6"
            android:ellipsize="end" />

        <LinearLayout
            android:id="@+id/widget_button_bar"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="end">

            <Button
                android:id="@+id/widget_btn_1"
                style="?android:attr/buttonBarStyle"
                android:layout_width="wrap_content"
                android:layout_height="28dp"
                android:minHeight="28dp"
                android:layout_marginEnd="4dp"
                android:paddingStart="8dp"
                android:paddingEnd="8dp"
                android:paddingTop="0dp"
                android:paddingBottom="0dp"
                android:text="Run AI"
                android:textColor="#00F0FF"
                android:textSize="11sp"
                android:background="@drawable/widget_btn_bg"
                android:visibility="gone" />

            <Button
                android:id="@+id/widget_btn_2"
                style="?android:attr/buttonBarStyle"
                android:layout_width="wrap_content"
                android:layout_height="28dp"
                android:minHeight="28dp"
                android:layout_marginEnd="4dp"
                android:paddingStart="8dp"
                android:paddingEnd="8dp"
                android:paddingTop="0dp"
                android:paddingBottom="0dp"
                android:text="Sync"
                android:textColor="#C084FC"
                android:textSize="11sp"
                android:background="@drawable/widget_btn_bg"
                android:visibility="gone" />

            <Button
                android:id="@+id/widget_btn_3"
                style="?android:attr/buttonBarStyle"
                android:layout_width="wrap_content"
                android:layout_height="28dp"
                android:minHeight="28dp"
                android:paddingStart="8dp"
                android:paddingEnd="8dp"
                android:paddingTop="0dp"
                android:paddingBottom="0dp"
                android:text="More"
                android:textColor="#38BDF8"
                android:textSize="11sp"
                android:background="@drawable/widget_btn_bg"
                android:visibility="gone" />
        </LinearLayout>
    </LinearLayout>
</FrameLayout>
"""
    with open(os.path.join(layout_dir, "antigravity_app_widget.xml"), "w", encoding="utf-8") as f:
        f.write(widget_layout_xml)

    # 7.4. AntigravityWidgetProvider.java
    provider_java = """package com.termux.app.widget;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.graphics.Shader;
import android.os.Build;
import android.view.View;
import android.widget.RemoteViews;

import com.termux.R;
import com.termux.app.TermuxActivity;

import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;

public class AntigravityWidgetProvider extends AppWidgetProvider {

    public static final String ACTION_WIDGET_UPDATE = "com.agycli.action.WIDGET_UPDATE";
    public static final String ACTION_WIDGET_ACTION = "com.agycli.action.WIDGET_ACTION";
    public static final String EXTRA_BTN_ID = "com.agycli.extra.BTN_ID";

    @Override
    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {
        for (int appWidgetId : appWidgetIds) {
            updateWidget(context, appWidgetManager, appWidgetId);
        }
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        super.onReceive(context, intent);
        String action = intent != null ? intent.getAction() : null;

        if (ACTION_WIDGET_UPDATE.equals(action) ||
            AppWidgetManager.ACTION_APPWIDGET_UPDATE.equals(action)) {
            AppWidgetManager manager = AppWidgetManager.getInstance(context);
            ComponentName name = new ComponentName(context, AntigravityWidgetProvider.class);
            int[] ids = manager.getAppWidgetIds(name);
            if (ids != null && ids.length > 0) {
                onUpdate(context, manager, ids);
            }
        }
    }

    private static File findFile(Context context, String relPath) {
        File f1 = new File("/data/data/" + context.getPackageName() + "/files/home/" + relPath);
        if (f1.exists()) return f1;
        File f2 = new File(context.getFilesDir(), "home/" + relPath);
        if (f2.exists()) return f2;
        File f3 = new File("/sdcard/" + relPath);
        if (f3.exists()) return f3;
        return f1;
    }

    public static void updateWidget(Context context, AppWidgetManager manager, int appWidgetId) {
        RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.antigravity_app_widget);

        File jsonFile = findFile(context, ".antigravity/widgets/widget.json");
        JSONObject json = null;
        if (jsonFile.exists()) {
            try {
                FileInputStream fis = new FileInputStream(jsonFile);
                byte[] data = new byte[(int) jsonFile.length()];
                fis.read(data);
                fis.close();
                json = new JSONObject(new String(data, "UTF-8"));
            } catch (Exception ignored) {}
        }

        int w = 800;
        int h = 480;

        // 1. Custom Shape & Background Rendering via Native Android Canvas
        String shape = json != null ? json.optString("shape", "chamfer") : "chamfer";
        String bgColor1Str = json != null ? json.optString("bg", "#E60B0F19") : "#E60B0F19";
        String bgColor2Str = json != null ? json.optString("bg2", bgColor1Str) : bgColor1Str;
        String borderColorStr = json != null ? json.optString("border", "#00F0FF") : "#00F0FF";
        float borderWidth = json != null ? (float) json.optDouble("border_width", 3.0) : 3.0f;
        float radius = json != null ? (float) json.optDouble("radius", 24.0) : 24.0f;

        int bgColor1 = parseColor(bgColor1Str, Color.parseColor("#0B0F19"));
        int bgColor2 = parseColor(bgColor2Str, bgColor1);
        int borderColor = parseColor(borderColorStr, Color.parseColor("#00F0FF"));

        Bitmap canvasBitmap = generateShapeBitmap(w, h, shape, bgColor1, bgColor2, borderColor, borderWidth, radius);

        // 2. Custom Image / Graphic Layer (if provided)
        File imageFile = findFile(context, ".antigravity/widgets/widget.png");
        String customImagePath = json != null ? json.optString("canvas_image", "") : "";
        if (!customImagePath.isEmpty()) {
            File customF = new File(customImagePath);
            if (customF.exists()) imageFile = customF;
        }

        if (imageFile != null && imageFile.exists()) {
            try {
                Bitmap userBmp = BitmapFactory.decodeFile(imageFile.getAbsolutePath());
                if (userBmp != null) {
                    Canvas compositeCanvas = new Canvas(canvasBitmap);
                    RectF dest = new RectF(0, 0, w, h);
                    compositeCanvas.drawBitmap(userBmp, null, dest, null);
                }
            } catch (Exception ignored) {}
        }

        views.setImageViewBitmap(R.id.widget_canvas, canvasBitmap);
        views.setViewVisibility(R.id.widget_canvas, View.VISIBLE);

        // 3. Overlay Visibility (Title, status, text, buttons)
        boolean showOverlay = json == null || json.optBoolean("show_overlay", true);
        views.setViewVisibility(R.id.widget_overlay, showOverlay ? View.VISIBLE : View.GONE);

        if (json != null) {
            String title = json.optString("title", "Antigravity CLI");
            views.setTextViewText(R.id.widget_title, title);
            views.setTextColor(R.id.widget_title, parseColor(json.optString("title_color", "#00F0FF"), Color.parseColor("#00F0FF")));

            String status = json.optString("status", "ONLINE");
            views.setTextViewText(R.id.widget_status, status);
            views.setTextColor(R.id.widget_status, parseColor(json.optString("status_color", "#22C55E"), Color.parseColor("#22C55E")));

            String text = json.optString("text", "Tap to open Antigravity CLI");
            views.setTextViewText(R.id.widget_text, text);
            views.setTextColor(R.id.widget_text, parseColor(json.optString("text_color", "#E2E8F0"), Color.parseColor("#E2E8F0")));

            bindButton(context, views, R.id.widget_btn_1, json.optJSONObject("btn1"), 1);
            bindButton(context, views, R.id.widget_btn_2, json.optJSONObject("btn2"), 2);
            bindButton(context, views, R.id.widget_btn_3, json.optJSONObject("btn3"), 3);
        } else {
            views.setTextViewText(R.id.widget_title, "Antigravity CLI");
            views.setTextViewText(R.id.widget_status, "ONLINE");
            views.setTextViewText(R.id.widget_text, "Ready. Tap to open terminal.\\nRun 'agy-widget help' to customize.");
            views.setViewVisibility(R.id.widget_btn_1, View.GONE);
            views.setViewVisibility(R.id.widget_btn_2, View.GONE);
            views.setViewVisibility(R.id.widget_btn_3, View.GONE);
        }

        // Root Click: Tap card to open TermuxActivity or run action
        String clickAction = json != null ? json.optString("click_action", "open") : "open";
        Intent rootIntent = new Intent(context, TermuxActivity.class);
        rootIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        if (!"open".equalsIgnoreCase(clickAction)) {
            rootIntent.putExtra("com.agycli.execute_command", clickAction);
        }
        int flags = Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE : PendingIntent.FLAG_UPDATE_CURRENT;
        PendingIntent rootPi = PendingIntent.getActivity(context, 0, rootIntent, flags);
        views.setOnClickPendingIntent(R.id.widget_root, rootPi);

        manager.updateAppWidget(appWidgetId, views);
    }

    private static void bindButton(Context context, RemoteViews views, int btnViewId, JSONObject btnJson, int btnId) {
        if (btnJson != null && btnJson.has("text") && !btnJson.optString("text").isEmpty()) {
            views.setTextViewText(btnViewId, btnJson.optString("text"));
            views.setViewVisibility(btnViewId, View.VISIBLE);

            String color = btnJson.optString("color", "");
            if (!color.isEmpty()) {
                views.setTextColor(btnViewId, parseColor(color, Color.parseColor("#00F0FF")));
            }

            String actionCmd = btnJson.optString("action", "");
            Intent btnIntent = new Intent(context, TermuxActivity.class);
            btnIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            if (!actionCmd.isEmpty()) {
                btnIntent.putExtra("com.agycli.execute_command", actionCmd);
            }
            int flags = Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE : PendingIntent.FLAG_UPDATE_CURRENT;
            PendingIntent pi = PendingIntent.getActivity(context, btnId, btnIntent, flags);
            views.setOnClickPendingIntent(btnViewId, pi);
        } else {
            views.setViewVisibility(btnViewId, View.GONE);
        }
    }

    private static int parseColor(String hex, int defaultColor) {
        if (hex == null || hex.trim().isEmpty()) return defaultColor;
        try {
            return Color.parseColor(hex.trim());
        } catch (Exception e) {
            return defaultColor;
        }
    }

    public static Bitmap generateShapeBitmap(int w, int h, String shape, int bgColor1, int bgColor2, int borderColor, float borderWidth, float radius) {
        Bitmap bitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);

        Paint fillPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        if (bgColor1 != bgColor2) {
            fillPaint.setShader(new LinearGradient(0, 0, w, h, bgColor1, bgColor2, Shader.TileMode.CLAMP));
        } else {
            fillPaint.setColor(bgColor1);
        }
        fillPaint.setStyle(Paint.Style.FILL);

        Paint strokePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        strokePaint.setColor(borderColor);
        strokePaint.setStrokeWidth(borderWidth);
        strokePaint.setStyle(Paint.Style.STROKE);

        float pad = borderWidth / 2f + 2f;
        RectF rect = new RectF(pad, pad, w - pad, h - pad);
        Path path = new Path();

        if ("circle".equalsIgnoreCase(shape)) {
            float cx = w / 2f;
            float cy = h / 2f;
            float r = Math.min(cx, cy) - pad;
            path.addCircle(cx, cy, r, Path.Direction.CW);
        } else if ("pill".equalsIgnoreCase(shape)) {
            float r = rect.height() / 2f;
            path.addRoundRect(rect, r, r, Path.Direction.CW);
        } else if ("chamfer".equalsIgnoreCase(shape)) {
            float c = Math.min(rect.width(), rect.height()) * 0.12f;
            path.moveTo(rect.left + c, rect.top);
            path.lineTo(rect.right - c, rect.top);
            path.lineTo(rect.right, rect.top + c);
            path.lineTo(rect.right, rect.bottom - c);
            path.lineTo(rect.right - c, rect.bottom);
            path.lineTo(rect.left + c, rect.bottom);
            path.lineTo(rect.left, rect.bottom - c);
            path.lineTo(rect.left, rect.top + c);
            path.close();
        } else if ("hex".equalsIgnoreCase(shape)) {
            float qw = rect.width() * 0.18f;
            float my = rect.centerY();
            path.moveTo(rect.left + qw, rect.top);
            path.lineTo(rect.right - qw, rect.top);
            path.lineTo(rect.right, my);
            path.lineTo(rect.right - qw, rect.bottom);
            path.lineTo(rect.left + qw, rect.bottom);
            path.lineTo(rect.left, my);
            path.close();
        } else {
            float r = radius > 0 ? radius : 24f;
            path.addRoundRect(rect, r, r, Path.Direction.CW);
        }

        canvas.drawPath(path, fillPaint);
        if (borderWidth > 0 && borderColor != Color.TRANSPARENT) {
            canvas.drawPath(path, strokePaint);
        }
        return bitmap;
    }
}
"""
    with open(os.path.join(widget_java_dir, "AntigravityWidgetProvider.java"), "w", encoding="utf-8") as f:
        f.write(provider_java)

    print("[✓] Successfully injected Antigravity Custom Widget engine into Termux project!")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "./termux-src"
    patch_termux(target_dir)
