# Post-download Version Consistency Check (moomoo OpenD)

After downloading and extracting, **before launching the installer**, verify that the extracted installation file version matches the expected latest version (`LATEST_VER`) to prevent CDN caching, interrupted downloads, or mirror desync issues.

## Verification Principle

The extracted directory and installer filenames contain version numbers (e.g., `moomoo_OpenD-GUI_10.1.6108_Windows.exe`). Verification: **find a GUI installer file whose name contains the expected version number (`LATEST_VER`)**. If found, verification passes; if not, verification fails.

**Note**: The archive may contain multiple version directories simultaneously (e.g., both `10.2.6208` and `10.1.6108`). Therefore, **do not use `Select-Object -First 1` or `head -1` to pick the first match and then compare versions** — filter directly by the expected version number.

## Windows

Execute verification after extraction and before launching the installer:

```powershell
# Step 2.5: Verify expected version exists in extracted files
$guiExe = Get-ChildItem -Path $extractDir -Recurse -Filter "*OpenD-GUI*$latestVer*.exe" | Select-Object -First 1
if ($guiExe) {
    Write-Host "Version verified: found $($guiExe.Name) (matches expected $latestVer)"
} else {
    $allGui = Get-ChildItem -Path $extractDir -Recurse -Filter "*OpenD-GUI*.exe"
    $foundVersions = ($allGui | ForEach-Object { if ($_.Name -match '(\d+\.\d+\.\d+)') { $Matches[1] } }) -join ", "
    Write-Host "WARNING: Expected version $latestVer not found in extracted files."
    Write-Host "Found versions: $foundVersions"
    Write-Host "The download may not contain the expected version. Aborting installation."
    exit 1
}
```

**Note**: `$latestVer` must be extracted from the redirect URL or download link filename and passed to the script. After verification passes, subsequent steps should use the `$guiExe` found here to launch the installer.

## macOS

Execute verification after extraction (step three) and before mounting the DMG (step four):

```bash
DMG_FILE=$(find "$HOME/Desktop" -maxdepth 3 -name "*OpenD-GUI*${LATEST_VER}*.dmg" -type f | head -1)
if [ -n "$DMG_FILE" ]; then
    echo "Version verified: found $(basename "$DMG_FILE") (matches expected $LATEST_VER)"
else
    ALL_DMG=$(find "$HOME/Desktop" -maxdepth 3 -name "*OpenD-GUI*.dmg" -type f 2>/dev/null)
    echo "WARNING: Expected version $LATEST_VER not found in extracted files."
    echo "Found DMG files: $ALL_DMG"
    echo "The download may not contain the expected version. Aborting installation."
    exit 1
fi
```

If the user specified a path via `-path`, replace `$HOME/Desktop` with the corresponding path. After verification passes, subsequent mount steps should use the `$DMG_FILE` found here.

## Linux

Execute verification after extraction and before installing the GUI package:

```bash
# Ubuntu/Debian
PKG_FILE=$(find ~/Desktop -maxdepth 3 \( -name "*OpenD-GUI*${LATEST_VER}*.deb" -o -name "*OpenD-GUI*${LATEST_VER}*.rpm" \) -type f 2>/dev/null | head -1)

# CentOS/RHEL
# PKG_FILE=$(find ~/Desktop -maxdepth 3 -name "*OpenD-GUI*${LATEST_VER}*.rpm" -type f | head -1)

if [ -n "$PKG_FILE" ]; then
    echo "Version verified: found $(basename "$PKG_FILE") (matches expected $LATEST_VER)"
else
    ALL_PKG=$(find ~/Desktop -maxdepth 3 \( -name "*OpenD-GUI*.deb" -o -name "*OpenD-GUI*.rpm" \) -type f 2>/dev/null)
    echo "WARNING: Expected version $LATEST_VER not found in extracted files."
    echo "Found packages: $ALL_PKG"
    echo "The download may not contain the expected version. Aborting installation."
    exit 1
fi
```

If the user specified a path via `-path`, replace `~/Desktop` with the corresponding path. After verification passes, subsequent installation steps should use the `$PKG_FILE` found here.

## Verification Failure Handling

| Situation | Action |
|-----------|--------|
| Expected version file found | Output "Version verified: found xxx", continue installation |
| Expected version file not found | Output warning and list actually found versions, **abort installation**, inform that the download may not contain the expected version |
