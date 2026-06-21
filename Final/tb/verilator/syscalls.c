#include <sys/stat.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdint.h>

extern char __heap_start[];
extern char __heap_end[];
static char *heap_ptr = __heap_start;

void *_sbrk(intptr_t increment) {
    char *prev_heap_ptr = heap_ptr;
    if (heap_ptr + increment > __heap_end) {
        return (void *)-1; // Out of memory
    }
    heap_ptr += increment;
    return prev_heap_ptr;
}

static int uart_putc(char c, FILE *file) {
    volatile char *uart = (volatile char *)0x10000000;
    *uart = c;
    return c;
}

static FILE __stdio = FDEV_SETUP_STREAM(uart_putc, NULL, NULL, _FDEV_SETUP_WRITE);
FILE * const stdout = &__stdio;
FILE * const stderr = &__stdio;
FILE * const stdin = &__stdio;

#include <sys/stat.h>

int open(const char *pathname, int flags, int mode) { 
    printf("[DEBUG] open(%s)\n", pathname);
    return -1; 
}
int close(int fd) { return -1; }
int read(int fd, void *buf, int count) { return 0; }
int write(int fd, const void *buf, int count) {
    const char *cbuf = (const char *)buf;
    volatile char *uart = (volatile char *)0x10000000;
    for (int i = 0; i < count; i++) {
        *uart = cbuf[i];
    }
    return count;
}
int lseek(int fd, int offset, int whence) { return 0; }
int unlink(const char *pathname) { return -1; }
int stat(const char *pathname, struct stat *st) { return -1; }
int fstat(int fd, struct stat *st) { return -1; }
int isatty(int fd) { return 1; }
int mkdir(const char *pathname, mode_t mode) { return -1; }
int rename(const char *oldpath, const char *newpath) { return -1; }

void _exit(int status) {
    while (1);
}

int _kill(int pid, int sig) {
    return -1;
}

int _getpid(void) {
    return 1;
}
