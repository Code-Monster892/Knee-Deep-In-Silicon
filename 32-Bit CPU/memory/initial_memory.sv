module memory #(
    parameter WORDS = 64
) (
    input  logic        clk,
    input  logic        rst_n,
    
    // Data Port
    input  logic        we,
    input  logic [31:0] address,
    input  logic [31:0] write_data,
    output logic [31:0] read_data,
    
    // Instruction Port
    input  logic [31:0] pc_address,
    output logic [31:0] instruction
);

    // Memory array
    reg [31:0] mem [0:WORDS-1];

    // Write logic (Synchronous)
    always @(posedge clk) begin
        if (rst_n == 1'b0) begin
            for (int i = 0; i < WORDS; i++) begin
                mem[i] <= 32'b0;  
            end
        end
        else if (we) begin
            if (address[1:0] == 2'b00) begin 
                mem[address[31:2]] <= write_data;
            end
        end
    end

    // Read logic (Asynchronous/Combinational)
    always @(*) begin
        read_data = mem[address[31:2]]; 
        instruction = mem[pc_address[31:2]];
    end

endmodule
