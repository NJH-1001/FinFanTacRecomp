"""Reproducible local Windows bring-up commands; outputs stay untracked."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from bootstrap import prepare


ROOT = Path(__file__).resolve().parents[1]
FW = (ROOT / "psxrecomp").resolve()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=("check", "generate", "build", "run"))
    ap.add_argument("--toolchain", type=Path, default=Path(r"C:\msys64\mingw64\bin"))
    ap.add_argument("--disc", type=Path)
    ap.add_argument("--port", type=int, default=4371)
    args = ap.parse_args()
    prepare()
    # Python canonicalizes Windows environment keys, removing conflicting
    # PATH/Path entries observed in PowerShell-launched CTest subprocesses.
    env = dict(os.environ)
    env["PATH"] = str(args.toolchain) + os.pathsep + env.get("PATH", "")
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PSX_BIOS_HLE"] = "0"

    def run(command, cwd=ROOT):
        subprocess.run(command, cwd=cwd, env=env, check=True)

    if args.action == "check":
        run(["cmake", "-S", "recompiler", "-B", "recompiler/build", "-G", "Ninja",
             "-DCMAKE_BUILD_TYPE=RelWithDebInfo", "-DPSXRECOMP_ENABLE_CHD=OFF",
             "-DCMAKE_C_COMPILER_LAUNCHER=", "-DCMAKE_CXX_COMPILER_LAUNCHER="], FW)
        run(["cmake", "--build", "recompiler/build", "-j8"], FW)
        run(["ctest", "--test-dir", "recompiler/build", "--output-on-failure", "-j8"], FW)
    elif args.action == "generate":
        command = [sys.executable, str(FW / "psxrecomp_cli.py"), "generate",
                   "--config", "game.toml", "--project-root", ".", "--no-toolchain-download"]
        if args.disc:
            command += ["--disc", str(args.disc.resolve())]
        run(command)
    elif args.action == "build":
        prefix = args.toolchain.parent
        run(["cmake", "-S", ".", "-B", "build-windows", "-G", "Ninja",
             "-DCMAKE_BUILD_TYPE=RelWithDebInfo", "-DPSX_GAME_VERSION=0.1.0",
             "-DPSX_DEBUG_TOOLS=ON", "-DPSX_RECOMP_UI=ON", "-DPSX_SDL_BACKEND=SDL3",
             "-DCMAKE_DISABLE_FIND_PACKAGE_SDL3=ON",
             "-DPSX_ENABLE_VULKAN=OFF", "-DBUILD_TESTING=OFF",
             "-DPSX_DEPS_OFFLINE=OFF", "-DPSXRECOMP_BIOS_STEMS=OpenBIOS",
             "-DCMAKE_C_COMPILER_LAUNCHER=", "-DCMAKE_CXX_COMPILER_LAUNCHER=",
             "-DZLIB_INCLUDE_DIR=" + (prefix / "include").as_posix(),
             "-DZLIB_LIBRARY=" + (prefix / "lib/libz.a").as_posix()])
        run(["cmake", "--build", "build-windows", "--target", "psx-runtime", "-j8"])
        for name in ("libstdc++-6.dll", "libgcc_s_seh-1.dll", "libwinpthread-1.dll"):
            shutil.copy2(args.toolchain / name, ROOT / "build-windows" / name)
    else:
        command = [str(ROOT / "build-windows/Final_Fantasy_Tactics_Recompiled.exe"),
                   "--game", str(ROOT / "game.toml"), "--bios", str(FW / "bios/openbios.bin"),
                   "--no-launcher", "--debug-port", str(args.port),
                   "--memcard-dir", str(ROOT / "saves")]
        if args.disc:
            command += ["--disc", str(args.disc.resolve())]
        run(command)


if __name__ == "__main__":
    main()
