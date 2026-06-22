# Knee-Deep-In-Silicon

"If you wish to make an apple pie from scratch, you must first invent the universe."  ~Carl Sagan

Welcome! This repository contains the complete source code, documentation, and personal notes for a custom 32-bit RISC-V CPU, built from the ground up based on the classic architectural principles outlined by Harris & Harris and Patterson.

The ultimate milestone of this project? Getting it to run DOOM. Whether you are a seasoned hardware engineer or a student trying to wrap your head around computer architecture, I've designed this repository to be as readable and educational as possible.




<img width="426" height="240" alt="getsitecontrol__compress-gif__free (2)" src="https://github.com/user-attachments/assets/16097de9-725a-4cdc-a22d-576895d77934" />


(This is at 10x speed, expect the actual gameplay 10 times slower than this)

 ----------------------------------------------------------------------------------------------------------------------------------------------------------------- 

🙏 Special Thanks & Acknowledgements

This project would not exist without the incredible open-source hardware community.

I want to extend a massive, specific thank you to 0BAB1's HOLY_CORE_COURSE. A vast majority of my initial single-cycle CPU design was heavily inspired by and based upon the foundations laid out in that repository. If you are learning CPU design, I highly recommend checking out their work. Also, if you are new to computer architecture like I was when starting this project, you should definitely check out the DDCA CH7 playlist on Sarah Harris' channel, god's work right there. A lot of work on this project (specifically the M Extension) was deeply based on The Hardware/Software Interface: RISC-V Edition by David A. Patterson and John L. Hennessy, so make sure to check that out as well. 
Based on these resources, i have also shared my handwritten notes as a standalone pdf, it's got most of the necessary theoretical knowledge you need for this

 -----------------------------------------------------------------------------------------------------------------------------------------------------------------

🗺️ What's in this Repository?

I wanted the journey of building this processor to be just as accessible as the final code. Here is exactly what you'll find across the hardware, software, and simulation layers:

A single-cycle RV32IM CPU, written in SystemVerilog, with a dedicated hardware multiply/divide unit and a from-scratch byte-enable/load-extend pipeline for sub-word memory access.

A bare-metal C runtime (custom crt0.s, linker script, picolibc) with no OS underneath it.

A port of doomgeneric, including a custom hardware abstraction layer and a fake filesystem that serves the WAD file straight out of a baked-in byte array.

A Verilator + SDL2 testbench acting as the "motherboard" — memory-mapped video, timer, keyboard, and UART.

The full, unfiltered debugging history of getting from "screen is black" to "DOOM boots." Three interesting stories below, including one that came down to a single wrong constant in the hardware.

 -----------------------------------------------------------------------------------------------------------------------------------------------------------------

📂 Navigating the Repository

I wanted to organize this repository so that it is useful whether you just want the finished product or you want to follow along with the exact, messy development process. Here is how the files are structured:

Final/: If you just want the clean, fully functional, end-state code that this whole project is about, start here. This directory contains the polished, final build of the CPU and the DOOM port.

32-Bit CPU/: Think of this folder as a timeline of my development process. Instead of just dumping the final SystemVerilog files, I have organized the modules step-by-step based on my progress. For example, you can find the exact .sv files from when I first implemented the lw instruction, and follow along as I gradually expanded the architecture to support more complex instructions. It also houses a few of the intermediate GTKWave waveform.vcd files and specific readme.md notes I made along the way. Although I tried my best to make it clear and informative, it's not the best and you'll have to figure out a lot of stuff by yourself (All the best).

Verilator Template/: Transitioning from cocotb to Verilator was a major milestone that required figuring out a whole new build process. I preserved my initial Verilator build in this folder to act as a standalone checkpoint. If you are trying to figure out how to set up a C++ testbench for your own SystemVerilog CPU, you can use this template as a foundational starting point. It currently just outputs a red screen. This was when i first tested the overall capabilities of the CPU.

 -----------------------------------------------------------------------------------------------------------------------------------------------------------------

📜 The Instruction Set

(RV32IM)At its core, this processor executes the RV32IM instruction set. While the base integer instructions (RV32I) provide the fundamental arithmetic, memory, and branching operations required to run standard C code, I also fully implemented the standard 'M' extension for Integer Multiplication and Division. Adding native hardware support for complex math operations—rather than relying on slow software emulation—was an absolutely crucial step for handling the heavy rendering calculations required by DOOM.
Here is the complete list of instructions currently supported and mapped out in the datapath:

R-Type (Arithmetic & Logic): add, sub, sll, slt, sltu, xor, srl, sra, or, and

I-Type (Immediate): addi, slti, sltiu, xori, ori, andi, slli, srli, srai

I-Type (Loads): lw (Word), lh (Halfword), lhu (Halfword Unsigned), lb (Byte), lbu (Byte Unsigned)

S-Type (Stores): sw (Word), sh (Halfword), sb (Byte)

B-Type (Branches): beq, bne, blt, bge, bltu, bgeu

J-Type (Jumps): jal (Jump and Link), jalr (Jump and Link Register)

U-Type (Upper Immediates): lui (Load Upper Immediate), auipc (Add Upper Immediate to PC)

M-Extension (Math): mul, mulh, mulhsu, mulhu, div, divu, rem, remu

 -----------------------------------------------------------------------------------------------------------------------------------------------------------------

🎮 The Road to DOOM

"It runs DOOM" is the ultimate rite of passage for any custom hardware.
Porting DOOM required not just a functioning CPU, but a stable toolchain, memory-mapped I/O for the display, and handling strict memory alignment. The guide covers the exact steps taken to cross-compile the game, map the framebuffers, and finally see the classic HUD render on custom silicon.

<img width="742" height="470" alt="image" src="https://github.com/user-attachments/assets/eab6c43a-1d3e-4b2e-9aff-604ed9218090" />


 -----------------------------------------------------------------------------------------------------------------------------------------------------------------

⚙️ Simulation, Verification & Performance Notes

It is important to note that this CPU is currently entirely simulation-based. I started the initial hardware verification process using cocotb (As done in the holy core repo by 0BAB1), but eventually migrated to Verilator to achieve the significantly faster simulation speeds required to run a full game engine. To thoroughly map out and debug the logic, I relied heavily on GTKWave. For reference and transparency, I have uploaded a few of the waveform.vcd files generated during the various verification stages so you can see exactly how the CPU signals behave under the hood.

Porting DOOM to this architecture was a wildly buggy, trial-by-fire experience. Because there is no operating system involved—this is purely bare-metal execution running straight out of 16MB of initialized RAM—the game runs at a very low framerate (Lowkey Unplayable. But atleast it runs). If you are looking for a buttery-smooth, playable DOOM port, this isn't it. Instead, this serves as a raw proof of concept that a custom, hand-built 32-bit processor is fully capable of handling complex, real-world software workloads.

Debugging the port also required some creative problem-solving. At one point, I hit a massive roadblock and couldn't tell if the issue was in my CPU logic, the C code, or the compiler. The screen was just black and it was hard to figure out where the bug was. Read the entire story below if you like:

"It runs DOOM" is the easy sentence. Getting there took three separate, stacked failures across the software and hardware boundary — and the only way through was refusing to guess and instead designing an experiment that could actually tell hardware and software bugs apart.

The method: QEMU as a lie detector

Any crash in a from-scratch CPU leaves you with two suspects: the C code/compiler, or the physical logic gates. There's no way to tell which from a black screen alone.

The fix was to boot the exact same compiled binary in QEMU — a battle-tested, industry-standard RISC-V emulator — alongside Verilator. The logic: if it crashes in QEMU too, the bug is in the software. If it only crashes on the custom CPU, the bug is in the hardware. This single technique is what cracked all three bugs below.

**Bug #1 — The keyboard that was always pressed**

Symptom: DOOM printed Doom Generic 0.1 in QEMU and froze instantly, never reaching the WAD loading stage.

Investigation: printf tracing pinned the hang to an infinite loop inside DOOM's I_GetEvent() — the engine was endlessly draining a keyboard event queue that never emptied.

Root cause: DG_GetKey() polls keyboard state from MMIO address 0x02600000, treating bit 16 as "a key is currently pressed." In Verilator, an idle keyboard reads back 0. But 0x02600000 isn't a real, mapped address in QEMU — reading an unmapped address there returns -1 (0xFFFFFFFF, all ones). Bit 16 of all-ones is 1. DOOM read that as a permanently-held key and tried to process effectively infinite phantom keystrokes per second.

Fix: corrected the "no input" sentinel handling so an unmapped/idle read can't be misread as a held key.

<img width="397" height="382" alt="image" src="https://github.com/user-attachments/assets/e1afc50d-3c93-407d-8f36-7cc994827cc3" />



**Bug #2 — malloc eating its own program**

Symptom: with the keyboard fixed, both QEMU and Verilator now crashed identically: Warning: recursive call to I_Error detected. Unable to allocate 5 MiB of RAM for zone.

The fact that QEMU failed the exact same way as the real hardware was good news — it meant the CPU logic itself was innocent. This was a software/toolchain bug.

Investigation: DOOM's Z_Init() requests ~6MB from malloc() in one shot. In a bare-metal environment, malloc() is backed by a small custom _sbrk() that hands out raw RAM starting from a __heap_start symbol defined by the linker script.

Root cause: link.ld had a layout bug — it placed .sdata and .sbss (global variables and internal C-library state) after __heap_start instead of before it. When malloc() claimed its 6MB block, it wrote its own allocator metadata at the start of that region — directly on top of DOOM's global variables and picolibc's own internal state. The next printf call saw corrupted library state, panicked, and called I_Error(). I_Error() tried to print its own error message, hit the same corruption, and panicked again — the "recursive call to I_Error" loop.

Fix: restructured link.ld (and link_qemu.ld) so every program section is strictly placed before __heap_start, guaranteeing malloc only ever hands out genuinely free RAM.

**Bug #3 — The CPU that wasn't frozen, it was rebooting**

Symptom: Verilator alone (QEMU now booted fine) just hung — no terminal output, no SDL window content, no visible signal of what the CPU was even doing.

Investigation: added a one-line trace to the Verilator testbench, printing the Program Counter every 50,000 cycles:

cppif (cycles % 50000 == 0) {
    std::cout << "[DEBUG] Cycle " << cycles << " | PC: 0x" << std::hex << dut->pc_out << std::endl;
}

The output told the real story:

[DEBUG] Cycle 1236600000 | PC: 0x1c
[DEBUG] Cycle 1236700000 | PC: 0x20
[DEBUG] Cycle 1236800000 | PC: 0x1c
[DEBUG] Cycle 1236900000 | PC: 0x18
[DEBUG] Cycle 1237000000 | PC: 0x20

Over a billion cycles had run — but the PC was only ever bouncing between 0x18, 0x1C, and 0x20: the very first few instructions of crt0.s, right around the jump into main(). The CPU wasn't stuck. It was endlessly rebooting.

Root cause: calling a function requires pushing a return address onto the stack, and the stack was positioned near the top of the 4.6MB DOOM binary's memory footprint — around the 4.5MB mark. But cpu.sv had this hardcoded into the MMIO decode:

systemverilogassign mmio_we = mem_write & (alu_result >= 32'h00400000);

Any address at or above 4MB was being treated as memory-mapped I/O, not RAM. The stack push at ~4.5MB landed in MMIO instead of RAM and vanished. When the function returned, the CPU read back 0x00000000 from nowhere, dutifully jumped there — and reset the entire program from the top. Forever.

Fix: corrected the MMIO boundary to match the actual RAM size, so the stack stays inside real, addressable memory.

A one-line std::cout in a testbench traced a high-level engine crash all the way down to a single off-by-orders-of-magnitude constant in the hardware description.

 -----------------------------------------------------------------------------------------------------------------------------------------------------------------

🗺️ Future Roadmap
A custom CPU is never really finished. While getting DOOM to boot was the primary milestone, I already have a few major upgrades on the drawing board to push this architecture further:

Pipelined Architecture: The natural next step. I plan to transition the current design into a fully pipelined architecture to significantly improve throughput, clock speeds, and overall simulation performance.

Audio & Music Support: DOOM just isn't the same without that hard metal Mick Gordan soundtrack. I am exploring ways to add memory-mapped audio peripherals or a basic sound controller to get those classic MIDI-style tracks playing directly from the hardware.

Hardware Acceleration: Since the CPU is currently doing all the heavy lifting in software, adding dedicated hardware acceleration blocks (perhaps for specific rendering operations or memory block transfers) could drastically improve the framerate.

The FPGA Dream: Right now, this project lives comfortably in simulation via Verilator. The ultimate stretch goal—though admittedly a bit far off—is to synthesize this entire design and deploy it onto a physical FPGA development board.
