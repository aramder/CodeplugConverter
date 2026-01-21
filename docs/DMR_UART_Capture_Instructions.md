# DMR UART Capture Instructions

## Objective
Capture UART traffic from the factory Guohetec CPS when programming a DMR channel to discover how color codes, timeslots, and DMR IDs are transmitted to the PMR-171 radio.

## What We Need to Discover
1. **Color Code (CC)** - `rxCc` / `txCc` (0-15)
2. **Timeslot** - `slot` (1 or 2)
3. **Talk Group ID** - `callId1-4` (32-bit big-endian)
4. **Own DMR ID** - `ownId1-4` (32-bit big-endian)

## Current Knowledge
- **Known packet structure (26 bytes):**
  ```
  | CH_IDX(2) | MODES(2) | RX_FREQ(4) | TX_FREQ(4) | CTCSS(2) | NAME(12) |
  ```
- **This does NOT include DMR fields!**
- Hypothesis: Either extended packet or separate command for DMR data

---

## Step 1: Install Serial Port Monitor

### Option A: Free Serial Port Monitor (Recommended)
- Download: https://www.eltima.com/products/serial-port-monitor/ (free trial)
- Or use: **Serial Port Monitor by HHD Software** (free)
- Or use: **Portmon** from Sysinternals (free but older)

### Option B: Open Source Alternative  
- **com0com** + **hub4com** for Windows (complex setup)

---

## Step 2: Set Up Capture

1. **Connect the PMR-171 programming cable** to your PC
2. **Note the COM port** (e.g., COM3, COM6)
3. **Open Serial Port Monitor** and start monitoring that COM port
4. Set capture options:
   - Capture: TX (sent to radio) and RX (received from radio)
   - Format: Hex view
   - Save to file option

---

## Step 3: Configure Factory CPS with DMR Test Channel

In Guohetec factory software, create or edit a DMR channel with these SPECIFIC values (easy to spot in hex):

| Field | Value | Hex Pattern to Find |
|-------|-------|---------------------|
| Channel # | 0 | `00 00` |
| Mode | DMR (9) | `09` |
| RX Freq | 446.100000 MHz | `1A 98 EE 60` (446,100,000 Hz) |
| TX Freq | 446.100000 MHz | `1A 98 EE 60` |
| **Color Code** | **7** | Look for `07` |
| **Timeslot** | **2** | Look for `02` |
| **Talk Group ID** | **91** | `00 00 00 5B` |
| **Own DMR ID** | **1234567** | `00 12 D6 87` |
| Name | "DMR TEST" | `44 4D 52 20 54 45 53 54` |

---

## Step 4: Program the Channel

1. **Start the UART capture** in Serial Port Monitor
2. In factory CPS, **write only channel 0** to the radio
3. **Stop the capture** after programming completes
4. **Save the capture** as `.spm` file or export to text/hex

---

## Step 5: Analyze the Capture

Look for packets with header `A5 A5 A5 A5`:

### What We Already Know
```
Command 0x40 = Channel Write (26-byte payload)
Packet: A5 A5 A5 A5 1D 40 [26 bytes data] [CRC]
```

### What to Look For
1. **Extended 0x40 packet** - Length > 0x1D (29), containing DMR fields after name
2. **New command code** - Different command (not 0x40) for DMR settings
3. **Multiple packets** - One for analog fields, another for DMR fields

### Hex Patterns to Search
```
07           - Color Code 7
02           - Timeslot 2
00 00 00 5B  - Talk Group 91 (big-endian)
00 12 D6 87  - DMR ID 1234567 (big-endian)
44 4D 52     - "DMR" in ASCII
```

---

## Step 6: Document Findings

After capture, please share:
1. **Full hex dump** of the write transaction
2. **Packet length** - Is it still 34 bytes (4 header + 1 len + 29 data) or longer?
3. **Any additional packets** after the main channel write
4. **Response from radio** - What does it send back?

---

## Quick Test Protocol

If you don't have Serial Port Monitor, you can try this Python sniffer:

```python
import serial
import time

# Replace with your COM port
PORT = "COM3"

# Open port in raw mode
ser = serial.Serial(PORT, 115200, timeout=1)
print(f"Listening on {PORT}...")

try:
    while True:
        if ser.in_waiting:
            data = ser.read(ser.in_waiting)
            hex_str = data.hex(' ')
            print(f"[{time.strftime('%H:%M:%S')}] {hex_str}")
except KeyboardInterrupt:
    print("\nStopped")
finally:
    ser.close()
```

**Note:** This won't work if factory CPS has the port open. Use a proper serial port monitor that can intercept traffic.

---

## Expected Outcome

After capture, we should know:
- [ ] Exact byte position of color codes in packet
- [ ] Exact byte position of timeslot in packet
- [ ] Exact byte position of DMR IDs in packet
- [ ] Whether extended packet or separate command is used
- [ ] Full packet structure for DMR channels

This information will allow us to implement proper DMR field transmission in our CPS.
