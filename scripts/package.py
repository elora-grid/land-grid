"""Create a fresh public-repository directory from the reviewed file allowlist."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from check_release import check


def package(root, destination):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    check(root)
    destination.mkdir(parents=True, exist_ok=False)
    names = json.loads((root / 'release-files.json').read_text()) + ['release-files.json']
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
    check(destination)
    digest = hashlib.sha256(''.join(name + '\0' + hashlib.sha256((destination/name).read_bytes()).hexdigest() + '\n' for name in sorted(names)).encode()).hexdigest()
    return {'files': len(names), 'content_sha256': digest, 'path': str(destination)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination'); args = parser.parse_args()
    print(json.dumps(package(Path(__file__).resolve().parents[1], args.destination), indent=2))
