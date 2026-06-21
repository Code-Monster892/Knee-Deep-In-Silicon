.global _start

.section .init
_start:
    # Initialize the Stack Pointer dynamically from the linker script
    la sp, __stack_top

    # Clear the BSS segment (Initialize global variables to zero)
    la t0, __bss_start
    la t1, __bss_end
    bgeu t0, t1, 2f
1:
    sw zero, 0(t0)
    addi t0, t0, 4
    bltu t0, t1, 1b
2:

    # Set argc and argv to 0 so C programs don't try to parse garbage
    li a0, 0
    li a1, 0

    # Call the main() function in our C code
    call main

    # If main() ever returns, get trapped in an infinite loop
3:  j 3b
