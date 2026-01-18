"""Analyze if CTCSS yayin values follow a pattern related to standard tone table"""

# Standard CTCSS tone frequencies (50 tones) in frequency order
# This is the standard used by CHIRP and most amateur radio software
STANDARD_CTCSS_TONES = [
    67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8,
    97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8,
    136.5, 141.3, 146.2, 151.4, 156.7, 162.2, 167.9, 173.8, 179.9, 186.2,
    192.8, 203.5, 210.7, 218.1, 225.7, 233.6, 241.8, 250.3, 69.3, 159.8,
    165.5, 171.3, 177.3, 183.5, 189.9, 196.6, 199.5, 206.5, 229.1, 254.1
]

# Discovered mappings from radio testing
DISCOVERED_MAPPINGS = {
    67.0: 1,
    88.5: 9,
    100.0: 13,
    123.0: 19,
    146.2: 24,
    156.7: 27,
}

print("=" * 70)
print("CTCSS Tone Encoding Pattern Analysis")
print("=" * 70)
print()

print("Testing Hypothesis: yayin = index_in_standard_table + offset")
print()

# Analyze pattern
print("Frequency | Std Index | yayin | Difference | Pattern")
print("-" * 70)

for freq, yayin in sorted(DISCOVERED_MAPPINGS.items()):
    try:
        std_index = STANDARD_CTCSS_TONES.index(freq) + 1  # 1-based index
        diff = yayin - std_index
        print(f"{freq:6.1f} Hz | {std_index:9d} | {yayin:5d} | {diff:+10d} | ", end="")
        
        if diff == 0:
            print("EXACT MATCH!")
        elif diff == 1:
            print("index + 1")
        elif diff == -1:
            print("index - 1")
        else:
            print(f"index {diff:+d}")
            
    except ValueError:
        print(f"{freq:6.1f} Hz | NOT FOUND | {yayin:5d} | N/A")

print()
print("=" * 70)
print("Pattern Summary")
print("=" * 70)

# Check if there's a consistent pattern
differences = []
for freq, yayin in DISCOVERED_MAPPINGS.items():
    if freq in STANDARD_CTCSS_TONES:
        std_index = STANDARD_CTCSS_TONES.index(freq) + 1
        differences.append(yayin - std_index)

if differences:
    if len(set(differences)) == 1:
        offset = differences[0]
        print(f"\n✅ PATTERN FOUND: yayin = standard_table_index {offset:+d}")
        print(f"\nFormula: yayin = (position in CTCSS table) {offset:+d}")
        
        # Test the pattern on all 50 tones
        print(f"\n{'=' * 70}")
        print("Predicted Mappings for All 50 CTCSS Tones")
        print("=" * 70)
        print()
        
        for i, freq in enumerate(STANDARD_CTCSS_TONES, 1):
            predicted_yayin = i + offset
            status = ""
            if freq in DISCOVERED_MAPPINGS:
                actual = DISCOVERED_MAPPINGS[freq]
                if actual == predicted_yayin:
                    status = "✅ VERIFIED"
                else:
                    status = f"❌ MISMATCH (actual={actual})"
            else:
                status = "⚠️  UNTESTED"
            
            print(f"{i:2d}. {freq:6.1f} Hz -> yayin = {predicted_yayin:3d}  {status}")
    else:
        print(f"\n❌ NO CONSISTENT PATTERN")
        print(f"Differences vary: {set(differences)}")
        print(f"\nThe encoding may be more complex or use a different tone ordering.")
else:
    print("\n❌ Could not determine pattern")

print()
