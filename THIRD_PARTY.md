# Source and dependency notices

This is an unofficial project. Final Fantasy Tactics game code, artwork, music
and disc data are not included. Players supply their own USA SCUS-94221 disc.

- PSXRecomp is pinned in `framework_pins.txt` and uses the PolyForm Noncommercial
  License 1.0.0. Its license is retained in `LICENSES/psxrecomp/LICENSE`. The
  bundled framework patch is a modified version, not an upstream release.
- recomp-ui retains its own license in the pinned submodule's `LICENSE`.
- OpenBIOS retains its MIT notice at `psxrecomp/bios/OpenBIOS.LICENSE`.
- The optional Beetle diagnostic core is separate from the native game runtime;
  its sources and patch retain the core's license and attribution. See
  `psxrecomp/docs/beetle-oracle.md` after bootstrap.
- Compiler runtime and compression-library notices used by Windows setup
  packages are retained under `LICENSES/`.

No blanket license is asserted over third-party components or game data.
This repository does not add a separate license grant for game-owned files;
the repository owner can select one before publication. Public availability
alone should not be described as an unrestricted open-source license.
