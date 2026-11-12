"""Render a public snapshot as standalone HTML, without the private application."""
import argparse
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

CSS = 'body{margin:0;background:#f5f8fa;color:#142b35;font:16px/1.7 system-ui}main{max-width:1060px;margin:auto;padding:36px 22px}header{background:#10252e;color:white;padding:30px}h1{font-size:clamp(1.8rem,4vw,3rem);line-height:1.15}h2{margin-top:34px}a{color:#087c9c}header a{color:#8bd6eb}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}.card{background:white;border:1px solid #d9e3e8;border-radius:12px;padding:20px}small{color:#536e79}dt{font-weight:650}dd{margin:0 0 12px}nav{display:flex;flex-wrap:wrap;gap:20px}footer{border-top:1px solid #cddbe2;margin-top:32px;padding-top:18px}'


def safe_url(value):
    parsed = urlsplit(value or '')
    return value if parsed.scheme in {'http', 'https'} and parsed.hostname and not parsed.username else ''


def document(title, body, canonical, description, *, indexable=False, metadata=None):
    schema = json.dumps(metadata or {}, ensure_ascii=False).replace('<', '\\u003c')
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Elora Land &amp; Grid</title><meta name="description" content="{escape(description, quote=True)}"><link rel="canonical" href="{escape(canonical, quote=True)}"><meta name="robots" content="{"index" if indexable else "noindex"},follow"><style>{CSS}</style><script type="application/ld+json">{schema}</script></head><body><header><nav><a href="/land-grid/">Land &amp; Grid</a><a href="https://eloragrid.ai/land-grid">Interactive map</a><a href="https://eloragrid.ai/land-grid/methodology">Methodology</a></nav></header><main>{body}<footer>Elora Grid research. Source dates and limitations apply. Nearby infrastructure does not establish a connection, available capacity or open procurement.</footer></main></body></html>'


def render(snapshot, destination, *, indexable=False):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    rows = [json.loads(line) for line in Path(snapshot).read_text().splitlines() if line.strip()]
    cards = []
    for row in rows:
        path = urlsplit(row['url']).path
        if not path.startswith('/land-grid/') or '..' in path or not row['slug'].replace('-', '').replace('_', '').isalnum():
            raise ValueError('Unsafe public entity path.')
        target = destination / path.lstrip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        sources = ''.join(f'<li><a href="{escape(safe_url(s["url"]), quote=True)}">{escape(s["title"])}</a> — {escape(s["note"])}</li>' for s in row['sources'])
        paragraphs = ''.join(f'<h2>{escape(p["heading"])}</h2><p>{escape(p["text"])}</p>' for p in row['paragraphs'])
        body = f'<small>{escape(row["kind"])} · {escape(row["country_name"])}</small><h1>{escape(row["name"])}</h1><p>{escape(row["summary"])}</p><dl><dt>Reported status</dt><dd>{escape(row["status"] or "Unknown")}</dd><dt>Operator</dt><dd>{escape(row["operator"] or "Unknown")}</dd><dt>Evidence reviewed</dt><dd>{escape(row["reviewed_on"] or "Not recorded")}</dd></dl>{paragraphs}'
        brief = row.get('opportunity')
        body += '<h2>Electrical work and project outlook</h2>'
        if brief:
            body += '<p>' + escape(brief['electrical_scope']) + '</p>'
            for party in brief['participants']:
                body += f'<p>{escape(party["name"])} — {escape(party["role"])} ({escape(party["basis"])}). <a href="{escape(safe_url(party["source_url"]), quote=True)}">Source</a></p>'
            estimate = brief['likelihood']
            if estimate:
                body += f'<p>Elora editorial estimate: {estimate["percent"]}% for {escape(estimate["event"])} by {escape(estimate["by"])}. Assessed {escape(estimate["assessed_on"])}.</p><p>{escape(estimate["rationale"])}</p>'
            for news in brief['news']:
                body += f'<h3><a href="{escape(safe_url(news["source_url"]), quote=True)}">{escape(news["title"])}</a></h3><p>{escape(news["published_on"])} · {escape(news["summary"])}</p>'
        if not brief or not brief['likelihood']:
            body += '<p>Probability not assessed. Builder and electrical contractor are unconfirmed unless a sourced role is listed above.</p>'
        body += f'<h2>Sources and dates</h2><ol>{sources}</ol><p>{escape(row["rights"])}</p>'
        target.write_text(document(row['name'], body, row['url'], row['summary'], indexable=indexable, metadata={'@context': 'https://schema.org', '@type': 'WebPage', 'name': row['name'], 'url': row['url'], 'description': row['summary'], 'citation': [s['url'] for s in row['sources']], 'about': {'@type': 'Place', 'name': row['name']}}))
        cards.append(f'<article class="card"><h2><a href="{escape(path, quote=True)}/">{escape(row["name"])}</a></h2><p>{escape(row["summary"])}</p><small>{escape(row["country_name"])} · {escape(row["status"])}</small></article>')
    index = destination / 'land-grid/index.html'
    index.parent.mkdir(exist_ok=True)
    index.write_text(document('Free infrastructure research', '<h1>Land &amp; Grid</h1><p>Source-linked research for electrical engineering teams.</p><div class="cards">' + ''.join(cards) + '</div>', 'https://eloragrid.ai/land-grid', 'Public infrastructure research with original sources, dates and explicit unknowns.', indexable=indexable))
    return len(rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot'); parser.add_argument('output'); parser.add_argument('--indexable', action='store_true')
    args = parser.parse_args()
    print(f'Rendered {render(args.snapshot, args.output, indexable=args.indexable)} entity pages.')
