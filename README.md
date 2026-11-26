# Supreme Snowboarding — Keyboard Persistence Fix

![Version](https://img.shields.io/badge/version-v0.1-blue)
![Status](https://img.shields.io/badge/status-experimental-orange)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Testing](https://img.shields.io/badge/runtime%20test-passed-brightgreen)

An unofficial community patch for **Supreme Snowboarding** that fixes keyboard bindings not being saved between game sessions.

Customize your controls directly in the game and keep them automatically, even after restarting.

## Download

**[Download the latest release](https://github.com/w0uFF/Supreme-Snowboarding-Keybind-Change-Saving-Fix/releases)**

> **Experimental release:** The patch has been successfully tested in-game. Custom keyboard bindings persist after restarting, and no issues were encountered during initial gameplay testing. Long-term stability has not yet been extensively tested.

## Features

- Automatically saves custom keyboard bindings.
- Restores saved bindings when launching the game.
- Supports all eight gameplay controls.
- No additional application or manual configuration required.
- Designed for compatibility with Display Config 1.8.0.
- Preserves the original keyboard configuration system.
- No intentional changes to gameplay, physics, rendering or timing.

## Compatibility

| Component | Status |
|---|---|
| SupremeLight `9617efe6` | Supported target build |
| Display Config 1.8.0 | Targeted compatibility |
| Windows runtime | Initial testing passed |
| Keyboard persistence | Confirmed working |
| In-game gameplay | Tested successfully |
| Extended gameplay sessions | Not extensively tested |
| Other game builds | Untested |

## Installation

### Automatic installation (recommended)

1. Download both  `Supreme.exe` and `Install.ps1`.
2. Close the game and launcher.
3. Run `Install.ps1` using PowerShell.
4. Select your Supreme Snowboarding installation folder.
5. Launch the game normally.

The installer automatically verifies the original executable's SHA-256 hash and creates a backup. Unsupported executable versions are rejected.

### Manual installation

1. Download `Supreme.exe`.
2. Close the game and launcher.
3. Replace `Supreme.exe` in your game directory with the patched executable.
4. Keep your existing `Display_Config.exe` and `winmm.dll` unchanged.
5. Launch the game normally.

The patch targets the executable included in `SupremeLight_9617efe6.zip`.

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

## Usage

1. Launch Supreme Snowboarding.
2. Open the in-game controls menu.
3. Customize your keyboard bindings.
4. Return to the main menu.

That's it. Your keyboard bindings are automatically saved and restored when you restart the game.

### Settings file

The patch automatically generates:

`Saved_Data/Keyboard_Bindings.bin`

This file stores your custom keyboard bindings independently of the original `Control_Config.txt`, which remains unchanged.

To restore the game's default keyboard bindings, close the game and delete or rename `Keyboard_Bindings.bin`.

You can also copy this file between compatible patched installations to transfer your custom controls.

## Testing and validation

### Confirmed

- [x] Static executable verification.
- [x] Successful game launch on Windows.
- [x] In-game keyboard customization.
- [x] Keyboard bindings retained after restarting the game.
- [x] Successful gameplay with custom keyboard bindings.
- [x] No issues observed during initial gameplay testing.

### Additional testing

- [ ] Extended gameplay sessions.
- [ ] Exhaustive testing of all eight controls.
- [ ] Multiple consecutive keyboard configuration changes.
- [ ] Broader community mod compatibility.
- [ ] Launcher file-overlay compatibility.
- [ ] Automated 32-bit test harness execution.

The patch is already usable, but additional community testing is welcome to identify potential edge cases or long-term stability issues.

## Troubleshooting

If your keyboard bindings are not saved:

- Verify that `Saved_Data/Keyboard_Bindings.bin` exists.
- Check that the file is exactly 36 bytes.
- Ensure your game directory is writable.
- Verify that the launcher has not replaced the patched executable.
- Confirm that you are using the supported game build.

## Uninstallation

Close the game and restore your original `Supreme.exe`.

If you used the automatic installer, the original executable is available as:

`Supreme.exe.original-keybind-fix`

The generated keyboard settings file can be kept for future use or deleted.

## Technical details

<details>
<summary>Root cause analysis</summary>

The original game stores input-device selection in `Saved_Data/Control_Config.txt`, but no individual keyboard-binding serialization was identified in the inspected execution paths.

The eight gameplay keycodes are hard-coded during startup. Changes made through the controls menu update in-memory objects and the runtime keyboard array, but are not retained between game sessions.

This patch introduces persistent keyboard serialization by extending the original initialization, menu update and cleanup routines.

No modifications to the Community Launcher itself are required.

</details>

<details>
<summary>Engine addresses and implementation</summary>

| Address | Purpose |
|---|---|
| `0x448560` | Original keyboard initialization |
| `0x44827F` | Runtime keyboard array |
| `0x10016A64` | Main_Menu.dll control objects at preferred base |
| `0x448598` | Custom binding load hook |
| `0x453887` | Post-menu-event save hook |
| `0x44CD8B` | Cleanup fallback save hook |

The keycode field is located at offset `0x14` within the `Control_Key` object.

The patch introduces separate RX and RW sections, preserves registers and flags around added calls, and imports additional Win32 file APIs without relocating the original IAT entries.

All addresses are specific to the targeted executable.

</details>

<details>
<summary>Keyboard settings file format</summary>

**File:** `Saved_Data/Keyboard_Bindings.bin`

**Size:** 36 bytes

**Byte order:** Little-endian

| Offset | Type | Field |
|---|---|---|
| `0x00` | 4 ASCII bytes | `SKB1` |
| `0x04` | uint32 | Cant |
| `0x08` | uint32 | Jump |
| `0x0C` | uint32 | Trick |
| `0x10` | uint32 | Left |
| `0x14` | uint32 | Right |
| `0x18` | uint32 | Forward |
| `0x1C` | uint32 | Backward |
| `0x20` | uint32 | Menu |

All keycodes must be within the range 0–255.

The difference between the original gameplay-array order and menu order is handled explicitly.

Missing, invalid or truncated files leave the original built-in bindings intact.

Settings are written only when bindings change. A temporary file and `MoveFileExA` are used to replace the saved configuration.

Failed writes leave the previous saved baseline unchanged, allowing subsequent save attempts.

</details>

## Source code and reproducibility

The release includes source code, reproducible build instructions and static verification results.

| File / Directory | Description |
|---|---|
| `Supreme.exe` | Patched executable |
| `Install.ps1` | Version-checked installer |
| `source/` | Source code and build instructions |
| `verification.txt` | Static verification results |

The modified executable is unsigned. Source code and hashes are provided for transparency and independent verification.

## Community resources

### [Supreme Snowboarding — Game Download](https://www.speedrun.com/Supreme_snowboarding/resources/34dpx)

Essential game download. A cleaned-up CD version recommended by the speedrunning community for its stability.

### [Supreme Snowboarding — Community Launcher](https://codeberg.org/SupremeSnowboardingCommunity/Launcher/src/branch/main/README.md)

A continually evolving community launcher featuring:

- Mod management.
- 4K resolution support.
- Easy skin customization.
- Music management.
- Community mod browsing and downloading.

## Feedback and contributions

Community testing, bug reports and technical contributions are welcome.

If you encounter an issue, please report it through the [GitHub Issues](https://github.com/w0uFF/Supreme-Snowboarding-Keybind-Change-Saving-Fix/issues) page.

Include your game version, launcher version and steps to reproduce the issue whenever possible.

## Development & AI Transparency

This patch was developed with the assistance of OpenAI's ChatGPT, which contributed to reverse engineering, technical analysis, code implementation, static verification and documentation.

The patched executable was manually tested on Windows by the project maintainer, confirming successful gameplay and keyboard binding persistence across game restarts.

While no issues were observed during initial gameplay testing, extended sessions and broader compatibility testing remain necessary to assess long-term stability.

Source code, technical documentation and reproducible build instructions are provided to encourage transparency, independent verification and community contributions.

AI-assisted development does not replace human testing, technical review or community feedback.

## Disclaimer

This is an independent community modification, not an official game update or an endorsed Community Launcher release.

---

**Made for the Supreme Snowboarding community, with the assistance of ChatGPT.**
