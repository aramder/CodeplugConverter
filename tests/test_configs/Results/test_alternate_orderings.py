"""Test if radio uses a different CTCSS tone ordering"""

# Discovered mappings
DISCOVERED = {
    67.0: 1,
    88.5: 9,
    100.0: 13,
    123.0: 19,
    146.2: 24,
    156.7: 27,
}

# Standard CTCSS ordering (CHIRP/most radios)
STANDARD_ORDER = [
    67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8,
    97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8,
    136.5, 141.3, 146.2, 151.4, 156.7, 162.2, 167.9, 173.8, 179.9, 186.2,
    192.8, 203.5, 210.7, 218.1, 225.7, 233.6, 241.8, 250.3, 69.3, 159.8,
    165.5, 171.3, 177.3, 183.5, 189.9, 196.6, 199.5, 206.5, 229.1, 254.1
]

print("=" * 70)
print("Testing Alternate Tone Table Orderings")
print("=" * 70)
print()

# Test 1: What if there's a skip at position 25/26?
print("HYPOTHESIS 1: Skip/Gap in Radio's Internal Table")
print("-" * 70)
print("Maybe the radio has a gap or reserved entry around index 25?")
print()

# Let's see if yayin values suggest positions with gaps
yayin_values = sorted(DISCOVERED.values())
print(f"Observed yayin values: {yayin_values}")
print(f"Gaps: {[yayin_values[i+1] - yayin_values[i] for i in range(len(yayin_values)-1)]}")
print()

# Test 2: What if 0 is reserved for "no tone"?
print("HYPOTHESIS 2: yayin starts at 1, with 0 = 'no tone'")
print("-" * 70)
print("If yayin=0 means 'no tone', then:")
print("  - yayin=1 corresponds to first tone (67.0 Hz)")
print("  - This matches! 67.0 Hz -> yayin = 1")
print()

# Check if pattern holds with yayin starting at 1
print("Testing: yayin = standard_table_position")
print()
print("Frequency | Table Pos | yayin | Match?")
print("-" * 70)

perfect_match = True
for freq, yayin in sorted(DISCOVERED.items()):
    std_pos = STANDARD_ORDER.index(freq) + 1  # 1-based
    match = "✅ YES" if std_pos == yayin else f"❌ NO (off by {yayin - std_pos})"
    if std_pos != yayin:
        perfect_match = False
    print(f"{freq:6.1f} Hz | {std_pos:9d} | {yayin:5d} | {match}")

print()
if perfect_match:
    print("✅✅✅ PERFECT MATCH! yayin = standard_table_position")
else:
    print("Pattern close but not perfect. Let me try other orderings...")
    print()
    
    # Test 3: Maybe there's an extra tone at position 26?
    print("HYPOTHESIS 3: Radio has extra entry between index 25 and 26")
    print("-" * 70)
    
    # Create modified table with gap at position 26
    modified_order = STANDARD_ORDER[:25] + [None] + STANDARD_ORDER[25:]
    
    print("\nTesting with hypothetical gap at position 26:")
    print("Frequency | Modified Pos | yayin | Match?")
    print("-" * 70)
    
    gap_match = True
    for freq, yayin in sorted(DISCOVERED.items()):
        std_pos = STANDARD_ORDER.index(freq) + 1
        # Adjust for gap if after position 25
        modified_pos = std_pos if std_pos <= 25 else std_pos + 1
        match = "✅ YES" if modified_pos == yayin else f"❌ NO (off by {yayin - modified_pos})"
        if modified_pos != yayin:
            gap_match = False
        print(f"{freq:6.1f} Hz | {modified_pos:12d} | {yayin:5d} | {match}")
    
    print()
    if gap_match:
        print("✅✅✅ PATTERN FOUND! Radio has gap at position 26")
        print("Formula: yayin = standard_position (positions 1-25)")
        print("         yayin = standard_position + 1 (positions 26+)")
    else:
        print("❌ Gap hypothesis doesn't explain the pattern")

print()
