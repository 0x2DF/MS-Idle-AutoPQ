# Visual Workflow Automation

## Installation

```bash
pip install mss opencv-python pyautogui pyyaml numpy

# For Windows window capture support:
pip install pywin32
```

## Configuration

Edit `config.yaml` to configure window capture:

```yaml
# Capture from specific window
window_name: "BlueStacks.exe"

# Or use full screen
# window_name: null
```

## Usage

```bash
python main.py
```