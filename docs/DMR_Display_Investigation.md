# DMR Display Mode Investigation

## ⚠️ DOCUMENTATION DISCREPANCY IDENTIFIED (January 21, 2026)

**There is a conflict between this document and `docs/DMR_Display_Modes.md`:**

| Document | Claim |
|----------|-------|
| `DMR_Display_Investigation.md` (this file) | `callFormat` does **NOT** control DMR vs DFM display |
| `DMR_Display_Modes.md` | `callFormat` **DOES** control it (0=DFM, 1/2=DMR) |

**Resolution Required:** Run Test 13 (`tests/test_configs/13_dmr_dfm_display_test.json`) to definitively determine which claim is correct.

---

## The Problem

When configuring DMR channels, the radio displays either "DMR" or "DFM" on the screen, but we cannot determine which field controls this display.

## What We've Learned

### Test Results (2026-01-21)

1. **Uploaded test config** with varied `callFormat` values (0, 1, 2 for private, group, all call)
2. **Radio displayed ALL channels as "DFM"** regardless of callFormat value
3. **Manually set channel 8** on the radio to "DMR, group call, 99"
4. **Read back the configuration** - channel 8 and all others still show `callFormat=0`

### Conclusion

**The `callFormat` field does NOT control the DMR vs DFM display.**

## Current Field Understanding

```python
# What we know callFormat does:
callFormat = 0  # Private/Single Call (but doesn't affect DMR/DFM display)
callFormat = 1  # Group Call (but doesn't affect DMR/DFM display)  
callFormat = 2  # All Call (but doesn't affect DMR/DFM display)
```

## Possible Explanations

1. **Global Setting**: DMR vs DFM might be a global radio setting, not per-channel
2. **Different Field**: Another field we haven't identified controls the display
3. **Computed Value**: The display might be determined by a combination of fields
4. **Firmware Version**: Different firmware might handle this differently

## Fields to Investigate

Looking at DMR channel data, these fields could potentially control the display:
- `vfoaMode` / `vfobMode` (currently 9 for DMR)
- `slot` (1 or 2)
- `rxCc` / `txCc` (color code)
- Some combination of DMR ID fields
- Unknown/undiscovered field

## Investigation Status (2026-01-21)

### What Works Correctly

✅ **Call Format Field (`callFormat`)**
- `callFormat = 0` → Private/Single call - **CONFIRMED WORKING**
- `callFormat = 1` → Group call - **CONFIRMED WORKING**
- `callFormat = 2` → All call - **CONFIRMED WORKING**

Manual testing confirmed that setting callFormat correctly changes the call behavior on the radio.

### What Doesn't Work

❌ **DMR vs DFM Display Label**
- All DMR channels currently display as "DFM" regardless of configuration
- The field controlling this display mode has **NOT been identified**
- This appears to be independent of `callFormat`, `chType`, and all tested DMR fields

### Data Collected

1. **Test uploads with varied callFormat** - Channels displayed as DFM
2. **Manual radio configuration** - Set channel 8 to DMR mode successfully
3. **Readback comparisons**:
   - Before manual change: All channels show DFM
   - After manual change: Channel 8 shows DMR (but field not identified)
   - Files: `radio_readback_260120_2331.json`, `radio_readback_260120_2349.json`, `radio_readback_260121_0037.json`

### Side Findings

- After testing, analog channels show `callFormat: 1` in readback (we didn't set this)
- Radio may auto-set certain fields during save/load operations
- DMR implementation otherwise works correctly (Color Codes, IDs, Slots, etc.)

## Next Steps for Investigation

### 🔴 ACTION REQUIRED: Run Test 13

**Test Configuration:** `tests/test_configs/13_dmr_dfm_display_test.json`
**Instructions:** `tests/test_configs/13_Test_Instructions.md`

This test systematically varies `callFormat` values (0, 1, 2, 255) across 10 channels to definitively determine if `callFormat` controls the DMR vs DFM display.

**Test Matrix:**
| Channel | callFormat | Expected if hypothesis correct |
|---------|------------|-------------------------------|
| 0, 4, 7 | 0 | DFM (Private call) |
| 1, 5, 8 | 1 | DMR (Group call) |
| 2, 9 | 2 | DMR (All call) |
| 3 | 255 | Unknown |

### If Test 13 is Inconclusive

1. **USB Serial Analysis Required**
   - Capture UART communication when manually changing DMR ↔ DFM on radio
   - Compare byte-level differences in channel data packets
   - Look for fields not currently mapped in our JSON structure

2. **Factory Codeplug Analysis**
   - Read factory-programmed channels that display as "DMR"
   - Compare field values with our test channels
   - May reveal undiscovered fields or global settings

3. **Possible Explanations to Test**
   - Global DMR mode setting (not per-channel)
   - Undiscovered byte/field in channel structure
   - Firmware-specific behavior (may vary by version)
   - Multi-byte field combination (e.g., chType + another field)

## Related Files

- **NEW Test 13**: `tests/test_configs/13_dmr_dfm_display_test.json` - callFormat variation test
- **Test Instructions**: `tests/test_configs/13_Test_Instructions.md`
- **Conflicting doc**: `docs/DMR_Display_Modes.md` - claims callFormat controls display
- Test config: `tests/test_configs/12_dmr_color_code_test.json`
- Writer code: `pmr_171_cps/writers/pmr171_writer.py`
- UART protocol docs: `docs/Pmr171_Protocol.md`

## Notes for Future Work

- The current implementation works for all DMR functionality except the display label
- Users can successfully use DMR features; the "DFM" label is cosmetic
- **Run Test 13 before pursuing UART capture** - may resolve the issue
- Consider this a low-priority issue since functionality is correct

## Document History

- **Created**: January 21, 2026
- **Updated**: January 21, 2026 - Added discrepancy note, Test 13 reference
