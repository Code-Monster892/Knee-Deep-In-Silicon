# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.clock import Clock
# pyrefly: ignore [missing-import]
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def cpu_jal_test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # 1. Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    
    # 2. Pre-load Memory 
    # Address 0: jal x1, +12
    # This should jump to Address 12!
    # And it should save PC+4 (which is 4) into register x1!
    dut.mem_inst.mem[0].value = 0x00C000EF 
    
    # Address 4 & 8: Random math that should be SKIPPED!
    dut.mem_inst.mem[1].value = 0x00000000
    dut.mem_inst.mem[2].value = 0x00000000
    
    # Address 12: add x4, x1, x0
    # We should land here. x4 will become whatever is in x1 + 0.
    dut.mem_inst.mem[3].value = 0x00008233 
    
    # 3. Run CPU
    dut.rst_n.value = 1
    
    print("\n========================================")
    print("             JAL TESTING                ")
    print("========================================")
    
    # Tick 1: Fetch and Execute `jal x1, 12`
    # PC = 0. target = 0 + 12 = 12. Next PC becomes 12!
    # writeback = PC + 4 = 4. 4 is written to x1!
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    
    print(f"After JAL, PC jumped to: {dut.pc.value.integer}")
    
    # Tick 2: Fetch and Execute `add x4, x1, x0` (At address 12)
    # x4 should become x1 + 0. (x1 holds the return address: 4).
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    
    # 4. Verify Results
    x1_val = dut.regf_inst.registers[1].value.integer
    x4_val = dut.regf_inst.registers[4].value.integer
    
    assert dut.pc.value.integer == 16, f"JAL FAILED! The PC didn't jump to 12. It went to {dut.pc.value.integer-4} instead."
    assert x1_val == 4, f"JAL FAILED! The return address (4) was not saved to x1! x1 has: {x1_val}"
    assert x4_val == 4, f"JAL FAILED! We didn't execute the landing instruction!"
    
    print("🎉 CPU PASSED THE JAL TEST! 🎉")
    print("========================================\n")
