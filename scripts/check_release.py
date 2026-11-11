"""Validate the exact standalone public-repository boundary and source hashes."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

SECRET = re.compile(rb'(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|AIza[0-9A-Za-z_-]{35}|sk-(?:proj-|live_|test_)[0-9A-Za-z_-]{16,}|gh[pousr]_[0-9A-Za-z]{30,})')


def check(root):
    root = Path(root).resolve()
    names = json.loads((root / 'release-files.json').read_text())
    if len(names) != len(set(names)):
        raise ValueError('Duplicate release paths.')
    for name in names:
        path = root / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f'Unsafe release path: {name}')
        if any(part in {'.git', '.env', 'app', 'backend', 'infra', 'node_modules'} for part in Path(name).parts):
            raise ValueError(f'Private application path: {name}')
        data = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        if SECRET.search(data):
            raise ValueError(f'Credential pattern in {name}')
    expected = set(names) | {'release-files.json'}
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and not any(part in {'.git', '__pycache__'} for part in p.relative_to(root).parts)}
    if actual != expected:
        raise ValueError(f'Unreviewed release contents: added={actual-expected}, missing={expected-actual}')
    release = root / 'data/releases/ireland'
    manifest = json.loads((release / 'manifest.json').read_text())
    for spec in manifest['files']:
        body = (release / spec['path']).read_bytes()
        if len(body) != spec['bytes'] or hashlib.sha256(body).hexdigest() != spec['sha256']:
            raise ValueError('Source release checksum failed.')
    source_rows = [json.loads(line) for line in gzip.open(release / 'records.ndjson.gz', 'rt')]
    if len(source_rows) != manifest['records']:
        raise ValueError('Source count mismatch.')
    source_keys = {'record_id', 'country', 'name', 'category', 'kind', 'stage', 'operator', 'voltage', 'geometry', 'bounds', 'source_ids', 'properties', 'detail'}
    for row in source_rows:
        if set(row) != source_keys or set(row['detail']) != {'stageBasis', 'locationBasis', 'evidence'}:
            raise ValueError('Unexpected raw/private source fields.')
    return len(names) + 1


if __name__ == '__main__':
    print(f'Validated {check(sys.argv[1] if len(sys.argv) > 1 else ".")} public release files.')
