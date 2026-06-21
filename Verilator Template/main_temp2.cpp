.PHONY: all clean software

all: software
	@echo "--- Compiling with Verilator ---"
	verilator -Wall -Wno-DECLFILENAME -Wno-UNOPTFLAT -Wno-EOFNEWLINE -Wno-WIDTHTRUNC -Wno-UNUSEDSIGNAL -Wno-CASEINCOMPLETE -Wno-SYNCASYNCNET -Wno-PINMISSING -LDFLAGS "-lSDL2" --trace --cc ../../src/*.sv --exe main.cpp --top-module cpu --build -j 0
	@echo "--- Running Simulation ---"
	./obj_dir/Vcpu

software:
	@echo "--- Compiling Bare-Metal Screen ---"
	riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 -O3 -T link.ld -nostartfiles -nostdlib crt0.s screen.c -o screen.elf
	riscv64-unknown-elf-objcopy -O binary screen.elf screen.bin
	python3 -c "import sys; b=sys.stdin.buffer.read(); print('\n'.join(b[i:i+4][::-1].hex() for i in range(0,len(b),4)))" < screen.bin > firmware.hex

clean:
	rm -rf obj_dir waveform.vcd screen.elf screen.bin firmware.hex
