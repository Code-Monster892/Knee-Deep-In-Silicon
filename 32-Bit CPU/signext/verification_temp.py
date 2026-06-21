# pyrefly: ignore [missing-import]
import cocotb
# pyrefly: ignore [missing-import]
from cocotb.triggers import Timer

@cocotb.test()
async def signext_test(dut):
    # We will test an I-Type instruction:
    # Say we have a load instruction with an immediate of -4 (12-bit hex 0xFFC)
    # The immediate is stored in the top 12 bits of the 32-bit instruction
    # 0xFFC << 20 = 0xFFC00000
    
    dut.imm_src.value = 0b00  # I-type
    dut.instr.value = 0xFFC00000
    
    await Timer(1, units="ns")
    
    # In a 32-bit signed integer, -4 is 0xFFFFFFFC
    assert dut.imm_ext.value.integer == 0xFFFFFFFC, f"Sign extension failed! Got {hex(dut.imm_ext.value.integer)}"
    
    print("Sign extender passed basic tests!")