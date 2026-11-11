import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_release import check
from query import search
from render import render
from sync import FIELDS


class PublicCompanionTests(unittest.TestCase):
    def test_exact_public_boundary_and_original_hashes(self):
        self.assertGreater(check(ROOT), 10)

    def test_sample_is_six_sourced_uncertain_planning_records(self):
        rows = list(search(ROOT / 'data/catalogue.ndjson', country='IE'))
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({r['id'] for r in rows}), 6)
        for row in rows:
            self.assertEqual(set(row), FIELDS)
            self.assertEqual(row['status'], 'approved')
            self.assertIsNone(row['opportunity'])
            self.assertTrue(row['sources'])
            self.assertIn('1,500', row['facts'][0]['value'].replace('1500', '1,500'))
        self.assertEqual(len(list(search(ROOT / 'data/catalogue.ndjson', term='Killala'))), 1)
        self.assertEqual(list(search(ROOT / 'data/catalogue.ndjson', country='US')), [])

    def test_every_sample_has_readable_html_and_explicit_unknowns(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'site'
            self.assertEqual(render(ROOT / 'data/catalogue.ndjson', target), 6)
            pages = list(target.rglob('index.html'))
            self.assertEqual(len(pages), 7)
            for page in pages:
                html = page.read_text()
                self.assertIn('noindex,follow', html)
                self.assertIn('rel="canonical"', html)
                self.assertNotIn('password', html)
            self.assertEqual(sum('Probability not assessed' in p.read_text() for p in pages), 6)

    def test_unknown_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            import shutil
            target = Path(temporary) / 'copy'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__', '.git'))
            (target / '.env.production').write_text('must never publish')
            with self.assertRaises(ValueError):
                check(target)


if __name__ == '__main__': unittest.main()
