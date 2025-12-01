#!/usr/bin/env python3
"""
Helper script to capture template images from ADB screenshots.
Use this to create templates that will match perfectly with ADB capture mode.
"""

import cv2
import sys
from core.input import ADBClient
from core.utils import ConfigLoader

def main():
    if len(sys.argv) < 2:
        print("Usage: python capture_template_adb.py <output_filename.png>")
        print("Example: python capture_template_adb.py assets/screens/Hunting/menu.png")
        return
    
    output_file = sys.argv[1]
    
    # Load config
    config_loader = ConfigLoader("config.yaml")
    config = config_loader.load()
    device_id = config.get("adb_device_id")
    
    # Connect to ADB
    print("Connecting to ADB device...")
    adb = ADBClient(device_id=device_id)
    
    # Capture screenshot
    print("Capturing screenshot...")
    cmd = adb._build_command("exec-out", "screencap", "-p")
    
    import subprocess
    import numpy as np
    result = subprocess.run(cmd, capture_output=True, timeout=5)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return
    
    nparr = np.frombuffer(result.stdout, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        print("Failed to decode screenshot")
        return
    
    print(f"Screenshot captured: {img.shape[1]}x{img.shape[0]}")
    print("\nInstructions:")
    print("1. A window will open showing the screenshot")
    print("2. Click and drag to select the area you want as a template")
    print("3. Press SPACE or ENTER to save")
    print("4. Press ESC to cancel")
    
    # Let user select ROI
    roi = cv2.selectROI("Select Template Area", img, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    
    if roi[2] == 0 or roi[3] == 0:
        print("No area selected, cancelled.")
        return
    
    # Crop the selected area
    x, y, w, h = roi
    template = img[y:y+h, x:x+w]
    
    # Save template
    cv2.imwrite(output_file, template)
    print(f"\n✓ Template saved to: {output_file}")
    print(f"  Size: {w}x{h}")
    print(f"  Center coordinates: ({x + w//2}, {y + h//2})")

if __name__ == "__main__":
    main()
