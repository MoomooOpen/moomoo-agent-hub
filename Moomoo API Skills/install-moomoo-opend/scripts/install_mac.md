# macOS Installation Steps (moomoo OpenD)

The macOS installer is a **tar.gz archive**, downloaded directly from the software download server.

Archive internal structure:
```
moomoo_OpenD_x.x.xxxx_Mac/
├── moomoo_OpenD-GUI_x.x.xxxx_Mac.dmg   ← GUI installer image (mount and install)
├── moomoo_OpenD_x.x.xxxx_Mac.app       ← Command-line version (NOT GUI, do not install)
├── moomoo_OpenD_x.x.xxxx_Mac/
│   ├── MoomooOpenD                         ← Command-line main program
│   ├── OpenD.xml                           ← Config file
│   └── ...
├── fixrun.sh                             ← Path fix script
└── README.txt
```

**Important**: `.app` is the command-line version, `.dmg` is the GUI version. Always install the `.dmg` (GUI version).

The installer is approximately **374MB**, so the download may take a while. **Execute step by step**, with each step in a separate Bash call to avoid timeouts.

## Step One: Get the Latest Version Filename

Get the latest version filename via the `fetch-lasted-link` API redirect (**do not use WebFetch to visit the official download page**):

```bash
curl -sI "https://www.moomoo.com/download/fetch-lasted-link?name=opend-macos" | grep -i "^location:" | awk '{print $2}' | tr -d '\r'
```

If the API returns a 400 error, use the "Fallback Download Method" in SKILL.md.

Extract the filename from the redirect URL (e.g., `moomoo_OpenD_10.2.6208_Mac.tar.gz`).

## Step Two: Download from softwaredownload Domain

Construct the download URL using the extracted filename. Use Bash tool with **timeout set to 600000** (10 minutes).

**Clean up existing files before downloading** to avoid conflicts with old versions:

```bash
rm -f "$HOME/Desktop/MoomooOpenD.tar.gz"
# Also clean up any existing extracted directories
rm -rf "$HOME/Desktop"/moomoo_OpenD_*_Mac
```

Download:

```bash
curl -L -o "$HOME/Desktop/MoomooOpenD.tar.gz" "https://softwaredownload.moomoo.com/moomoo_OpenD_10.2.6208_Mac.tar.gz"
```

Replace the filename with the actual one obtained in step one.

Path substitution rules:
- Default: `$HOME/Desktop`
- User-specified via `-path`: replace with the corresponding path

After downloading, verify the file size:
```bash
du -h "$HOME/Desktop/MoomooOpenD.tar.gz"
```

## Step Three: Extract

```bash
tar -xzf "$HOME/Desktop/MoomooOpenD.tar.gz" -C "$HOME/Desktop/" && rm -f "$HOME/Desktop/MoomooOpenD.tar.gz"
```

If the user specified a path via `-path`, replace `$HOME/Desktop` with the corresponding path.

## Step Four: Mount .dmg and Install GUI Version

After extraction, the directory contains `.dmg` (GUI) and `.app` (command-line). **Install the `.dmg`**.

Find and mount the `.dmg` file:

```bash
DMG_PATH=$(find "$HOME/Desktop" -maxdepth 3 -name "*OpenD-GUI*.dmg" -type f | head -1) && echo "Found DMG: $DMG_PATH"
```

Mount the DMG image:

```bash
hdiutil attach "$DMG_PATH" -nobrowse
```

After mounting, find the `.app` in the mount point and copy to `/Applications`:

```bash
VOLUME_PATH=$(hdiutil attach "$DMG_PATH" -nobrowse | grep "/Volumes" | awk -F'\t' '{print $NF}') && echo "Mounted: $VOLUME_PATH"
APP_IN_DMG=$(find "$VOLUME_PATH" -maxdepth 1 -name "*.app" -type d | head -1) && echo "Found app: $APP_IN_DMG" && cp -R "$APP_IN_DMG" /Applications/ && echo "Installed to /Applications/"
```

Remove the macOS Gatekeeper quarantine attribute to prevent launch blocking:

```bash
APP_NAME=$(basename "$APP_IN_DMG") && xattr -rd com.apple.quarantine "/Applications/$APP_NAME"
```

Unmount the DMG image:

```bash
hdiutil detach "$VOLUME_PATH"
```

## Step Five: Launch GUI Version

```bash
APP_NAME=$(ls /Applications/ | grep "OpenD-GUI" | head -1) && open "/Applications/$APP_NAME"
```

## Error Handling

- **Gatekeeper still blocking**: Direct the user to "System Preferences -> Security & Privacy -> General" and click "Open Anyway"
- **Path issues**: If a config file path error appears after launch, run `fixrun.sh` from the extracted directory:
```bash
FIXRUN=$(find "$HOME/Desktop" -maxdepth 3 -name "fixrun.sh" | head -1) && chmod +x "$FIXRUN" && bash "$FIXRUN"
```

## Step Six: Clean Up

Automatically clean up the extracted directory after installation:

```bash
EXTRACT_DIR=$(find "$HOME/Desktop" -maxdepth 1 -type d -name "*OpenD*" | head -1) && rm -rf "$EXTRACT_DIR" && echo "Cleaned up: $EXTRACT_DIR"
```
