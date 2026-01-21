# DMR Display Modes: DFM vs DMR

## Discovery Summary

The PMR-171 radio displays DMR channels in two different modes: **DFM** and **DMR**. Both modes use the same underlying digital mode (`chType = 1`, `vfoaMode/vfobMode = 9`), but the radio's display changes based on the `callFormat` field.

**Discovery Date:** January 20-21, 2026  
**Test Configuration:** `tests/test_configs/12_dmr_color_code_test.json`  
**Readback File:** `radio_readback_260120_2331.json`

## Field Mappings

### Channel Type Field (`chType`)
- **Analog channels:** `chType = 0`
- **Digital channels (both DFM and DMR):** `chType = 1`

### Call Format Field (`callFormat`)

The `callFormat` field determines how the radio displays the digital channel:

| callFormat | Display Mode | Call Type | Description |
|------------|--------------|-----------|-------------|
| 0 | **DFM** | Single/Private | Private call to specific DMR ID |
| 1 | **DMR** | Group | Group call to talk group |
| 2 | **DMR** | All Call | Broadcast to all stations |

## Test Results

### Test Configuration (12_dmr_color_code_test.json)

```json
Channel 0: "DMR Private"  - callFormat: 0 → Radio displays: DFM
Channel 1: "DMR Group"    - callFormat: 1 → Radio displays: DMR
Channel 2: "DMR AllCall"  - callFormat: 2 → Radio displays: DMR
```

### Radio Readback Confirmation

All test channels had identical settings except for `callFormat`:
- All used `chType: 1` (digital mode)
- All used `vfoaMode/vfobMode: 9` (DMR mode value)
- Channel 0 with `callFormat: 0` read back with radio showing "DFM"
- Channels 1-2 with `callFormat: 1/2` read back with radio showing "DMR"

## Implementation Notes

### Writer Code
The `PMR171Writer.create_channel()` method has been updated to:

```python
# All digital modes use chType 1 (both DFM and DMR)
if is_digital:
    ch_type = 1  # All digital modes use chType 1
else:
    ch_type = 0  # Analog channels use chType 0
```

The `callFormat` field should be passed via `kwargs` to control the display mode:
- Pass `callFormat=0` for private/single calls (displays as DFM)
- Pass `callFormat=1` for group calls (displays as DMR)
- Pass `callFormat=2` for all calls (displays as DMR)

### Color Code Behavior

The DMR Color Code (CC) fields (`rxCc`, `txCc`) work independently of the DFM/DMR display:
- Both DFM and DMR modes support all color codes (0-15)
- Color code filtering operates the same in both display modes
- The display mode is purely cosmetic based on call type

## Technical Details

### DFM (Digital FM) Mode
- Used for **private/single calls** to specific DMR IDs
- Still uses DMR protocol (mode 9)
- Still uses digital channel type (chType 1)
- Display shows "DFM" instead of "DMR"
- Uses `callId1-4` fields to specify target DMR ID

### DMR (Digital Mobile Radio) Mode
- Used for **group calls** and **all calls**
- Same technical implementation as DFM
- Display shows "DMR" instead of "DFM"
- Group calls use talk group ID in `callId1-4` fields
- All calls use `callId1-4 = 0xFF, 0xFF, 0xFF, 0xFF`

## Historical Context

Prior to this discovery, the writer was incorrectly setting:
- Analog channels: `chType = 255` (should be `0`)
- Digital channels: `chType = 1` (correct)

The correct mapping is:
- Analog channels: `chType = 0`
- Digital channels: `chType = 1`

The radio's display of "DFM" vs "DMR" is controlled by `callFormat`, not by a separate field.

## References

- Test Configuration: `tests/test_configs/12_dmr_color_code_test.json`
- Test Readback: `radio_readback_260120_2331.json`
- Writer Implementation: `pmr_171_cps/writers/pmr171_writer.py`
- Test Instructions: `tests/test_configs/12_Test_Instructions.md`
