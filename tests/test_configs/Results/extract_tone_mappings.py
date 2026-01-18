import json
import os

# Read the manual CTCSS file
print("Reading 05_manual_CTCSS_only_readback_uart_monitored.json...")
filepath = r'D:\Radio\Guohetec\Testing\old\05_manual_CTCSS_only_readback_uart_monitored.json'
with open(filepath, 'r') as f:
    data = json.load(f)

# Extract channels with tones
channels_with_tones = {}
for ch_id, ch_data in data.items():
    emit = ch_data['emitYayin']
    receive = ch_data['receiveYayin']
    if emit != 0 or receive != 0:
        name = ch_data['channelName'].strip('\x00')
        channels_with_tones[int(ch_id)] = {
            'name': name,
            'emit': emit,
            'receive': receive
        }

# Create output
output = []
output.append("=" * 60)
output.append("CTCSS Tone Mappings from Manual Configuration")
output.append("=" * 60)
output.append("")

for ch_num in sorted(channels_with_tones.keys()):
    ch = channels_with_tones[ch_num]
    line = f"Ch {ch_num:3d}: {ch['name']:20s} | emit={ch['emit']:3d} receive={ch['receive']:3d}"
    output.append(line)
    print(line)

output.append("")
output.append(f"Total tones found: {len(channels_with_tones)}")
print(f"\nTotal tones found: {len(channels_with_tones)}")

# Parse tone frequencies from channel names
print("\n" + "=" * 60)
print("Tone Frequency → emitYayin/receiveYayin Mapping")
print("=" * 60)
output.append("")
output.append("=" * 60)
output.append("Tone Frequency → emitYayin/receiveYayin Mapping")
output.append("=" * 60)

tone_mappings = {}
for ch_num in sorted(channels_with_tones.keys()):
    ch = channels_with_tones[ch_num]
    name = ch['name']
    
    # Extract frequency from name (e.g., "CTCSS 67.0" -> "67.0")
    if 'CTCSS' in name:
        parts = name.split()
        if len(parts) >= 2:
            freq = parts[1]
            if ch['emit'] == ch['receive']:
                tone_mappings[freq] = ch['emit']
                line = f"  {freq:6s} Hz → yayin = {ch['emit']}"
                output.append(line)
                print(line)

output.append("")
output.append(f"Total CTCSS mappings: {len(tone_mappings)}")
print(f"\nTotal CTCSS mappings: {len(tone_mappings)}")

# Save to file  
with open('CTCSS_MAPPINGS_DISCOVERED.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("\nOutput saved to CTCSS_MAPPINGS_DISCOVERED.txt")
