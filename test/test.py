# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # 10MHz clock = 100ns period
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test Counter: Decimal Mode Up")
    # ui_in[0] = 1 (Up), ui_in[1] = 0 (Dec)
    dut.ui_in.value = 0x01 
    
    # Define the 7-segment patterns for 0-9 (Decimal mode)
    # Segments {g,f,e,d,c,b,a} mapped to bits [6:0]
    # '0' = 0x3F (0111111)
    # '1' = 0x06 (0000110)
    # etc.
    expected_dec = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]
    
    for i in range(10):
        # We wait for the 'tick'. 
        # If you used the `ifdef SIM` fix, it happens every 17 cycles (0 to 16)
        await ClockCycles(dut.clk, 17) 
        
        # Check uo_out[6:0]. We use & 0x7F to ignore the Mode Indictor (bit 7)
        current_segments = int(dut.uo_out.value) & 0x7F
        dut._log.info(f"Checking digit {i}: Expected {hex(expected_dec[i])}, got {hex(current_segments)}")
        assert current_segments == expected_dec[i]

    dut._log.info("Test Counter: Hex Mode indicator")
    # Turn on Hex mode (ui_in[1] = 1)
    dut.ui_in.value = 0x03
    await ClockCycles(dut.clk, 1)
    # uo_out[7] should now be 1
    assert int(dut.uo_out.value) & 0x80 == 0x80
