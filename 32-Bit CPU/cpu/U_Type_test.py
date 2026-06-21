# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.clock import Clock
# pyrefly: ignore [missing-import]
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def cpu_utype_test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # 1. Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    
    # 2. Pre-load Memory 
    # Address 0: lui x1, 0x12345    
    # -> Shoves 0x12345 into the top 20 bits. Bottom 12 are zeroed.
    # -> x1 should become 0x12345000
    dut.mem_inst.mem[0].value = 0x123450B7  
    
    # Address 4: auipc x2, 0x00004  
    # -> Shoves 0x00004 into the top 20 bits = 0x00004000
    # -> Adds PC (which is 4 at this instruction)
    # -> x2 should become 0x00004004
    dut.mem_inst.mem[1].value = 0x00004117  
    
    # 3. Run CPU
    dut.rst_n.value = 1
    
    print("\n========================================")
    print("             U-TYPE TESTING             ")
    print("========================================")
    
    # Tick 1: lui
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    
    # Tick 2: auipc
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    
    # 4. Verify Results
    x1_val = dut.regf_inst.registers[1].value.integer
    x2_val = dut.regf_inst.registers[2].value.integer
    
    print(f"x1 (lui):   {hex(x1_val)}")
    print(f"x2 (auipc): {hex(x2_val)}")
    
    assert x1_val == 0x12345000, f"LUI FAILED! Expected 0x12345000, got {hex(x1_val)}"
    assert x2_val == 0x00004004, f"AUIPC FAILED! Expected 0x00004004, got {hex(x2_val)}"
    
    print("🎉 CPU PASSED THE U-TYPE TEST! 🎉")
    print("========================================\n")
