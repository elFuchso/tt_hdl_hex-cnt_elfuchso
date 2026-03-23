/*
 * Copyright (c) 2026 Maximilian Fuchs
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_hexcnt_elfuchso (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // Pin assignment for clarity
    wire up_down = ui_in[0];    // 1 for Up, 0 for Down
    wire mode_hex = ui_in[1];   // 1 for Hex (0-F), 0 for Decimal (0-9)

    // assign unused pins
    assign uio_out = 0;
    assign uio_oe  = 0;
    
    // Internal signals
    reg [23:0] clk_divider;  // To slow down the ~10MHz clock
    reg [3:0]  counter;      // The 4-bit value to display

    // Clock divider: 1.6M cycles for hardware (~6Hz), 
    // but only 16 cycles for simulation so tests run fast.
    wire tick;
    `ifdef SIM
        assign tick = (clk_divider == 24'd16); 
    `else
        assign tick = (clk_divider == 24'd1600000);
    `endif

    always @(posedge clk) begin
        if (!rst_n) begin
            clk_divider <= 0;
            counter <= 0;
        end else begin
            clk_divider <= clk_divider + 1;
            
            if (tick) begin
                clk_divider <= 0;
                
                if (up_down) begin
                    // COUNT UP LOGIC
                    if (mode_hex)
                        counter <= counter + 1; // Natural overflow at 15
                    else
                        counter <= (counter >= 9) ? 0 : counter + 1;
                end else begin
                    // COUNT DOWN LOGIC
                    if (mode_hex)
                        counter <= counter - 1; // Natural underflow at 0
                    else
                        counter <= (counter == 0) ? 4'd9 : counter - 1;
                end
            end
        end
    end

    // 7-segment decoder
    // Segments:   a b c d e f g
    // Pin order: uo[0] to uo[6]
    reg [6:0] segments;
    always @(*) begin
        case (counter)
            4'h0: segments = 7'b0111111;
            4'h1: segments = 7'b0000110;
            4'h2: segments = 7'b1011011;
            4'h3: segments = 7'b1001111;
            4'h4: segments = 7'b1100110;
            4'h5: segments = 7'b1101101;
            4'h6: segments = 7'b1111101;
            4'h7: segments = 7'b0000111;
            4'h8: segments = 7'b1111111;
            4'h9: segments = 7'b1101111;
            4'hA: segments = 7'b1110111;
            4'hB: segments = 7'b1111100;
            4'hC: segments = 7'b0111001;
            4'hD: segments = 7'b1011110;
            4'hE: segments = 7'b1111001;
            4'hF: segments = 7'b1110001;
            default: segments = 7'b0000000;
        endcase
    end

    // Assign segments to outputs. uo[7] is the decimal point (mode indicator)
    assign uo_out[6:0] = segments;
    assign uo_out[7] = mode_hex; // DP lights up if we are in Hex mode

    wire _unused = &{ui_in[7:2], ena, rst_n, 1'b0};

endmodule
