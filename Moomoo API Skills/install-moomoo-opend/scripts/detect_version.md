# Version Detection Scripts (moomoo OpenD)

## Get Latest Online Version Number

Extract the latest version number from the redirect URL of the `fetch-lasted-link` API (`{platform}` is replaced with `windows`, `macos`, `centos`, or `ubuntu` based on `detected_os`).

**Note**: The moomoo API may return a 400 error or no redirect. The scripts below automatically fall back to the Futu shared version API (`futunn.com`) when the moomoo API fails, since both editions share the same version numbers.

### macOS / Linux

```bash
# Try moomoo API first
LATEST_URL=$(curl -sI "https://www.moomoo.com/download/fetch-lasted-link?name=opend-{platform}" | grep -i "^location:" | awk '{print $2}' | tr -d '\r')
LATEST_VER=$(echo "$LATEST_URL" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')

# Fallback to Futu shared version API if moomoo API fails
if [ -z "$LATEST_VER" ]; then
    LATEST_URL=$(curl -sI "https://www.futunn.com/download/fetch-lasted-link?name=opend-{platform}" | grep -i "^location:" | awk '{print $2}' | tr -d '\r')
    LATEST_VER=$(echo "$LATEST_URL" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
fi

echo "Latest version: $LATEST_VER"
```

### Windows

Generate a PowerShell script (to avoid `$` escaping issues in Bash):

```powershell
$latestVer = ""

# Try moomoo API first
$response = Invoke-WebRequest -Uri "https://www.moomoo.com/download/fetch-lasted-link?name=opend-windows" -MaximumRedirection 0 -ErrorAction SilentlyContinue
$redirectUrl = $response.Headers.Location
if ($redirectUrl -match '(\d+\.\d+\.\d+)') { $latestVer = $Matches[1] }

# Fallback to Futu shared version API if moomoo API fails
if (-not $latestVer) {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $request = [System.Net.HttpWebRequest]::Create("https://www.futunn.com/download/fetch-lasted-link?name=opend-windows")
    $request.AllowAutoRedirect = $true
    $response = $request.GetResponse()
    $finalUrl = $response.ResponseUri.ToString()
    $response.Close()
    if ($finalUrl -match '(\d+\.\d+\.\d+)') { $latestVer = $Matches[1] }
}

Write-Host "LATEST_VER=$latestVer"
```

## Detect Locally Installed Version

### Windows

Generate a PowerShell script to detect the locally installed version using the following methods in order. Detection targets are moomoo-specific: `moomoo_OpenD`.

1. Read `DisplayVersion` from registry uninstall entries (most reliable, GUI installer writes to registry)
2. Detect running moomoo_OpenD GUI process
3. Search common installation paths for the GUI executable

**Note (Windows only)**: The GUI executable's `VersionInfo.ProductVersion` is empty — you cannot get the version from file properties. Registry is the preferred source. macOS and Linux are not affected.

```powershell
$localVer = "not_installed"
$targetName = "moomoo_OpenD"
$processName = "moomoo_OpenD"
$installDir = "moomoo_OpenD"

# Method 1: Check registry uninstall entries (most reliable)
$regPaths = @(
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
)
foreach ($regPath in $regPaths) {
    if ($localVer -ne "not_installed") { break }
    if (-not (Test-Path $regPath)) { continue }
    Get-ChildItem -Path $regPath -ErrorAction SilentlyContinue | ForEach-Object {
        $props = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
        if ($props.DisplayName -eq $targetName -and $props.DisplayVersion) {
            if ($props.DisplayVersion -match '(\d+\.\d+\.\d+)') {
                $localVer = $Matches[1]
            }
        }
    }
}

# Method 2: Check running GUI OpenD process
if ($localVer -eq "not_installed") {
    $proc = Get-Process -Name $processName -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($proc -and $proc.Path) {
        if ($proc.Path -match '(\d+\.\d+\.\d+)') {
            $localVer = $Matches[1]
        }
    }
}

# Method 3: Check if GUI OpenD executable exists at default install path
if ($localVer -eq "not_installed") {
    $guiPath = Join-Path $env:APPDATA "$installDir\$processName.exe"
    if (Test-Path $guiPath) {
        $localVer = "installed_unknown"
    }
}

Write-Host "LOCAL_VER=$localVer"
```

### macOS

Detect using the following methods in order, using moomoo-specific names:

```bash
LOCAL_VER="not_installed"
BRAND_PREFIX="moomoo"
# Possible app names: installer may use different naming conventions
APP_NAMES=("moomoo_OpenD" "moomoo OpenD-GUI" "moomoo OpenD")

# Method 1: Check running moomoo OpenD process and read version from its app bundle
OPEND_PID=$(pgrep -f "${BRAND_PREFIX}_OpenD" 2>/dev/null | head -1)
if [ -n "$OPEND_PID" ]; then
    # Use full command path (args=) instead of comm= to locate the .app bundle
    OPEND_FULL_PATH=$(ps -p "$OPEND_PID" -o args= 2>/dev/null | awk '{print $1}')
    # Extract .app bundle path (everything up to and including .app)
    APP_BUNDLE=$(echo "$OPEND_FULL_PATH" | sed -n 's|\(.*\.app\)/.*|\1|p')
    if [ -n "$APP_BUNDLE" ] && [ -d "$APP_BUNDLE" ]; then
        LOCAL_VER=$(defaults read "$APP_BUNDLE/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo "not_installed")
    fi
fi

# Method 2: Read Info.plist from /Applications/ (try all known app names)
if [ "$LOCAL_VER" = "not_installed" ]; then
    for APP_NAME in "${APP_NAMES[@]}"; do
        if [ -d "/Applications/${APP_NAME}.app" ]; then
            LOCAL_VER=$(defaults read "/Applications/${APP_NAME}.app/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo "not_installed")
            [ "$LOCAL_VER" != "not_installed" ] && break
        fi
    done
fi

# Method 3: Search common paths for .app bundles or .dmg installers (GUI version has underscore: moomoo_OpenD)
if [ "$LOCAL_VER" = "not_installed" ]; then
    FOUND=$(find "$HOME/Desktop" /Applications /opt "$HOME/Downloads" -maxdepth 4 \( -name "${BRAND_PREFIX}_OpenD*.dmg" -o -name "${BRAND_PREFIX}_OpenD*.app" \) 2>/dev/null | head -1)
    if [ -n "$FOUND" ]; then
        # Try reading Info.plist if it's an .app bundle
        if echo "$FOUND" | grep -q '\.app$' && [ -f "$FOUND/Contents/Info.plist" ]; then
            LOCAL_VER=$(defaults read "$FOUND/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo "not_installed")
        fi
        # Fall back to extracting version from filename
        if [ "$LOCAL_VER" = "not_installed" ] && echo "$FOUND" | grep -qoE '[0-9]+\.[0-9]+\.[0-9]+'; then
            LOCAL_VER=$(echo "$FOUND" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        fi
    fi
fi

echo "Local version: $LOCAL_VER"
```

### Linux

Detect using the following methods in order, using moomoo-specific names:

```bash
LOCAL_VER="not_installed"
BRAND_PROCESS="moomoo_OpenD"
BRAND_PREFIX="moomoo"

# Method 1: Check running OpenD process
OPEND_PID=$(pgrep -f "$BRAND_PROCESS" 2>/dev/null | head -1)
if [ -n "$OPEND_PID" ]; then
    OPEND_PATH=$(readlink -f /proc/"$OPEND_PID"/exe 2>/dev/null)
    # Try extracting version from path first
    if [ -n "$OPEND_PATH" ] && echo "$OPEND_PATH" | grep -qoE '[0-9]+\.[0-9]+\.[0-9]+'; then
        LOCAL_VER=$(echo "$OPEND_PATH" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    fi
    # If path has no version, try --version
    if [ "$LOCAL_VER" = "not_installed" ] && [ -n "$OPEND_PATH" ] && [ -x "$OPEND_PATH" ]; then
        VER_OUTPUT=$("$OPEND_PATH" --version 2>/dev/null || true)
        if echo "$VER_OUTPUT" | grep -qoE '[0-9]+\.[0-9]+\.[0-9]+'; then
            LOCAL_VER=$(echo "$VER_OUTPUT" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        fi
    fi
fi

# Method 2: Search common paths for OpenD executable
if [ "$LOCAL_VER" = "not_installed" ]; then
    OPEND_BIN=$(find "$HOME/Desktop" /opt /usr/local "$HOME/Downloads" -maxdepth 4 -name "$BRAND_PROCESS" -type f 2>/dev/null | head -1)
    if [ -n "$OPEND_BIN" ]; then
        # Try extracting version from path
        if echo "$OPEND_BIN" | grep -qoE '[0-9]+\.[0-9]+\.[0-9]+'; then
            LOCAL_VER=$(echo "$OPEND_BIN" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        fi
        # If path has no version, try --version
        if [ "$LOCAL_VER" = "not_installed" ] && [ -x "$OPEND_BIN" ]; then
            VER_OUTPUT=$("$OPEND_BIN" --version 2>/dev/null || true)
            if echo "$VER_OUTPUT" | grep -qoE '[0-9]+\.[0-9]+\.[0-9]+'; then
                LOCAL_VER=$(echo "$VER_OUTPUT" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            fi
        fi
    fi
fi

# Method 3: Search for installer/package by filename (GUI version has underscore: moomoo_OpenD)
if [ "$LOCAL_VER" = "not_installed" ]; then
    FOUND=$(find "$HOME/Desktop" /opt /usr/local "$HOME/Downloads" -maxdepth 4 -name "${BRAND_PREFIX}_OpenD*" 2>/dev/null | head -1)
    if [ -n "$FOUND" ] && echo "$FOUND" | grep -qoE '[0-9]+\.[0-9]+\.[0-9]+'; then
        LOCAL_VER=$(echo "$FOUND" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    fi
fi

LOCAL_VER=${LOCAL_VER:-"not_installed"}
echo "Local version: $LOCAL_VER"
```

## Version Comparison Logic

Version format is `X.Y.ZZZZ` (e.g., `10.2.6208`), compared numerically segment by segment.

**Bash comparison** (macOS / Linux):

```bash
if [ "$LOCAL_VER" = "not_installed" ]; then
    echo "STATUS=not_installed"
elif printf '%s\n' "$LATEST_VER" "$LOCAL_VER" | sort -V | head -1 | grep -qx "$LATEST_VER"; then
    echo "STATUS=up_to_date"
else
    echo "STATUS=needs_update"
fi
```

**PowerShell comparison** (Windows):

```powershell
if ($localVer -eq "not_installed") {
    Write-Host "STATUS=not_installed"
} elseif ([version]$localVer -ge [version]$latestVer) {
    Write-Host "STATUS=up_to_date"
} else {
    Write-Host "STATUS=needs_update"
}
```

## Actions Based on Comparison

| Status | Action |
|--------|--------|
| Not installed (`not_installed`) | Proceed with normal download and installation |
| Local version < latest (`needs_update`) | Inform "Found local OpenD version {LOCAL_VER}. Latest version is {LATEST_VER} — upgrading automatically.", proceed with download |
| Local version >= latest (`up_to_date`) | Inform "moomoo OpenD is already up to date (version {LOCAL_VER}). No reinstallation needed.", **skip download and installation**, proceed to SDK upgrade |
