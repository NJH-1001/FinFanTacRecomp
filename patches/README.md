# Verified framework changes

`psxrecomp-fft.patch` applies to the PSXRecomp commit in `framework_pins.txt`.
It includes the rendering, controller database loading, Windows verification,
packaging and independent Beetle diagnostic changes used for this project.
`manifest.json` records the patch digest and complete affected-file list.

Run `python tools/bootstrap.py` after cloning. It verifies dependency pins,
applies the patch once, and refuses conflicting edits. It does not reset or
overwrite an existing checkout. `--check` performs read-only verification.
The Windows development helper also runs this preparation step.

The patch was applied against a pristine pinned Git index and every resulting
file compared with the locally verified implementation. The procedural raster
fixture contains generated test patterns and hashes, not game pixels or code.
Private session logs are omitted. Existing upstream notices remain intact;
see `THIRD_PARTY.md`. No framework fork or unpublished commit is required.
