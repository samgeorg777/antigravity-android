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
                            session.write(cmd.trim() + "\\\\n");
                        } else if (mTerminalView.mEmulator != null) {
                            mTerminalView.mEmulator.paste(cmd.trim() + "\\\\n");
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
    <uses-permission android:name="android.permission.USB_PERMISSION" />
    <uses-permission android:name="android.permission.VIBRATE" />"""

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
                <action android:name="com.agycli.action.WIDGET_REFRESH" />
                <action android:name="com.agycli.action.WIDGET_CYCLE_THEME" />
                <action android:name="com.agycli.action.WIDGET_EXECUTE" />
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
    <solid android:color="#2600F0FF" />
    <corners android:radius="6dp" />
    <stroke android:width="1dp" android:color="#4D00F0FF" />
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

    # 7.3. Live Animated & Interactive Widget Layout XML
    widget_layout_xml = """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/widget_root"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@drawable/widget_bg_rounded"
    android:clickable="true"
    android:focusable="true">

    <ImageView
        android:id="@+id/widget_canvas"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:scaleType="fitXY"
        android:adjustViewBounds="true"
        android:clickable="false"
        android:focusable="false" />

    <LinearLayout
        android:id="@+id/widget_overlay"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical"
        android:padding="11dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="▲ "
                android:textColor="#00F0FF"
                android:textSize="13sp"
                android:textStyle="bold" />

            <TextView
                android:id="@+id/widget_title"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:text="ANTIGRAVITY // NODE"
                android:textColor="#00F0FF"
                android:textSize="13sp"
                android:textStyle="bold"
                android:singleLine="true" />

            <!-- Live Animated ViewFlipper (Cycles frames automatically every 1.5s) -->
            <ViewFlipper
                android:id="@+id/widget_flipper"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:autoStart="true"
                android:flipInterval="1500">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:paddingStart="7dp"
                    android:paddingEnd="7dp"
                    android:paddingTop="2dp"
                    android:paddingBottom="2dp"
                    android:text="● LIVE"
                    android:textColor="#22C55E"
                    android:textSize="10sp"
                    android:textStyle="bold"
                    android:background="@drawable/widget_badge_bg" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:paddingStart="7dp"
                    android:paddingEnd="7dp"
                    android:paddingTop="2dp"
                    android:paddingBottom="2dp"
                    android:text="◈ AI CORE"
                    android:textColor="#00F0FF"
                    android:textSize="10sp"
                    android:textStyle="bold"
                    android:background="@drawable/widget_badge_bg" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:paddingStart="7dp"
                    android:paddingEnd="7dp"
                    android:paddingTop="2dp"
                    android:paddingBottom="2dp"
                    android:text="✦ QUANTUM"
                    android:textColor="#C084FC"
                    android:textSize="10sp"
                    android:textStyle="bold"
                    android:background="@drawable/widget_badge_bg" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:paddingStart="7dp"
                    android:paddingEnd="7dp"
                    android:paddingTop="2dp"
                    android:paddingBottom="2dp"
                    android:text="▲ ACTIVE"
                    android:textColor="#FFD166"
                    android:textSize="10sp"
                    android:textStyle="bold"
                    android:background="@drawable/widget_badge_bg" />
            </ViewFlipper>

            <TextView
                android:id="@+id/widget_status"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:paddingStart="7dp"
                android:paddingEnd="7dp"
                android:paddingTop="2dp"
                android:paddingBottom="2dp"
                android:text="ONLINE"
                android:textColor="#22C55E"
                android:textSize="10sp"
                android:textStyle="bold"
                android:background="@drawable/widget_badge_bg"
                android:visibility="gone" />
        </LinearLayout>

        <TextView
            android:id="@+id/widget_text"
            android:layout_width="match_parent"
            android:layout_height="0dp"
            android:layout_weight="1"
            android:layout_marginTop="4dp"
            android:layout_marginBottom="4dp"
            android:text="Loading system telemetry..."
            android:textColor="#E2E8F0"
            android:textSize="11sp"
            android:lineSpacingExtra="2dp"
            android:gravity="bottom"
            android:maxLines="4"
            android:ellipsize="end" />

        <LinearLayout
            android:id="@+id/widget_button_bar"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical">

            <TextView
                android:id="@+id/widget_btn_1"
                android:layout_width="0dp"
                android:layout_height="28dp"
                android:layout_weight="1"
                android:gravity="center"
                android:layout_marginEnd="3dp"
                android:text="⚡ Ask AI"
                android:textColor="#00F0FF"
                android:textSize="11sp"
                android:textStyle="bold"
                android:background="@drawable/widget_btn_bg"
                android:clickable="true"
                android:focusable="true" />

            <TextView
                android:id="@+id/widget_btn_2"
                android:layout_width="0dp"
                android:layout_height="28dp"
                android:layout_weight="1"
                android:gravity="center"
                android:layout_marginEnd="3dp"
                android:text="🔄 Refresh"
                android:textColor="#22C55E"
                android:textSize="11sp"
                android:textStyle="bold"
                android:background="@drawable/widget_btn_bg"
                android:clickable="true"
                android:focusable="true" />

            <TextView
                android:id="@+id/widget_btn_3"
                android:layout_width="0dp"
                android:layout_height="28dp"
                android:layout_weight="1"
                android:gravity="center"
                android:layout_marginEnd="3dp"
                android:text="🎨 Theme"
                android:textColor="#C084FC"
                android:textSize="11sp"
                android:textStyle="bold"
                android:background="@drawable/widget_btn_bg"
                android:clickable="true"
                android:focusable="true" />

            <TextView
                android:id="@+id/widget_btn_4"
                android:layout_width="0dp"
                android:layout_height="28dp"
                android:layout_weight="1"
                android:gravity="center"
                android:text="📱 Open"
                android:textColor="#38BDF8"
                android:textSize="11sp"
                android:textStyle="bold"
                android:background="@drawable/widget_btn_bg"
                android:clickable="true"
                android:focusable="true" />
        </LinearLayout>
    </LinearLayout>
</FrameLayout>
"""
    with open(os.path.join(layout_dir, "antigravity_app_widget.xml"), "w", encoding="utf-8") as f:
        f.write(widget_layout_xml)

    # 7.4. AntigravityWidgetProvider.java (Full Interactive & Live Animated Provider)
    provider_java = r"""package com.termux.app.widget;

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
import android.net.Uri;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.View;
import android.widget.RemoteViews;
import android.widget.Toast;

import com.termux.R;
import com.termux.app.TermuxActivity;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class AntigravityWidgetProvider extends AppWidgetProvider {

    public static final String ACTION_WIDGET_UPDATE = "com.agycli.action.WIDGET_UPDATE";
    public static final String ACTION_WIDGET_REFRESH = "com.agycli.action.WIDGET_REFRESH";
    public static final String ACTION_WIDGET_CYCLE_THEME = "com.agycli.action.WIDGET_CYCLE_THEME";
    public static final String ACTION_WIDGET_EXECUTE = "com.agycli.action.WIDGET_EXECUTE";
    public static final String EXTRA_COMMAND = "com.agycli.extra.COMMAND";
    public static final String EXTRA_BTN_ID = "com.agycli.extra.BTN_ID";

    private static final String[] THEME_SHAPES = {"chamfer", "matrix", "pill", "hex", "rounded_rect", "nothing_pet"};
    private static int sThemeIndex = 0;

    // In-memory live state for immediate interactive feedback without disk lag
    private static volatile boolean sIsSleeping = false;
    private static volatile String sCurrentPetState = "idle";
    private static volatile int sPetFrame = 0;
    private static volatile String sPetMoodText = null;
    private static volatile String sPetStatusText = null;
    private static volatile String sPetStatusColor = null;

    // Cat Bitmap definitions (18x18 subgrid)
    private static final String[] CAT_IDLE_1 = {
        "....##......##....",
        "...####....####...",
        "...######.######..",
        "..##############..",
        "..##############..",
        "..##..######..##..",
        "..##..######..##..",
        "..##############..",
        "...############...",
        "....##########....",
        ".....########.....",
        "....##########....",
        "...############...",
        "..##############..",
        "..##############..",
        "..####.####.####..",
        "..####.####.####..",
        "...##...##...##..."
    };

    private static final String[] CAT_IDLE_2 = {
        "....##......##....",
        "...####....####...",
        "...######.######..",
        "..##############..",
        "..##############..",
        "..##############..",
        "..##############..",
        "..##############..",
        "...############...",
        "....##########....",
        ".....########.....",
        "....##########....",
        "...############...",
        "..##############..",
        "..##############..",
        "..####.####.####..",
        "..####.####.####..",
        "...##...##...###.."
    };

    private static final String[] CAT_SLEEP_1 = {
        "..................",
        "..................",
        "..................",
        "..................",
        "..................",
        "..................",
        ".....########.....",
        "...############...",
        "..##############..",
        "..##############..",
        "..##..######..##..",
        "..##############..",
        "...############...",
        "....##########....",
        ".....########.....",
        "......######......",
        "..................",
        ".................."
    };

    private static final String[] CAT_SLEEP_2 = {
        "..................",
        "..................",
        "..................",
        "..................",
        "..................",
        "......#...#.......",
        ".....########.....",
        "...############...",
        "..##############..",
        "..##############..",
        "..##..######..##..",
        "..##############..",
        "...############...",
        "....##########....",
        ".....########.....",
        "......######......",
        "..................",
        ".................."
    };

    private static final String[] SPRITE_HEART = {
        "....##....##....",
        "...####..####...",
        "..############..",
        "..############..",
        "...##########...",
        "....########....",
        ".....######.....",
        "......####......",
        ".......##.......",
        "................"
    };

    private static final String[] SPRITE_FISH = {
        "......##........",
        "....######..#...",
        "...########.##..",
        "...########.###.",
        "....######..##..",
        "......##....#...",
        "................",
        "................"
    };

    @Override
    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {
        for (int appWidgetId : appWidgetIds) {
            updateWidget(context, appWidgetManager, appWidgetId);
        }
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        super.onReceive(context, intent);
        if (intent == null) return;
        String action = intent.getAction();

        if (ACTION_WIDGET_UPDATE.equals(action) ||
            AppWidgetManager.ACTION_APPWIDGET_UPDATE.equals(action)) {
            refreshAllWidgets(context);
        } else if (ACTION_WIDGET_REFRESH.equals(action)) {
            vibrate(context, 35);
            Toast.makeText(context, "⚡ Telemetry Refreshed", Toast.LENGTH_SHORT).show();
            refreshAllWidgets(context);
        } else if (ACTION_WIDGET_CYCLE_THEME.equals(action)) {
            vibrate(context, 45);
            cycleTheme(context);
            refreshAllWidgets(context);
        } else if (ACTION_WIDGET_EXECUTE.equals(action)) {
            String cmd = intent.getStringExtra(EXTRA_COMMAND);
            if (cmd == null) cmd = "";
            handleWidgetAction(context, cmd.trim());
        }
    }

    private static void handleWidgetAction(Context context, String cmd) {
        // 1. Explicit Open / Terminal actions
        if ("open".equalsIgnoreCase(cmd) || "launch".equalsIgnoreCase(cmd) ||
            cmd.startsWith("open:") || cmd.startsWith("terminal:")) {
            vibrate(context, 35);
            String termCmd = "";
            if (cmd.startsWith("open:")) {
                termCmd = cmd.substring(5).trim();
            } else if (cmd.startsWith("terminal:")) {
                termCmd = cmd.substring(9).trim();
            }
            launchTerminal(context, termCmd);
            return;
        }

        // 2. Refresh action
        if ("refresh".equalsIgnoreCase(cmd) || ACTION_WIDGET_REFRESH.equals(cmd)) {
            vibrate(context, 35);
            refreshAllWidgets(context);
            return;
        }

        // 3. Theme cycle action
        if ("theme".equalsIgnoreCase(cmd) || "cycle_theme".equalsIgnoreCase(cmd) || ACTION_WIDGET_CYCLE_THEME.equals(cmd)) {
            vibrate(context, 45);
            cycleTheme(context);
            refreshAllWidgets(context);
            return;
        }

        // 4. Pet actions (In-place on home screen - NEVER opens Termux!)
        String lowerCmd = cmd.toLowerCase(Locale.US);
        if (lowerCmd.equals("pet") || lowerCmd.startsWith("state:pet") || lowerCmd.contains("pet the cat") || lowerCmd.equals("love")) {
            handlePetAction(context, "pet");
            return;
        }

        if (lowerCmd.equals("fish") || lowerCmd.equals("feed") || lowerCmd.startsWith("state:fish") || lowerCmd.startsWith("state:feed") || lowerCmd.contains("fish") || lowerCmd.contains("feed")) {
            handlePetAction(context, "fish");
            return;
        }

        if (lowerCmd.equals("sleep") || lowerCmd.startsWith("state:sleep") || lowerCmd.startsWith("toggle:sleep") || lowerCmd.contains("sleep")) {
            handlePetAction(context, "sleep");
            return;
        }

        // 5. Generic Custom State (state:<name>)
        if (cmd.startsWith("state:")) {
            String stateName = cmd.substring(6).trim();
            handleCustomState(context, stateName);
            return;
        }

        // 6. Generic Text Update (text:<msg>)
        if (cmd.startsWith("text:")) {
            vibrate(context, 25);
            String newText = cmd.substring(5).trim();
            sPetMoodText = newText;
            refreshAllWidgets(context);
            return;
        }

        // 7. Generic Silent Background Execution (e.g. bash scripts, device actions)
        // Does NOT open TermuxActivity!
        vibrate(context, 30);
        executeBackgroundCommand(context, cmd);
    }

    private static void handlePetAction(Context context, String petAction) {
        if ("sleep".equals(petAction)) {
            sIsSleeping = !sIsSleeping;
            vibrate(context, sIsSleeping ? 25 : 45);
            if (sIsSleeping) {
                sCurrentPetState = "sleep";
                sPetMoodText = "MOOD: SLEEPING 💤";
                sPetStatusText = "ASLEEP";
                sPetStatusColor = "#C084FC";
            } else {
                sCurrentPetState = "idle";
                sPetMoodText = "MOOD: AWAKE";
                sPetStatusText = "IDLE";
                sPetStatusColor = "#22C55E";
            }
            refreshAllWidgets(context);
            return;
        }

        // If sleeping, tapping pet or fish wakes up
        if (sIsSleeping) {
            sIsSleeping = false;
        }

        if ("pet".equals(petAction)) {
            vibrate(context, 45);
            sCurrentPetState = "pet";
            sPetMoodText = "MOOD: PURRING ♥";
            sPetStatusText = "HAPPY";
            sPetStatusColor = "#FF5370";
            sPetFrame = 0;
            refreshAllWidgets(context);

            new Thread(() -> {
                try {
                    Thread.sleep(300);
                    sPetFrame = 1;
                    postWidgetRefresh(context);

                    Thread.sleep(300);
                    sPetFrame = 2;
                    postWidgetRefresh(context);

                    Thread.sleep(300);
                    sPetFrame = 0;
                    postWidgetRefresh(context);

                    Thread.sleep(2600);

                    if (!sIsSleeping && "pet".equals(sCurrentPetState)) {
                        sCurrentPetState = "idle";
                        sPetMoodText = "MOOD: CHILL";
                        sPetStatusText = "IDLE";
                        sPetStatusColor = "#22C55E";
                        sPetFrame = 0;
                        postWidgetRefresh(context);
                    }
                } catch (Exception ignored) {}
            }).start();
            return;
        }

        if ("fish".equals(petAction)) {
            vibratePattern(context, new long[]{0, 30, 60, 40});
            sCurrentPetState = "fish";
            sPetMoodText = "MOOD: MUNCHING 🐟";
            sPetStatusText = "FEEDING";
            sPetStatusColor = "#38BDF8";
            sPetFrame = 0;
            refreshAllWidgets(context);

            new Thread(() -> {
                try {
                    Thread.sleep(350);
                    sPetFrame = 1;
                    postWidgetRefresh(context);

                    Thread.sleep(350);
                    sPetFrame = 2;
                    postWidgetRefresh(context);

                    Thread.sleep(350);
                    sPetFrame = 0;
                    postWidgetRefresh(context);

                    Thread.sleep(2800);

                    if (!sIsSleeping && "fish".equals(sCurrentPetState)) {
                        sCurrentPetState = "idle";
                        sPetMoodText = "MOOD: CHILL";
                        sPetStatusText = "IDLE";
                        sPetStatusColor = "#22C55E";
                        sPetFrame = 0;
                        postWidgetRefresh(context);
                    }
                } catch (Exception ignored) {}
            }).start();
            return;
        }
    }

    private static void postWidgetRefresh(Context context) {
        new Handler(Looper.getMainLooper()).post(() -> refreshAllWidgets(context));
    }

    private static void handleCustomState(Context context, String stateName) {
        vibrate(context, 35);
        try {
            File jsonFile = findFile(context, ".antigravity/widgets/widget.json");
            if (jsonFile.exists()) {
                FileInputStream fis = new FileInputStream(jsonFile);
                byte[] data = new byte[(int) jsonFile.length()];
                fis.read(data);
                fis.close();
                JSONObject json = new JSONObject(new String(data, "UTF-8"));
                JSONObject states = json.optJSONObject("states");
                if (states != null && states.has(stateName)) {
                    JSONObject st = states.getJSONObject(stateName);
                    if (st.has("text")) sPetMoodText = st.getString("text");
                    if (st.has("status")) sPetStatusText = st.getString("status");
                    if (st.has("status_color")) sPetStatusColor = st.getString("status_color");
                    sCurrentPetState = stateName;
                    refreshAllWidgets(context);

                    int autoRevert = st.optInt("auto_revert", 0);
                    if (autoRevert > 0) {
                        new Thread(() -> {
                            try {
                                Thread.sleep(autoRevert);
                                sCurrentPetState = "idle";
                                sPetMoodText = null;
                                sPetStatusText = null;
                                postWidgetRefresh(context);
                            } catch (Exception ignored) {}
                        }).start();
                    }
                    return;
                }
            }
        } catch (Exception ignored) {}
        sCurrentPetState = stateName;
        refreshAllWidgets(context);
    }

    private static void executeBackgroundCommand(Context context, String command) {
        if (command == null || command.trim().isEmpty()) return;
        new Thread(() -> {
            try {
                String cleanCmd = command.startsWith("bg:") ? command.substring(3).trim() : command;
                String bashPath = "/data/data/" + context.getPackageName() + "/files/usr/bin/bash";
                File bashFile = new File(bashPath);
                String[] cmdArray;
                if (bashFile.exists()) {
                    cmdArray = new String[]{bashPath, "-c", cleanCmd};
                } else {
                    cmdArray = new String[]{"/system/bin/sh", "-c", cleanCmd};
                }
                Process p = Runtime.getRuntime().exec(cmdArray);
                p.waitFor();
                postWidgetRefresh(context);
            } catch (Exception ignored) {}
        }).start();
    }

    private static void vibrate(Context context, long ms) {
        try {
            Vibrator v = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
            if (v != null && v.hasVibrator()) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    v.vibrate(VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE));
                } else {
                    v.vibrate(ms);
                }
            }
        } catch (Exception ignored) {}
    }

    private static void vibratePattern(Context context, long[] timings) {
        try {
            Vibrator v = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
            if (v != null && v.hasVibrator()) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    v.vibrate(VibrationEffect.createWaveform(timings, -1));
                } else {
                    v.vibrate(timings, -1);
                }
            }
        } catch (Exception ignored) {}
    }

    private static void launchTerminal(Context context, String command) {
        try {
            Intent actIntent = new Intent(context, TermuxActivity.class);
            actIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            if (command != null && !command.trim().isEmpty()) {
                actIntent.putExtra("com.agycli.execute_command", command);
                Toast.makeText(context, "⚡ Running: " + command, Toast.LENGTH_SHORT).show();
            }
            context.startActivity(actIntent);
        } catch (Exception e) {
            Toast.makeText(context, "Failed to launch: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    public static void refreshAllWidgets(Context context) {
        AppWidgetManager manager = AppWidgetManager.getInstance(context);
        ComponentName name = new ComponentName(context, AntigravityWidgetProvider.class);
        int[] ids = manager.getAppWidgetIds(name);
        if (ids != null && ids.length > 0) {
            for (int id : ids) {
                updateWidget(context, manager, id);
            }
        }
    }

    private static void cycleTheme(Context context) {
        sThemeIndex = (sThemeIndex + 1) % THEME_SHAPES.length;
        String newShape = THEME_SHAPES[sThemeIndex];
        try {
            File jsonFile = findFile(context, ".antigravity/widgets/widget.json");
            JSONObject json = new JSONObject();
            if (jsonFile.exists()) {
                FileInputStream fis = new FileInputStream(jsonFile);
                byte[] data = new byte[(int) jsonFile.length()];
                fis.read(data);
                fis.close();
                json = new JSONObject(new String(data, "UTF-8"));
            }

            if ("nothing_pet".equals(newShape)) {
                json.put("shape", "nothing_pet");
                json.put("title", "NOTHING OS • PET");
                json.put("title_color", "#888888");
                json.put("status", "IDLE");
                json.put("status_color", "#22C55E");
                json.put("text", "MOOD: CHILL");
                json.put("click_action", "pet");
            } else if ("chamfer".equals(newShape)) {
                json.put("shape", "chamfer");
                json.put("bg", "#E60B0F19");
                json.put("bg2", "#E6151B28");
                json.put("border", "#00F0FF");
                json.put("title", "ANTIGRAVITY // COSMIC");
                json.put("title_color", "#00F0FF");
                json.put("text", getLiveSystemStats());
                json.put("status", "");
                json.put("click_action", "open");
            } else if ("matrix".equals(newShape)) {
                json.put("shape", "rounded_rect");
                json.put("bg", "#F2030804");
                json.put("bg2", "#E6081409");
                json.put("border", "#22C55E");
                json.put("title", "ANTIGRAVITY // MATRIX");
                json.put("title_color", "#22C55E");
                json.put("text", getLiveSystemStats());
                json.put("status", "ROOT");
                json.put("status_color", "#22C55E");
                json.put("click_action", "open");
            } else if ("pill".equals(newShape)) {
                json.put("shape", "pill");
                json.put("bg", "#CC0F172A");
                json.put("bg2", "#CC1E293B");
                json.put("border", "#38BDF8");
                json.put("title", "ANTIGRAVITY // GLASS");
                json.put("title_color", "#38BDF8");
                json.put("text", getLiveSystemStats());
                json.put("status", "SYNCED");
                json.put("status_color", "#38BDF8");
                json.put("click_action", "open");
            } else if ("hex".equals(newShape)) {
                json.put("shape", "hex");
                json.put("bg", "#E6140B24");
                json.put("bg2", "#E62E1065");
                json.put("border", "#C084FC");
                json.put("title", "ANTIGRAVITY // TELEMETRY");
                json.put("title_color", "#C084FC");
                json.put("text", getLiveSystemStats());
                json.put("status", "MONITOR");
                json.put("status_color", "#C084FC");
                json.put("click_action", "open");
            } else {
                json.put("shape", "rounded_rect");
                json.put("bg", "#E60B0F19");
                json.put("bg2", "#E61F293D");
                json.put("border", "#FFD166");
                json.put("title", "ANTIGRAVITY // AMBER");
                json.put("title_color", "#FFD166");
                json.put("text", getLiveSystemStats());
                json.put("status", "READY");
                json.put("status_color", "#FFD166");
                json.put("click_action", "open");
            }

            File p = jsonFile.getParentFile();
            if (p != null) p.mkdirs();
            FileOutputStream fos = new FileOutputStream(jsonFile);
            fos.write(json.toString(2).getBytes("UTF-8"));
            fos.close();
            Toast.makeText(context, "🎨 Theme: " + newShape.toUpperCase(Locale.US), Toast.LENGTH_SHORT).show();
        } catch (Exception ignored) {}
    }

    private static File findFile(Context context, String relPath) {
        File f1 = new File("/data/data/" + context.getPackageName() + "/files/home/" + relPath);
        if (f1.exists()) return f1;
        File f2 = new File(context.getFilesDir(), "home/" + relPath);
        if (f2.exists()) return f2;
        File f3 = new File("/sdcard/" + relPath);
        if (f3.exists()) return f3;
        File f4 = new File("/data/data/com.termux/files/home/" + relPath);
        if (f4.exists()) return f4;
        return f1;
    }

    private static String getLiveSystemStats() {
        String battery = "85%";
        try {
            File bf = new File("/sys/class/power_supply/battery/capacity");
            if (bf.exists()) {
                BufferedReader br = new BufferedReader(new FileReader(bf));
                battery = br.readLine().trim() + "%";
                br.close();
            }
        } catch (Exception ignored) {}

        String mem = "RAM: 3.5 GB / 8.0 GB";
        try {
            File mf = new File("/proc/meminfo");
            if (mf.exists()) {
                BufferedReader br = new BufferedReader(new FileReader(mf));
                String totalLine = br.readLine();
                br.readLine();
                String availLine = br.readLine();
                br.close();
                if (totalLine != null && availLine != null) {
                    long totalKb = Long.parseLong(totalLine.replaceAll("\\D+", ""));
                    long availKb = Long.parseLong(availLine.replaceAll("\\D+", ""));
                    long usedKb = totalKb - availKb;
                    mem = String.format(Locale.US, "RAM: %.1f / %.1f GB", usedKb / 1048576.0, totalKb / 1048576.0);
                }
            }
        } catch (Exception ignored) {}

        SimpleDateFormat sdf = new SimpleDateFormat("HH:mm:ss  •  MMM dd", Locale.US);
        String timeStr = sdf.format(new Date());

        return "● " + mem + "  |  PWR: " + battery + "\n● " + timeStr + "\n● Antigravity Neural Engine: Ready";
    }

    private static PendingIntent makeBroadcastPendingIntent(Context context, String action, String command, int requestCode) {
        Intent intent = new Intent(context, AntigravityWidgetProvider.class);
        intent.setAction(action);
        if (command != null) {
            intent.putExtra(EXTRA_COMMAND, command);
        }
        intent.putExtra(EXTRA_BTN_ID, requestCode);
        String dataUri = "agycli://widget/action/" + requestCode + "/" + action + "/" + Uri.encode(command != null ? command : "");
        intent.setData(Uri.parse(dataUri));
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= PendingIntent.FLAG_IMMUTABLE;
        }
        return PendingIntent.getBroadcast(context, requestCode, intent, flags);
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

        String shape = json != null ? json.optString("shape", "chamfer") : "chamfer";
        String title = json != null ? json.optString("title", "ANTIGRAVITY // NODE") : "ANTIGRAVITY // NODE";

        boolean isPetMode = "nothing_pet".equalsIgnoreCase(shape) || "pet".equalsIgnoreCase(shape) ||
                            title.toUpperCase(Locale.US).contains("PET") ||
                            (json != null && json.has("btn1") && json.optJSONObject("btn1").optString("text", "").contains("Pet"));

        Bitmap canvasBitmap;
        if (isPetMode) {
            boolean isLight = json != null && json.optBoolean("light_theme", false);
            canvasBitmap = generateNothingPetBitmap(w, h, sCurrentPetState, sPetFrame, isLight);
        } else {
            String bgColor1Str = json != null ? json.optString("bg", "#E60B0F19") : "#E60B0F19";
            String bgColor2Str = json != null ? json.optString("bg2", bgColor1Str) : bgColor1Str;
            String borderColorStr = json != null ? json.optString("border", "#00F0FF") : "#00F0FF";
            float borderWidth = json != null ? (float) json.optDouble("border_width", 3.0) : 3.0f;
            float radius = json != null ? (float) json.optDouble("radius", 24.0) : 24.0f;

            int bgColor1 = parseColor(bgColor1Str, Color.parseColor("#0B0F19"));
            int bgColor2 = parseColor(bgColor2Str, bgColor1);
            int borderColor = parseColor(borderColorStr, Color.parseColor("#00F0FF"));

            canvasBitmap = generateShapeBitmap(w, h, shape, bgColor1, bgColor2, borderColor, borderWidth, radius);
        }

        // Custom canvas image or state-specific image
        File imageFile = null;
        if (json != null) {
            JSONObject states = json.optJSONObject("states");
            if (states != null && states.has(sCurrentPetState)) {
                String stImg = states.getJSONObject(sCurrentPetState).optString("image", "");
                if (!stImg.isEmpty()) {
                    File f = new File(stImg);
                    if (f.exists()) imageFile = f;
                }
            }
            if (imageFile == null) {
                String customImagePath = json.optString("canvas_image", "");
                if (!customImagePath.isEmpty()) {
                    File customF = new File(customImagePath);
                    if (customF.exists()) imageFile = customF;
                }
            }
        }
        if (imageFile == null && !isPetMode) {
            imageFile = findFile(context, ".antigravity/widgets/widget.png");
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

        boolean showOverlay = json == null || json.optBoolean("show_overlay", true);
        views.setViewVisibility(R.id.widget_overlay, showOverlay ? View.VISIBLE : View.GONE);

        // Header Title
        views.setTextViewText(R.id.widget_title, title);
        int titleColor = parseColor(json != null ? json.optString("title_color", isPetMode ? "#888888" : "#00F0FF") : "#00F0FF", Color.parseColor("#00F0FF"));
        views.setTextColor(R.id.widget_title, titleColor);

        // Status Badge vs Flipper
        String statusText = (isPetMode && sPetStatusText != null) ? sPetStatusText :
                            (json != null ? json.optString("status", isPetMode ? "IDLE" : "") : (isPetMode ? "IDLE" : ""));
        String statusColorStr = (isPetMode && sPetStatusColor != null) ? sPetStatusColor :
                                (json != null ? json.optString("status_color", "#22C55E") : "#22C55E");

        if (!statusText.isEmpty()) {
            views.setTextViewText(R.id.widget_status, statusText);
            views.setTextColor(R.id.widget_status, parseColor(statusColorStr, Color.parseColor("#22C55E")));
            views.setViewVisibility(R.id.widget_status, View.VISIBLE);
            views.setViewVisibility(R.id.widget_flipper, View.GONE);
        } else {
            views.setViewVisibility(R.id.widget_status, View.GONE);
            views.setViewVisibility(R.id.widget_flipper, View.VISIBLE);
        }

        // Body Text
        String bodyText = (isPetMode && sPetMoodText != null) ? sPetMoodText :
                          (json != null ? json.optString("text", isPetMode ? "MOOD: CHILL" : getLiveSystemStats()) : (isPetMode ? "MOOD: CHILL" : getLiveSystemStats()));
        views.setTextViewText(R.id.widget_text, bodyText);
        int textColor = parseColor(json != null ? json.optString("text_color", "#E2E8F0") : "#E2E8F0", Color.parseColor("#E2E8F0"));
        views.setTextColor(R.id.widget_text, textColor);

        // Buttons
        if (isPetMode) {
            bindInteractiveButton(context, views, R.id.widget_btn_1, json != null ? json.optJSONObject("btn1") : null, "❤️ Pet", "pet", 1);
            bindInteractiveButton(context, views, R.id.widget_btn_2, json != null ? json.optJSONObject("btn2") : null, "🐟 Fish", "fish", 2);
            bindInteractiveButton(context, views, R.id.widget_btn_3, json != null ? json.optJSONObject("btn3") : null, "💤 Sleep", "sleep", 3);
            bindInteractiveButton(context, views, R.id.widget_btn_4, json != null ? json.optJSONObject("btn4") : null, "📱 Open", "open", 4);
        } else if (json != null) {
            bindInteractiveButton(context, views, R.id.widget_btn_1, json.optJSONObject("btn1"), "⚡ Ask AI", "agy", 1);
            bindInteractiveButton(context, views, R.id.widget_btn_2, json.optJSONObject("btn2"), "🔄 Refresh", ACTION_WIDGET_REFRESH, 2);
            bindInteractiveButton(context, views, R.id.widget_btn_3, json.optJSONObject("btn3"), "🎨 Theme", ACTION_WIDGET_CYCLE_THEME, 3);
            bindInteractiveButton(context, views, R.id.widget_btn_4, json.optJSONObject("btn4"), "📱 Open", "open", 4);
        } else {
            bindInteractiveButton(context, views, R.id.widget_btn_1, null, "⚡ Ask AI", "agy", 1);
            bindInteractiveButton(context, views, R.id.widget_btn_2, null, "🔄 Refresh", ACTION_WIDGET_REFRESH, 2);
            bindInteractiveButton(context, views, R.id.widget_btn_3, null, "🎨 Theme", ACTION_WIDGET_CYCLE_THEME, 3);
            bindInteractiveButton(context, views, R.id.widget_btn_4, null, "📱 Open", "open", 4);
        }

        // Tap on Canvas / Widget Body
        String clickAction = json != null ? json.optString("click_action", isPetMode ? "pet" : "open") : (isPetMode ? "pet" : "open");
        views.setOnClickPendingIntent(R.id.widget_root, makeBroadcastPendingIntent(context, ACTION_WIDGET_EXECUTE, clickAction, 100));

        manager.updateAppWidget(appWidgetId, views);
    }

    private static void bindInteractiveButton(Context context, RemoteViews views, int btnViewId, JSONObject btnJson, String defaultText, String defaultAction, int btnId) {
        String label = defaultText;
        String action = defaultAction;
        String color = "";

        if (btnJson != null) {
            label = btnJson.optString("text", defaultText);
            action = btnJson.optString("action", defaultAction);
            color = btnJson.optString("color", "");
        }

        views.setTextViewText(btnViewId, label);
        views.setViewVisibility(btnViewId, View.VISIBLE);

        if (!color.isEmpty()) {
            views.setTextColor(btnViewId, parseColor(color, Color.parseColor("#00F0FF")));
        }

        PendingIntent pi;
        if (ACTION_WIDGET_REFRESH.equals(action) || "refresh".equalsIgnoreCase(action)) {
            pi = makeBroadcastPendingIntent(context, ACTION_WIDGET_REFRESH, null, btnId);
        } else if (ACTION_WIDGET_CYCLE_THEME.equals(action) || "theme".equalsIgnoreCase(action)) {
            pi = makeBroadcastPendingIntent(context, ACTION_WIDGET_CYCLE_THEME, null, btnId);
        } else {
            pi = makeBroadcastPendingIntent(context, ACTION_WIDGET_EXECUTE, action, btnId);
        }
        views.setOnClickPendingIntent(btnViewId, pi);
    }

    private static int parseColor(String hex, int defaultColor) {
        if (hex == null || hex.trim().isEmpty()) return defaultColor;
        try {
            return Color.parseColor(hex.trim());
        } catch (Exception e) {
            return defaultColor;
        }
    }

    public static Bitmap generateNothingPetBitmap(int w, int h, String state, int frame, boolean isLight) {
        Bitmap bitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);

        // 1. Background Card
        int cardBg = isLight ? Color.parseColor("#F4F5F5") : Color.parseColor("#111312");
        Paint bgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        bgPaint.setColor(cardBg);
        bgPaint.setStyle(Paint.Style.FILL);

        float pad = 4f;
        RectF cardRect = new RectF(pad, pad, w - pad, h - pad);
        float cardRadius = 36f;
        canvas.drawRoundRect(cardRect, cardRadius, cardRadius, bgPaint);

        // Border
        Paint borderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        borderPaint.setColor(isLight ? Color.argb(25, 0, 0, 0) : Color.argb(35, 255, 255, 255));
        borderPaint.setStyle(Paint.Style.STROKE);
        borderPaint.setStrokeWidth(2f);
        canvas.drawRoundRect(cardRect, cardRadius, cardRadius, borderPaint);

        // 2. Nothing OS 28x28 LED Dot Matrix
        int dotOff = isLight ? Color.parseColor("#DFE2E0") : Color.parseColor("#1C201E");
        int dotWhite = isLight ? Color.parseColor("#000000") : Color.parseColor("#FFFFFF");
        int dotRed = Color.parseColor("#D71921");
        int dotCyan = Color.parseColor("#38BDF8");

        Paint dotPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        dotPaint.setStyle(Paint.Style.FILL);

        int gridSize = 28;
        float dotSpacing = 11.5f;
        float dotRadius = dotSpacing * 0.36f;

        float matrixWidth = gridSize * dotSpacing;
        float matrixHeight = gridSize * dotSpacing;
        float startX = (w - matrixWidth) / 2f;
        float startY = 48f; // Below top bar, leaving space for text and buttons

        // Draw background inactive LED dots
        dotPaint.setColor(dotOff);
        for (int y = 0; y < gridSize; y++) {
            for (int x = 0; x < gridSize; x++) {
                float cx = startX + x * dotSpacing + dotSpacing / 2f;
                float cy = startY + y * dotSpacing + dotSpacing / 2f;
                canvas.drawCircle(cx, cy, dotRadius, dotPaint);
            }
        }

        // 3. Select Cat Sprite
        String[] catSprite;
        if ("sleep".equals(state)) {
            catSprite = (frame % 2 == 0) ? CAT_SLEEP_1 : CAT_SLEEP_2;
        } else if (frame == 1 || frame == 2) {
            catSprite = CAT_IDLE_2;
        } else {
            catSprite = CAT_IDLE_1;
        }

        // Subgrid start for cat (centered in 28x28 grid)
        int catStartX = 5;
        int catStartY = 7;

        dotPaint.setColor(dotWhite);
        for (int r = 0; r < catSprite.length; r++) {
            String row = catSprite[r];
            for (int c = 0; c < row.length(); c++) {
                if (row.charAt(c) == '#') {
                    int gx = catStartX + c;
                    int gy = catStartY + r;
                    if (gx >= 0 && gx < gridSize && gy >= 0 && gy < gridSize) {
                        float cx = startX + gx * dotSpacing + dotSpacing / 2f;
                        float cy = startY + gy * dotSpacing + dotSpacing / 2f;
                        canvas.drawCircle(cx, cy, dotRadius * 1.08f, dotPaint);
                    }
                }
            }
        }

        // 4. Draw Red Heart if state is pet
        if ("pet".equals(state)) {
            dotPaint.setColor(dotRed);
            int hStartX = 6;
            int hStartY = 1;
            float heartScale = (frame == 1) ? 1.25f : 1.15f;
            for (int r = 0; r < SPRITE_HEART.length; r++) {
                String row = SPRITE_HEART[r];
                for (int c = 0; c < row.length(); c++) {
                    if (row.charAt(c) == '#') {
                        int gx = hStartX + c;
                        int gy = hStartY + r;
                        if (gx >= 0 && gx < gridSize && gy >= 0 && gy < gridSize) {
                            float cx = startX + gx * dotSpacing + dotSpacing / 2f;
                            float cy = startY + gy * dotSpacing + dotSpacing / 2f;
                            canvas.drawCircle(cx, cy, dotRadius * heartScale, dotPaint);
                        }
                    }
                }
            }
        }

        // 5. Draw Blue Fish if state is fish
        if ("fish".equals(state)) {
            dotPaint.setColor(dotCyan);
            int fStartX = 6;
            int fStartY = (frame == 1) ? 3 : 2;
            for (int r = 0; r < SPRITE_FISH.length; r++) {
                String row = SPRITE_FISH[r];
                for (int c = 0; c < row.length(); c++) {
                    if (row.charAt(c) == '#') {
                        int gx = fStartX + c;
                        int gy = fStartY + r;
                        if (gx >= 0 && gx < gridSize && gy >= 0 && gy < gridSize) {
                            float cx = startX + gx * dotSpacing + dotSpacing / 2f;
                            float cy = startY + gy * dotSpacing + dotSpacing / 2f;
                            canvas.drawCircle(cx, cy, dotRadius * 1.15f, dotPaint);
                        }
                    }
                }
            }
        }

        // 6. Draw Floating Z's if state is sleep
        if ("sleep".equals(state)) {
            dotPaint.setColor(dotRed);
            int[][] zDots = {
                {20, 4}, {21, 3}, {22, 3}, {21, 4}, {20, 5}, {21, 5}, {22, 5},
                {24, 2}, {25, 2}, {24, 3}, {25, 3}
            };
            for (int[] pt : zDots) {
                int gx = pt[0];
                int gy = pt[1];
                if (gx < gridSize && gy >= 0) {
                    float cx = startX + gx * dotSpacing + dotSpacing / 2f;
                    float cy = startY + gy * dotSpacing + dotSpacing / 2f;
                    canvas.drawCircle(cx, cy, dotRadius * 1.1f, dotPaint);
                }
            }
        }

        return bitmap;
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
