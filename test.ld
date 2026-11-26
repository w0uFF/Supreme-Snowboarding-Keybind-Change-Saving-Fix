SECTIONS {
 . = 0x48a000; .text : { keybinds.o(.text) }
 . = 0x48b000; .data : { keybinds.o(.data) }
 . = 0x8049000; .htext : { test.o(.text*) }
 . = 0x804b000; .hdata : { test.o(.data*) test.o(.rodata*) test.o(.bss*) *(COMMON) }
 /DISCARD/ : { *(.note*) *(.comment*) *(.eh_frame*) }
}
