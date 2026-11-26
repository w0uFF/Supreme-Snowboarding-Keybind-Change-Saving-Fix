# Supreme Snowboarding — Keyboard Persistence Fix v0.1 (experimental)

Community compatibility patch prepared for the exact `Supreme.exe` included in `SupremeLight_9617efe6.zip`, with the intention of preserving compatibility with Display Config 1.8.0. Not an official release or endorsed by launcher maintainers.

## Install

1. Close the game and launcher. Back up `Supreme.exe` from your installed game folder (the folder containing `Saved_Data`).
2. Replace it with the `Supreme.exe` in this archive. Only use this binary with the specified SupremeLight build. To check its version and create a backup automatically instead, run `Install.ps1` in PowerShell, supplying your game folder when prompted. The installer refuses a different SHA-256. No administrator privileges should be necessary in a user-writable game folder.
3. Keep your existing Display Config 1.8.0 `Display_Config.exe` and `winmm.dll` unchanged.
4. Open Display Config normally, launch the game, change the controls inside the game, and return to the main menu.
5. Confirm that `Saved_Data/Keyboard_Bindings.bin` appears. Close and relaunch the game through the launcher.

The new binary settings file is generated automatically after a binding differs from the loaded/default values. Do not copy the default `Control_Config.txt` over it; that separate legacy file is intentionally untouched.

## Manual acceptance tests (not yet run)

- Launch the patched game with the existing Display Config 1.8.0 files. Verify it reaches the main menu without an error.
- Change Jump and Cant to two distinct keys and change at least one other action. Confirm `Saved_Data/Keyboard_Bindings.bin` is 36 bytes. Close and relaunch; verify the menu shows the new keys and they work in a race. Check all eight actions if possible.
- Change another key, leave the menu, and relaunch again. Verify the newest change persists without losing prior settings.
- Rebind one key back to its original value. Verify this is also retained after relaunch.
- With the game closed, temporarily rename the new file and relaunch: the original built-in bindings should return. Restore the file to recover your custom bindings.
- If a change does not persist, check whether the file exists, its timestamp, and the launcher/game working directory. Try a user-writable folder and ensure the launcher has not replaced `Supreme.exe`. A launcher file-overlay interaction is also possible and is not yet validated.

## Rollback

Close game and launcher; restore your original `Supreme.exe` (or `Supreme.exe.original-keybind-fix` if using the installer). The new binary keybind file may be left in place for a future reinstall or deleted. Existing save files, scores, launcher settings and libraries are not deliberately changed by the patch.

## Technical diagnosis

The supplied original `Saved_Data/Control_Config.txt` contains `Keyboard` only. In `Supreme.exe`, the legacy I/O for that file reads/writes a string for device selection. The eight gameplay keycodes are hard-coded at startup (`0x448560` onwards). `Main_Menu.dll` updates the in-memory `Control_Key` objects (`0x10016a64` at its preferred base), with the code at object offset `0x14`. The game copies them into its runtime array (`0x44827f` onwards). No individual keycode serialization was identified in the inspected paths. The original constructor and menu update paths are therefore targeted instead of rewriting the community launcher.

The patch adds a small RX code section and a separate RW section. The three version-specific jump sites are `0x448598` (load before menu key objects are constructed), `0x453887` (save after the original keyboard menu event returns), and `0x44cd8b` (normal cleanup fallback before the keyboard array and objects are freed). Registers and flags are preserved around added calls. New Win32 file APIs are imported separately without moving the original IAT entries.

File format: 36 bytes, four ASCII bytes `SKB1` followed by eight little-endian uint32 codes in original gameplay-array order: Cant, Jump, Trick, Left, Right, Forward, Backward, Menu. The first two UI entries use the reverse order, handled explicitly by the patch. All eight codes must be 0–255. Missing, invalid, or truncated files leave the built-in defaults intact. Writes are skipped if bindings have not changed; changed bindings are written to a temporary file then replaced via `MoveFileExA`. A failed write does not update the in-memory saved baseline, allowing retry on another keyboard event or cleanup.

## Validation / limitations

See `verification.txt`. Static PE, import, original byte preservation, and reconstruction checks passed. The freestanding 32-bit mocked API test harness compiles, but this environment cannot execute 32-bit binaries; the actual Windows game and launcher were not run. The patch is therefore an experimental candidate, not a confirmed working Windows release. The exact launcher authorship and a launcher-side cause were not established. The patch does not change rendering, gameplay logic, timings, or the launcher itself.

Source and reproducible build instructions are in `source/`. The supplied EXE is unsigned, like a typical local binary modification. Do not bypass security warnings blindly; source and hashes are included for inspection.
