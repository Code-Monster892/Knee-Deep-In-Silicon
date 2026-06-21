.PHONY: all clean

all:
	@echo "--- Compiling with Verilator ---"
	verilator -Wall -Wno-DECLFILENAME -Wno-UNOPTFLAT -Wno-EOFNEWLINE -Wno-WIDTHTRUNC -Wno-UNUSEDSIGNAL -Wno-CASEINCOMPLETE -Wno-SYNCASYNCNET -Wno-PINMISSING --trace --cc ../../src/*.sv --exe main.cpp --top-module cpu --build -j 0
	@echo "--- Running Simulation ---"
	./obj_dir/Vcpu

clean:
	rm -rf obj_dir waveform.vcd
