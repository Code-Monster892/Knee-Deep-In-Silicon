#include "doomgeneric/doomgeneric/doomgeneric.h"
#include <stdint.h>

#define MMIO_VIDEO_BASE    0x02000000
#define MMIO_TIMER_BASE    0x02500000
#define MMIO_KEYBOARD_BASE 0x02600000

void DG_Init() {
    volatile char *uart = (volatile char *)0x10000000;
    const char *msg = "\n[DG_Init] Initializing Bare-Metal RISC-V Hardware...\n";
    while (*msg) { *uart = *msg++; }

    // Hardware is already initialized by the Verilator testbench.
}

void DG_DrawFrame() {
    // Copy the internal DOOM screen buffer to our memory-mapped video RAM
    volatile uint32_t* vram = (volatile uint32_t*)MMIO_VIDEO_BASE;
    uint32_t* src = DG_ScreenBuffer;
    
    // DOOMGENERIC_RESX * DOOMGENERIC_RESY pixels
    for (int i = 0; i < DOOMGENERIC_RESX * DOOMGENERIC_RESY; i++) {
        vram[i] = src[i];
    }

    // Tell the simulator to render the frame to SDL
    volatile uint32_t* flush = (volatile uint32_t*)0x02700000;
    *flush = 1;
}

void DG_SleepMs(uint32_t ms) {
    uint32_t start = DG_GetTicksMs();
    while (DG_GetTicksMs() - start < ms) {
        // Busy wait
    }
}

uint32_t DG_GetTicksMs() {
    // Read from our hardware timer MMIO register
    volatile uint32_t* timer = (volatile uint32_t*)MMIO_TIMER_BASE;
    return *timer;
}

int DG_GetKey(int* pressed, unsigned char* doomKey) {
    // Read from our hardware keyboard MMIO register
    volatile uint32_t* kb = (volatile uint32_t*)MMIO_KEYBOARD_BASE;
    uint32_t event = *kb;
    
    if (event & (1 << 16)) { // Bit 16 is the "valid" bit
        *pressed = (event >> 8) & 1; // Bit 8 is the "pressed" bit
        *doomKey = event & 0xFF;     // Bits 0-7 are the keycode
        return 1;
    }
    
    return 0; // No key event
}

void DG_SetWindowTitle(const char * title) {
    // We don't have a windowing system, so we ignore this.
}

// Entry point for bare metal
int main() {
    doomgeneric_Create(0, NULL);
    
    while (1) {
        doomgeneric_Tick();
    }
    
    return 0;
}
