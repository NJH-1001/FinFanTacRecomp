# Public source and release policy

The Git index contains the reviewed game project and pinned submodule links.
The framework patch preserves the locally verified fixes without committing
the shared framework checkout. Run `python tools/public_audit.py` immediately
before committing; it checks the staged bytes rather than the working tree.
The same audit runs on GitHub pushes and pull requests without loading a disc.

Local `disc/`, `generated/`, `verification/`, builds, captures, memory cards,
credentials and package archives are ignored. Do not force-add them or publish
the locally generated game executable. Seeds, symbol addresses and disc hashes
are identification metadata, not copies of game instructions or assets.

Before each push, review `git diff --cached --stat` and run the staged audit.
Keep upstream license notices intact. Source publication and release assets
must not include locally generated game output or private evidence.

After cloning, run `python tools/bootstrap.py` to fetch the two pinned source
dependencies and apply the reviewed framework patch. The optional netplay and
rewind dependencies are not required by this single-player build. Supply a legal
disc locally and follow README.md. Runtime verification covers the opening
scenes and first battle; see VERIFICATION.md for the remaining test scope.

Release ZIPs are separate from Git source publication. Build an isolated setup
host using `tools/package_windows.py`; it intentionally refuses to reuse an
existing snapshot. Inspect the resulting archive before uploading it. The public v0.1.0 setup kit includes the final locked-digital controller
defaults. Older local rendering-fix ZIPs should not be uploaded as this release.
