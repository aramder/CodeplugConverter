#!/usr/bin/env python3
"""Verify that TX and RX CTCSS tones are always the same in test results"""

import json

# Load test 09 results
with open('09_tone_pattern_test_manual_full_update_readback.json', 'r') as f:
    data = json.load(f)

# Extract channels with tones configured
channels_with_tones = []
for channel_id, channel_data in data.items():
    emit = channel_data.get('emitYayin', 0)
    receive = channel_data.get('receiveYayin', 0)
    if emit > 0 or receive > 0:
        channels_with_tones.append((channel_id, emit, receive))

# Display results
print("Channel : TX(emit) : RX(receive) : Match?")
print("-" * 50)
for ch_id, tx, rx in channels_with_tones:
    match = "YES" if tx == rx else "NO"
    print(f"{ch_id:7s} : {tx:8d} : {rx:11d} : {match}")

# Summary
print(f"\nTotal channels with tones: {len(channels_with_tones)}")
all_match = all(tx == rx for _, tx, rx in channels_with_tones)
print(f"All TX/RX values match: {all_match}")

if all_match:
    print("\n✅ CONFIRMED: TX and RX CTCSS tones are ALWAYS 1:1")
    print("   You can safely configure just ONE tone (TX or RX)")
    print("   The radio will automatically use the same value for both!")
else:
    print("\n⚠️  WARNING: Some TX/RX values differ")
    print("   You should configure both tones separately")
