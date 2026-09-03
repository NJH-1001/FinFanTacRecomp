# Final Fantasy Tactics Recompiled

An unofficial, noncommercial PSXRecomp compatibility project for **Final Fantasy
Tactics** (USA, `SCUS-94221`), also called **FinFanTacRecomp**.

**[Download the latest Windows setup kit](https://github.com/NJH-1001/FinFanTacRecomp/releases/latest)**

Releases are **owned-input setup kits**: you supply your legally obtained disc
and generate the playable executable locally. No disc data, extracted game
executable, generated game code, retail PlayStation BIOS, saves, captures, or
analysis databases are included. OpenBIOS is included and used by default.

## Supported target

- Windows 10 or 11, x86-64, Intel or AMD processor
- Final Fantasy Tactics (USA), `SCUS-94221`
- Matching Redump-style CUE/BIN disc dump (data track MD5: `b156ba386436d20fd5ed8d37bab6b624`)
- OpenBIOS with recompiled LLE execution
- Keyboard and SDL3-compatible controllers

## Using a release kit

1. Download `FinFanTacRecomp-setup-0.1.0-windows-x64.zip` from
   [Releases](https://github.com/NJH-1001/FinFanTacRecomp/releases).
2. Extract the entire ZIP to a writable folder outside `Program Files`.
3. Run `Final_Fantasy_Tactics_Recompiled.exe`.
4. Select your legally obtained USA CUE file, then choose **Generate and Rebuild**.
   Game code is generated and compiled only on your computer.
5. Reopen the same executable after the build finishes. It starts the locally
   built game from `build-release/`.

The initial build requires Python 3 and a compatible CMake/Ninja/Clang toolchain;
the setup wizard can download its supported toolchain. Keep the extracted kit
together. See `README-SETUP.txt` inside the ZIP for setup details. Connect your
controller before launch and review Player 1's device and bindings in the launcher.

## Optional enhancements

### 16:9 3D View

Enable **16:9 3D View** in the launcher's **Mods** page before starting the game.
It reveals additional scenery in battles and in-engine 3D cutscenes. Standalone
2D screens and FMVs retain 4:3 presentation, and the battle interface keeps its
authored proportions rather than being stretched.

The option is disabled by default and marked experimental. The opening church,
first battle, four camera rotations, scene fades, battle-condition splash and
command-menu backdrop have been checked. Later maps still need broader testing.

### Rendering and supersampling

Software rendering is the default. **OpenGL with 2x supersampling** has also
been verified in the opening scenes and first battle. This release includes
corrections for the comb-like texture edges, background-gradient seams,
transition corners and terrain disappearing beneath the widened menu backdrop.
Vulkan has not received the same live scene verification.

## Controller compatibility

Player 1 selects a connected controller automatically. The guest controller is
locked to **digital mode**, with hybrid mode disabled; modern controllers are
mapped to the original PlayStation buttons. Bindings remain configurable.

| Controller family | Compatibility and verification |
|---|---|
| Nintendo Switch | SDL3 support; physical testing pending |
| Nintendo Switch 2-compatible | **PowerA Advantage Wired Controller for Nintendo Switch 2** (`20D6:A720`) tested over USB; explicit mapping included |
| PlayStation 4 / DualShock 4 | SDL3 support; physical testing pending |
| PlayStation 5 / DualSense | SDL3 support; physical testing pending |
| Xbox | SDL3 support; physical testing pending |

The PowerA test does not establish compatibility with every Switch 2 controller.
Bluetooth/wireless operation, rumble, stick clicks and extra rear buttons remain
unverified. The measured PowerA mapping intentionally omits unverified extra buttons.

## Controls

**FFT USA uses Circle to confirm**: press **K** on the keyboard, **A** on a
Nintendo controller, **Circle** on PlayStation, or **B** on Xbox.

| PlayStation input | Keyboard | Switch / Switch 2 | PS4 / PS5 | Xbox |
|---|---|---|---|---|
| D-pad | WASD or arrows | D-pad / left stick | D-pad / left stick | D-pad / left stick |
| Cross / Circle | J / K | B / A | Cross / Circle | A / B |
| Square / Triangle | U / I | Y / X | Square / Triangle | X / Y |
| L1 / R1 | Q / E | L / R | L1 / R1 | LB / RB |
| L2 / R2 | 1 / 3 | ZL / ZR | L2 / R2 | LT / RT |
| Start / Select | Enter / Backspace | Plus / Minus | Options / Share or Create | Menu / View |

These are positional mappings. If the controller is not responding, check that
Player 1 is using the connected gamepad and that only one game instance is running.

## Building from the repository

The Git repository uses two pinned source submodules and a reviewed framework
patch. Use Git, Python 3.11 or newer, and a MinGW-w64 GCC/CMake/Ninja toolchain.
The development helper defaults to `C:/msys64/mingw64/bin`; use `--toolchain`
for another installation. Network access is needed for initial dependencies.

```powershell
git clone https://github.com/NJH-1001/FinFanTacRecomp.git
cd FinFanTacRecomp
python tools/bootstrap.py
python tools/windows.py check
python tools/windows.py generate --disc "C:/path/to/Final Fantasy Tactics (USA).cue"
python tools/windows.py build
python tools/windows.py run --disc "C:/path/to/Final Fantasy Tactics (USA).cue"
```

The development build is `build-windows/Final_Fantasy_Tactics_Recompiled.exe`
(RelWithDebInfo). Bootstrap verifies the upstream pins and applies the checked
patch without resetting local edits. Release kits already contain the prepared
SDK; use their launcher rather than these Git-checkout commands.

Never commit `disc/`, `generated/`, retail BIOS files, memory cards, save states,
captures, logs, or Ghidra projects. See [PUBLICATION.md](PUBLICATION.md).

## Status and reporting

Local verification covers disc validation, native OpenBIOS boot, title/menu,
character creation, church scenes, first-battle movement and attacks, the command
menu, the PowerA controller and keyboard input. This is **not a full-game
completion claim**. Extended play, save/load round trips, separate Windows 10/11
systems and AMD hardware remain outside the verified scope.

All 58 enabled emitter tests and five focused renderer tests pass, including
116 procedural Beetle raster comparisons. See [VERIFICATION.md](VERIFICATION.md)
and [RENDERING.md](RENDERING.md) for the detailed evidence and limits.

[Report a problem](https://github.com/NJH-1001/FinFanTacRecomp/issues) with the
release version, renderer, supersampling level, enabled mods, controller model
and reproduction steps. Do not attach disc data, generated game code, memory
cards, saves, captures or analysis databases to this repository.

## Licensing and trademarks

Framework and third-party components retain their licenses; see
[THIRD_PARTY.md](THIRD_PARTY.md). Game-owned files do not currently assert a new
license. Names and trademarks identify compatibility only. This project is not
affiliated with or endorsed by Square Enix, Sony Interactive Entertainment, or
the original developers and publishers.
