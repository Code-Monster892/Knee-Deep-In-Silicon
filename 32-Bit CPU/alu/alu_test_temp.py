# pyrefly: ignore [missing-import]
import cocotb

# pyrefly: ignore [missing-import]
from cocotb.triggers import Timer

@cocotb.test()
async def alu_basic_test(dut):
    # Test cases: (alu_control, src1, src2, expected_result)
    test_cases = [
        # Addition (000)
        (0b000, 10, 15, 25),
        (0b000, 0xFFFFFFFF, 1, 0), # Overflow case, should wrap to 0 in 32-bit
        # Bitwise AND (001)
        (0b001, 0b1100, 0b1010, 0b1000),
        # Bitwise OR (010)
        (0b010, 0b1100, 0b1010, 0b1110),
        # Bitwise XOR (100)
        (0b100, 0b1100, 0b1010, 0b0110),
        # Subtraction (110)
        (0b110, 20, 5, 15),
        (0b110, 5, 5, 0),
    ]

    for ctrl, a, b, expected in test_cases:
        dut.alu_control.value = ctrl
        dut.src1.value = a
        dut.src2.value = b
        
        await Timer(1, units="ns")
        
        # Mask expected result to 32 bits since Python handles arbitrarily large integers
        expected_32bit = expected & 0xFFFFFFFF
        
        assert dut.alu_result.value.integer == expected_32bit, f"ALU Error: ctrl={bin(ctrl)}, {a} op {b} = {dut.alu_result.value.integer}, expected {expected_32bit}"
        
        # Check zero flag
        expected_zero = 1 if expected_32bit == 0 else 0
        assert dut.zero.value == expected_zero, f"Zero flag error: expected {expected_zero}, got {dut.zero.value}"

    print("ALU passed all basic tests!")
