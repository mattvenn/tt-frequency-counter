import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
from frequency_counter.test.test_seven_segment import read_segments
import random

async def reset(dut):
    dut.rst_n.value = 0
    dut.ui_in[2].value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1;
    await ClockCycles(dut.clk, 5)

async def update_period(dut, period):
    dut.ui_in[2].value = 1
    dut.ui_in[1].value = 0
    dut.uio_in.value = period >> 4
    await ClockCycles(dut.clk, 1)
    dut.ui_in[2].value = 0
    await ClockCycles(dut.clk, 1)

@cocotb.test()
async def test_load(dut):
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    await reset(dut)
    for period in range(0, 2000, 100):
        await update_period(dut, period)

@cocotb.test()
async def test_all(dut):
    clock_mhz = 10
    clk_period_ns = round(1/clock_mhz * 1000, 2)
    dut._log.info("input clock = %d MHz, period = %.2f ns" %  (clock_mhz, clk_period_ns))

    clock = Clock(dut.clk, clk_period_ns, units="ns")
    clock_sig = cocotb.start_soon(clock.start())
    await reset(dut)
   
    # adjust the update period to match clock freq
    period = clock_mhz * 100 - 1
    await update_period(dut, period)
    
    for input_freq in [10, 69, 90]:
        # create an input signal
        period_us = round((1/input_freq) * 100, 3)
        dut._log.info("input freq = %d kHz, period = %.2f us" %  (input_freq, period_us))
        input_signal = cocotb.start_soon(Clock(dut.ui_in[0], period_us,  units="us").start())

        # give it 4 update periods to allow counters to adjust
        await ClockCycles(dut.clk, period * 4)
        assert await read_segments(dut) == input_freq

        # kill signal
        input_signal.kill()

    clock_sig.kill()
