#!/usr/bin/env python3
"""
Generate protocol sequence diagrams for PMR-171 UART documentation.

Creates visual diagrams showing the communication flow between
the computer and radio during read/write operations.

Requires: matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os


def draw_message_arrow(ax, from_x, to_x, y, label, hex_data, is_request=True, show_box=True):
    """
    Draw a message arrow with consistent styling.
    
    Args:
        ax: matplotlib axis
        from_x: starting x position
        to_x: ending x position
        y: y position of arrow
        label: text label for the message
        hex_data: hex packet example (or None)
        is_request: True for computer->radio (blue), False for radio->computer (green)
        show_box: whether to draw a box around the label
    
    Returns:
        new y position after drawing
    """
    # Colors
    if is_request:
        arrow_color = '#1976D2'
        box_color = '#E3F2FD'
        edge_color = '#1976D2'
    else:
        arrow_color = '#388E3C'
        box_color = '#E8F5E9'
        edge_color = '#388E3C'
    
    # Draw arrow
    ax.annotate('', xy=(to_x, y), xytext=(from_x, y),
                arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))
    
    if show_box:
        # Draw label box - consistent width (4.4 units centered at 5.0)
        box_width = 4.4
        box_x = 5.0 - box_width / 2
        ax.add_patch(FancyBboxPatch((box_x, y - 0.35), box_width, 0.38, 
                                    boxstyle="round,pad=0.02", 
                                    facecolor=box_color, edgecolor=edge_color, linewidth=1.5))
        ax.text(5, y - 0.17, label, ha='center', fontsize=10)
        y -= 0.45
    else:
        # Just text, no box
        ax.text(5, y + 0.15, label, ha='center', fontsize=10, style='italic')
        y -= 0.35
    
    # Draw hex data if provided
    if hex_data:
        ax.text(5, y, hex_data, ha='center', fontsize=9, family='monospace', color='#555')
        y -= 0.35
    
    return y


def create_sequence_diagram():
    """Create a sequence diagram showing read/write protocol flow."""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 13))
    ax.set_xlim(0, 10)
    ax.set_ylim(0.5, 13.5)
    ax.axis('off')
    
    # Title
    ax.text(5, 13.2, 'PMR-171 UART Protocol Sequence', 
            ha='center', va='center', fontsize=20, fontweight='bold')
    ax.text(5, 12.8, '(Analog Channels - DMR channels use slightly different payload structure)', 
            ha='center', va='center', fontsize=10, style='italic', color='#666')
    
    # Lifelines
    computer_x = 2.5
    radio_x = 7.5
    
    # Actor boxes - positioned below subtitle with more space
    ax.add_patch(FancyBboxPatch((computer_x - 1.0, 11.7), 2.0, 0.7, 
                                boxstyle="round,pad=0.05", 
                                facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2))
    ax.text(computer_x, 12.05, 'Computer', ha='center', va='center', fontsize=14, fontweight='bold')
    
    ax.add_patch(FancyBboxPatch((radio_x - 1.0, 11.7), 2.0, 0.7, 
                                boxstyle="round,pad=0.05", 
                                facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=2))
    ax.text(radio_x, 12.05, 'PMR-171', ha='center', va='center', fontsize=14, fontweight='bold')
    
    # Lifelines (dashed vertical lines) - start below actor boxes, end below content
    ax.plot([computer_x, computer_x], [11.65, 0.8], 'k--', linewidth=1, alpha=0.5)
    ax.plot([radio_x, radio_x], [11.65, 0.8], 'k--', linewidth=1, alpha=0.5)
    
    y = 11.3
    
    # === INITIALIZATION PHASE ===
    y -= 0.3
    ax.text(0.3, y, 'INITIALIZATION', fontsize=13, fontweight='bold', color='#1565C0')
    
    y -= 0.6
    # DTR/RTS Setup (no box, just text above arrow)
    ax.annotate('', xy=(radio_x - 0.1, y), xytext=(computer_x + 0.1, y),
                arrowprops=dict(arrowstyle='->', color='#1976D2', lw=2))
    ax.text(5, y + 0.18, 'Set DTR=HIGH, RTS=HIGH', ha='center', fontsize=11, style='italic')
    
    y -= 0.5
    ax.text(5, y, '(Radio enters programming mode)', ha='center', fontsize=10, color='gray')
    
    y -= 0.5
    # Equipment Type Query - no box for initialization commands
    y = draw_message_arrow(ax, computer_x + 0.1, radio_x - 0.1, y, 
                           'CMD 0x27: Equipment Type', None, is_request=True, show_box=False)
    
    # Equipment Type Response - no box for initialization commands
    y = draw_message_arrow(ax, radio_x - 0.1, computer_x + 0.1, y, 
                           'Response: Model/FW', None, is_request=False, show_box=False)
    
    y -= 0.4
    
    # === READ OPERATION ===
    read_box_top = y
    ax.text(0.5, y - 0.1, 'READ CHANNEL LOOP (repeat for each channel)', fontsize=12, fontweight='bold', color='#E65100')
    
    y -= 0.7
    # Read Request
    y = draw_message_arrow(ax, computer_x + 0.1, radio_x - 0.1, y, 
                           'CMD 0x41: Read Channel N', 
                           '[A5 A5 A5 A5] [05] [41] [00 0N] [CRC]', is_request=True)
    
    y -= 0.1
    # Read Response
    y = draw_message_arrow(ax, radio_x - 0.1, computer_x + 0.1, y, 
                           'Response: 26-byte Channel Data', 
                           '[A5 A5 A5 A5] [1D] [41] [26 bytes] [CRC]', is_request=False)
    
    y -= 0.25
    ax.text(5, y, '↺ repeat', ha='center', fontsize=11, style='italic', color='#E65100')
    
    read_box_bottom = y - 0.3
    # Draw read loop box
    ax.add_patch(FancyBboxPatch((0.2, read_box_bottom), 9.6, read_box_top - read_box_bottom, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#FFF8E1', edgecolor='#FFA000', linewidth=2, linestyle='--'))
    
    y -= 0.7
    
    # === WRITE OPERATION ===
    write_box_top = y
    ax.text(0.5, y - 0.1, 'WRITE CHANNEL LOOP (repeat for each channel)', fontsize=12, fontweight='bold', color='#283593')
    
    y -= 0.7
    # Write Request
    y = draw_message_arrow(ax, computer_x + 0.1, radio_x - 0.1, y, 
                           'CMD 0x40: Write Channel N (26 bytes)', 
                           '[A5 A5 A5 A5] [1D] [40] [26 bytes] [CRC]', is_request=True)
    
    y -= 0.1
    # Write Response
    y = draw_message_arrow(ax, radio_x - 0.1, computer_x + 0.1, y, 
                           'ACK: Echo of written data', 
                           '[A5 A5 A5 A5] [1D] [40] [26 bytes] [CRC]', is_request=False)
    
    y -= 0.25
    ax.text(5, y, '↺ repeat', ha='center', fontsize=11, style='italic', color='#283593')
    
    write_box_bottom = y - 0.3
    # Draw write loop box
    ax.add_patch(FancyBboxPatch((0.2, write_box_bottom), 9.6, write_box_top - write_box_bottom, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#E8EAF6', edgecolor='#3F51B5', linewidth=2, linestyle='--'))
    
    y -= 0.7
    
    # === CLOSE ===
    ax.text(0.3, y, 'DISCONNECT', fontsize=13, fontweight='bold', color='#1565C0')
    
    y -= 0.6
    ax.annotate('', xy=(radio_x - 0.1, y), xytext=(computer_x + 0.1, y),
                arrowprops=dict(arrowstyle='->', color='#1976D2', lw=2))
    ax.text(5, y + 0.18, 'Set DTR=LOW, RTS=LOW, Close Port', ha='center', fontsize=11, style='italic')
    
    y -= 0.4
    ax.text(5, y, '(Radio exits programming mode)', ha='center', fontsize=10, color='gray')
    
    plt.tight_layout()
    return fig


def create_packet_structure_diagram():
    """Create a diagram showing packet structure in detail."""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'PMR-171 Packet Structure', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # === Generic Packet Format ===
    y = 8.5
    ax.text(0.5, y, 'Generic Packet Format:', fontsize=12, fontweight='bold')
    
    y -= 0.8
    # Draw packet boxes
    fields = [
        ('Header\n4 bytes', 2.0, '#BBDEFB', '0xA5 A5 A5 A5'),
        ('Length\n1 byte', 1.0, '#C8E6C9', 'N'),
        ('Command\n1 byte', 1.0, '#FFF9C4', '0x__'),
        ('Payload\nVariable', 2.5, '#FFCCBC', 'Data...'),
        ('CRC-16\n2 bytes', 1.2, '#E1BEE7', 'BE'),
    ]
    
    x = 0.5
    for label, width, color, sublabel in fields:
        ax.add_patch(FancyBboxPatch((x, y - 0.8), width, 1.0, 
                                    boxstyle="round,pad=0.02", 
                                    facecolor=color, edgecolor='black', linewidth=1.5))
        ax.text(x + width/2, y - 0.2, label, ha='center', va='center', fontsize=9, fontweight='bold')
        ax.text(x + width/2, y - 0.65, sublabel, ha='center', va='center', fontsize=8, color='#666')
        x += width + 0.1
    
    # Length calculation note
    y -= 1.4
    ax.text(0.5, y, 'Length = Command (1) + Payload (N) + CRC (2)', fontsize=9, style='italic', color='#666')
    
    y -= 0.8
    
    # === Channel Read Request ===
    ax.text(0.5, y, 'Channel Read Request (CMD 0x41):', fontsize=12, fontweight='bold')
    
    y -= 0.8
    fields = [
        ('A5 A5\nA5 A5', 1.5, '#BBDEFB'),
        ('05', 0.6, '#C8E6C9'),
        ('41', 0.6, '#FFF9C4'),
        ('Ch Hi', 0.7, '#FFCCBC'),
        ('Ch Lo', 0.7, '#FFCCBC'),
        ('CRC\nHi Lo', 1.0, '#E1BEE7'),
    ]
    
    x = 0.5
    for label, width, color in fields:
        ax.add_patch(FancyBboxPatch((x, y - 0.7), width, 0.9, 
                                    boxstyle="round,pad=0.02", 
                                    facecolor=color, edgecolor='black', linewidth=1.5))
        ax.text(x + width/2, y - 0.25, label, ha='center', va='center', fontsize=8, fontweight='bold')
        x += width + 0.05
    
    ax.text(x + 0.3, y - 0.25, '← 9 bytes total', fontsize=9, color='#666')
    
    y -= 1.3
    
    # === Channel Read Response / Write Request ===
    ax.text(0.5, y, 'Channel Data Packet (Response or Write):', fontsize=12, fontweight='bold')
    
    y -= 0.8
    fields = [
        ('A5 A5\nA5 A5', 1.2, '#BBDEFB'),
        ('1D', 0.5, '#C8E6C9'),
        ('40/41', 0.6, '#FFF9C4'),
        ('Ch\nIdx', 0.6, '#FFCCBC'),
        ('RX\nMode', 0.5, '#FFCCBC'),
        ('TX\nMode', 0.5, '#FFCCBC'),
        ('RX Freq\n4 bytes', 1.0, '#FFE0B2'),
        ('TX Freq\n4 bytes', 1.0, '#FFE0B2'),
        ('RX\nTone', 0.5, '#B2DFDB'),
        ('TX\nTone', 0.5, '#B2DFDB'),
        ('Name\n12 bytes', 1.5, '#F8BBD9'),
        ('CRC', 0.7, '#E1BEE7'),
    ]
    
    x = 0.3
    for label, width, color in fields:
        ax.add_patch(FancyBboxPatch((x, y - 0.7), width, 0.9, 
                                    boxstyle="round,pad=0.02", 
                                    facecolor=color, edgecolor='black', linewidth=1.5))
        ax.text(x + width/2, y - 0.25, label, ha='center', va='center', fontsize=7, fontweight='bold')
        x += width + 0.03
    
    ax.text(x + 0.2, y - 0.25, '← 33 bytes total\n   (26 byte payload)', fontsize=9, color='#666')
    
    y -= 1.5
    
    # === Byte offset table ===
    ax.text(0.5, y, 'Channel Payload Structure (26 bytes):', fontsize=12, fontweight='bold')
    
    y -= 0.5
    offsets = [
        ('0x00-01', 'Channel Index', 'Big-endian uint16'),
        ('0x02', 'RX Mode', 'Mode enum (0-9, 255)'),
        ('0x03', 'TX Mode', 'Mode enum (0-9, 255)'),
        ('0x04-07', 'RX Frequency', 'Big-endian uint32 (Hz)'),
        ('0x08-0B', 'TX Frequency', 'Big-endian uint32 (Hz)'),
        ('0x0C', 'RX CTCSS Index', 'Tone index (0-55)'),
        ('0x0D', 'TX CTCSS Index', 'Tone index (0-55)'),
        ('0x0E-19', 'Channel Name', '12 bytes ASCII, null-term'),
    ]
    
    # Table header
    ax.text(1.0, y, 'Offset', fontsize=9, fontweight='bold')
    ax.text(3.0, y, 'Field', fontsize=9, fontweight='bold')
    ax.text(6.5, y, 'Format', fontsize=9, fontweight='bold')
    ax.plot([0.5, 10], [y - 0.15, y - 0.15], 'k-', linewidth=0.5)
    
    y -= 0.35
    for offset, field, fmt in offsets:
        ax.text(1.0, y, offset, fontsize=8, family='monospace')
        ax.text(3.0, y, field, fontsize=8)
        ax.text(6.5, y, fmt, fontsize=8, color='#666')
        y -= 0.3
    
    plt.tight_layout()
    return fig


def main():
    """Generate all diagrams and save to docs folder."""
    
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'docs', 'images')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate sequence diagram
    print("Generating protocol sequence diagram...")
    fig1 = create_sequence_diagram()
    seq_path = os.path.join(output_dir, 'protocol_sequence.png')
    fig1.savefig(seq_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  Saved: {seq_path}")
    plt.close(fig1)
    
    # Generate packet structure diagram
    print("Generating packet structure diagram...")
    fig2 = create_packet_structure_diagram()
    pkt_path = os.path.join(output_dir, 'packet_structure.png')
    fig2.savefig(pkt_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  Saved: {pkt_path}")
    plt.close(fig2)
    
    print("\nDone! Images saved to docs/images/")


if __name__ == '__main__':
    main()
