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

    // --- Pre-load Firmware ---
    initial begin
        $readmemh("firmware.hex", mem);
    end
    // --- Write logic (Synchronous) ---
    always @(posedge clk) begin
        // (We removed the rst_n wiping loop! RAM retains its data on reset.)
        if (we && rst_n) begin
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
