module control (
    input  logic [6:0] op,
    input  logic [2:0] funct3,
    input  logic [6:0] funct7,
    input  logic       alu_zero,
    output logic [2:0] alu_control,
    output logic [2:0] imm_src,
    output logic       reg_write,
    output logic       mem_write,
    output logic       alu_src,    
    output logic [1:0] result_src,
    output logic       pc_src  
);
    logic [1:0] alu_op;
    logic branch;
    logic jump;
    always_comb begin
        // 1. Set safe defaults for all signals!
        reg_write  = 1'b0;
        mem_write  = 1'b0;
        alu_src    = 1'b0;
        result_src = 2'b00;
        imm_src    = 3'b000;
        alu_op     = 2'b00;
        branch     = 1'b0;
        jump       = 1'b0;
        // 2. Main Decoder
        case (op)
            7'b0000011: begin // 'lw' instruction
                reg_write  = 1'b1;
                imm_src    = 3'b000;
                mem_write  = 1'b0;
                alu_src    = 1'b1;  
                result_src = 2'b01;  
                alu_op     = 2'b00; 
            end
            7'b0100011: begin // 'sw' instruction
                mem_write = 1'b1;
                alu_src   = 1'b1;
                imm_src   = 3'b001;
                reg_write = 1'b0;
                result_src= 2'b00;
                alu_op    = 2'b00; 
            end
            7'b0110011: begin // R-Type Instruction
                reg_write = 1'b1;
                imm_src   = 3'b000;
                mem_write = 1'b0;
                alu_src   = 1'b0;  
                result_src= 2'b00;  
                alu_op    = 2'b10;  
            end
            7'b1100011: begin // B-Type Instruction (beq)
                reg_write  = 1'b0;
                imm_src    = 3'b010;  
                mem_write  = 1'b0;
                alu_src    = 1'b0;   
                result_src = 2'b00;
                branch     = 1'b1;   
                alu_op     = 2'b01;  
            end
            7'b1101111: begin // J-Type Instruction (jal)
                reg_write  = 1'b1;
                imm_src    = 3'b011;
                mem_write  = 1'b0;
                alu_src    = 1'b0;
                result_src = 2'b10;  // Save PC+4 to register!
                branch     = 1'b0;
                jump       = 1'b1;
                alu_op     = 2'b00;
            end
            7'b0010011: begin // I-Type Arithmatic (addi, etc) 
                reg_write = 1'b1;
                imm_src = 3'b000;   
                mem_write = 1'b0;
                alu_src   = 1'b1;   // ALU uses the immediate, not rs2
                result_src = 2'b00;  // RegFile uses ALU output
                branch = 1'b0;
                jump = 1'b0;
                alu_op    = 2'b00;  // ALU should ADD
            end
        endcase
    end
    // 3. ALU Decoder
    always @(*) begin
        case (alu_op)
            2'b00: alu_control = 3'b000; // 'lw' and 'sw' always Add
            2'b01: alu_control = 3'b110; // beq always subtracts to check equality
            2'b10: begin // R-Type instructions
                // We combine funct7[5] and funct3 to uniquely identify the math operation
                case ({funct7[5], funct3})
                    4'b0000: alu_control = 3'b000; // add
                    4'b1000: alu_control = 3'b110; // sub
                    4'b0111: alu_control = 3'b001; // and
                    4'b0110: alu_control = 3'b010; // or
                    4'b0100: alu_control = 3'b100; // xor
                    default: alu_control = 3'b000;
                endcase
            end
            default: alu_control = 3'b000;
        endcase
    end
    assign pc_src = (branch & alu_zero) | jump;
endmodule