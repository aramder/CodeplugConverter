#!/usr/bin/env python3
"""
UART Capture Analysis Script for PMR-171 Programming Protocol

This script parses Eltima Serial Monitor .spm files to extract and analyze
the UART transactions for programming the PMR-171 radio.

Protocol Reference: See docs/PMR171_PROTOCOL.md

Packet Format:
  | 0xA5 | 0xA5 | 0xA5 | 0xA5 | Length | Command | DATA... | CRC_H | CRC_L |

Phase 1: Extract and understand the .spm file format
Phase 2: Identify packet structure and patterns  
Phase 3: Correlate with known channel data (CTCSS tones, frequencies)
Phase 4: Reverse engineer checksums
Phase 5: Document the protocol
"""

import struct
import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import re


# PMR-171 Protocol Constants
PACKET_HEADER = bytes([0xA5, 0xA5, 0xA5, 0xA5])
SPECTRUM_HEADER = bytes([0x7E, 0x7E, 0x7E, 0x7E])

# CTCSS Tone mapping (index -> frequency Hz)
CTCSS_TONES = {
    0: None, 1: 67.0, 2: 69.3, 3: 71.9, 4: 74.4, 5: 77.0, 6: 79.7,
    7: 82.5, 8: 85.4, 9: 88.5, 10: 91.5, 11: 94.8, 12: 97.4, 13: 100.0,
    14: 103.5, 15: 107.2, 16: 110.9, 17: 114.8, 18: 118.8, 19: 123.0,
    20: 127.3, 21: 131.8, 22: 136.5, 23: 141.3, 24: 146.2, 25: 150.0,
    26: 151.4, 27: 156.7, 28: 159.8, 29: 162.2, 30: 165.5, 31: 167.9,
    32: 171.3, 33: 173.8, 34: 177.3, 35: 179.9, 36: 183.5, 37: 186.2,
    38: 189.9, 39: 192.8, 40: 196.6, 41: 199.5, 42: 203.5, 43: 206.5,
    44: 210.7, 45: 213.8, 46: 218.1, 47: 221.3, 48: 225.7, 49: 229.1,
    50: 233.6, 51: 237.1, 52: 241.8, 53: 245.5, 54: 250.3, 55: 254.1
}

# Known command codes from manual
COMMANDS = {
    0x07: "PTT Control",
    0x0A: "Mode Setting",
    0x0B: "Status Synchronization",
    0x27: "Equipment Type Recognition",
    0x28: "Power Class",
    0x29: "RIT Setting",
    0x39: "Spectrum Data Request",
    # Discovered from UART captures:
    0x40: "Channel Write",
    0x43: "Channel Read",
}

# Mode values (from manual)
MODES = {
    0: "USB", 1: "LSB", 2: "CWR", 3: "CWL",
    4: "AM", 5: "WFM", 6: "NFM", 7: "DIGI", 8: "PKT"
}


def crc16_ccitt(data: bytes) -> int:
    """
    Calculate CRC-16-CCITT for PMR-171 protocol.
    
    From manual (Sheet 39):
    - Polynomial: 0x1021
    - Initial value: 0xFFFF
    - Input: bytes from Length field through last DATA byte (before CRC)
    """
    crc = 0xFFFF
    for byte in data:
        cur = byte << 8
        for _ in range(8):
            if (crc ^ cur) & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
            cur = (cur << 1) & 0xFFFF
    return crc


def verify_packet_crc(packet_data: bytes) -> Tuple[bool, int, int]:
    """
    Verify CRC of a packet.
    
    Args:
        packet_data: Full packet including header
        
    Returns:
        (is_valid, calculated_crc, packet_crc)
    """
    if len(packet_data) < 8:
        return False, 0, 0
    
    # CRC is calculated over Length byte through last data byte
    # i.e., bytes[4] through bytes[-3] (excluding last 2 CRC bytes)
    crc_data = packet_data[4:-2]
    calculated = crc16_ccitt(crc_data)
    
    # Packet CRC is big-endian
    packet_crc = (packet_data[-2] << 8) | packet_data[-1]
    
    return calculated == packet_crc, calculated, packet_crc


class ChannelData:
    """Decoded channel data from a Channel Write/Read packet"""
    def __init__(self, data: bytes):
        """
        Parse channel data from packet payload.
        
        Observed structure (29 byte packet, 26 byte payload after header+length):
        Offset 0-1: Channel index (big-endian)
        Offset 2: RX Mode
        Offset 3: TX Mode  
        Offset 4-7: RX Frequency (big-endian Hz)
        Offset 8-11: TX Frequency (big-endian Hz)
        Offset 12: RX CTCSS index
        Offset 13: TX CTCSS index
        ... more fields ...
        Last 2 bytes: CRC
        """
        self.raw = data
        
        if len(data) >= 14:
            # Channel index
            self.channel_index = struct.unpack('>H', data[0:2])[0]
            
            # Modes
            self.rx_mode = data[2]
            self.tx_mode = data[3]
            
            # Frequencies (big-endian 4 bytes)
            self.rx_freq = struct.unpack('>I', data[4:8])[0]
            self.tx_freq = struct.unpack('>I', data[8:12])[0]
            
            # CTCSS tones
            self.rx_ctcss_index = data[12]
            self.tx_ctcss_index = data[13]
        else:
            self.channel_index = 0
            self.rx_mode = 0
            self.tx_mode = 0
            self.rx_freq = 0
            self.tx_freq = 0
            self.rx_ctcss_index = 0
            self.tx_ctcss_index = 0
    
    @property
    def rx_freq_mhz(self):
        return self.rx_freq / 1_000_000
    
    @property  
    def tx_freq_mhz(self):
        return self.tx_freq / 1_000_000
    
    @property
    def rx_ctcss_hz(self):
        return CTCSS_TONES.get(self.rx_ctcss_index, None)
    
    @property
    def tx_ctcss_hz(self):
        return CTCSS_TONES.get(self.tx_ctcss_index, None)
    
    @property
    def rx_mode_name(self):
        return MODES.get(self.rx_mode, f"Unknown({self.rx_mode})")
    
    @property
    def tx_mode_name(self):
        return MODES.get(self.tx_mode, f"Unknown({self.tx_mode})")
    
    def __repr__(self):
        rx_tone = f"{self.rx_ctcss_hz} Hz" if self.rx_ctcss_hz else "None"
        tx_tone = f"{self.tx_ctcss_hz} Hz" if self.tx_ctcss_hz else "None"
        return (f"Ch{self.channel_index}: {self.rx_freq_mhz:.4f} MHz ({self.rx_mode_name}) "
                f"RX_Tone={rx_tone}, TX_Tone={tx_tone}")


class PMR171Packet:
    """Represents a decoded PMR-171 protocol packet"""
    def __init__(self, raw_data: bytes, position: int):
        self.raw_data = raw_data
        self.position = position  # Position in file where packet was found
        self.length = raw_data[4] if len(raw_data) > 4 else 0
        self.command = raw_data[5] if len(raw_data) > 5 else 0
        self.data = raw_data[6:-2] if len(raw_data) > 8 else b''
        self.crc = raw_data[-2:] if len(raw_data) >= 2 else b''
        
        # Verify CRC
        self.crc_valid, self.calculated_crc, self.packet_crc = verify_packet_crc(raw_data)
        
        # Parse channel data if this is a channel command
        self.channel_data = None
        if self.command in (0x40, 0x43) and len(self.data) >= 14:
            self.channel_data = ChannelData(self.data)
        
    @property
    def command_name(self):
        return COMMANDS.get(self.command, f"Unknown (0x{self.command:02X})")
    
    def __repr__(self):
        if self.channel_data:
            return f"Packet @{self.position}: {self.command_name} - {self.channel_data}"
        hex_str = ' '.join(f'{b:02X}' for b in self.raw_data[:20])
        if len(self.raw_data) > 20:
            hex_str += f"... ({len(self.raw_data)} bytes total)"
        return f"Packet @{self.position}: Cmd={self.command_name}, Len={self.length}, Data={hex_str}"


def extract_raw_bytes_from_spm(filepath: Path) -> bytes:
    """
    Extract raw serial bytes from Eltima Serial Monitor .spm file.
    
    The .spm format contains metadata in UTF-16LE encoding mixed with
    actual serial data bytes.
    """
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # The .spm file has a complex structure with UTF-16LE strings
    # We need to find the actual data bytes
    
    # Strategy: Search for our known packet header pattern
    raw_bytes = bytearray()
    
    # Method 1: Look for 0xA5 sequences that form valid packets
    # First, let's extract all bytes that could be serial data
    # (bytes between the metadata markers)
    
    return bytes(content)


def find_packet_headers(data: bytes) -> List[int]:
    """Find all occurrences of the 0xA5 0xA5 0xA5 0xA5 packet header"""
    positions = []
    pos = 0
    while True:
        pos = data.find(PACKET_HEADER, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1  # Allow overlapping searches in case of corruption
    return positions


def find_spectrum_headers(data: bytes) -> List[int]:
    """Find all occurrences of the 0x7E 0x7E 0x7E 0x7E spectrum header"""
    positions = []
    pos = 0
    while True:
        pos = data.find(SPECTRUM_HEADER, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    return positions


def extract_packets(data: bytes, header_positions: List[int]) -> List[PMR171Packet]:
    """Extract and decode packets starting at the given header positions"""
    packets = []
    
    for i, pos in enumerate(header_positions):
        # Check if we have enough bytes for a minimal packet (header + length + cmd + crc)
        if pos + 8 > len(data):
            continue
            
        length_byte = data[pos + 4]
        
        # Sanity check: length should be reasonable (not corrupted)
        # Minimum: 1 (command) + 2 (CRC) = 3
        # Maximum: probably around 256 for most commands
        if length_byte < 3 or length_byte > 250:
            continue
            
        # Total packet size = 4 (header) + 1 (length) + length_byte
        packet_size = 4 + 1 + length_byte
        
        if pos + packet_size > len(data):
            continue
            
        raw_packet = data[pos:pos + packet_size]
        packet = PMR171Packet(raw_packet, pos)
        packets.append(packet)
    
    return packets


def analyze_spm_file(filepath: Path) -> Dict:
    """
    Comprehensive analysis of an Eltima Serial Monitor .spm file.
    """
    print(f"\n{'='*70}")
    print(f"Analyzing: {filepath.name}")
    print(f"{'='*70}\n")
    
    with open(filepath, 'rb') as f:
        content = f.read()
    
    print(f"File size: {len(content)} bytes")
    
    # Check file header
    header_text = content[:50]
    print(f"File header (raw): {header_text}")
    
    # Find packet headers
    packet_positions = find_packet_headers(content)
    spectrum_positions = find_spectrum_headers(content)
    
    print(f"\nFound {len(packet_positions)} potential packet headers (0xA5 0xA5 0xA5 0xA5)")
    print(f"Found {len(spectrum_positions)} potential spectrum headers (0x7E 0x7E 0x7E 0x7E)")
    
    # Show first few packet header positions
    if packet_positions:
        print(f"\nFirst 10 packet header positions: {packet_positions[:10]}")
        print(f"Last 10 packet header positions: {packet_positions[-10:] if len(packet_positions) >= 10 else packet_positions}")
    
    # Extract and analyze packets
    packets = extract_packets(content, packet_positions)
    print(f"\nSuccessfully parsed {len(packets)} valid packets")
    
    # Analyze command distribution
    cmd_counts = {}
    for pkt in packets:
        cmd_counts[pkt.command] = cmd_counts.get(pkt.command, 0) + 1
    
    print("\n=== Command Distribution ===")
    for cmd, count in sorted(cmd_counts.items()):
        name = COMMANDS.get(cmd, "Unknown")
        print(f"  0x{cmd:02X} ({name}): {count} packets")
    
    # CRC Verification
    valid_crc = sum(1 for p in packets if p.crc_valid)
    invalid_crc = len(packets) - valid_crc
    print(f"\n=== CRC Verification ===")
    print(f"  Valid CRC: {valid_crc} packets")
    print(f"  Invalid CRC: {invalid_crc} packets")
    
    if invalid_crc > 0:
        print(f"\n  First few invalid CRC packets:")
        for pkt in [p for p in packets if not p.crc_valid][:5]:
            print(f"    @{pkt.position}: Calc=0x{pkt.calculated_crc:04X}, Pkt=0x{pkt.packet_crc:04X}")
    
    # Show sample packets
    if packets:
        print("\n=== Sample Packets (First 10) ===")
        for pkt in packets[:10]:
            print(f"  {pkt}")
    
    # Analyze channel data if present
    channel_packets = [p for p in packets if p.channel_data]
    if channel_packets:
        print(f"\n=== Channel Data Analysis ({len(channel_packets)} channel packets) ===")
        
        # Group by channel index
        channels = {}
        for pkt in channel_packets:
            ch_idx = pkt.channel_data.channel_index
            if ch_idx not in channels:
                channels[ch_idx] = []
            channels[ch_idx].append(pkt)
        
        print(f"\nFound {len(channels)} unique channels:")
        for ch_idx in sorted(channels.keys())[:30]:
            # Show first packet for each channel
            pkt = channels[ch_idx][0]
            ch = pkt.channel_data
            rx_tone = f"{ch.rx_ctcss_hz} Hz (idx={ch.rx_ctcss_index})" if ch.rx_ctcss_hz else f"None (idx={ch.rx_ctcss_index})"
            tx_tone = f"{ch.tx_ctcss_hz} Hz (idx={ch.tx_ctcss_index})" if ch.tx_ctcss_hz else f"None (idx={ch.tx_ctcss_index})"
            print(f"  Ch {ch_idx:3d}: {ch.rx_freq_mhz:10.4f} MHz {ch.rx_mode_name:4s} "
                  f"RX={rx_tone:20s} TX={tx_tone:20s}")
        
        # Analyze CTCSS distribution
        print("\n=== CTCSS Tone Distribution ===")
        rx_tones = {}
        tx_tones = {}
        for pkt in channel_packets:
            ch = pkt.channel_data
            rx_tones[ch.rx_ctcss_index] = rx_tones.get(ch.rx_ctcss_index, 0) + 1
            tx_tones[ch.tx_ctcss_index] = tx_tones.get(ch.tx_ctcss_index, 0) + 1
        
        print("\nRX CTCSS tones found:")
        for idx, count in sorted(rx_tones.items()):
            hz = CTCSS_TONES.get(idx, "Unknown")
            print(f"  Index {idx:2d} ({hz} Hz): {count} occurrences")
        
        print("\nTX CTCSS tones found:")
        for idx, count in sorted(tx_tones.items()):
            hz = CTCSS_TONES.get(idx, "Unknown")
            print(f"  Index {idx:2d} ({hz} Hz): {count} occurrences")
    
    # Look for patterns in packet data
    print("\n=== Packet Length Distribution ===")
    len_counts = {}
    for pkt in packets:
        len_counts[pkt.length] = len_counts.get(pkt.length, 0) + 1
    
    for length, count in sorted(len_counts.items())[:20]:
        print(f"  Length {length}: {count} packets")
    
    return {
        'filepath': str(filepath),
        'file_size': len(content),
        'packet_count': len(packets),
        'spectrum_header_count': len(spectrum_positions),
        'command_distribution': cmd_counts,
        'length_distribution': len_counts,
        'packets': packets
    }


def parse_spm_file(filepath: Path) -> List:
    """Legacy function - calls new analyze_spm_file"""
    result = analyze_spm_file(filepath)
    return result.get('packets', [])


def analyze_remaining_fields(packets: List[PMR171Packet]):
    """
    Analyze the remaining bytes in channel packets to identify field meanings.
    
    Known structure (26 data bytes after command):
    0-1:   Channel Index (big-endian)
    2:     RX Mode
    3:     TX Mode  
    4-7:   RX Frequency (big-endian Hz)
    8-11:  TX Frequency (big-endian Hz)
    12:    RX CTCSS index
    13:    TX CTCSS index
    14-25: UNKNOWN (12 bytes) - This is what we're analyzing
    """
    print("\n" + "="*70)
    print("ANALYZING REMAINING 12 BYTES IN CHANNEL DATA")
    print("="*70)
    
    channel_pkts = [p for p in packets if p.channel_data and p.command == 0x40]
    
    if not channel_pkts:
        print("No channel write packets found")
        return
    
    # Group packets by channel for comparison
    by_channel = {}
    for pkt in channel_pkts:
        ch = pkt.channel_data.channel_index
        if ch not in by_channel:
            by_channel[ch] = pkt
    
    # Print raw bytes for first 30 channels
    print("\n=== Raw Packet Data (Bytes 14-25 after command) ===")
    print("Ch#  | Freq MHz    | Mode | RX_T TX_T | Bytes 14-25 (hex)")
    print("-"*80)
    
    for ch_idx in sorted(by_channel.keys())[:35]:
        pkt = by_channel[ch_idx]
        ch = pkt.channel_data
        data = pkt.data  # Data after command byte (26 bytes)
        
        if len(data) >= 26:
            remaining = data[14:26]  # Bytes 14-25 (indices after command)
            hex_str = ' '.join(f'{b:02X}' for b in remaining)
            rx_t = ch.rx_ctcss_index
            tx_t = ch.tx_ctcss_index
            print(f"{ch_idx:3d}  | {ch.rx_freq_mhz:10.4f} | {ch.rx_mode:3d}  | {rx_t:3d}  {tx_t:3d} | {hex_str}")
    
    # Analyze byte patterns across all channels
    print("\n=== Byte-by-Byte Analysis (Bytes 14-25) ===")
    
    byte_values = {i: {} for i in range(12)}  # Track unique values for each byte position
    
    for pkt in channel_pkts:
        data = pkt.data
        if len(data) >= 26:
            for i, b in enumerate(data[14:26]):
                byte_values[i][b] = byte_values[i].get(b, 0) + 1
    
    for pos in range(12):
        values = byte_values[pos]
        unique = len(values)
        most_common = sorted(values.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print(f"\nByte {pos+14} (offset in data): {unique} unique values")
        for val, count in most_common:
            print(f"  0x{val:02X} ({val:3d}): {count} occurrences")
    
    # Look for patterns that might indicate specific fields
    print("\n=== Field Hypothesis ===")
    
    # Byte 14-15: Could be DCS codes or another tone type
    # Byte 16-17: Could be TX power or squelch level
    # Byte 18-19: Could be bandwidth or step
    # Byte 20-25: Could be name (6 chars) or other settings
    
    # Check if bytes 20-25 look like ASCII characters
    print("\n=== Checking if Bytes 20-25 are ASCII (Name field?) ===")
    for ch_idx in sorted(by_channel.keys())[:15]:
        pkt = by_channel[ch_idx]
        data = pkt.data
        if len(data) >= 26:
            name_bytes = data[20:26]
            # Try to decode as ASCII
            try:
                name = ''.join(chr(b) if 32 <= b < 127 else '.' for b in name_bytes)
                hex_str = ' '.join(f'{b:02X}' for b in name_bytes)
                print(f"  Ch {ch_idx:3d}: [{hex_str}] = '{name}'")
            except:
                pass


def analyze_test11_upload(filepath: Path):
    """
    Analyze the Test 11 upload capture - the largest and most complete capture.
    This contains the full programming sequence.
    """
    print(f"\n{'='*70}")
    print(f"Analyzing: {filepath.name}")
    print(f"{'='*70}\n")
    
    packets = parse_spm_file(filepath)
    
    # Analyze remaining fields
    analyze_remaining_fields(packets)
    
    # Try to correlate with known data
    # Test 11 has 25 test channels with known CTCSS tones
    known_tones = {
        67.0: 0x01,   # emitYayin/receiveYayin value
        100.0: 0x02,
        107.2: 0x03,
        123.0: 0x04,
        131.8: 0x05,
        156.7: 0x06,
    }
    
    print("\n=== Known CTCSS Tones to Look For ===")
    for freq, yayin in known_tones.items():
        print(f"  {freq} Hz -> yayin value 0x{yayin:02X}")


def main():
    results_dir = Path(__file__).parent
    
    # Start with the largest, most complete capture
    test11_upload = results_dir / "11_complete_ctcss_validation_readback_uploade.spm"
    
    if test11_upload.exists():
        analyze_test11_upload(test11_upload)
    else:
        print(f"Error: Could not find {test11_upload}")
        return 1
    
    print("\n" + "="*70)
    print("Phase 1 Complete: Initial .spm format exploration")
    print("="*70)
    print("\nNext steps:")
    print("1. Identify packet boundaries and structure")
    print("2. Extract actual data bytes vs. metadata")
    print("3. Look for correlations with CTCSS tone values")
    print("4. Identify command sequences")
    print("5. Reverse engineer checksums")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
