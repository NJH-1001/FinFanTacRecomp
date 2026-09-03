# FinFanTacRecomp v0.1.0

Initial public owned-input setup release for **Final Fantasy Tactics**
(USA, `SCUS-94221`). Kits are provided for Windows x86-64, Linux x86-64,
macOS Apple Silicon and macOS Intel.

## Download and setup

Download the **FinFanTacRecomp-setup-0.1.0** ZIP for your platform and extract
the entire kit. Run `Final_Fantasy_Tactics_Recompiled.exe` on Windows or
`Final_Fantasy_Tactics_Recompiled` from a terminal on Linux/macOS. Select your
legally obtained USA Redump-style CUE file and choose **Generate and Rebuild**.
Reopen the same executable when the build finishes. Python 3 is required; the
wizard can obtain the supported compiler toolchain. OpenBIOS is included and
used by default.

This is an owned-input build kit, not a playable game download. It contains no
disc data, extracted game executable, generated game code, retail PlayStation
BIOS, memory cards, saves, captures or analysis databases. All game code is
generated locally from the player's matching disc.

## Highlights

- Optional **16:9 3D View** for battles and in-engine cutscenes; enable it in
  the launcher's Mods page. Standalone 2D screens and FMVs retain 4:3. Disabled
  by default and marked experimental.
- Corrected texture-coordinate artifacts, widescreen background seams,
  transition corners and missing terrain beneath the command-menu backdrop.
- Software rendering and OpenGL at 2x supersampling verified in opening scenes.
- SDL3 support for Switch, Switch 2-compatible, PS4, PS5 and Xbox controller
  families. The PowerA Advantage Wired Controller for Nintendo Switch 2
  (`20D6:A720`) was physically tested over USB and has an explicit mapping.
- Digital controller mode is locked and hybrid mode disabled. Other controller
  families, wireless modes, rumble, stick clicks and extra buttons remain
  unverified on physical hardware.
- WASD/arrows for direction, J/K/U/I for face buttons, Q/E for L1/R1, 1/3 for
  L2/R2, Enter for Start and Backspace for Select. Circle confirms: K, Nintendo
  A, PlayStation Circle, or Xbox B.

## Verification and limits

- Native OpenBIOS LLE boot, title/menu, character creation, church scenes and
  first-battle movement, attacks and command menus were verified locally.
- All 58 enabled emitter tests pass; three upstream-disabled tests remain
  unchanged. Five focused renderer tests pass, including 116 procedural Beetle
  raster comparisons.
- The public setup executable is the same data-free host used for the verified
  rendering-fix3 package. This release refreshes configuration, documentation
  and source-publication tooling, including the final digital-controller lock.
- The ZIP passed private-data, source/configuration and archive-integrity audits;
  the extracted setup host passes its Windows DLL-loading smoke check.
- Extended gameplay, game completion, save/load round trips, live Vulkan parity,
  Linux/macOS gameplay, separate Windows 10/11 systems and AMD hardware are not
  yet verified. Linux and macOS setup hosts are native-runner smoke tested.

See the repository README for setup, controller compatibility and 16:9 details.
The accompanying `.sha256` file identifies the exact setup archive.
