#!/usr/bin/env python3
"""Test to confirm channel 3 issue is related to active channel selection"""
import sys
sys.path.insert(0, '.')

from pmr_171_cps.radio.pmr171_uart import PMR171Radio, ChannelData, Mode

def main():
    radio = PMR171Radio('COM3')
    radio.connect()
    print('Testing channels 0-10, skipping channel 3 (the active channel)...')
    print('='*50)

    passed = 0
    failed = 0

    for ch_num in [0,1,2,4,5,6,7,8,9,10]:
        print(f'Channel {ch_num}: ', end='', flush=True)
        try:
            original = radio.read_channel(ch_num)
            test = ChannelData(index=ch_num, rx_mode=Mode.NFM, tx_mode=Mode.NFM,
                               rx_freq_hz=446_000_000 + (ch_num * 1000),
                               tx_freq_hz=446_000_000 + (ch_num * 1000),
                               rx_ctcss_index=0, tx_ctcss_index=0, name=f'TEST_{ch_num:02d}')
            radio.write_channel(test)
            readback = radio.read_channel(ch_num)
            if readback.rx_freq_hz == test.rx_freq_hz and readback.name.strip() == test.name:
                print('W:OK ', end='', flush=True)
                radio.write_channel(original)
                restored = radio.read_channel(ch_num)
                if restored.rx_freq_hz == original.rx_freq_hz:
                    print('R:OK')
                    passed += 1
                else:
                    print('R:FAIL')
                    failed += 1
            else:
                print('W:FAIL')
                failed += 1
                radio.write_channel(original)
        except Exception as e:
            print(f'ERROR: {e}')
            failed += 1

    radio.disconnect()
    print('='*50)
    print(f'RESULTS: {passed}/10 passed, {failed}/10 failed')
    
    if failed == 0:
        print('\nCONFIRMED: Skipping channel 3 (active channel) results in 100% pass rate!')
        print('The radio has issues responding when the currently-selected channel is being modified.')

if __name__ == '__main__':
    main()
