# Rebuild from source

On a Linux host with GNU binutils, Python 3 and the original Supreme.exe from SupremeLight_9617efe6.zip:

```sh
as --32 keybinds.s -o keybinds.o
ld -m elf_i386 -T layout.ld keybinds.o -o keybinds.elf
objcopy -O binary --only-section=.text keybinds.elf code.bin
objcopy -O binary --only-section=.data keybinds.elf data.bin
python3 patch.py /path/to/original/Supreme.exe /path/to/patched/Supreme.exe
python3 verify.py /path/to/original/Supreme.exe /path/to/patched/Supreme.exe
```

Optional: assemble and run the actual load/save routines against mocked Win32 APIs on a host supporting 32-bit Linux executables:

```sh
gcc -m32 -ffreestanding -fno-pic -fno-pie -fno-stack-protector -O2 -c test.c -o test.o
ld -m elf_i386 -e _start -T test.ld keybinds.o test.o -o test.elf
./test.elf
```

Exit code 0 means all 16 mock assertions passed; nonzero identifies the failed assertion. This does not substitute for testing on Windows.
