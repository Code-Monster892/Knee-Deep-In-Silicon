# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.clock import Clock
# pyrefly: ignore [missing-import]
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def regfile_basic_test(dut):
    # Start a 10 ns clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # Initialize inputs
    dut.write_enable.value = 0
    dut.address1.value = 0
    dut.address2.value = 0
    dut.address3.value = 0
    dut.write_data.value = 0
    
    # Apply reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Test 1: Verify register 0 is always 0, even if we try to write to it
    print("Testing Register 0 hardwiring...")
    dut.address3.value = 0
    dut.write_data.value = 0xDEADBEEF
    dut.write_enable.value = 1
    await RisingEdge(dut.clk)
    
    dut.write_enable.value = 0
    dut.address1.value = 0
    await Timer(1, units="ns")
    assert dut.read_data1.value == 0, f"Register 0 should be 0, but got {hex(dut.read_data1.value)}"
    
    # Test 2: Write to a few registers and read them back
    print("Testing writes to normal registers...")
    test_vectors = [
        (1, 0x11111111),
        (2, 0x22222222),
        (15, 0xAAAAAAAA),
        (31, 0xFFFFFFFF)
    ]
    
    for addr, data in test_vectors:
        dut.address3.value = addr
        dut.write_data.value = data
        dut.write_enable.value = 1
        await RisingEdge(dut.clk)
        
    dut.write_enable.value = 0
    
    # Now read them back
    for addr, data in test_vectors:
        dut.address1.value = addr
        await Timer(1, units="ns")
        assert dut.read_data1.value == data, f"Mismatch at reg {addr}: expected {hex(data)}, got {hex(dut.read_data1.value.integer)}"
        
    print("Register file passed basic tests!")
