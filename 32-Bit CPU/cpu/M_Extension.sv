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
    logic [2:0] result_src; //upgraded to 3 bits
    logic [2:0] imm_src;    //upgraded to 3 bits
    logic [3:0] alu_control;    //upgraded to 4 bits
    logic       take_branch;      //flag to decide whether to take the branch or not
    logic       jalr;

    // --- Program Counter (PC) ---
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) pc <= 32'b0;
        else        pc <= next_pc;
    end

    
    assign pc_target = pc + imm_ext;
    assign next_pc = jalr ? (alu_result & 32'hFFFFFFFE) : (pc_src ? pc_target : (pc + 32'd4));

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

    // --- Branch Comparator ---
    always_comb begin
        case(instr[14:12])
            3'b000: take_branch = (reg_data1 == reg_data2);    //beq
            3'b001: take_branch = (reg_data1 != reg_data2);    //bne
            3'b100: take_branch = ($signed(reg_data1) < $signed(reg_data2));     //blt
            3'b101: take_branch = ($signed(reg_data1) >= $signed(reg_data2));    //bge
            3'b110: take_branch = (reg_data1 < reg_data2);     //bltu
            3'b111: take_branch = (reg_data1 >= reg_data2);    //bgeu
            default: take_branch = 1'b0;
        endcase
    end
            

    // --- Control Unit ---
    control ctrl_inst (
        .op(instr[6:0]),
        .funct3(instr[14:12]),
        .funct7(instr[31:25]),
        .take_branch(take_branch),  // Changed from alu_zero
        .alu_control(alu_control),
        .imm_src(imm_src),
        .reg_write(reg_write),
        .mem_write(mem_write),
        .alu_src(alu_src),
        .result_src(result_src),
        .pc_src(pc_src),
        .jalr(jalr)
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
        .alu_result(alu_result)    // .zero() is ignored and disconnected because we now have branch Comparator
    );

    // --- Hardware Multiplier ---
    logic [31:0] mul_result;

    multiplier mul_inst (
        .src1(reg_data1),
        .src2(alu_src_b),
        .funct3(instr[14:12]),
        .mul_result(mul_result)
    );

    // --- Writeback Multiplexer ---
    always_comb begin
        case(result_src)
            3'b000: writeback_data = alu_result;     //Track 0: ALU math
            3'b001: writeback_data = mem_read_data;  //Track 1: Memory load
            3'b010: writeback_data = pc + 32'd4;     //Track 2 : Return Address for JAL
            3'b011: writeback_data = imm_ext;        //Track 3 : Immediate value
            3'b100: writeback_data = pc_target;      //Track 4 : for auipc
            3'b101: writeback_data = mul_result;     //Track 5: Hardware Multiplier
            
            default: writeback_data = 32'b0;        //Track 6 : Reserved/Unused
        endcase

    end

endmodule