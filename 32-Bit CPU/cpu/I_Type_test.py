# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.clock import Clock
# pyrefly: ignore [missing-import]
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def cpu_addi_test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # 1. Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    
    # 2. Pre-load Memory 
    # Address 0: addi x1, x0, 15    (Positive immediate!)
    # Address 4: addi x2, x1, -5    (Negative immediate!)
    
    dut.mem_inst.mem[0].value = 0x00F00093  
    dut.mem_inst.mem[1].value = 0xFFB08113  
    
    # 3. Run CPU
    dut.rst_n.value = 1
    
    print("\n========================================")
    print("             ADDI TESTING               ")
    print("========================================")
    
    # Tick 1: addi x1, x0, 15
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    
    # Tick 2: addi x2, x1, -5
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    
    # 4. Verify Results
    x1_val = dut.regf_inst.registers[1].value.integer
    x2_val = dut.regf_inst.registers[2].value.integer
    
    # Handle two's complement for negative numbers from Python
    # Python reads raw bits, so a 32-bit negative number looks massive (e.g. 4294967291)
    if x2_val > 0x7FFFFFFF:
        x2_val -= 0x100000000
    
    assert x1_val == 15, f"ADDI FAILED! x1 should be 15, but got {x1_val}"
    assert x2_val == 10, f"ADDI FAILED! x2 should be 10, but got {x2_val}"
    
    print(f"x1 (15 + 0) = {x1_val}")
    print(f"x2 (15 - 5) = {x2_val}")
    print("🎉 CPU PASSED THE ADDI TEST! 🎉")
    print("========================================\n")
