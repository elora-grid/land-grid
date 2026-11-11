"""Download only the anonymous public catalogue, without an app login or token."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

FIELDS = {'id', 'slug', 'kind', 'name', 'url', 'map_url', 'country', 'country_name', 'region', 'region_name', 'locality', 'address', 'operator', 'status', 'geometry', 'summary', 'location_uncertainty', 'paragraphs', 'facts', 'metrics', 'sources', 'opportunity', 'reviewed_on', 'updated_at', 'rights'}


def sync(base, target):
    if base not in {'https://eloragrid.ai', 'https://app.eloragrid.ai'}:
        raise ValueError('Use the fixed public Elora catalogue host.')
    items, seen, expected, revision = [], set(), None, None
    for number in range(1, 1001):
        request = Request(f'{base}/land-grid/catalogue.json?page={number}&limit=500', headers={'Accept': 'application/json', 'User-Agent': 'Elora-LandGrid-Public-Snapshot/1.0'})
        with urlopen(request, timeout=30) as response:
            if response.url.split('/')[2] != base.split('/')[2]:
                raise ValueError('Unexpected upstream redirect.')
            body = response.read(16 * 1024 * 1024 + 1)
        if len(body) > 16 * 1024 * 1024:
            raise ValueError('Catalogue page too large.')
        packet = json.loads(body)
        if packet.get('format') != 'elora-land-grid-public-v1' or packet['page'] != number:
            raise ValueError('Unsupported public catalogue contract.')
        revision = packet['revision'] if revision is None else revision
        if packet['revision'] != revision:
            raise ValueError('Public content changed during export; retry the snapshot.')
        expected = packet['total'] if expected is None else expected
        if packet['total'] != expected:
            raise ValueError('Publication changed during export; retry the snapshot.')
        for item in packet['items']:
            if set(item) != FIELDS or item['id'] in seen:
                raise ValueError('Unknown fields or duplicate public identity.')
            seen.add(item['id']); items.append(item)
        if packet['next_page'] is None:
            break
        if packet['next_page'] != number + 1:
            raise ValueError('Invalid pagination sequence.')
    if len(items) != expected:
        raise ValueError('Incomplete snapshot; previous output preserved.')
    # Exclusive creation preserves the prior snapshot on failure or a mistyped path.
    with Path(target).open('x', encoding='utf8') as output:
        for item in items:
            output.write(json.dumps(item, ensure_ascii=False, allow_nan=False) + '\n')
    return len(items)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output'); parser.add_argument('--base-url', default='https://eloragrid.ai')
    args = parser.parse_args()
    print(f'Exported {sync(args.base_url, args.output)} public entities. Review per-source rights before redistributing.')
