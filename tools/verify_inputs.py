"""Verify a VM input ZIP against its sidecar and per-file handoff inventory."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import sys
import zipfile


def verify(path):
    checksum_path = path.with_suffix(path.suffix + '.sha256')
    parts = checksum_path.read_text(encoding='ascii').strip().split()
    if len(parts) != 2 or parts[1] != path.name:
        raise ValueError('Unexpected checksum sidecar filename')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != parts[0]:
        raise ValueError('ZIP SHA-256 differs from the checksum sidecar')
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive paths')
        for item in archive.infolist():
            name = item.filename
            relative = PurePosixPath(name)
            if (relative.is_absolute() or '..' in relative.parts or '\\' in name
                    or ':' in name or not name or item.is_dir()
                    or (item.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('Unsafe archive path: ' + name)
        manifest = json.loads(archive.read('handoff-manifest.json'))
        if manifest['schema'] != 'desk-helper-training-handoff/1':
            raise ValueError('Unexpected handoff schema')
        if manifest['full_workspace'] or manifest['policy_bundle']:
            raise ValueError('Unexpected handoff scope')
        if set(names) != set(manifest['files']) | {'handoff-manifest.json'}:
            raise ValueError('Archive and declared inventories differ')
        for name, record in manifest['files'].items():
            data = archive.read(name)
            if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
                raise ValueError('Artifact SHA-256 or size differs: ' + name)
    print(f'PASS: ZIP checksum and {len(names)} archive entries; training inputs only.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python verify_inputs.py <handoff.zip>')
    try:
        verify(Path(sys.argv[1]))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        raise SystemExit('FAIL: ' + str(error))
