# Linux Installation Steps (moomoo OpenD)

The Linux installer is a **tar.gz archive**, similar to macOS. After extraction, it contains both the GUI installer and the command-line version.

Archive internal structure (Ubuntu example):
```
moomoo_OpenD_x.x.xxxx_Ubuntu/
├── moomoo_OpenD-GUI_x.x.xxxx_Ubuntu.deb   ← GUI installer package (install this)
├── moomoo_OpenD_x.x.xxxx_Ubuntu/
│   ├── MoomooOpenD                            ← Command-line version (do NOT run)
│   ├── OpenD.xml                              ← Config file
│   └── ...
├── fixrun.sh                                ← Path fix script
└── README.txt
```

## Step One: Download and Extract

Clean up existing files before downloading to avoid conflicts with old versions:

```bash
rm -f ~/Desktop/MoomooOpenD.tar.gz
rm -rf ~/Desktop/moomoo_OpenD_*
```

**CentOS**:
```bash
curl -L -o ~/Desktop/MoomooOpenD.tar.gz "https://www.moomoo.com/download/fetch-lasted-link?name=opend-centos"
tar -xzf ~/Desktop/MoomooOpenD.tar.gz -C ~/Desktop/
rm ~/Desktop/MoomooOpenD.tar.gz
```

**Ubuntu**:
```bash
curl -L -o ~/Desktop/MoomooOpenD.tar.gz "https://www.moomoo.com/download/fetch-lasted-link?name=opend-ubuntu"
tar -xzf ~/Desktop/MoomooOpenD.tar.gz -C ~/Desktop/
rm ~/Desktop/MoomooOpenD.tar.gz
```

If the user specified a path via `-path`, replace `~/Desktop/` with the corresponding path.

## Step Two: Install GUI Version

Locate the extracted GUI installer package and install it:

**Ubuntu/Debian (.deb)**:
```bash
DEB_PATH=$(find ~/Desktop -maxdepth 3 -name "*OpenD-GUI*.deb" -type f | head -1) && echo "Found: $DEB_PATH"
sudo dpkg -i "$DEB_PATH"
sudo apt-get install -f -y  # fix dependencies
```

**CentOS/RHEL (.rpm)**:
```bash
RPM_PATH=$(find ~/Desktop -maxdepth 3 -name "*OpenD-GUI*.rpm" -type f | head -1) && echo "Found: $RPM_PATH"
sudo rpm -ivh "$RPM_PATH"
```

## Step Three: Launch GUI Version

```bash
# Find installed GUI version of OpenD
GUI_BIN=$(which moomoo_OpenD 2>/dev/null || find /opt /usr/local /usr/bin -name "moomoo_OpenD" -type f 2>/dev/null | head -1)
if [ -n "$GUI_BIN" ]; then
    nohup "$GUI_BIN" &
    echo "GUI OpenD started: $GUI_BIN"
else
    echo "GUI OpenD not found. Check installation."
fi
```

## Step Four: Clean Up

Automatically clean up the extracted directory after installation:

```bash
EXTRACT_DIR=$(find ~/Desktop -maxdepth 1 -type d -name "moomoo_OpenD_*" | head -1) && rm -rf "$EXTRACT_DIR" && echo "Cleaned up: $EXTRACT_DIR"
```
