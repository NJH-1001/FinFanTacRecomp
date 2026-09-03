# Rendering investigation — 2026-09-03

## Artifact and cause

The reported comb pattern is a texture-coordinate interpolation error in the
software triangle rasterizer. It is visible in native VRAM, before window
scaling. The inspected prologue and church frames use progressive 256 × 240,
15-bit output; GPUSTAT's interlace flag is clear. Applying a deinterlacing
filter would hide symptoms without correcting the rendered pixels.

Both textured-triangle paths interpolated UVs along floating-point triangle
edges, then interpolated between those values using rounded integer scanline
coverage endpoints. As an edge crosses successive pixel columns, that changes
the texture's horizontal position from row to row. Glyphs and near-vertical
window textures make the resulting comb especially obvious.

`gpu_sw_attributes.h` now computes the PS1 attribute plane independently of
coverage: signed 12-fraction-bit derivatives, wrapping 8.24 accumulation,
half-texel bias and the original-vertex tie ordering used by Beetle. Nearest
sampling takes the integer texel directly from the accumulator. The correction
is shared by flat-textured and Gouraud-textured triangles. No guest functions,
textures, executable bytes or generated C were edited.

## Path reviewed

| Stage | Implementation | Finding / action |
|---|---|---|
| Guest geometry and submission | Recompiled CPU / GTE; SDK DMA queue inspected in Ghidra | Preserve guest projection and instruction behavior. Live DMA attribution identifies submission, not necessarily the original packet author. |
| GPU command transport | `runtime/src/dma.c`, GP0 FIFO in `gpu.c` | Captured complete GP0 frames through TCP; commands and draw state reach the decoder. |
| Primitive decoding | `gpu.c` polygon handlers | Decode colors, vertices, UV/CLUT/tpage, offset, clipping, masks and transparency; split quads into two triangles. No decoder change needed for the texture fault. |
| Backend dispatch | `gpu_render.c` | Selected game default is software. GL/Vulkan are separate renderers, not used as substitutes for verification. |
| Rasterization | `gpu_sw_renderer.c`, `gpu_sw_edges.h`, `gpu_sw_attributes.h` | Coverage stays unchanged; fix affine UV evaluation in both textured-triangle paths. Texture lookup, palette decode and blend/mask behavior are retained. |
| Framebuffers | Canonical 1024 × 512 VRAM and optional software mirrors | Drawing and display origins remain separate. Native-wide uses its own wider surfaces rather than reading into the adjacent guest framebuffer. |
| Scanout | `gpu_get_display_info`, `gpu_display_pixel_argb`, `display_scanout.h` | Use GP1-selected rectangle and pixel depth. Inspected artifact frames are progressive; no field weaving is involved. |
| Movies | MDEC uploads and 24-bit scanout in `main.cpp` | Retain original display canvas and 4:3 presentation. No movie-processing change. |
| Window presentation | `main.cpp`, SDL texture upload / destination rectangle | Capture the composed output as well as native pixels; scaling magnified the fault but did not create it. |

This is an end-to-end investigation of the active software path, not a claim
of exhaustive correctness for every backend or optional enhancement. PGXP
perspective correction, bilinear texture filtering and higher internal scales
have separate paths and are not covered by the native oracle comparison.

## Independent verification

Beetle core: `5759277be50052b9f3f388578bf56cc7899d833f`.
Reference implementation: `mednafen/psx/gpu_polygon.cpp`, specifically
`CalcIDeltas`, `DrawTriangle`, and `DrawSpan`.

The TCP `gpu_probe` runs actual Beetle GPU commands against a procedural texture,
saving/restoring the complete core around each probe. The native side loads a
DLL compiled from the actual software rasterizer. The 116 cases cover raw flat
and raw Gouraud textured triangles, six vertex permutations, clipping, negative
coordinates and texture wrapping. Before: all 116 failed, with 256,930 different
pixels. After: all 116 pass, with zero different pixels. This isolates UV and
coverage behavior; it does not certify Gouraud color modulation or every GPU
operation. Asset-free oracle hashes are retained as a CTest regression fixture.

Required emitter gate: 58 enabled tests pass; three upstream-disabled tests
remain unchanged. Focused runtime gates cover primitive rejection, edge
coverage, the Beetle raster fixture and wide-gradient eligibility.

Private evidence remains under ignored `verification/rendering/`: pre/post
probe results, GP0 frame captures, live GPU state, Ghidra overlay snapshots,
and native/composed screenshots. No game captures are bundled with this report.

## Optional 16:9 view

The game-owned `fft.widescreen` activation plugin selects 16:9 through the
framework's mod API. Native-wide mode preserves guest projection and canonical
VRAM, and renders additional scenery into a separate surface. At 256 × 240 this
surface is 342 × 240, adding 43 native columns on each side. Presentation maps
that surface to 16:9 with the game's pixel proportions retained.

The existing GTE scene classifier selects 3D scenes, with its normal 45-frame
hysteresis. Menus and prologue screens use 4:3; 24-bit FMVs are explicitly pinned
to 4:3. No guest mode addresses, culling patches or generated-code overrides are
installed. UI elements retain their authored layout, centered in the wider view.

First-battle testing exposed a full-screen vertical sky gradient ending at the
original right edge. A narrowly gated, opt-in renderer operation continues each
rendered gradient row into the reveal margins. It accepts only opaque,
axis-aligned G4s covering the entire display-sized draw area with equal colors
across each horizontal edge, without mask operations or rejected triangles.
It writes only the separate wide margins; canonical VRAM is untouched. Partial
dialogs, horizontal gradients and projected world polygons do not qualify.

Opening church scenes, the first battle, all four camera rotations and Ramza's
Move/Act/Wait interface were visually checked, including composed 16:9 output.
The backdrop margins remain clean through those rotations. The feature is
optional, defaults off, and ships in the experimental channel.

Opening church scenes and the first battle are the visual verification scope.
Later maps, scene-classification transitions and authored off-screen culling
still need broader playtesting; no full-game compatibility claim is made.

## Supersampling and transition follow-up (2026-09-03)

The user's OpenGL 2x settings exposed two separate enhancement faults. The
sky extension read quantized 15-bit VRAM and repeated native rows while the
centre was rendered into an RGBA8 supersampled framebuffer. The GL backend now
continues the actual rendered edge columns into the margins with two GPU blits,
preserving color precision and every supersampled row. The software backend
likewise reads its actual high-resolution rows. Vulkan retains the earlier
native-row gradient fallback; smooth Vulkan gradients are not claimed here.

TCP captures of the first church transition identified an untextured subtractive
fade quad: post-offset vertices (0,240), (256,240), (-128,496), (256,496), color
FFFFFF, blend mode 2. Its sloping edge fully covers the original viewport but
leaves parts of the expanded margins exposed. The compositor now recognizes a
uniform flat quad whose two horizontal edges cover the full display-sized draw
area. Its original canonical triangles still execute unchanged; only the wide
mirror is replaced by one full-width filter, clipped to that framebuffer's
vertical band. This uses existing blend implementations in SW, GL and Vulkan.
Ghidra inspection of the live overlay confirms the recorded DMA PC is not the
fade packet's author; no guest address hook or generated-code change is used.

OpenGL flat batches now flush before changing wide targets and before sampling
the gradient. Otherwise queued triangles could land in a later target or leave
the sampled gradient stale. The high-resolution diagnostic readback now reads
the actual GL framebuffer instead of falling back to native-resolution VRAM.

OpenBIOS LLE / OpenGL 2x verification: captured 404 baseline and 430 corrected
frames through TCP across the first church transition. The baseline had 19
sampled frames with black centres and exposed side fragments; the corrected
sequence had zero (33 sampled fully black wide frames). The outdoor sky's
inspected clear strip has exact color continuity across the old 4:3 boundary
in all 190 sampled rows. The baseline strip matched in zero of 190 rows.
These are pixel checks of clear sky strips at different camera angles, not
whole-scene deterministic comparisons. Composed window output was also viewed.

Five focused runtime tests pass, including the 116-case Beetle raster fixture,
full-screen eligibility, 12 gradient surface cases across scales 1/2/4 and
both framebuffer bands/bases, and 48 fade cases covering all four blend modes.
The surface tests assert no canonical VRAM/high-resolution changes and no
writes into the other framebuffer band. All 58 enabled emitter tests pass;
three pre-existing disabled tests remain unchanged. Private captures and GPU
packets are under ignored verification/wide-ssaa and are excluded from packages.

## Battle splash and command-menu follow-up (2026-09-03, fix3)

Real GP0 captures identified two wide-surface faults. The battle splash sends
an alpha-blended 256x256 flat filter into a 256x240 draw area. The direct GL
wide overlay ignored the vertical draw-area clip, spilling 16 rows into the
other framebuffer band. It now expands only X and preserves the guest Y clip.
Vulkan's equivalent direct overlay now retains its existing band scissor too.
The surface regression exercises oversized 256-row filters against 240-row
bands at scales 1/2/4, both framebuffer bases/bands and all four blend modes.

The command menu sends a full-width subtractive rectangle and one-row soft
edges after queued flat terrain triangles. GL mirror suppression was enabled
before those earlier triangles flushed, losing terrain in the margins; the
filter itself could later mirror twice. Earlier geometry now flushes before
suppression, and canonical filter triangles flush while suppression is active.
The separate wide filter then executes once. Canonical guest drawing, game
code, projection and authored packet order are unchanged.

OpenBIOS LLE / OpenGL 2x live verification captured 309 baseline and 283 corrected
frames through the first battle splash. The corrected sequence has clean top
corners. At Ramza's first command menu, the lower-left terrain face remains
present; entering Move and returning to the menu preserves it. Screenshots and
real GP0 packets are private under ignored verification/wide-ui. These are
visual comparisons of the reported scenes, not deterministic full-frame parity.
Ghidra MCP was connected and the recorded guest PC was disassembled; no guest
address hook or generated-code edit was introduced.

Five focused runtime tests pass, including the 116-case Beetle raster fixture;
all 58 enabled emitter tests pass (three existing disabled tests unchanged).
Live validation covers OpenGL at 2x; Vulkan's scissor correction is build-checked
but has not received equivalent live scene verification. Later battles remain
outside this verification scope.
