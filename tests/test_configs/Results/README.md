# PMR-171 Test Configuration Files

This directory contains a comprehensive set of test JSON files for validating PMR-171 radio compatibility.

## Purpose

These test files are designed to verify that generated JSON configurations are correctly processed by:
1. Guohetec PMR-171 factory programming software
2. The actual PMR-171 radio hardware

**IMPORTANT**: All test files have been updated (January 17, 2026) to match the actual format extracted from a real PMR-171 radio. Key changes:
- `callFormat`: 255 for analog (not 0)
- `chType`: 255 for analog (not 0)
- `txCc`: 1 (not 2)
- `rxCtcss`/`txCtcss`: 255 for "no tone" (not 0)

## Test Files

### 01_simple_analog.json
**Purpose**: Basic analog FM operation test  
**Channels**: 3  
**Tests**:
- VHF simplex (146.52 MHz)
- UHF simplex (446.0 MHz)  
- VHF repeater with offset (146.94/146.34 MHz)

**Format Details**:
- callFormat: 255 (analog)
- chType: 255 (analog)
- txCc: 1 (standard)
- rxCtcss/txCtcss: 255 (no tone)

**Expected Results**:
- All channels should load without errors
- Frequencies should display correctly
- NFM mode should be selected
- Simplex channels should show same RX/TX
- Repeater channel should show split frequencies

---

### 02_multi_mode.json
**Purpose**: Verify all modulation modes  
**Channels**: 11  
**Tests**:
- Mode 0: USB (14.2 MHz HF)
- Mode 1: LSB (3.8 MHz HF)
- Mode 2: CWR - CW Reverse (3.8 MHz)
- Mode 3: CWL - CW Lower (14.2 MHz)
- Mode 4: AM (118.1 MHz aviation)
- Mode 5: WFM - Wide FM (98.5 MHz broadcast)
- Mode 6: NFM - Narrow FM (146.52 MHz)
- Mode 7: DIGI - Generic digital (446.0 MHz)
- Mode 8: PKT - Packet (146.94 MHz)
- Mode 9: DMR - Digital Mobile Radio (446.0 MHz)
- Mode 6: 223 MHz band test

**Format Details**:
- Analog channels: callFormat=255, chType=255
- Digital channels: callFormat=2, chType=1
- All use txCc=1

**Expected Results**:
- Factory software should recognize all mode types
- Radio should correctly display mode on each channel
- Mode transitions between analog and digital should work

**Note**: CWR/CWL are BFO (Beat Frequency Oscillator) receiver modes for CW reception:
- CWR = USB-side BFO (typically 700-800 Hz above carrier)
- CWL = LSB-side BFO (typically 700-800 Hz below carrier)

---

### 03_digital_dmr.json
**Purpose**: Digital DMR channel validation  
**Channels**: 13  
**Tests**:
- DMR slot 1 and slot 2 channels
- Various talk groups (TG 0, 1, 9, 255, 1000, 10000, 30000, 50000, 100000)
- Different color codes (CC 1, 2)
- Simplex and repeater DMR
- DMR ID: 3107683 (0x002F6743)
- Various callId values

**Format Details**:
- callFormat: 2 (digital)
- chType: 1 (digital)
- rxCtcss/txCtcss: 255 (not used in DMR)
- rxCc/txCc: DMR color code (1-15)
- slot: 1 or 2

**Expected Results**:
- Channels should be marked as "Digital" or "DMR"
- DMR ID should display as 3107683
- Slot 1 and Slot 2 should be differentiated
- Talk group numbers should display correctly
- Color codes should be configurable
- Factory software should not show errors

**Key Fields**:
- `callFormat`: 2 (required for digital)
- `chType`: 1 (digital)
- `vfoaMode`/`vfobMode`: 9 (DMR)
- `ownId`: [0, 47, 103, 67] = 3107683
- `callId`: Big-endian 32-bit talk group ID
- `slot`: 1 or 2 (DMR timeslot)
- `rxCc`/`txCc`: 1-15 (DMR color code)

---

### 04_mixed_analog_digital.json
**Purpose**: Verify mixed analog/digital channel operation  
**Channels**: 11  
**Tests**:
- Channel 0: Analog FM simplex (callFormat=255, chType=255)
- Channel 1: Digital DMR slot 1 (callFormat=2, chType=1)
- Channel 2: Analog FM with CTCSS (callFormat=255, chType=255)
- Channel 3: Digital DMR slot 2 (callFormat=2, chType=1)
- Channel 4: Analog UHF repeater (callFormat=255, chType=255)
- Channel 5: Analog AM (callFormat=255, chType=255)
- Channel 6: Digital DMR TG 1000 (callFormat=2, chType=1)
- Channel 7: Analog USB HF (callFormat=255, chType=255)
- Channel 8: Analog 223 MHz with CTCSS (callFormat=255, chType=255)
- Channel 9: Digital DMR simplex (callFormat=2, chType=1)
- Channel 10: Analog Wide FM (callFormat=255, chType=255)

**Format Details**:
- Analog: callFormat=255, chType=255, txCc=1, no tone=255
- Digital: callFormat=2, chType=1, rxCc/txCc=DMR color code

**Expected Results**:
- Factory software should load all channels without conflict
- Analog channels should show callFormat=255
- Digital channels should show callFormat=2
- Mode indicators should be correct for each channel
- No cross-contamination between analog/digital settings
- Channel order alternating between types should work

---

### 05_ctcss_dcs.json
**Purpose**: CTCSS and DCS tone encoding validation  
**Channels**: 13  
**Tests**:
- Channel 0: No tone (rxCtcss=255, txCtcss=255)
- Channel 1: CTCSS 67.0 Hz (rxCtcss=0, txCtcss=0) - index 0 encoding
- Channel 2: CTCSS 100.0 Hz (rxCtcss=10, txCtcss=10)
- Channel 3: CTCSS 123.0 Hz (rxCtcss=17, txCtcss=17)
- Channel 4: CTCSS 146.2 Hz with repeater offset (rxCtcss=23, txCtcss=23)
- Channel 5: Split tone (RX 100.0, TX 146.2)
- Channel 6: DCS 023 (rxCtcss=104, txCtcss=104)
- Channel 7: DCS 754 (rxCtcss=186, txCtcss=186)
- Channel 8: RX tone only (rxCtcss=17, txCtcss=255)
- Channel 9: TX tone only (rxCtcss=255, txCtcss=17)
- Channel 10: CTCSS 88.5 Hz with repeater
- Channel 11: CTCSS 156.7 Hz with repeater
- Channel 12: DCS 114

**Format Details**:
- No tone: 255 (not 0!)
- CTCSS tones: Index into standard CTCSS table (0-50)
- DCS codes: Index into standard DCS table (104+)

**Expected Results**:
- Channel 0 should show "Off" or no tone indicator
- CTCSS channels should display tone frequency correctly
- DCS channels should display code correctly
- Split tone operation should work
- RX-only and TX-only tones should function
- Factory software should correctly interpret tone encoding

**CTCSS/DCS Encoding Pattern** (Based on actual radio dump):
- 255 = No tone/Off
- 0-50 = CTCSS tones (indexed, e.g., 0=67.0Hz, 10=100.0Hz, 17=123.0Hz, 23=146.2Hz)
- 104+ = DCS codes (e.g., 104=D023N, 115=D114N, 186=D754N)

---

### 06_edge_cases.json
**Purpose**: Boundary condition and edge case testing  
**Channels**: 10  
**Tests**:
- Channel 0 (minimum channel number)
- Channel 255 (max single-byte)
- Channel 256 (first double-byte)
- Channel 511 (max 9-bit)
- Channel 512 (first triple in channelHigh)
- Channel 999 (maximum channel supported by radio)
- Channel 100 (15-character name test)
- Channel 200 (large repeater offset ~5.5 MHz)
- Channel 300 (DMR with maximum values)
- Channel 500 (minimum VHF frequency ~137 MHz)
- Channel 600 (maximum VHF frequency ~174 MHz)
- Channel 700 (minimum UHF frequency ~400 MHz)
- Channel 800 (maximum UHF frequency ~480 MHz)
- Channel 900 (empty/minimal name)

**Format Details**:
- Tests channelHigh/channelLow encoding across full range (0-999)
- Tests frequency limits for VHF (137-174 MHz) and UHF (400-480 MHz)
- Tests maximum DMR ID values (4294967295)
- Tests maximum color code (15)
- Tests 15-character name limit

**Expected Results**:
- All channel numbers should encode/decode correctly
- Frequency boundaries should be respected
- Large channel numbers (>255) should work
- Maximum values shouldn't cause overflow
- Name truncation at 15 characters should work

---

## Validation Checklist

Use this checklist when testing with factory software and radio:

### Factory Software Tests

- [ ] **File Loading**
  - [ ] All 6 files load without errors
  - [ ] No warnings about invalid fields
  - [ ] No corruption messages

- [ ] **Field Display**
  - [ ] Channel numbers display correctly (0, 1, 2, ...)
  - [ ] Channel names are readable (not garbled)
  - [ ] Frequencies display in MHz with correct precision

- [ ] **Analog Channels (01, 02, 04, 05, 06)**
  - [ ] callFormat shows 255 or "Analog"
  - [ ] chType shows 255 or "Analog"
  - [ ] Modes display correctly (USB, LSB, AM, FM, etc.)
  - [ ] CTCSS/DCS tones show correct values

- [ ] **Digital Channels (03, 04, 06)**
  - [ ] callFormat shows 2 or "Digital"
  - [ ] chType shows 1 or "Digital" or "DMR"
  - [ ] DMR ID displays as 3107683
  - [ ] Call ID/Talk Group displays correctly
  - [ ] Slot 1/2 differentiated

### Radio Hardware Tests

- [ ] **Programming**
  - [ ] Files program to radio without errors
  - [ ] No "Format Error" or "Invalid Data" messages
  - [ ] Radio accepts all channel types

- [ ] **Channel Display**
  - [ ] Channel names display correctly on radio screen
  - [ ] Frequencies match what was programmed
  - [ ] Mode indicators show correctly

- [ ] **Analog Operation**
  - [ ] FM channels transmit and receive
  - [ ] CTCSS tones work (squelch opens with correct tone)
  - [ ] Repeater offsets work correctly
  - [ ] SSB/AM/WFM modes function (if supported)

- [ ] **Digital Operation** (if radio supports DMR)
  - [ ] DMR channels transmit and receive
  - [ ] Timeslot selection works
  - [ ] DMR ID is transmitted correctly
  - [ ] Talk group functions properly
  - [ ] Color code selection works

---

## Format Updates (January 17, 2026)

Based on analysis of real PMR-171 radio dump (`test_read_from_radio_20260117.json`), the following format corrections were made:

### Critical Changes:
1. **callFormat**: Changed from 0 to **255** for analog channels
2. **chType**: Changed from 0 to **255** for analog channels  
3. **txCc**: Changed from 2 to **1** for all channels
4. **rxCtcss/txCtcss**: Use **255** (not 0) to indicate "no tone"

### Why These Changes Matter:
The factory software and radio firmware expect these exact values. Using the old values (0, 0, 2, 0) may cause:
- Channels to not load properly
- Radio to misinterpret channel type
- Unexpected behavior during operation

---

## Frequency Reference

All test files use valid amateur radio frequencies:

- **146.52 MHz**: VHF 2-meter simplex calling frequency
- **146.94 MHz**: Example VHF repeater output (146.34 MHz input, -600 kHz offset)
- **446.0 MHz**: UHF 70cm band (common for testing)
- **223.5 MHz**: 1.25-meter band
- **3.8 MHz**: 80-meter HF band (LSB voice)
- **14.2 MHz**: 20-meter HF band (USB voice)
- **98.5 MHz**: FM broadcast band (WFM test)
- **118.1 MHz**: Aviation band (AM test)

---

## Expected Test Results Summary

| File | Channels | Critical Tests | Expected Outcome |
|------|----------|----------------|------------------|
| 01_simple_analog.json | 3 | Basic FM, Repeater | ✅ All load and function |
| 02_multi_mode.json | 11 | All modes (0-9) | ✅ All modes recognized |
| 03_digital_dmr.json | 13 | DMR with TGs | ✅ Digital channels work |
| 04_mixed_analog_digital.json | 11 | Mixed types | ✅ No conflicts |
| 05_ctcss_dcs.json | 13 | Tone encoding | ✅ Tones decode correctly |
| 06_edge_cases.json | 10 | Boundaries | ✅ Edge cases handled |

---

## Technical Notes

### Frequency Encoding
Frequencies are stored as big-endian 32-bit integers in Hz:
- 146.52 MHz = 146,520,000 Hz = `[8, 187, 183, 192]`
- 446.0 MHz = 446,000,000 Hz = `[26, 149, 107, 128]`

### DMR ID Encoding
DMR IDs are stored as big-endian 32-bit integers:
- ID 3107683 = 0x002F6743 = `[0, 47, 103, 67]`

### callFormat Values (Updated)
- **255** = Analog channel (from real radio)
- **2** = Digital/DMR channel

### chType Values (Updated)
- **255** = Analog (from real radio)
- **1** = Digital

### txCc Values (Updated)
- Analog channels: **1** (from real radio, not 2!)
- Digital channels: 1-15 (DMR color code)

### CTCSS/DCS Values (Updated)
- **255** = No tone/Off (from real radio, not 0!)
- 0-50 = CTCSS tone codes (indexed)
- 104+ = DCS codes (indexed)

### Mode Values
- 0 = USB, 1 = LSB, 2 = CWR, 3 = CWL
- 4 = AM, 5 = WFM, 6 = NFM
- 7 = DIGI, 8 = PKT, 9 = DMR

---

## Troubleshooting

### Issue: Files won't load
**Possible Causes**:
- JSON syntax error (missing comma, bracket, etc.)
- Incompatible software version
- File encoding issue

**Solutions**:
- Validate JSON syntax with online validator
- Try opening in text editor to check for corruption
- Re-save with UTF-8 encoding

### Issue: Channels load but show errors
**Possible Causes**:
- Invalid frequency range for radio
- Unsupported mode
- Invalid field values (check for old format: callFormat=0, chType=0, txCc=2)

**Solutions**:
- Check frequency is within radio's supported range
- Verify mode values match factory patterns (0-9)
- **Ensure using updated format** (callFormat=255, chType=255, txCc=1)
- Compare with actual radio dump

### Issue: Digital channels fail
**Possible Causes**:
- callFormat not set to 2
- Missing or invalid DMR IDs
- Incorrect chType

**Solutions**:
- Verify callFormat=2 for all digital channels
- Ensure ownId bytes are set correctly
- Confirm chType=1 for digital

### Issue: CTCSS/DCS not working
**Possible Causes**:
- Using 0 instead of 255 for "no tone"
- Incorrect tone index
- Radio doesn't support that tone

**Solutions**:
- **Use 255 for "no tone", not 0**
- Verify tone index matches radio's table
- Try common tones first (CTCSS 0, 10, 17, 23)

---

## Reporting Results

After testing, please document:

1. **Software Version**: Which version of factory software was used
2. **Radio Firmware**: PMR-171 firmware version
3. **Load Success**: Which files loaded successfully
4. **Field Accuracy**: Were frequencies, modes, tones displayed correctly?
5. **Programming Success**: Did files program to radio without errors?
6. **Operation Test**: Do channels transmit/receive as expected?
7. **Issues Found**: Any errors, warnings, or unexpected behavior

This information will help refine the format compatibility and improve the converter.

---

**Last Updated**: January 17, 2026  
**Validation Status**: Updated to match actual radio format  
**Format Version**: PMR-171 JSON v2.0 (Real Radio Compatible)  
**Source**: Based on `D:\Radio\Guohetec\Testing\test_read_from_radio_20260117.json`
