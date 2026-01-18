import json

# Read Test 10 readback file
print("Reading 10_complete_ctcss_mapping_test_readback.json...")
filepath = r'D:\Radio\Guohetec\Testing\10_complete_ctcss_mapping_test_readback.json'
with open(filepath, 'r') as f:
    data = json.load(f)

# Extract channels with named tones
tone_mappings = {}
for ch_id, ch_data in data.items():
    name = ch_data['channelName'].strip('\x00')
    emit = ch_data['emitYayin']
    
    # Only process channels with names containing "Pos" (position markers)
    if 'Pos' in name and emit != 0:
        # Extract position and frequency from name
        # Format: "Pos4 77.0Hz" or "Pos11 97.4H"
        parts = name.split()
        if len(parts) >= 2:
            pos_str = parts[0].replace('Pos', '')
            freq_str = parts[1].replace('Hz', '').replace('H', '')
            
            try:
                position = int(pos_str)
                frequency = float(freq_str)
                tone_mappings[position] = {
                    'frequency': frequency,
                    'yayin': emit,
                    'channel': int(ch_id)
                }
            except ValueError:
                pass

# Display results sorted by position
print("\n" + "=" * 70)
print("CTCSS Tone Mappings from Test 10")
print("=" * 70)
print(f"{'Pos':<5} {'Frequency':<12} {'yayin':<8} {'Offset':<8} {'Channel':<8}")
print("-" * 70)

output_lines = []
for pos in sorted(tone_mappings.keys()):
    mapping = tone_mappings[pos]
    freq = mapping['frequency']
    yayin = mapping['yayin']
    offset = yayin - pos
    ch = mapping['channel']
    
    line = f"{pos:<5} {freq:<12.1f} {yayin:<8} {offset:<8} {ch:<8}"
    print(line)
    output_lines.append(line)

print(f"\nTotal new mappings discovered: {len(tone_mappings)}")

# Save to file
output_file = 'TEST_10_MAPPINGS.txt'
with open(output_file, 'w') as f:
    f.write("CTCSS Tone Mappings from Test 10\n")
    f.write("=" * 70 + "\n")
    f.write(f"{'Pos':<5} {'Frequency':<12} {'yayin':<8} {'Offset':<8} {'Channel':<8}\n")
    f.write("-" * 70 + "\n")
    for line in output_lines:
        f.write(line + "\n")
    f.write(f"\nTotal new mappings discovered: {len(tone_mappings)}\n")

print(f"\nOutput saved to {output_file}")

# Analyze offset patterns
print("\n" + "=" * 70)
print("Offset Pattern Analysis")
print("=" * 70)

offset_changes = []
prev_pos = None
prev_offset = None

for pos in sorted(tone_mappings.keys()):
    offset = tone_mappings[pos]['yayin'] - pos
    
    if prev_pos is not None and offset != prev_offset:
        offset_changes.append({
            'after_pos': prev_pos,
            'old_offset': prev_offset,
            'new_offset': offset,
            'gap_entries': offset - prev_offset
        })
    
    prev_pos = pos
    prev_offset = offset

if offset_changes:
    print("\nOffset changes detected (indicating reserved/gap entries):")
    for change in offset_changes:
        print(f"  After position {change['after_pos']}: offset {change['old_offset']} → {change['new_offset']} "
              f"({change['gap_entries']} gap entries)")
else:
    print("No offset changes detected - uniform offset pattern")
