# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.clock import Clock
# pyrefly: ignore [missing-import]
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def cpu_lw_test(dut):
    # Start a 10 ns clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # 1. Reset the CPU
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    
    # 2. Pre-load Memory with our program and data!
    # Our program: "lw x1, 4(x0)"
    # Machine Code: 0x00402083
    # We will load this at memory address 0. (memory array index 0)
    dut.mem_inst.mem[0].value = 0x00402083
    
    # Our data: We want to load the value 0xDEADBEEF
    # We will put this at memory address 4. (memory array index 1)
    dut.mem_inst.mem[1].value = 0xDEADBEEF
    
    # 3. Release reset and let the CPU run!
    dut.rst_n.value = 1
    
    # Wait for 1 clock cycle for the instruction to fetch and execute
    await RisingEdge(dut.clk)
    
    # Wait a tiny bit for the writeback to settle into the Register File
    await Timer(1, units="ns")
    
    # 4. Check the results!
    # Register x1 (index 1) should now contain 0xDEADBEEF!
    result = dut.regf_inst.registers[1].value.integer
    
    assert result == 0xDEADBEEF, f"CPU Test Failed! x1 contains {hex(result)} instead of 0xDEADBEEF"
    
    print("========================================")
    print("🎉 CPU PASSED THE LOAD WORD TEST! 🎉")
    print("========================================")
