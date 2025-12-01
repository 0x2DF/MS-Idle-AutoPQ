# Visual Workflow Automation

Automate UI interactions using computer vision and either mouse control (PyAutoGUI) or direct device control (ADB).

## Installation

```bash
pip install mss opencv-python pyautogui pyyaml numpy

# For Windows window capture support:
pip install pywin32
```

## Input Methods

### PyAutoGUI (Default)
Controls your physical mouse cursor. Simple but takes over your mouse.

### ADB (Recommended for Android Emulators)
Sends commands directly to Android devices/emulators without touching your mouse. Perfect for BlueStacks!

## Setting Up ADB

### 1. Install ADB

**Option A: Download Platform Tools (Recommended)**
1. Download [Android SDK Platform Tools](https://dl.google.com/android/repository/platform-tools-latest-windows.zip)
2. Extract to a folder (e.g., `C:\platform-tools`)
3. Add to your PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" under System Variables
   - Add the platform-tools folder path
   - Restart your terminal

**Option B: Package Manager**
```bash
# Using Chocolatey
choco install adb

# Using Scoop
scoop install adb
```

### 2. Enable ADB in BlueStacks

**BlueStacks 5:**
1. Open BlueStacks
2. Click the hamburger menu (≡) in the top-right
3. Go to **Settings** → **Advanced**
4. Enable **Android Debug Bridge (ADB)**
5. Note the port (usually 5555)
6. Restart BlueStacks

**BlueStacks 4:**
1. Go to **Settings** → **Preferences**
2. Enable **Enable Android Debug Bridge (ADB)**
3. Restart BlueStacks

### 3. Connect ADB

```bash
# Connect to BlueStacks
adb connect localhost:5555

# Verify connection
adb devices
```

You should see:
```
List of devices attached
localhost:5555    device
```

### 4. Configure the App

Set `input_method: "adb"` in config.yaml

### Troubleshooting

- **"No ADB devices connected"**: Make sure BlueStacks is running and ADB is enabled, then run `adb connect localhost:5555`
- **"ADB not found"**: Verify platform-tools is in your PATH and restart your terminal
- **Multiple devices**: Specify device ID in config.yaml: `adb_device_id: "localhost:5555"`

**For detailed instructions and troubleshooting:** See [docs/ADB_SETUP.md](docs/ADB_SETUP.md)

## Configuration

Edit `config.yaml`:

```yaml
# Input method: "pyautogui" or "adb"
input_method: "adb"

# ADB device (optional, uses first device if not specified)
adb_device_id: null

# Window to capture
window_name: "BlueStacks"
```

## Usage

```bash
# Run with default output (clean, user-friendly)
python main.py

# Run with debug output (shows matching details)
python main.py -debug

# Run with verbose output (shows everything)
python main.py -verbose

# Run in quiet mode (errors only)
python main.py -quiet
```

Select a workflow and watch it run automatically!

**Press 'q' at any time to stop execution and return to the menu.**

### Output Modes

- **Default (INFO)**: Clean output showing workflow progress, steps, and results with progress bars for waits
- **Debug**: Adds template matching details and coordinate information
- **Verbose**: Shows all internal details including frame captures and transformations
- **Quiet**: Only shows critical errors