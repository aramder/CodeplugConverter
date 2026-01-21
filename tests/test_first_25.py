#!/usr/bin/env python3
"""Test write/verify/restore on first 25 channels"""
import sys
sys.path.insert(0, '.')

from pmr_171_cps.radio.pmr171_uart import PMR171Radio, ChannelData, Mode

def main():
    radio = PMR171Radio('COM3')
    radio.connect()
    print('Connected to radio on COM3')
    print('='*50)

    passed = 0
    failed = 0
    
    for ch_num in range(25):
        print(f'Channel {ch_num:2d}: ', end='', flush=True)
        
        try:
            # Read original
            original = radio.read_channel(ch_num)
            
            # Create test data - unique freq/name per channel
            test = ChannelData(
                index=ch_num,
                rx_mode=Mode.NFM,
                tx_mode=Mode.NFM,
                rx_freq_hz=446_000_000 + (ch_num * 1000),
                tx_freq_hz=446_000_000 + (ch_num * 1000),
                rx_ctcss_index=0,
                tx_ctcss_index=0,
                name=f'TEST_{ch_num:02d}'
            )
            
            # Write test data
            radio.write_channel(test)
            
            # Read back and verify
            readback = radio.read_channel(ch_num)
            
            if readback.rx_freq_hz == test.rx_freq_hz and readback.name.strip() == test.name:
                print('WRITE:OK ', end='', flush=True)
            else:
                print(f'WRITE:FAIL (got {readback.rx_freq_hz/1e6:.6f}MHz, "{readback.name}")')
                failed += 1
                radio.write_channel(original)  # Try to restore anyway
                continue
            
            # Restore original
            radio.write_channel(original)
            
            # Verify restore
            restored = radio.read_channel(ch_num)
            if restored.rx_freq_hz == original.rx_freq_hz:
                print('RESTORE:OK')
                passed += 1
            else:
                print(f'RESTORE:FAIL (expected {original.rx_freq_hz/1e6:.6f}, got {restored.rx_freq_hz/1e6:.6f})')
                failed += 1
                
        except Exception as e:
            print(f'ERROR: {e}')
            failed += 1

    radio.disconnect()
    
    print('='*50)
    print(f'RESULTS: {passed}/25 passed, {failed}/25 failed')
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
