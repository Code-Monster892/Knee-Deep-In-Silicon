# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.clock import Clock
# pyrefly: ignore [missing-import]
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def cpu_rtype_test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # 1. Reset the CPU
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    
    # 2. Pre-load Memory with our Math Program!
    dut.mem_inst.mem[0].value = 0x01002083 # lw x1, 16(x0)
    dut.mem_inst.mem[1].value = 0x01402103 # lw x2, 20(x0)
    dut.mem_inst.mem[2].value = 0x002081B3 # add x3, x1, x2
    dut.mem_inst.mem[3].value = 0x40208233 # sub x4, x1, x2
    
    # The Math Data!
    dut.mem_inst.mem[4].value = 10  # Value for x1 (Address 16, Index 4)
    dut.mem_inst.mem[5].value = 5   # Value for x2 (Address 20, Index 5)
    
    dut.rst_n.value = 1
    
    print("\n========================================")
    print("      R-TYPE ARITHMETIC TRACE           ")
    print("========================================")
    
    # Cycle 1: lw x1, 16(x0) -> Loads 10 into x1
    await Timer(1, units="ns")
    print(f"CYCLE 1: Loading 10 into x1...")
    await RisingEdge(dut.clk)
    
    # Cycle 2: lw x2, 20(x0) -> Loads 5 into x2
    await Timer(1, units="ns")
    print(f"CYCLE 2: Loading 5 into x2...")
    await RisingEdge(dut.clk)
    
    # Cycle 3: add x3, x1, x2 -> x3 should become 15
    await Timer(1, units="ns")
    print(f"\nCYCLE 3: Executing ADD!")
    print(f"  Instruction: {hex(dut.instr.value.integer)}")
    print(f"  ALU Control Signal: {bin(dut.alu_control.value)}")
    print(f"  ALU Operand 1 (x1): {dut.reg_data1.value.integer}")
    print(f"  ALU Operand 2 (x2): {dut.alu_src_b.value.integer}")
    print(f"  ALU Add Result: {dut.alu_result.value.integer}")
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    print(f"  --> x3 safely updated to: {dut.regf_inst.registers[3].value.integer}")
    
    # Cycle 4: sub x4, x1, x2 -> x4 should become 5
    print(f"\nCYCLE 4: Executing SUB!")
    print(f"  Instruction: {hex(dut.instr.value.integer)}")
    print(f"  ALU Control Signal: {bin(dut.alu_control.value)}")
    print(f"  ALU Subtract Result: {dut.alu_result.value.signed_integer}")
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    print(f"  --> x4 safely updated to: {dut.regf_inst.registers[4].value.integer}")
    print("========================================\n")
    
    # 4. Check the results!
    assert dut.regf_inst.registers[3].value.integer == 15, "ADD Failed!"
    assert dut.regf_inst.registers[4].value.integer == 5, "SUB Failed!"
