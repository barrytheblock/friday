"""
list_devices.py
Run this to find your microphone device index.
Then set MIC_DEVICE_INDEX in config.py to that number.
"""

import sounddevice as sd

print("\nAvailable audio devices:\n")
print(sd.query_devices())
print("\nSet MIC_DEVICE_INDEX in config.py to the index of your microphone.")
