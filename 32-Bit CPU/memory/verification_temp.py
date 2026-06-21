# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.clock import Clock
# pyrefly: ignore [missing-import]
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def memory_data_test(dut):
    # Start a 10 ns clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await RisingEdge(dut.clk)

    # Reset
    dut.rst_n.value = 0
    dut.write_enable.value = 0
    dut.address.value = 0
    dut.write_data.value = 0  

    await RisingEdge(dut.clk)    
    dut.rst_n.value = 1 
    await RisingEdge(dut.clk)  

    # All is 0 after reset
    print("Checking reset...")
    for address in range(64):
        dut.address.value = address * 4 # Word aligned
        await Timer(1, units="ns")
        assert dut.read_data.value == 0, f"Read data was {dut.read_data.value} at address {address*4}"
      
    # Test: Write and read back data
    print("Writing data...")
    test_data = [
        (0, 0xDEADBEEF),
        (4, 0xCAFEBABE),
        (8, 0x12345678),
        (12, 0xA5A5A5A5)
    ]

    for address, data in test_data:
        # Write data to memory
        dut.address.value = address
        dut.write_data.value = data
        dut.write_enable.value = 1
        await RisingEdge(dut.clk)

        # Disable write after one cycle
        dut.write_enable.value = 0
        await RisingEdge(dut.clk)

        # Verify the write by reading back
        dut.address.value = address
        await Timer(1, units="ns")
        print(f"Read at {address}: {hex(dut.read_data.value.integer)}")
        assert dut.read_data.value.integer == data, f"Data mismatch! Expected {hex(data)} got {hex(dut.read_data.value.integer)}"

    print("Finished test_data successfully!")