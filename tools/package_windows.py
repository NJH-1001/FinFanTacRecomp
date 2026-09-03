"""Build a source-only setup host in isolation; never link local game output."""
import os
from pathlib import Path
import shutil
import subprocess
from bootstrap import prepare

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "build-package-src"
TOOLCHAIN = Path(r"C:\msys64\mingw64")

# Reviewed source additions that are not in the upstream index yet. Never
# recursively copy a working tree: its build/analysis folders contain game data.
FRAMEWORK_SOURCE_ADDITIONS = (
    "docs/beetle-oracle.md", "docs/beetle_oracle_hooks.patch",
    "runtime/src/beetle_observe.cpp", "runtime/src/gpu_sw_attributes.h",
    "runtime/src/gpu_wide_gradient.h", "runtime/tests/gpu_raster_beetle.json",
    "runtime/tests/gpu_sw_probe_support.c", "runtime/tests/test_gpu_wide_gradient.c",
    "runtime/tests/test_gpu_wide_gradient_surface.py",
    "tools/build_beetle_oracle.ps1", "tools/verify_beetle_oracle.py",
    "tools/verify_gpu_raster.py",
)


def tracked_snapshot(source, destination):
    names = subprocess.check_output([
        "git", "-c", "safe.directory=" + source.as_posix(), "-C", str(source),
        "ls-files", "-z"], text=True).split("\0")
    for name in names:
        if not name:
            continue
        rel = Path(name)
        # Framework documentation contains game screenshots and tracked cards.
        # They are never part of this SDK source snapshot.
        if (name.startswith(("docs/assets/", ".github/")) or
                ("boxart" in name.lower() and rel.suffix.lower() in {".tga", ".png", ".jpg", ".jpeg"}) or
                rel.suffix.lower() in {".mcd", ".mcr", ".sav", ".state", ".cue", ".iso", ".chd"} or
                (rel.suffix.lower() == ".bin" and name != "bios/openbios.bin")):
            continue
        src = source / rel
        if not src.is_file():
            continue
        dst = destination / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main():
    prepare()
    if SNAPSHOT.exists():
        raise SystemExit(f"Snapshot already exists; review it before rebuilding: {SNAPSHOT}")
    SNAPSHOT.mkdir()
    tracked_snapshot((ROOT / "psxrecomp").resolve(), SNAPSHOT / "psxrecomp")
    for name in FRAMEWORK_SOURCE_ADDITIONS:
        target = SNAPSHOT / "psxrecomp" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "psxrecomp" / name, target)
    tracked_snapshot((ROOT / "recomp-ui").resolve(), SNAPSHOT / "recomp-ui")
    for name in ("CMakeLists.txt", "game.toml", "game_options.toml", "VERSION",
                 "codegen_setup.c", "codegen_setup.h", "README.md", "RENDERING.md", "VERIFICATION.md", "keybinds.ini",
                 "gamecontrollerdb.txt", "framework_pins.txt", "psx_symbols.h"):
        shutil.copy2(ROOT / name, SNAPSHOT / name)
    for name in ("seeds", "mods", "scripts", "tools", "LICENSES", "src"):
        shutil.copytree(ROOT / name, SNAPSHOT / name, ignore=shutil.ignore_patterns("__pycache__"))
    config = SNAPSHOT / "game.toml"
    lines = config.read_text().splitlines()
    config.write_text("\n".join('disc = "disc/Final Fantasy Tactics (USA).cue"'
                                 if line.startswith("disc = ") else line for line in lines) + "\n")
    archive = "third_party/SDL3-3.4.10.tar.gz"
    if (ROOT / "psxrecomp" / archive).is_file():
        shutil.copy2(ROOT / "psxrecomp" / archive, SNAPSHOT / "psxrecomp" / archive)
    assert not (SNAPSHOT / "generated").exists()
    assert not (SNAPSHOT / "psxrecomp/generated").exists()
    env = dict(os.environ)
    env["PATH"] = str(TOOLCHAIN / "bin") + os.pathsep + env.get("PATH", "")
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    flags = ["-DCMAKE_BUILD_TYPE=RelWithDebInfo", "-DPSX_GAME_VERSION=0.1.0",
             "-DPSXRECOMP_FORCE_SETUP_HOST=ON", "-DPSXRECOMP_ALLOW_NO_BIOS=ON",
             "-DPSX_RECOMP_UI=ON", "-DPSX_SETUP_WIZARD=ON", "-DPSX_DEBUG_TOOLS=ON",
             "-DPSX_SDL_BACKEND=SDL3", "-DCMAKE_DISABLE_FIND_PACKAGE_SDL3=ON",
             "-DPSX_ENABLE_VULKAN=OFF", "-DBUILD_TESTING=OFF",
             "-DPSX_DEPS_OFFLINE=OFF", "-DCMAKE_C_COMPILER_LAUNCHER=",
             "-DCMAKE_CXX_COMPILER_LAUNCHER=", "-DZLIB_INCLUDE_DIR=" + (TOOLCHAIN / "include").as_posix(),
             "-DZLIB_LIBRARY=" + (TOOLCHAIN / "lib/libz.a").as_posix()]
    for command in (["cmake", "-S", ".", "-B", "build-setup", "-G", "Ninja", *flags],
                    ["cmake", "--build", "build-setup", "--target", "psx-runtime", "-j8"]):
        subprocess.run(command, cwd=SNAPSHOT, env=env, check=True)
    for name in ("libstdc++-6.dll", "libgcc_s_seh-1.dll", "libwinpthread-1.dll"):
        shutil.copy2(TOOLCHAIN / "bin" / name, SNAPSHOT / "build-setup" / name)
    print("Isolated setup host built:", SNAPSHOT / "build-setup")


if __name__ == "__main__":
    main()
