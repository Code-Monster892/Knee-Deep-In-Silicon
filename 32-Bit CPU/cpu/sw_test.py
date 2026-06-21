# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.clock import Clock
# pyrefly: ignore [missing-import]
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def cpu_sw_test(dut):
    # Start a 10 ns clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # 1. Reset the CPU
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    
    # 2. Pre-load Memory
    dut.mem_inst.mem[0].value = 0x00802083 # lw x1, 8(x0)
    dut.mem_inst.mem[1].value = 0x00100623 # sw x1, 12(x0)
    dut.mem_inst.mem[2].value = 0xBADC0DE5 # Secret data at addr 8
    dut.mem_inst.mem[3].value = 0x00000000 # Empty slot at addr 12
    
    dut.rst_n.value = 1
    
    print("\n========================================")
    print("        CPU SIMULATION TRACE            ")
    print("========================================")
    
    # Give the combinational logic a tiny bit of time to settle
    await Timer(1, units="ns")
    
    print(f"CLOCK CYCLE 1:")
    print(f"  [Fetch] PC is at address: {dut.pc.value.integer}")
    print(f"  [Fetch] Instruction read from Memory: {hex(dut.instr.value.integer)}")
    print(f"  [Decode] Control Unit 'mem_write' signal: {dut.mem_write.value}")
    print(f"  [Execute] ALU calculated memory address: {dut.alu_result.value.integer}")
    print(f"  [Memory] Memory read data is: {hex(dut.mem_read_data.value.integer)}")
    
    # Tick the clock! This writes the memory data into Register x1.
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    
    print(f"  --> TICK! Data safely written to Register x1: {hex(dut.regf_inst.registers[1].value.integer)}\n")
    
    print(f"CLOCK CYCLE 2:")
    print(f"  [Fetch] PC advanced to address: {dut.pc.value.integer}")
    print(f"  [Fetch] Instruction read from Memory: {hex(dut.instr.value.integer)}")
    print(f"  [Decode] Control Unit 'mem_write' signal: {dut.mem_write.value}")
    print(f"  [Execute] ALU calculated memory address: {dut.alu_result.value.integer}")
    print(f"  [Execute] Data sitting on the 'write_data' wire to RAM: {hex(dut.reg_data2.value.integer)}")
    
    # Tick the clock! This triggers the RAM to save the data.
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    
    print(f"  --> TICK! RAM Address 12 now holds: {hex(dut.mem_inst.mem[3].value.integer)}")
    print("========================================\n")
    
    # 4. Check the results!
    mem_result = dut.mem_inst.mem[3].value.integer
    assert mem_result == 0xBADC0DE5, "CPU Test Failed!"
