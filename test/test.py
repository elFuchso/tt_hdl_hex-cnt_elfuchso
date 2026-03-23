# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui.value = 0
    dut.uio.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    dut._log.info("Test Counter: Decimal Mode Up")
    dut.ui.value = 0b00000001 # ui[0]=1 (Up), ui[1]=0 (Dec)
    
    # Wait for a few cycles and check segments
    # 0 should be 0x3F (63)
    # 1 should be 0x06 (6)
    # 2 should be 0x5B (91)
    
    expected_segments = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]
    
    for val in expected_segments:
        assert int(dut.uo_out.value) == val
        await ClockCycles(dut.clk, 1)

    dut._log.info("Test Counter: Hex Mode")
    dut.ui.value = 0b00000011 # ui[0]=1 (Up), ui[1]=1 (Hex)
    await ClockCycles(dut.clk, 10) # Advance to 'A'
    
    # 0xA in segments is 0x77 (binary 1110111) + uo[7] is 1 for Hex mode = 0xF7 (247)
    assert int(dut.uo_out.value) == 0xF7
