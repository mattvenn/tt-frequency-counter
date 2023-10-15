import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles


segments = [ 63, 6, 91, 79, 102, 109, 124, 7, 127, 103 ]

async def check_display(dut, compare):
    # reset
    dut._log.info("reset")
    dut.rst_n.value = 0
    # set the compare value
    dut.ui_in.value = compare
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    await ClockCycles(dut.clk, 1000)

@cocotb.test()
async def test_7seg(dut):
    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    await check_display(dut, 1)

