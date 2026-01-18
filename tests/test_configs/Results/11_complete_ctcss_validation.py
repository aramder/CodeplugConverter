"""
Generate Test 11: Complete CTCSS Validation Codeplug

This test creates a validation codeplug with:
1. Common CTCSS tones (most frequently used)
2. Edge case tones (highest/lowest frequencies)
3. Split tone examples
4. TX-only and RX-only examples
5. Coverage of all offset ranges

Total: 25 channels testing critical CTCSS functionality
"""

import json
from pathlib import Path

# Base frequency for all test channels (2m band)
BASE_FREQ_MHZ = 146.520  # National simplex frequency

def freq_to_bytes(freq_mhz):
    """Convert frequency in MHz to 4-byte representation"""
    freq_hz = int(freq_mhz * 1_000_000)
    return [
        (freq_hz >> 24) & 0xFF,
        (freq_hz >> 16) & 0xFF,
        (freq_hz >> 8) & 0xFF,
        freq_hz & 0xFF
    ]

def create_test_channel(index, name, tx_tone=0, rx_tone=0, freq_mhz=BASE_FREQ_MHZ):
    """Create a test channel with specified CTCSS tones"""
    freq_bytes = freq_to_bytes(freq_mhz)
    
    return {
        "callFormat": 255,
        "callId1": 0,
        "callId2": 0,
        "callId3": 0,
        "callId4": 0,
        "chBsMode": 0,
        "chType": 255,
        "channelHigh": (index >> 8) & 0xFF,
        "channelLow": index & 0xFF,
        "channelName": name + "\u0000",
        "dmodGain": 0,
        "emitYayin": tx_tone,
        "ownId1": 0,
        "ownId2": 0,
        "ownId3": 0,
        "ownId4": 0,
        "receiveYayin": rx_tone,
        "rxCc": 0,
        "rxCtcss": 255,
        "scrEn": 0,
        "scrSeed1": 0,
        "scrSeed2": 0,
        "slot": 0,
        "spkgain": 0,
        "sqlevel": 0,
        "txCc": 1,
        "txCtcss": 255,
        "vfoaFrequency1": freq_bytes[0],
        "vfoaFrequency2": freq_bytes[1],
        "vfoaFrequency3": freq_bytes[2],
        "vfoaFrequency4": freq_bytes[3],
        "vfoaMode": 6,  # FM
        "vfobFrequency1": freq_bytes[0],
        "vfobFrequency2": freq_bytes[1],
        "vfobFrequency3": freq_bytes[2],
        "vfobFrequency4": freq_bytes[3],
        "vfobMode": 6   # FM
    }

# Test channels configuration
test_channels = [
    # Common tones (most important for users)
    (0, "100.0Hz Both", 13, 13),    # Most common USA tone
    (1, "123.0Hz Both", 19, 19),    # IRLP/EchoLink
    (2, "131.8Hz Both", 21, 21),    # Common repeater
    (3, "141.3Hz Both", 23, 23),    # Regional
    (4, "146.2Hz Both", 24, 24),    # Common repeater
    (5, "156.7Hz Both", 27, 27),    # Regional
    
    # Edge cases - lowest frequencies
    (10, "67.0Hz Both", 1, 1),      # Lowest CTCSS tone
    (11, "69.3Hz Both", 2, 2),      # Second lowest
    
    # Edge cases - highest frequencies
    (12, "250.3Hz Both", 54, 54),   # Second highest
    (13, "254.1Hz Both", 55, 55),   # Highest CTCSS tone
    
    # Middle range
    (14, "107.2Hz Both", 15, 15),   # Common
    (15, "162.2Hz Both", 29, 29),   # Mid-range
    (16, "186.2Hz Both", 37, 37),   # Upper mid-range
    
    # Split tone examples
    (20, "Split 100/131", 13, 21),  # Different TX/RX
    (21, "Split 123/146", 19, 24),  # Different TX/RX
    (22, "Split 67/254", 1, 55),    # Min/Max split
    
    # TX-only examples
    (25, "TX Only 100", 13, 0),     # Transmit only
    (26, "TX Only 123", 19, 0),     # Transmit only
    
    # RX-only examples
    (27, "RX Only 100", 0, 13),     # Receive only
    (28, "RX Only 131", 0, 21),     # Receive only
    
    # No tone reference
    (30, "No Tone", 0, 0),          # Baseline
    
    # Test across offset ranges
    (35, "94.8Hz Both", 11, 11),    # Offset +1 range
    (36, "151.4Hz Both", 26, 26),   # Offset +2 range (yayin 26, gap before 25)
    (37, "218.1Hz Both", 46, 46),   # Higher range with gaps
    (38, "229.1Hz Both", 49, 49),   # Near highest
]

# Generate codeplug
channels = {}
for index, name, tx_tone, rx_tone in test_channels:
    channels[str(index)] = create_test_channel(index, name, tx_tone, rx_tone)

# Save to file
output_file = Path(__file__).parent / "11_complete_ctcss_validation.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(channels, f, indent=4, ensure_ascii=False)

print(f"Created test codeplug with {len(channels)} channels")
print(f"Saved to: {output_file}")
print("\nTest coverage:")
print(f"  - {6} common tones")
print(f"  - {4} edge cases (lowest/highest)")
print(f"  - {3} mid-range tones")
print(f"  - {3} split tone examples")
print(f"  - {2} TX-only examples")
print(f"  - {2} RX-only examples")
print(f"  - {1} no tone reference")
print(f"  - {4} offset range coverage")
print(f"  Total: {len(test_channels)} test scenarios")
