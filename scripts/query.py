"""Search a public NDJSON snapshot locally; uses no credentials or network."""
import argparse
import json
from pathlib import Path


def search(path, *, kind=None, country=None, term=''):
    with Path(path).open(encoding='utf8') as source:
        for line in source:
            row = json.loads(line)
            if kind and row['kind'] != kind: continue
            if country and row['country'] != country: continue
            if term.casefold() not in ' '.join(str(row.get(k) or '') for k in ['name', 'operator', 'locality', 'summary']).casefold(): continue
            yield row


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot'); parser.add_argument('--kind', choices=['data-centres', 'mines', 'substations'])
    parser.add_argument('--country'); parser.add_argument('--q', default=''); parser.add_argument('--limit', type=int, default=20)
    args = parser.parse_args()
    for index, row in enumerate(search(args.snapshot, kind=args.kind, country=args.country, term=args.q)):
        if index >= max(0, min(args.limit, 500)): break
        print(json.dumps(row, ensure_ascii=False))
