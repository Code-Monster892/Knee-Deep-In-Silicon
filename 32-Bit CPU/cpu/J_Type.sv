module cpu (
    input logic clk,
    input logic rst_n
);

    `ifdef COCOTB_SIM
    initial begin
        $dumpfile("sim_build/waveform.vcd");
        $dumpvars(0, cpu);
    end
    `endif

    // --- Internal Wires ---
    logic [31:0] pc, next_pc;
    logic [31:0] instr;
    logic [31:0] pc_target;
    logic pc_src;
    
    // Register File Wires
    logic [31:0] reg_data1, reg_data2, writeback_data;
    
    // Immediate Wires
    logic [31:0] imm_ext;
    
    // ALU Wires
    logic [31:0] alu_src_b, alu_result;
    logic        alu_zero;
    
    // Memory Wires
    logic [31:0] mem_read_data;
    
    // Control Wires
    logic       reg_write, mem_write, alu_src;
    logic [1:0] result_src; //upgraded to 2 bits
    logic [2:0] imm_src;    //upgraded to 3 bits
    logic [2:0] alu_control;

    // --- Program Counter (PC) ---
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) pc <= 32'b0;
        else        pc <= next_pc;
    end

    
    assign pc_target = pc + imm_ext;
    assign next_pc = pc_src ? pc_target : (pc + 32'd4);

    // --- Memory (Instruction & Data) ---
    memory mem_inst (
        .clk(clk),
        .rst_n(rst_n),
        .we(mem_write),
        .address(alu_result),      // Data Address from ALU
        .write_data(reg_data2),    // Data to write
        .read_data(mem_read_data), // Data read
        .pc_address(pc),           // Instruction Address
        .instruction(instr)        // Instruction read
    );

    // --- Control Unit ---
    control ctrl_inst (
        .op(instr[6:0]),
        .funct3(instr[14:12]),
        .funct7(instr[31:25]),
        .alu_zero(alu_zero),
        .alu_control(alu_control),
        .imm_src(imm_src),
        .reg_write(reg_write),
        .mem_write(mem_write),
        .alu_src(alu_src),
        .result_src(result_src),
        .pc_src(pc_src)
    );

    // --- Register File ---
    regfile regf_inst (
        .clk(clk),
        .rst_n(rst_n),
        .address1(instr[19:15]),
        .address2(instr[24:20]),
        .address3(instr[11:7]),    // Destination register rd
        .write_data(writeback_data),
        .write_enable(reg_write),
        .read_data1(reg_data1),
        .read_data2(reg_data2)
    );

    // --- Sign Extender ---
    signext sext_inst (
        .instr(instr),
        .imm_src(imm_src),
        .imm_ext(imm_ext)
    );

    // --- ALU ---
    // Multiplexer to choose between Register 2 and Immediate for ALU input B
    assign alu_src_b = (alu_src) ? imm_ext : reg_data2;

    alu alu_inst (
        .src1(reg_data1),
        .src2(alu_src_b),
        .alu_control(alu_control),
        .alu_result(alu_result),
        .zero(alu_zero)
    );

    // --- Writeback Multiplexer ---
    always_comb begin
        case(result_src)
            2'b00: writeback_data = alu_result;     //Track 0: ALU math
            2'b01: writeback_data = mem_read_data;  //Track 1: Memory load
            2'b10: writeback_data = pc + 32'd4;     //Track 2 : Return Address for JAL
            
            default: writeback_data = 32'b0;        //Track 3 : Reserved/Unused
        endcase

    end

endmodule