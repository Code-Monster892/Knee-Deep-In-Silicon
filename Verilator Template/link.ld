OUTPUT_ARCH( "riscv" )
ENTRY( _start )

MEMORY {
    ram : ORIGIN = 0x00000000, LENGTH = 0x00800000 /* 8MB of RAM */
}

SECTIONS {
    .text : {
        *(.init)
        *(.text)
    } > ram
    .data : {
        *(.data)
    } > ram
    .bss : {
        *(.bss)
    } > ram
}
