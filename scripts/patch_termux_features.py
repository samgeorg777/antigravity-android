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
        }"""

        if target_drawer in c and "add_image_button" not in c:
            c = c.replace(target_drawer, replacement_drawer, 1)
            print("[+] Attached drawer button click listeners in TermuxActivity.java")

        target_cm = "menu.add(Menu.NONE, CONTEXT_MENU_SELECT_URL_ID, Menu.NONE, R.string.action_select_url);"
        replacement_cm = """menu.add(Menu.NONE, CONTEXT_MENU_SELECT_URL_ID, Menu.NONE, R.string.action_select_url);
        menu.add(Menu.NONE, CONTEXT_MENU_INSERT_IMAGE_ID, Menu.NONE, "Insert Image");
        menu.add(Menu.NONE, CONTEXT_MENU_INSERT_FILE_ID, Menu.NONE, "Insert File");"""

        if target_cm in c and "CONTEXT_MENU_INSERT_IMAGE_ID" not in c:
            c = c.replace(target_cm, replacement_cm, 1)
            print("[+] Added Insert Image / File to context menu in TermuxActivity.java")

        target_cms = "case CONTEXT_MENU_SELECT_URL_ID:"
        replacement_cms = """case CONTEXT_MENU_INSERT_IMAGE_ID:
                pickFileOrImage(true);
                return true;
            case CONTEXT_MENU_INSERT_FILE_ID:
                pickFileOrImage(false);
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
}
"""
        if "public void pickFileOrImage" not in c:
            last_brace = c.rfind("}")
            c = c[:last_brace] + helper_methods
            print("[+] Added file import and drag-drop helper methods in TermuxActivity.java")

        with open(act_file, "w", encoding="utf-8") as f:
            f.write(c)

    print("[✓] Finished patching Termux features successfully!")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "./termux-src"
    patch_termux(target_dir)
