# Windows Installation Steps (moomoo OpenD)

## Installer Details

The Windows installer is a **7z archive**. After extraction, the `*OpenD-GUI*.exe` is an **installer program** (not the final executable). It launches an installation wizard that the user needs to follow.

Archive internal structure:
```
moomoo_OpenD_x.x.xxxx_Windows/
├── moomoo_OpenD-GUI_x.x.xxxx_Windows/
│   └── moomoo_OpenD-GUI_x.x.xxxx_Windows.exe   ← GUI installer (installs to %APPDATA%\moomoo_OpenD\moomoo_OpenD.exe)
├── moomoo_OpenD_x.x.xxxx_Windows/
│   ├── MoomooOpenD.exe                             ← Command-line version (do NOT launch)
│   ├── OpenD.xml                                   ← Config file
│   ├── AppData.dat                                 ← Data file
│   └── ...(DLLs and dependencies)
└── README.txt
```

**Important**: `moomoo_OpenD-GUI*.exe` is the GUI installer. After installation, the GUI version is installed to `%APPDATA%\moomoo_OpenD\moomoo_OpenD.exe`. The `moomoo_OpenD_x.x.xxxx_Windows/` directory contains the command-line version — **do not launch the command-line version**.

## PowerShell Download + Extract + Launch Installer

Generate a PowerShell script (install_opend.ps1) to **download, extract, and launch the installer in one go**.

**After launching the installer**:
- If you can automate screen interactions (e.g., via MCP tools for screenshots + simulated clicks), help the user complete each step of the installation wizard automatically
- Otherwise, inform the user: "The installer has been launched. Please follow the installation wizard to complete setup."

**Important: PowerShell scripts must use English output.** When running `.ps1` scripts via `powershell -ExecutionPolicy Bypass -File` in MINGW64/Git Bash, Chinese characters cause `TerminatorExpectedAtEndOfString` parsing errors. All `Write-Host` output must be in English.

```powershell
# ===== moomoo version, replace path as needed =====
$url = "https://www.moomoo.com/download/fetch-lasted-link?name=opend-windows"
$downloadDir = [Environment]::GetFolderPath("Desktop")  # or user-specified path
$archiveName = "MoomooOpenD.7z"
# =====================================================

$archivePath = Join-Path $downloadDir $archiveName
$extractDir = Join-Path $downloadDir "MoomooOpenD"

# Step 1: Clean up existing files, then download
if (Test-Path $archivePath) { Remove-Item $archivePath -Force; Write-Host "Removed existing archive: $archivePath" }
if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force; Write-Host "Removed existing directory: $extractDir" }
Write-Host "Downloading latest moomoo OpenD..."
Invoke-WebRequest -Uri $url -OutFile $archivePath -UseBasicParsing
$size = [math]::Round((Get-Item $archivePath).Length / 1MB, 2)
Write-Host "Download complete! File size: $size MB"

# Step 2: Extract (requires 7-Zip)
$sevenZip = "C:\Program Files\7-Zip\7z.exe"
if (-not (Test-Path $sevenZip)) {
    $sevenZip = "C:\Program Files (x86)\7-Zip\7z.exe"
}
if (Test-Path $sevenZip) {
    Write-Host "Extracting..."
    & $sevenZip x $archivePath -o"$extractDir" -y | Out-Null
    Write-Host "Extracted to: $extractDir"
} else {
    Write-Host "7-Zip not found. Please extract manually: $archivePath"
    Write-Host "Download 7-Zip: https://www.7-zip.org/download.html"
    Write-Host "Backup link: https://github.com/ip7z/7zip/releases"
    exit 1
}

# Step 3: Launch OpenD installer
$guiExe = Get-ChildItem -Path $extractDir -Recurse -Filter "*OpenD-GUI*.exe" | Select-Object -First 1
if ($guiExe) {
    Write-Host "Launching moomoo OpenD installer: $($guiExe.FullName)"
    Start-Process $guiExe.FullName
    Write-Host "Installer launched. Please follow the installation wizard to complete setup."
} else {
    Write-Host "Installer not found. Check directory: $extractDir"
}

# Cleanup archive
Remove-Item $archivePath -Force

# Wait for installer to finish, then clean up extracted directory
Write-Host "Waiting for installer to finish..."
$guiProc = Get-Process | Where-Object { $_.Path -eq $guiExe.FullName } | Select-Object -First 1
if ($guiProc) { $guiProc.WaitForExit() }
Remove-Item $extractDir -Recurse -Force
Write-Host "Done! Cleaned up temporary files."
```

## Path Substitution Rules

- Default (Desktop): `$downloadDir = [Environment]::GetFolderPath("Desktop")`
- User-specified: `$downloadDir = "user-provided-path"`

## Prerequisites

Requires 7-Zip. If not found, the script will display an error. Direct the user to:
- Download 7-Zip: `https://www.7-zip.org/download.html`
- Backup link: `https://github.com/ip7z/7zip/releases`
- Or manually extract the .7z file

## Execution Steps

1. Use Write tool to save the script as a temporary file `install_opend.ps1`
2. Use Bash tool to execute: `powershell -ExecutionPolicy Bypass -File "install_opend.ps1"`
3. Delete the temporary script after completion: `rm install_opend.ps1`

Note: `$` symbols in Bash are escaped, so you must write the `.ps1` file first then execute it.
