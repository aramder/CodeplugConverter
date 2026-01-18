#!/usr/bin/env python3
"""Generate test file for remaining CTCSS tone mappings"""

import json

# Standard CTCSS tone table (50 tones)
CTCSS_TONES = [
    67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8,       # 1-10
    97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8,  # 11-20
    136.5, 141.3, 146.2, 151.4, 156.7, 162.2, 167.9, 173.8, 179.9, 186.2, # 21-30
    192.8, 203.5, 210.7, 218.1, 225.7, 233.6, 241.8, 250.3, 69.3, 159.8,  # 31-40
    165.5, 171.3, 177.3, 183.5, 189.9, 196.6, 199.5, 206.5, 229.1, 254.1  # 41-50
]

# Positions we already have (1-indexed)
KNOWN_POSITIONS = [1, 2, 3, 7, 8, 10, 15, 20, 22, 23, 24, 25, 26, 30, 35, 50]

# Positions we need to test
NEEDED_POSITIONS = [p for p in range(1, 51) if p not in KNOWN_POSITIONS]

def create_channel(index, position):
    """Create a channel entry for testing"""
    tone_freq = CTCSS_TONES[position - 1]
    
    return {
        "callFormat": 255,
        "callId1": 0,
        "callId2": 0,
        "callId3": 0,
        "callId4": 0,
        "chBsMode": 0,
        "chType": 255,
        "channelHigh": 0,
        "channelLow": index,
        "channelName": f"Pos{position} {tone_freq}Hz",
        "dmodGain": 0,
        "emitYayin": 0,
        "ownId1": 0,
        "ownId2": 0,
        "ownId3": 0,
        "ownId4": 0,
        "receiveYayin": 0,
        "rxCc": 0,
        "rxCtcss": 255,
        "scrEn": 0,
        "scrSeed1": 0,
        "scrSeed2": 0,
        "slot": 0,
        "spkgain": 0,
        "sqlevel": 0,
        "txCc": 2,
        "txCtcss": 255,
        "vfoaFrequency1": 26,
        "vfoaFrequency2": 149,
        "vfoaFrequency3": 107,
        "vfoaFrequency4": 128,
        "vfoaMode": 6,
        "vfobFrequency1": 26,
        "vfobFrequency2": 149,
        "vfobFrequency3": 107,
        "vfobFrequency4": 128,
        "vfobMode": 6
    }

# Generate test file
channels = {}
for i, position in enumerate(NEEDED_POSITIONS):
    channels[str(i)] = create_channel(i, position)

# Save to file
output_file = "10_complete_ctcss_mapping_test.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(channels, f, indent=4, ensure_ascii=False)

print(f"Generated {output_file} with {len(channels)} channels")
print(f"Testing positions: {NEEDED_POSITIONS}")
print(f"\nLoad this file into the PMR-171, then read it back.")
print(f"The radio will populate emitYayin/receiveYayin with the yayin values.")
