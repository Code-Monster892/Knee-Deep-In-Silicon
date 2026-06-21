#define SCREEN_WIDTH 320
#define SCREEN_HEIGHT 200
#define VIDEO_BASE 0x00400000

int main() {
    // Create a pointer that points directly to our magical MMIO Video address
    volatile unsigned int *vram = (volatile unsigned int *)VIDEO_BASE;
    
    // Fill the screen with Red pixels
    for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
        vram[i] = 0xFFFF0000; // Hex code for Solid Red (ARGB format)
    }

    // Enter an infinite loop so the CPU doesn't crash into garbage memory
    while (1) {}
    
    return 0;
}