# Test 13A: DMR vs DFM Display Test (Safe Version)

## Purpose
Test whether the `callFormat` field controls the "DMR" vs "DFM" display label on the radio screen, using only safe/valid callFormat values.

## Issue with Test 13
Test 13 caused the radio to crash and lose channel names after reboot. The issue was likely caused by `callFormat=255`, which is wildly out of range. Test 13A removes this problematic value.

## Test Configuration
File: `tests/test_configs/13a_dmr_dfm_safe_test.json`

All channels at 446.000 MHz with DMR configuration:
- DMR ID: 3107683
- Color Code: 1 (RX/TX)
- vfoaMode=9, vfobMode=9 (DMR)

### Channel Layout
| Ch# | Name | callFormat | Call Type | Slot | Call ID | Notes |
|-----|------|------------|-----------|------|---------|-------|
| 0 | CF0_CH0 | 0 | Private | 1 | 1 | Private call to ID 1 |
| 1 | CF1_CH1 | 1 | Group | 1 | 9 | Group call to TG 9 |
| 2 | CF2_CH2 | 2 | All | 1 | 16 | All call |
| 3 | CF0_CH3 | 0 | Private | 1 | 10000 | Private call to larger ID |
| 4 | CF1_CH4 | 1 | Group | 1 | 91 | Group call to TG 91 |
| 5 | CF2_CH5 | 2 | All | 1 | 16 | All call (duplicate) |
| 6 | ANALOG_REF | N/A | Analog | N/A | N/A | Analog reference channel |
| 7 | CF0_TS2 | 0 | Private | 2 | 1 | Private on timeslot 2 |
| 8 | CF1_TS2 | 1 | Group | 2 | 9 | Group on timeslot 2 |
| 9 | CF2_ALLCALL | 2 | All | 1 | 16 | All call |

## Test Procedure

### 1. Upload Configuration
1. Open PMR-171 CPS GUI
2. File → Open → `tests/test_configs/13a_dmr_dfm_safe_test.json`
3. Radio → Write to Radio
4. Wait for write to complete successfully

### 2. Observe Display Mode on Radio
Power cycle the radio if needed, then check each channel:
1. Navigate through channels 0-9 using the channel selector
2. For each digital channel (0-5, 7-9), record:
   - Channel number
   - Channel name shown
   - Display mode shown ("DMR" or "DFM")
   - Whether radio is stable

### 3. Read Back Configuration
1. Radio → Read from Radio
2. Save as `tests/test_configs/Results/13a_dmr_dfm_safe_readback.json`

### 4. Manual Verification (Optional)
If all channels show the same mode:
1. Manually change 2-3 channels to the opposite mode (DMR ↔ DFM)
2. Note which channels were changed
3. Read from radio again
4. Save as `tests/test_configs/Results/13a_manual_change_readback.json`

## Expected Outcomes

### If callFormat Controls Display
- Channels with callFormat=0 (Ch 0, 3, 7) should show "DFM"
- Channels with callFormat=1 (Ch 1, 4, 8) should show "DMR"
- Channels with callFormat=2 (Ch 2, 5, 9) should show "DMR"

### If callFormat Does NOT Control Display
- All channels will show the same mode ("DMR" or "DFM")
- Manual changes will reveal the actual controlling field

## Analysis

Run the following to compare readback with expected values:

```python
import json

# Load readback
with open('tests/test_configs/Results/13a_dmr_dfm_safe_readback.json', 'r') as f:
    readback = json.load(f)

# Check if callFormat was preserved
print("Channel | callFormat | Preserved?")
print("--------|------------|----------")
expected = {
    "0": 0, "1": 1, "2": 2, "3": 0, "4": 1,
    "5": 2, "7": 0, "8": 1, "9": 2
}
for ch, exp_cf in expected.items():
    actual_cf = readback[ch].get('callFormat', 'N/A')
    match = "✓" if actual_cf == exp_cf else "✗"
    print(f"{ch:7} | {exp_cf:10} | {actual_cf:10} {match}")
```

If manual changes were made, compare the two readback files to identify which fields changed.

## Success Criteria
1. Radio remains stable throughout test (no crashes)
2. Channel names persist after reboot
3. All callFormat values are preserved correctly in readback
4. Clear pattern emerges showing which field controls DMR vs DFM display

## Notes
- This test uses only valid callFormat values (0, 1, 2)
- If this test is successful, it definitively proves/disproves the callFormat hypothesis
- If inconclusive, UART capture will be needed to identify the controlling field
