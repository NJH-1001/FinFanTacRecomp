"""Initialize pinned dependencies and apply the reviewed FFT framework patch."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(directory, *args, check=True):
    directory = directory.resolve()
    return subprocess.run(
        ["git", "-c", "safe.directory=" + directory.as_posix(), "-C", str(directory), *args],
        check=check, capture_output=True, text=True)


def prepare(check_only=False):
    pins = dict(line.split("=", 1) for line in
                (ROOT / "framework_pins.txt").read_text().splitlines() if line)
    for name, pin in pins.items():
        folder = ROOT / name
        if not (folder / ".git").exists():
            if check_only:
                raise RuntimeError(f"Missing dependency: {name}; run python tools/bootstrap.py")
            git(ROOT, "submodule", "update", "--init", "--", name)
        if git(folder, "rev-parse", "HEAD").stdout.strip() != pin:
            raise RuntimeError(f"{name} does not match framework_pins.txt; preserve local work before changing it")
    manifest = json.loads((ROOT / "patches/manifest.json").read_text())
    patch = ROOT / "patches/psxrecomp-fft.patch"
    if (manifest["framework_base"] != pins["psxrecomp"] or
            hashlib.sha256(patch.read_bytes()).hexdigest() != manifest["patch_sha256"]):
        raise RuntimeError("Framework patch identity check failed")
    fw = ROOT / "psxrecomp"
    if git(fw, "apply", "--reverse", "--check", str(patch), check=False).returncode == 0:
        print("Pinned dependencies and FFT framework patch verified.")
        return
    result = git(fw, "apply", "--check", str(patch), check=False)
    if result.returncode:
        raise RuntimeError("Framework patch conflicts with local edits:\n" + result.stderr)
    if check_only:
        raise RuntimeError("Framework patch is not applied; run python tools/bootstrap.py")
    git(fw, "apply", "--whitespace=nowarn", str(patch))
    print("Applied the reviewed FFT framework patch.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without modifying dependencies")
    try:
        prepare(parser.parse_args().check)
    except (RuntimeError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
