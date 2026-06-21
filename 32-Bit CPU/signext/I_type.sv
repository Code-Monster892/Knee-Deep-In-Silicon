module signext (
    input  logic [31:0] instr,
    input  logic [1:0]  imm_src, 
    
    output logic [31:0] imm_ext
);

    always @(*) begin 
        case (imm_src)
            2'b00 : imm_ext = {{20{instr[31]}}, instr[31:20]}; // I-Type
            default: imm_ext = 32'b0; 
        endcase
    end

endmodule