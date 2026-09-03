# Verification - 2026-09-03

## Completed

Setup-package rebuild correction: the original rendering ZIP omitted the
project's `PSX_REWIND=OFF` default; only the development/setup build commands
supplied it. A plain launcher Release rebuild requested the absent
retcomm-rbengine dependency. The default now lives in CMakeLists.txt before the
framework include. Helper scripts no longer mask it with a duplicate override.

Verified the user's extracted project through the actual launcher CLI using
cmake-clang-v1 / Clang 22.1.8. The full Release build and five-package mod staging
completed. A second rebuild cleared only the cached option with `-UPSX_REWIND`;
the project default selected OFF and configure/link succeeded again. Existing
failed installs need their cached ON value cleared or set OFF once. This is a
build configuration correction; runtime and generated game code are unchanged.

- Read the framework CLAUDE.md and timing plans. Confirmed Ghidra MCP at localhost:8089 before game analysis.
- Disc matches Redump disc 55 (https://redump.info/disc/55): 541315152 bytes, 230151 Mode 2 sectors, CRC32 377f6510, MD5 b156ba386436d20fd5ed8d37bab6b624, SHA1 2b5d4db3229cdc7bbd0358b95fcba33dddae8bba.
- Boot SCUS_942.21: load 0x80010000, entry 0x80010A30, payload 0x56800, stack 0x801FFFF0. EXE SHA256 287169026029ea8ff80b9d4e2bdfd8a401e828b7cf7544e0a22c19d41b6cc562. Ghidra raw MIPS payload mapped 0x80010000-0x800667FF; BootEntry disassembled and saved.
- Separate FinFanTacRecomp Git repository scaffolded. 433 initial JAL/entry candidate seeds, not 433 Ghidra-verified boundaries. No per-game hacks.
- Required CTest gate: 58 enabled tests pass; three upstream-disabled tests remain disabled. No new disabled tests. tools/windows.py check reproduces the configured toolchain environment.
- Generated game output through the canonical CLI: 23 C shards, 1398 dispatch entries. Generated OpenBIOS: 651 functions, zero interpreted functions. Four skipped data/table candidates were checked in Ghidra. Generated files never hand-edited.
- Built native RelWithDebInfo Windows x86-64 game with GCC 16.2 and static SDL 3.4.10; launcher and setup wizard included. Also booted standalone recompiled OpenBIOS to its cube shell before native game testing.
- Native FFT reached Squaresoft logo, opening movie, title menu, character creation, church scene and the first battle with unit movement, attacks and Ramza's interactive Move/Act/Wait command menu. TCP bios_info matches OpenBIOS SHA256 fabe498fbf224e4721f12f31b6f5fe0659205e341dc4e5c5f91b9bd1a1011c57; hle_dump reports LLE (recompiled BIOS), boot_skip=0, boot_turbo_active=0 and zero HLE calls.
- Restored and verified the independent Beetle/OpenBIOS oracle, including TCP live memory, cycle watch and event rings. Evidence: framework runtime/build-oracle/verification/oracle-proof.json. The oracle was stopped after verification to avoid duplicate audio.
- PowerA Advantage Wired Controller for Nintendo Switch 2 detected outside the sandbox. USB 20d6:a720; SDL GUID 03007bbfd620000020a7000000000000. Measured A/B/X/Y = buttons 2/1/3/0, L/R/ZL/ZR = 4/5/6/7, minus/plus = 8/9, D-pad hat0 values 1/2/4/8, sticks axes 0/1 and 2/3. SDL accepts the bundled mapping. GDB confirmed player-one controller handle; user confirmed plus and New Game input works after p1_device=auto. Initial failure was keyboard-only routing, not guest emulation.
- Keyboard harness compiled the actual runtime psx_keybinds.c with SDL3 and verified all 18 configured primary/alternate keys produce the expected active-low PS1 pad bits.
- Isolated setup-host build succeeded with no generated game code or BIOS backend linked. Package staging/DLL verification succeeded after correcting MSYS2 executable-suffix detection. Archive integrity and content audit pass. A fresh extraction regenerated BIOS/game C from the verified disc, compiled all 478 build steps, and booted headlessly through the opening movie with the correct OpenBIOS hash, zero HLE calls and no reported failure. Package executable DLL loading was checked with PATH restricted to Windows/System32; setup-host mode correctly reports that Generate & Rebuild is required. No GUI wizard completion is claimed.

## Verified framework/tooling corrections

Rendering follow-up: traced the active software path from guest/GTE submission
through GP0, triangle rasterization, VRAM scanout and SDL composition. The
reported comb artifact was affine UV interpolation tied to rounded coverage
edges, not interlaced output. Corrected both textured-triangle paths using
Beetle-compatible fixed-point attribute planes. All 116 procedural oracle
comparisons now match exactly (previously 256,930 differing pixels). Four
focused runtime CTests pass, and the required 58 enabled emitter tests pass.
New Game text, church windows and the first battle were visually inspected.

Optional **16:9 3D View** now uses a game-owned mod activation plugin and the
framework's separate native-wide surfaces. No guest projection or canonical
VRAM changes. A full-display vertical-gradient backdrop is continued into the
new margins with strict geometry/color/mask gates. Verified church scenes,
first battle, four camera rotations, battle interface and composed 16:9 output.
Menus/prologue retain 4:3; the explicit 24-bit FMV presentation gate is retained.
The feature ships off by default in the experimental channel; later maps and
transitions need broader playtesting. See RENDERING.md for the detailed scope.

The overlay compiler now enforces the runtime loader's actual 2 MiB RAM limit. The stale dirty-text test now executes the actual guard and checks full-function dirty ranges, backedges, data gaps and restoration; runtime semantics were retained. AOT fixtures use the canonical cache namespace. Standalone emitter builds produce the real overlay source hash. Windows fixtures explicitly preserve expected bytes/UTF-8. Python canonicalizes conflicting PATH/Path environment entries. The runtime optionally loads an exe-relative SDL gamecontrollerdb.txt before SDL initialization, preserving explicit player overrides. MSYS2 packaging preserves the .exe suffix so DLL staging recognizes the Windows host.

## Remaining gates

The rendering-fix3 follow-up verifies the battle splash corners and terrain
beneath the command-menu backdrop using OpenBIOS LLE / OpenGL 2x. GP0 captures
confirmed vertical clipping and deferred-batch mirror-state faults. Both are
corrected in the wide-surface renderer; five focused runtime tests and all 58
enabled emitter tests pass. See RENDERING.md for evidence and backend limits.

The rendering-fix2 follow-up verifies the church fade and smooth background
continuation using OpenBIOS LLE with OpenGL at 2x supersampling. The corrected
transition has no exposed margins while the centre is black, and a clear sky
strip matches across the original screen boundary in 190/190 sampled rows.
Five focused runtime tests and all 58 enabled emitter tests pass. See the
follow-up section of RENDERING.md for evidence and backend limits.

Refreshed rendering package: `dist/fft-0.1.0-windows-x86_64-rendering.zip`,
77,253,336 bytes, SHA256
`7d3cd431063a18528f1e0d8c143c55fde4758761cc92de9e097e8686c6a3a241`.
The isolated setup host compiled all 428 steps. Archive integrity, source/mod
presence, OpenBIOS hashes and private-data exclusions pass. Windows DLL loading
passes with PATH restricted to System32; the host correctly requires local
generation. This update did not repeat the earlier full extracted-disc rebuild
or claim completion of the clean-machine GUI wizard gate.

First battle is running; extended gameplay and save/load round trips are not yet verified. Switch, PS4, PS5 and Xbox physical hardware tests, Switch 2 stick clicks/extra buttons, rumble and wireless modes remain unverified. End-to-end setup wizard Generate & Rebuild on a clean Windows installation is pending. AMD hardware and separate Windows 10/11 systems have not been tested. Do not call this a finished compatibility release.

Local screenshots, Ghidra programs, pad-event evidence and save data are ignored under verification/ and disc/. The public source and setup kit exclude disc data, game-generated C, game-linked executables, captures, cards and game assets. The package source snapshot excludes tracked framework cards, game screenshots and sample game box art.

## Public-source preparation (2026-09-03)

The game configuration now locks digital controller mode and disables hybrid
mode as requested. This changes configuration only; the existing rendering and
controller bindings remain intact. Public-source game/disc metadata use relative
paths. A reviewed patch reconstructs all 34 local framework source/test changes
from the pinned upstream base, checked against the working implementation using
an isolated pristine Git index. No private session log is included in that patch.
The root staged-source audit checks private-data exclusions and patch identity.
Public preparation does not claim extended gameplay or new physical controller
validation, and no remote repository or push has been created.

This preparation reran all 58 enabled emitter tests successfully (three existing
upstream-disabled tests unchanged). The staged audit passed for 42 text files
and two pinned submodule links. Both upstream commit pins were fetched through
the public GitHub API without authentication. Representative disc, generated
code, card, capture, build, credential and release paths all match ignore rules.
