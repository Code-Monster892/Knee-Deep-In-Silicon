# Knee-Deep-In-Silicon

"If you wish to make an apple pie from scratch, you must first invent the universe."  ~Carl Sagan

Welcome! This repository contains the complete source code, documentation, and personal notes for a custom 32-bit RISC-V CPU, built from the ground up based on the classic architectural principles outlined by Harris & Harris and Patterson.

The ultimate milestone of this project? Getting it to run DOOM. Whether you are a seasoned hardware engineer or a student trying to wrap your head around computer architecture, I've designed this repository to be as readable and educational as possible.

 ----------------------------------------------------------------------------------------------------------------------------------------------------------------- 

🙏 Special Thanks & Acknowledgements

This project would not exist without the incredible open-source hardware community.

I want to extend a massive, specific thank you to 0BAB1's HOLY_CORE_COURSE. A vast majority of my initial single-cycle CPU design was heavily inspired by and based upon the foundations laid out in that repository. If you are learning CPU design, I highly recommend checking out their work. Also, if you are new to computer architecture like I was when starting this project, you should definitely check out the DDCA CH7 playlist on Sarah Harris' channel, god's work right there. A lot of work on this project (specifically the M Extension) was deeply based on The Hardware/Software Interface: RISC-V Edition by David A. Patterson and John L. Hennessy, so make sure to check that out as well. 
Based on these resources, i have also shared my handwritten notes as a standalone pdf, it's got most of the necessary theoretical knowledge you need for this

 -----------------------------------------------------------------------------------------------------------------------------------------------------------------

🗺️ What's in this Repository?

I wanted to make sure the journey of building this was just as accessible as the final code. Here is what you'll find:

1. The Hardware: Custom RV32IM CPU
We designed and built a fully functional 32-bit RISC-V processor from scratch in SystemVerilog. The CPU implements the RV32IM instruction set architecture, meaning it supports the base integer instructions (RV32I) and the hardware multiplication/division extension (M).
CPU Architecture Highlights:

Single-Cycle Execution: The core is currently a single-cycle design, where each instruction is fetched, decoded, and executed in one clock cycle.

Memory Interface: Distinct instruction and data pathways (handled via a unified memory arbiter in the Verilator testbench).

Hardware Multiplier Unit (multiplier.sv): A dedicated combination unit handling all signed, unsigned, and mixed signedness multiplication and division operations.

Branch Evaluator (be.sv): Dedicated combinational logic for evaluating all 6 conditional branch types.

2. The Software: Bare-Metal C Runtime
To run C code without an operating system, we had to build a complete bare-metal runtime environment using the GNU RISC-V toolchain (riscv64-unknown-elf-gcc).

Bootloader (crt0.s): We wrote a custom assembly boot sequence that sets up the stack pointer (0x01000000), clears the .bss (uninitialized variables) memory segment to zero, and jumps into the C main() function.

Linker Script (link.ld): We laid out the 16 MB of physical RAM, allocating space for the instruction .text, .data, and .bss sections, and feeding the remaining ~10 MB of RAM directly to the C Standard Library as the malloc heap.

C Standard Library (picolibc): We linked against picolibc, a lightweight libc variant tailored for embedded devices, which gave us access to malloc, printf, and string.h functions natively.

3. The Port: DOOM Generic
We ported DOOM Generic, an abstraction of the original DOOM engine designed for easy porting to new hardware.

Hardware Abstraction Layer (HAL): In doomgeneric_riscv.c, we wrote custom "Operating System" wrappers for DOOM.

Fake File System: DOOM relies heavily on file I/O to read graphics and levels from the doom1.wad file. We bundled the 4 MB WAD file directly into our C binary as a byte array (doom1_wad.c) and intercepted C system calls (read, open, lseek, close) to read directly from this array instead of a real hard drive.

4. The Simulator: Verilator & Memory-Mapped I/O (MMIO)
We used Verilator to translate our SystemVerilog CPU into a highly optimized C++ model. The Verilator harness (main.cpp) acted as the "Motherboard" for our CPU.
Video Output (0x02000000): We dedicated a region of memory as the "Video RAM." When the CPU writes DOOM's generated pixels to this address, the Verilator C++ testbench intercepts the write and paints the color onto an SDL2 graphical window.
System Timer (0x02500000): DOOM requires a precise real-time clock to keep the game running at the correct speed. We exposed the host PC's wall-clock time to the CPU by letting the CPU read from this hardware address.
Keyboard Input (0x02600000): We routed SDL2 keystrokes from the host PC directly into a memory address so the CPU could read player inputs. (these are very unstable but I ain't touching a thing as long as it's working fine lol)
UART Console (0x10000000): We hooked printf to output characters to this address, which Verilator intercepted and printed to the terminal for debugging.

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

 -----------------------------------------------------------------------------------------------------------------------------------------------------------------

⚙️ Simulation, Verification & Performance Notes

It is important to note that this CPU is currently entirely simulation-based. I started the initial hardware verification process using cocotb (As done in the holy core repo by 0BAB1), but eventually migrated to Verilator to achieve the significantly faster simulation speeds required to run a full game engine. To thoroughly map out and debug the logic, I relied heavily on GTKWave. For reference and transparency, I have uploaded a few of the waveform.vcd files generated during the various verification stages so you can see exactly how the CPU signals behave under the hood.

Porting DOOM to this architecture was a wildly buggy, trial-by-fire experience. Because there is no operating system involved—this is purely bare-metal execution running straight out of 16MB of initialized RAM—the game runs at a very low framerate (Lowkey Unplayable. But atleast it runs). If you are looking for a buttery-smooth, playable DOOM port, this isn't it. Instead, this serves as a raw proof of concept that a custom, hand-built 32-bit processor is fully capable of handling complex, real-world software workloads.

Debugging the port also required some creative problem-solving. At one point, I hit a massive roadblock and couldn't tell if the issue was in my CPU logic, the C code, or the compiler. To isolate the bug, I briefly spun up QEMU to emulate the architecture and test the compiled binaries. This confirmed the compiler instructions were sound, allowing me to confidently jump back into Verilator, pinpoint the actual hardware flaw, and finally get the game rendering. (This alone took me 5-6 Hours btw)

 -----------------------------------------------------------------------------------------------------------------------------------------------------------------
