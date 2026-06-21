#include "Vcpu.h"
#include "verilated.h"
#include <SDL2/SDL.h>
#include <iostream>
#include <queue>

#define SCREEN_WIDTH 320
#define SCREEN_HEIGHT 200

// DOOM Keyboard mappings
#define DOOM_KEY_RIGHTARROW	0xae
#define DOOM_KEY_LEFTARROW	0xac
#define DOOM_KEY_UPARROW	0xad
#define DOOM_KEY_DOWNARROW	0xaf
#define DOOM_KEY_ESCAPE		27
#define DOOM_KEY_ENTER		13
#define DOOM_KEY_TAB		9
#define DOOM_KEY_BACKSPACE	127
#define DOOM_KEY_RCTRL		(0x80+0x1d)
#define DOOM_KEY_LALT		(0x80+0x38)

unsigned char map_sdl_to_doom_key(SDL_Keycode sym) {
    switch(sym) {
        case SDLK_RIGHT: return DOOM_KEY_RIGHTARROW;
        case SDLK_LEFT: return DOOM_KEY_LEFTARROW;
        case SDLK_UP: return DOOM_KEY_UPARROW;
        case SDLK_DOWN: return DOOM_KEY_DOWNARROW;
        case SDLK_ESCAPE: return DOOM_KEY_ESCAPE;
        case SDLK_RETURN: return DOOM_KEY_ENTER;
        case SDLK_TAB: return DOOM_KEY_TAB;
        case SDLK_BACKSPACE: return DOOM_KEY_BACKSPACE;
        case SDLK_RCTRL:
        case SDLK_LCTRL: return DOOM_KEY_RCTRL;
        case SDLK_RALT:
        case SDLK_LALT: return DOOM_KEY_LALT;
        default:
            if (sym >= SDLK_a && sym <= SDLK_z) return sym - SDLK_a + 'a';
            if (sym >= SDLK_0 && sym <= SDLK_9) return sym - SDLK_0 + '0';
            if (sym == SDLK_SPACE) return ' ';
            if (sym == SDLK_COMMA) return ',';
            if (sym == SDLK_PERIOD) return '.';
            if (sym == SDLK_MINUS) return '-';
            if (sym == SDLK_EQUALS) return '=';
            return 0;
    }
}

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);
    Vcpu* dut = new Vcpu;

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) < 0) {
        std::cerr << "SDL could not initialize! SDL_Error: " << SDL_GetError() << std::endl;
        return -1;
    }

    SDL_Window* window = SDL_CreateWindow("RISC-V DOOM - Bare Metal",
                                          SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
                                          SCREEN_WIDTH, SCREEN_HEIGHT, SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE);
    
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    SDL_RenderSetLogicalSize(renderer, SCREEN_WIDTH, SCREEN_HEIGHT);
    SDL_Texture* texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888, 
                                             SDL_TEXTUREACCESS_STREAMING, 
                                             SCREEN_WIDTH, SCREEN_HEIGHT);

    uint32_t* pixels = new uint32_t[SCREEN_WIDTH * SCREEN_HEIGHT];
    for(int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) pixels[i] = 0xFF000000;

    dut->clk = 0;
    dut->rst_n = 0;

    bool quit = false;
    SDL_Event e;
    
    std::cout << "Starting Bare-Metal Simulation with SDL2 Video..." << std::endl;

    int cycles = 0;
    std::queue<uint32_t> key_queue;
    uint32_t start_time = SDL_GetTicks();
    
    while (!quit) {
        while (SDL_PollEvent(&e) != 0) {
            if (e.type == SDL_QUIT) quit = true;
            else if (e.type == SDL_KEYDOWN || e.type == SDL_KEYUP) {
                unsigned char doom_key = map_sdl_to_doom_key(e.key.keysym.sym);
                if (doom_key != 0) {
                    int pressed = (e.type == SDL_KEYDOWN) ? 1 : 0;
                    uint32_t event = (1 << 16) | (pressed << 8) | doom_key; // valid=1, pressed=bit 8, key=bits 0-7
                    key_queue.push(event);
                }
            }
        }

        if (cycles == 2) dut->rst_n = 1;

        // PHASE 1: Combinational logic (clk = 0)
        dut->clk = 0;
        
        // Feed MMIO read data BEFORE evaluating combinational logic
        dut->mmio_read_data = 0;
        if (dut->mmio_read_en) {
            if (dut->mmio_address == 0x02500000) {
                dut->mmio_read_data = SDL_GetTicks() - start_time;
            } else if (dut->mmio_address == 0x02600000) {
                if (!key_queue.empty()) {
                    dut->mmio_read_data = key_queue.front();
                    key_queue.pop();
                } else {
                    dut->mmio_read_data = 0;
                }
            }
        }

        dut->eval();

        // Handle MMIO Writes (triggered by combinational logic of current instruction)
        if (dut->mmio_we) {
            if (dut->mmio_address >= 0x02000000 && dut->mmio_address < 0x02000000 + (SCREEN_WIDTH * SCREEN_HEIGHT * 4)) {
                uint32_t offset = (dut->mmio_address - 0x02000000) / 4;
                pixels[offset] = dut->mmio_write_data; 
            } else if (dut->mmio_address == 0x02700000) {
                // DOOM signaled that the frame is complete! Update SDL texture.
                SDL_UpdateTexture(texture, NULL, pixels, SCREEN_WIDTH * sizeof(uint32_t));
                SDL_RenderClear(renderer);
                SDL_RenderCopy(renderer, texture, NULL, NULL);
                SDL_RenderPresent(renderer);
            } else if (dut->mmio_address == 0x10000000) {
                std::putchar((char)dut->mmio_write_data);
                std::fflush(stdout);
            }
        }

        // PHASE 2: Sequential logic (clk = 1)
        dut->clk = 1;
        dut->eval();

        cycles++;
    }

    std::cout << "Shutting down..." << std::endl;
    
    delete[] pixels;
    SDL_DestroyTexture(texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    delete dut;

    return 0;
}