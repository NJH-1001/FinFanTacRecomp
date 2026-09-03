"""Check the exact Git index intended for publication; never scan local dumps."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
TOP_FILES = {
    '.gitattributes', '.gitignore', '.gitmodules', 'CMakeLists.txt', 'README.md',
    'RENDERING.md', 'VERIFICATION.md', 'PUBLICATION.md', 'THIRD_PARTY.md', 'RELEASE_NOTES.md', 'VERSION',
    'catalog_identity.json', 'disc_probe.json', 'framework_pins.txt', 'game.toml',
    'game_options.toml', 'gamecontrollerdb.txt', 'keybinds.ini', 'codegen_setup.c',
    'codegen_setup.h', 'psx_symbols.h', 'symbols.toml',
}
TOP_DIRS = {'LICENSES', 'mods', 'seeds', 'src', 'scripts', 'tools', 'patches', '.github'}
FORBIDDEN = {'.bin', '.cue', '.iso', '.chd', '.mcd', '.mcr', '.sav', '.state',
             '.exe', '.dll', '.wav', '.png', '.jpg', '.jpeg', '.bmp', '.mp4',
             '.webm', '.zip', '.pem', '.key', '.pfx', '.p12', '.dmp', '.pyc'}


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def main():
    entries = [entry.split(b'\t', 1) for entry in git('ls-files', '--stage', '-z').split(b'\0') if entry]
    files = {}
    links = {}
    errors = []
    for metadata, raw_name in entries:
        mode, oid, stage = metadata.decode().split()
        name = raw_name.decode('utf-8')
        if stage != '0':
            errors.append(f'Unmerged index entry: {name}')
        if mode == '160000':
            links[name] = oid
            continue
        path = PurePosixPath(name)
        if (name not in TOP_FILES and path.parts[0] not in TOP_DIRS) or path.suffix.lower() in FORBIDDEN:
            errors.append(f'Unreviewed or private path: {name}')
        if mode not in {'100644', '100755'}:
            errors.append(f'Unexpected file mode: {name}')
        data = git('show', ':' + name)
        files[name] = data
        if b'\0' in data or len(data) > 2_000_000:
            errors.append(f'Binary or oversized content: {name}')
        text = data.decode('utf-8', errors='replace')
        patterns = [r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
                    r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{30,}',
                    r'AKIA[0-9A-Z]{16}', r'[A-Za-z]:[/\\]Users[/\\][^\s"<>]+']
        if any(re.search(pattern, text) for pattern in patterns):
            errors.append(f'Credential or personal-path pattern: {name}')
    pins = dict(line.split('=', 1) for line in files['framework_pins.txt'].decode().splitlines() if line)
    if links != pins:
        errors.append('Gitlinks differ from the reviewed dependency pins')
    config = tomllib.loads(files['game.toml'].decode())
    controller = config['controller']
    if not (controller['default_mode'] == 'digital' and controller['lock_mode'] is True
            and controller['allow_hybrid'] is False):
        errors.append('Controller configuration does not match the requested digital lock')
    if config['game']['disc'] != 'disc/Final Fantasy Tactics (USA).cue':
        errors.append('Public disc path must be relative')
    manifest = json.loads(files['patches/manifest.json'])
    if hashlib.sha256(files['patches/psxrecomp-fft.patch']).hexdigest() != manifest['patch_sha256']:
        errors.append('Framework patch checksum mismatch')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(files)} staged text files and {len(links)} pinned submodules; '
          'private-data, credential-pattern, controller and patch-identity checks passed.')


if __name__ == '__main__':
    main()
