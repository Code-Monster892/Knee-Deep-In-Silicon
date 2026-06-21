.global _start

.section .init
_start:
    # Initialize the Stack Pointer to the very top of our 8MB RAM!
    li sp, 0x00800000

    # Call the main() function in our C code
    call main

    # If main() ever returns, get trapped in an infinite loop
1:  j 1b
