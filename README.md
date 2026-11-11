# Elora Land & Grid — public research and tools

Free infrastructure research for electrical engineering companies investigating data centres, mines and substations. Browse the [canonical tool and map](https://eloragrid.ai/land-grid).

This repository is the public companion: public facts, source attribution, schemas and small reader/export/render tools. It is independently runnable with Python 3.11+. It contains no application backend, login implementation, credentials, customer workspaces, private reports, professional contacts or raw research archives.

## Published sample and live catalogue

The checked-in sample contains **six Irish planning records** cleared for redistribution under CC BY 4.0. These examples do not imply live map additions or current construction. Approval dates are historical observations. Every location has a 1,500 m uncertainty radius. See [data/README.md](data/README.md).

The live release publishes individual data-centre pages. Substations and mines remain visible on the map, with individual pages disabled and excluded from the discovery sitemap. The sample in Git is separate from the live catalogue; API availability does not grant bulk redistribution rights.

The broader European research collection has 1,508 mapped operating/pipeline records plus 42 permit-only locations. It is not included here: most source registers still lack recorded redistribution clearance. Do not replace this sample with an internal database, raw research snapshot or reviewed-data transfer packet.

## Use locally

```sh
python3 scripts/query.py data/catalogue.ndjson --country IE --kind data-centres --q Killala
python3 scripts/render.py data/catalogue.ndjson /tmp/land-grid-preview
python3 -m unittest discover -s tests -v
```

The renderer creates one HTML page per entity and an index under `land-grid/`. Serve its output with any static server. Preview pages default to noindex. `--indexable` is for reviewed publication only. Standalone output does not reproduce the authenticated application or private map workspace.

Download the live public catalogue's published projection:

```sh
python3 scripts/sync.py /tmp/land-grid-current.ndjson
```

No account, cookie, API key or access token is needed. Output uses exclusive creation. Pagination, schema and identity checks must pass before any file is written. Review source rights before adding a new snapshot to Git.

## Query with an LLM

[OpenAPI](openapi.json) documents these anonymous GET endpoints:

- `/land-grid/catalogue.json?q=...&kind=data-centres&country=AU&page=1&limit=100`
- `/land-grid/entities/{slug}.json`
- `/land-grid/entities/{slug}.md`
- `/land-grid/llms.txt`

The [discovery sitemap index](https://eloragrid.ai/land-grid/sitemaps/index.xml) groups published indexable pages by asset type and country. Public directories and entity pages also expose ordinary HTML links. Map links return to the public tool with the selected country and record.

Follow `next_page` until null. The maximum page size is 500. Cite the canonical entity URL, original source and evidence date. Preserve record scope and uncertain locations. Null means unknown. Inventory records, campuses and filings are not interchangeable facility counts.

## Opportunities and likelihoods

Public briefs distinguish developer, operator, main contractor, electrical contractor and network operator. Roles are either reported or inferred, with citations. News uses original short summaries with publication dates and links.

A likelihood is an explicitly reviewed Elora editorial judgement with a percentage, named event, horizon, assessment date, rationale and sources. It is not a calibrated forecast. A planning stage or source-signal score is never automatically converted to a probability. An operating asset or nearby substation does not imply a new contract or available capacity.

## Rights and corrections

The MIT licence applies to code in this repository. The six NPAD source observations retain CC BY 4.0 with attribution to the Department of Housing, Local Government and Heritage. Other linked publications retain their own rights. No blanket third-party data licence is granted.

Use GitHub issues for source-backed corrections to public research. Include the entity ID, canonical URL, changed fact, original source and evidence date; do not include customer documents or private contact information. Security reporting is described in [SECURITY.md](SECURITY.md).
