# Test 12: DMR Color Code Mapping Verification

## Purpose
Verify that all 16 DMR color codes (0-15) are correctly sent to and read back from the PMR-171 radio.

## Test Configuration
- **File**: `12_dmr_color_code_test.json`
- **Channels**: 0-15 (16 channels total)
- **Frequency Range**: 446.006000 - 446.118750 MHz (12.5 kHz steps)
- **Mode**: DMR (mode 9)

## Channel Assignments

| Ch | Name       | Frequency (MHz) | RX CC | TX CC | Slot | TG   |
|----|------------|-----------------|-------|-------|------|------|
| 0  | DMR CC 0   | 446.006000      | 0     | 0     | TS1  | 9    |
| 1  | DMR CC 1   | 446.018750      | 1     | 1     | TS1  | 9    |
| 2  | DMR CC 2   | 446.031250      | 2     | 2     | TS1  | 9    |
| 3  | DMR CC 3   | 446.043750      | 3     | 3     | TS1  | 9    |
| 4  | DMR CC 4   | 446.056250      | 4     | 4     | TS1  | 9    |
| 5  | DMR CC 5   | 446.068750      | 5     | 5     | TS1  | 9    |
| 6  | DMR CC 6   | 446.081250      | 6     | 6     | TS1  | 9    |
| 7  | DMR CC 7   | 446.093750      | 7     | 7     | TS1  | 9    |
| 8  | DMR CC 8   | 446.106250      | 8     | 8     | TS1  | 9    |
| 9  | DMR CC 9   | 446.118750      | 9     | 9     | TS1  | 9    |
| 10 | DMR CC 10  | 446.131250      | 10    | 10    | TS2  | 91   |
| 11 | DMR CC 11  | 446.143750      | 11    | 11    | TS2  | 91   |
| 12 | DMR CC 12  | 446.156250      | 12    | 12    | TS2  | 91   |
| 13 | DMR CC 13  | 446.168750      | 13    | 13    | TS2  | 91   |
| 14 | DMR CC 14  | 446.181250      | 14    | 14    | TS2  | 91   |
| 15 | DMR CC 15  | 446.193750      | 15    | 15    | TS2  | 91   |

## Test Procedure

### Step 1: Upload Test Configuration
1. Open the PMR-171 CPS GUI
2. File → Open JSON → Select `tests/test_configs/12_dmr_color_code_test.json`
3. Verify all 16 channels appear with correct names (DMR CC 0 through DMR CC 15)
4. Connect radio programming cable
5. Program → Write to Radio
6. Select "Write all channels" or range 0-15
7. Confirm write completes successfully

### Step 2: Verify on Radio Display
1. Navigate to each channel on the radio (CH 0 through CH 15)
2. For each channel, verify:
   - Name shows "DMR CC X" where X matches the channel number
   - Frequency matches expected value
   - Color Code display (if available) shows the correct value

### Step 3: Read Back and Compare
1. In CPS, File → New (or close and reopen)
2. Program → Read from Radio
3. Select channels 0-15
4. After read completes, verify each channel:
   - `rxCc` field matches expected (0-15)
   - `txCc` field matches expected (0-15)
   - `slot` field is correct (1 for CH 0-9, 2 for CH 10-15)
5. Save readback as `tests/test_configs/Results/12_dmr_color_code_readback.json`

### Step 4: Automated Verification
Run the Python verification script:

```bash
cd tests/test_configs/Results
python verify_color_codes.py
```

Or use this inline verification:

```python
import json

# Load original test config
with open('12_dmr_color_code_test.json') as f:
    original = json.load(f)

# Load readback
with open('Results/12_dmr_color_code_readback.json') as f:
    readback = json.load(f)

# Compare color codes
print("Color Code Verification:")
print("-" * 50)
all_pass = True
for ch in range(16):
    ch_id = str(ch)
    expected_cc = ch
    actual_rx_cc = readback[ch_id].get('rxCc', -1)
    actual_tx_cc = readback[ch_id].get('txCc', -1)
    
    rx_ok = actual_rx_cc == expected_cc
    tx_ok = actual_tx_cc == expected_cc
    status = "PASS" if (rx_ok and tx_ok) else "FAIL"
    
    if not (rx_ok and tx_ok):
        all_pass = False
    
    print(f"CH {ch:2d}: Expected CC={expected_cc:2d} | "
          f"RX CC={actual_rx_cc:2d} {'✓' if rx_ok else '✗'} | "
          f"TX CC={actual_tx_cc:2d} {'✓' if tx_ok else '✗'} | {status}")

print("-" * 50)
print(f"OVERALL: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
```

## Expected Results
- All 16 color codes (0-15) should read back correctly
- RX CC and TX CC should match for each channel
- Timeslot should match (TS1 for CH 0-9, TS2 for CH 10-15)

## Notes
- Color codes 0-15 are valid DMR color codes
- The test also exercises different timeslots
- Own ID is set to 1234567 (0x0012D687) for all channels
- Call ID is TG 9 for CH 0-9, TG 91 for CH 10-15

## Troubleshooting
If color codes don't read back correctly:
1. Check if factory CPS shows the correct values
2. Verify UART capture shows correct bytes being sent
3. Check if radio firmware has color code limitations
