# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.triggers import Timer

@cocotb.test()
async def control_basic_test(dut):
    # Initialize all inputs
    dut.op.value = 0
    dut.funct3.value = 0
    dut.funct7.value = 0
    dut.alu_zero.value = 0
    
    await Timer(1, units="ns")
    
    print("Testing 'lw' instruction decode...")
    # 'lw' opcode is 0000011
    dut.op.value = 0b0000011
    
    await Timer(1, units="ns")
    
    # Check if the control signals match our expectations for Load Word
    assert dut.reg_write.value == 1, f"Expected reg_write=1, got {dut.reg_write.value}"
    assert dut.alu_src.value == 1, f"Expected alu_src=1, got {dut.alu_src.value}"
    assert dut.mem_write.value == 0, f"Expected mem_write=0, got {dut.mem_write.value}"
    assert dut.result_src.value == 1, f"Expected result_src=1, got {dut.result_src.value}"
    assert dut.imm_src.value == 0b00, f"Expected imm_src=00, got {dut.imm_src.value}"
    assert dut.alu_control.value == 0b000, f"Expected alu_control=000 (ADD), got {dut.alu_control.value}"

    print("Control Unit passed basic tests!")
