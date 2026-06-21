OUTPUT_ARCH( "riscv" )
ENTRY( _start )

MEMORY {
    ram : ORIGIN = 0x00000000, LENGTH = 0x01000000 /* 16MB of RAM */
}

SECTIONS {
    .text : {
        *(.init)
        *(.text*)
    } > ram
    .rodata : {
        *(.rodata*)
        *(.srodata*)
    } > ram
    .data : {
        *(.data*)
        *(.sdata*)
    } > ram
    .bss : {
        PROVIDE(__bss_start = .);
        *(.bss*)
        *(.sbss*)
        *(COMMON)
        . = ALIGN(8);
        PROVIDE(__bss_end = .);
        PROVIDE(end = .);
        PROVIDE(_end = .);
        PROVIDE(__end = .);
        PROVIDE(__end__ = .);
        PROVIDE(__heap_start = .);
    } > ram

    PROVIDE(__heap_end = ORIGIN(ram) + LENGTH(ram));
    PROVIDE(__stack_top = ORIGIN(ram) + LENGTH(ram));
}
