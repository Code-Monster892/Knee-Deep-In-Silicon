module signext (
    input  logic [31:0] instr,
    input  logic [1:0]  imm_src, 
    
    output logic [31:0] imm_ext
);

    always @(*) begin 
        case (imm_src)
            2'b00 : imm_ext = {{20{instr[31]}}, instr[31:20]}; // I-Type
            2'b01 : imm_ext = {{20{instr[31]}}, instr[31:25], instr[11:7]}; // S-Type
            2'b10 : imm_ext = {{20{instr[31]}}, instr[7], instr[30:25], instr[11:8], 1'b0}; // B-Type
            default: imm_ext = 32'b0; 
        endcase
    end

endmodule