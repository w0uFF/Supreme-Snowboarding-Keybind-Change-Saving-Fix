SECTIONS {
 . = 0x48a000; .text : { *(.text) }
 . = 0x48b000; .data : { *(.data) }
 /DISCARD/ : { *(.note*) *(.comment*) }
}
