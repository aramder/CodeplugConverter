# Test 13: DMR vs DFM Display Mode Investigation

## Purpose
Determine which JSON field controls whether a digital channel displays as "DMR" or "DFM" on the PMR-171 radio screen.

## Background

### The Issue
DMR channels may display as either "DMR" or "DFM" on the radio. Previous testing has produced conflicting results:
- Some documentation claims `callFormat` controls this (0=DFM, 1/2=DMR)
- Other documentation states `callFormat` does NOT control the display

### Hypothesis
The `callFormat` field determines the display:
| callFormat | Expected Display | Call Type |
|------------|------------------|-----------|
| 0 | DFM | Private/Single call |
| 1 | DMR | Group call |
| 2 | DMR | All Call |
| 255 | Unknown | Undefined |

## Test Configuration
- **File**: `13_dmr_dfm_display_test.json`
- **Channels**: 10 (0-9)
- **Frequency**: 446.000 MHz (all channels, simplex)
- **Mode**: DMR (vfoaMode=9, vfobMode=9)
- **chType**: 1 for all digital channels (channel 6 is analog reference)
- **DMR ID**: 3107683 (ownId bytes: 0, 47, 103, 67)

## Channel Assignments

| Ch | Name | callFormat | chType | slot | callId | Expected Display |
|----|------|------------|--------|------|--------|------------------|
| 0 | CF0_PRIVATE | 0 | 1 | TS1 | TG 9 | DFM (?) |
| 1 | CF1_GROUP | 1 | 1 | TS1 | TG 9 | DMR (?) |
| 2 | CF2_ALL | 2 | 1 | TS1 | TG 9 | DMR (?) |
| 3 | CF255_UNK | 255 | 1 | TS1 | TG 9 | Unknown |
| 4 | CF0_PVCALL | 0 | 1 | TS1 | ID 3107683 | DFM (?) |
| 5 | CF1_TG91 | 1 | 1 | TS1 | TG 91 | DMR (?) |
| 6 | ANALOG_REF | 0 | 0 | - | - | FM (reference) |
| 7 | CF0_TS2 | 0 | 1 | TS2 | TG 9 | DFM (?) |
| 8 | CF1_TS2 | 1 | 1 | TS2 | TG 9 | DMR (?) |
| 9 | CF2_ALLCALL | 2 | 1 | TS1 | All (255.255.255.255) | DMR (?) |

## Test Procedure

### Step 1: Upload Test Configuration
1. Open the PMR-171 CPS GUI
2. File → Open JSON → Select `tests/test_configs/13_dmr_dfm_display_test.json`
3. Verify all 10 channels load correctly
4. Connect radio programming cable
5. Radio → Write to Radio
6. Select channels 0-9
7. Confirm write completes successfully

### Step 2: Observe Radio Display
For each channel (0-9), navigate on the radio and record:

| Ch | Name Displayed | Mode Displayed | Notes |
|----|----------------|----------------|-------|
| 0 | | DMR / DFM / Other | |
| 1 | | DMR / DFM / Other | |
| 2 | | DMR / DFM / Other | |
| 3 | | DMR / DFM / Other | |
| 4 | | DMR / DFM / Other | |
| 5 | | DMR / DFM / Other | |
| 6 | | FM (expected) | Analog reference |
| 7 | | DMR / DFM / Other | |
| 8 | | DMR / DFM / Other | |
| 9 | | DMR / DFM / Other | |

### Step 3: Read Back Configuration
1. Radio → Read from Radio
2. Select channels 0-9
3. Save readback as `tests/test_configs/Results/13_dmr_dfm_display_readback.json`
4. Compare to original to check for any field changes

### Step 4: Manual Verification (if all display same mode)
If all digital channels display the SAME mode (all DFM or all DMR):
1. Manually change ONE channel on the radio:
   - Go to channel 1
   - Use radio menu to toggle between DMR and DFM mode
2. Read back from radio again
3. Save as `13_dmr_dfm_display_manual_change_readback.json`
4. Compare the two readback files to find the changed field

### Step 5: UART Capture (Optional)
If the controlling field cannot be identified from JSON:
1. Connect UART monitoring device (USB-to-serial + serial monitor software)
2. Capture bytes during manual DMR↔DFM toggle on radio
3. Analyze byte patterns to identify the controlling field

## Expected Results

### If hypothesis is CORRECT:
| callFormat | Display |
|------------|---------|
| 0 | DFM |
| 1 | DMR |
| 2 | DMR |

### If hypothesis is INCORRECT:
All channels may display the same mode, indicating:
- A global setting controls DMR vs DFM (not per-channel)
- A different/unknown field controls the display
- The field is not exposed in JSON format

## Analysis Script

```python
import json

# Load original test config
with open('13_dmr_dfm_display_test.json') as f:
    original = json.load(f)

# Load readback (after upload)
with open('Results/13_dmr_dfm_display_readback.json') as f:
    readback = json.load(f)

print("callFormat Comparison:")
print("-" * 60)
for ch in range(10):
    ch_id = str(ch)
    if ch_id in original.get('channels', original):
        orig_cf = original.get('channels', original)[ch_id].get('callFormat', 'N/A')
        read_cf = readback.get('channels', readback).get(ch_id, {}).get('callFormat', 'N/A')
        name = original.get('channels', original)[ch_id].get('channelName', '').replace('\x00', '')
        
        match = "✓" if orig_cf == read_cf else "✗ CHANGED"
        print(f"CH {ch}: {name:12s} | Original CF={orig_cf:3} | Readback CF={read_cf:3} | {match}")

print("-" * 60)
print("\nRecord observed display modes and update documentation.")
```

## Possible Findings

### Scenario A: callFormat controls display
- CH 0, 4, 7 show "DFM" (callFormat=0)
- CH 1, 5, 8 show "DMR" (callFormat=1)
- CH 2, 9 show "DMR" (callFormat=2)
- **Action**: Document callFormat as the controlling field

### Scenario B: All channels show DFM
- All digital channels display "DFM" regardless of callFormat
- **Action**: Look for unmapped field or global setting

### Scenario C: All channels show DMR
- All digital channels display "DMR" regardless of callFormat
- **Action**: Look for unmapped field or global setting

### Scenario D: Radio changes callFormat values
- Readback shows different callFormat than uploaded
- **Action**: Radio may auto-correct to a default; note the pattern

## Documentation Updates

After testing, update these files:
1. `docs/DMR_Display_Investigation.md` - Update with findings
2. `docs/DMR_Display_Modes.md` - Correct if hypothesis wrong
3. `TODO.md` - Update Known Issues section
4. `pmr_171_cps/writers/pmr171_writer.py` - Update comments if needed

## Related Files
- Test config: `tests/test_configs/13_dmr_dfm_display_test.json`
- Previous investigation: `docs/DMR_Display_Investigation.md`
- Previous conclusions: `docs/DMR_Display_Modes.md`
- Writer code: `pmr_171_cps/writers/pmr171_writer.py`

---

**Created**: January 21, 2026
**Purpose**: Resolve conflicting documentation about DMR vs DFM display control
**Status**: Ready for testing
