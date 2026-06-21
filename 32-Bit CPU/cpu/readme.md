J-type instruction Note:

Right now, our writeback_data multiplexer in cpu.sv is just a simple 2-way train switch:
assign writeback_data = (result_src) ? mem_read_data : alu_result;

If result_src is 0: Route the ALU output into the Register File (for math).
If result_src is 1: Route the Memory output into the Register File (for lw).

The Problem: There’s no way to route pc + 4 into the Register File because the switch only has two tracks.
The Solution: A bigger switch!

To add a 3rd track (for pc + 4), we need to replace the 1-bit result_src wire with a 2-bit result_src wire. A 2-bit wire gives us 4 combinations (00, 01, 10, 11).
With more than two options, we can’t use the simple ? : syntax anymore. Instead, we’ll build a larger switch using an always_comb block and a case statement


Working for the J-Type instructions CPU Test:

```
# Address 0: 
jal x1, +12       // Jump forward 12 bytes. Save the bookmark (PC+4) into x1.
# Address 4: 
00000000          // (Empty space, the CPU should skip this)
# Address 8: 
00000000          // (Empty space, the CPU should skip this)
# Address 12:
add x4, x1, x0    // We land here! Add x1 + 0, and save it into x4.
```

**1. The Jump Decision** At Address `0`, the CPU fetches the `jal` instruction. The Target Adder calculates the destination: `0 + 12 = 12`. The Control Unit throws the `jump` switch, and the PC Multiplexer routes `12` into the Program Counter. The CPU immediately fast-forwards to Address `12`, completely ignoring the empty space at Addresses `4` and `8`.
**2. The Return Bookmark** At the exact same time the CPU is jumping, the `jal` instruction calculates the address of the *next* line of code in case we ever want to return. Since we were at Address `0`, the next line is Address `4` (`PC + 4`). Because of the new 3-way Writeback MUX you built, that number `4` gets routed directly into Register `x1`!
**3. The Landing Zone** The CPU lands at Address `12` and fetches the `add` instruction. It takes the value sitting inside Register `x1` (which should be our `4` bookmark), adds `0` (since `x0` is always zero), and saves the answer into Register `x4`.