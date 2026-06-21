#include "Vcpu.h"
#include "verilated.h"
#include "verilated_vcd_c.h"
#include <iostream>

int main(int argc, char** argv) {
    // Initialize Verilator
    Verilated::commandArgs(argc, argv);
    Verilated::traceEverOn(true); // Enable VCD tracing

    // Instantiate the CPU module
    Vcpu* dut = new Vcpu;
    
    // Set up the VCD trace file
    VerilatedVcdC* m_trace = new VerilatedVcdC;
    dut->trace(m_trace, 5); // Trace 5 levels of hierarchy deep
    m_trace->open("waveform.vcd");

    // Initial hardware state
    dut->clk = 0;
    dut->rst_n = 0;

    int time = 0;
    std::cout << "Starting Verilator Simulation..." << std::endl;

    // Run for 25 clock edges (12.5 full clock cycles)
    for (int i = 0; i < 25; i++) {
        // Release reset after 2 ticks
        if (i == 2) {
            dut->rst_n = 1;
        }
        
        dut->clk = !dut->clk; // Toggle clock
        dut->eval();          // Let the hardware evaluate
        
        m_trace->dump(time);  // Save signal states to VCD
        time++;
    }

    std::cout << "Simulation Complete! Generated waveform.vcd" << std::endl;

    // Cleanup
    m_trace->close();
    delete dut;
    return 0;
}
